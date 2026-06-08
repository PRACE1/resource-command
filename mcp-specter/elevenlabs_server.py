#!/usr/bin/env python3
"""
Specter-Audio MCP Server — v1.0
ElevenLabs voice synthesis wired into Claude Code.
Generates narration, voiceovers, and ambient audio for Specter-Vision.

Requires: ELEVENLABS_API_KEY environment variable
"""

import asyncio
import os
import httpx
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

TOKEN   = os.getenv("ELEVENLABS_API_KEY", "")
API     = "https://api.elevenlabs.io/v1"
OUT_DIR = Path(os.getenv("AUDIO_OUTPUT_DIR",
               str(Path(__file__).parent / "audio_output")))

# ── Voices curated for institutional/sovereign use ────────────────────────────
VOICES = {
    "adam":       {"id": "pNInz6obpgDQGcFmaJgB", "desc": "Deep, authoritative — boardroom narration"},
    "rachel":     {"id": "21m00Tcm4TlvDq8ikWAM", "desc": "Clear, professional — documentary"},
    "domi":       {"id": "AZnzlk1XvdvUeBnXmlld", "desc": "Strong, confident — investor pitch"},
    "bella":      {"id": "EXAVITQu4vr4xnSDxMaL", "desc": "Warm, trustworthy — stakeholder update"},
    "josh":       {"id": "TxGEqnHWrfWFTfGW9XjX", "desc": "Energetic, clear — technical explainer"},
    "arnold":     {"id": "VR6AewLTigWG4xSOukaG", "desc": "Commanding, gravitas — sovereign statement"},
}

server = Server("specter-audio")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="audio_status",
            description="Check ElevenLabs API connection and available voices.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="audio_speak",
            description=(
                "Convert text to speech using ElevenLabs. "
                "Perfect for: investor pitch narration, documentary voiceovers, "
                "Specter-Vision video audio tracks, stakeholder briefings. "
                "Returns path to the generated MP3 file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to synthesize. Can be a full script.",
                    },
                    "voice": {
                        "type": "string",
                        "enum": ["adam", "rachel", "domi", "bella", "josh", "arnold"],
                        "description": "Voice preset. Default: adam (authoritative).",
                        "default": "adam",
                    },
                    "stability": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Voice stability 0-1. Higher = more consistent. Default: 0.5.",
                        "default": 0.5,
                    },
                    "similarity_boost": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Similarity to original voice. Default: 0.75.",
                        "default": 0.75,
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (no extension). Default: auto-generated.",
                    },
                },
                "required": ["text"],
            },
        ),
        types.Tool(
            name="audio_list_voices",
            description="List all available voice presets with descriptions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    async with httpx.AsyncClient(timeout=60.0) as client:

        if name == "audio_status":
            if not TOKEN:
                return [types.TextContent(type="text", text=(
                    "❌ ELEVENLABS_API_KEY not set.\n"
                    "Add it to ~/.claude.json under mcpServers.specter-audio.env"
                ))]
            try:
                r = await client.get(f"{API}/user", headers={"xi-api-key": TOKEN})
                if r.status_code == 401:
                    return [types.TextContent(type="text", text="❌ Invalid API key.")]
                r.raise_for_status()
                data = r.json()
                chars_used  = data.get("subscription", {}).get("character_count", 0)
                chars_limit = data.get("subscription", {}).get("character_limit", 0)
                return [types.TextContent(type="text", text=(
                    f"✅ Specter-Audio ONLINE (ElevenLabs)\n"
                    f"Characters used: {chars_used:,} / {chars_limit:,}\n"
                    f"Voices: adam, rachel, domi, bella, josh, arnold\n"
                    f"Ready for narration and voiceover synthesis."
                ))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Cannot reach ElevenLabs: {e}")]

        elif name == "audio_speak":
            if not TOKEN:
                return [types.TextContent(type="text", text="❌ ELEVENLABS_API_KEY not set.")]

            text       = arguments["text"]
            voice_key  = arguments.get("voice", "adam")
            stability  = arguments.get("stability", 0.5)
            similarity = arguments.get("similarity_boost", 0.75)
            filename   = arguments.get("filename")

            voice_id = VOICES.get(voice_key, VOICES["adam"])["id"]

            OUT_DIR.mkdir(parents=True, exist_ok=True)

            if not filename:
                import time
                filename = f"specter_audio_{int(time.time())}"
            out_path = OUT_DIR / f"{filename}.mp3"

            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity,
                },
            }

            try:
                r = await client.post(
                    f"{API}/text-to-speech/{voice_id}",
                    headers={"xi-api-key": TOKEN, "Content-Type": "application/json"},
                    json=payload,
                    timeout=60.0,
                )
                r.raise_for_status()
                out_path.write_bytes(r.content)

                size_kb = len(r.content) // 1024
                return [types.TextContent(type="text", text=(
                    f"✅ AUDIO GENERATED\n"
                    f"File: {out_path}\n"
                    f"Voice: {voice_key} — {VOICES[voice_key]['desc']}\n"
                    f"Size: {size_kb} KB\n"
                    f"Characters: {len(text):,}\n\n"
                    f"Open the file to preview. Add to Specter-Vision video in your editor."
                ))]
            except httpx.HTTPStatusError as e:
                return [types.TextContent(type="text", text=f"❌ API error {e.response.status_code}: {e.response.text[:200]}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Failed: {e}")]

        elif name == "audio_list_voices":
            lines = ["Specter-Audio Voice Roster:\n"]
            for key, v in VOICES.items():
                lines.append(f"  {key:10} — {v['desc']}")
            lines.append("\nDefault: adam (boardroom narration)")
            return [types.TextContent(type="text", text="\n".join(lines))]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
