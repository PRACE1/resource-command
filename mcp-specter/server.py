#!/usr/bin/env python3
"""
Specter-Vision MCP Server — v3.0  (Replicate Cloud · Full Creative Suite)
Gives Claude direct access to the full Replicate AI media stack:
  • Flux 1.1 Pro  — photorealistic still image generation
  • Flux Dev      — fast image generation / rapid iteration
  • Wan 2.1 14B   — cinematic video (I2V + T2V)
  • Real-ESRGAN   — 4× upscale to 4K
  • Recraft v3    — brand/design/illustration style images

Requires: REPLICATE_API_TOKEN environment variable
"""

import asyncio
import os
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
API   = "https://api.replicate.com/v1"

# ── Model IDs ─────────────────────────────────────────────────────────────────
MODELS = {
    "flux_pro":   "black-forest-labs/flux-1.1-pro",
    "flux_dev":   "black-forest-labs/flux-dev",
    "recraft":    "recraft-ai/recraft-v3",
    "wan_t2v":    "wavespeedai/wan-2.1-t2v-480p",
    "wan_i2v":    "lucataco/wan-2.1-i2v-480p",
    "upscale":    "nightmareai/real-esrgan",
}

# ── Director presets (video) ───────────────────────────────────────────────────
VIDEO_PRESETS = {
    "institutional_hero": {
        "description": "ORACLE vehicle hero shot — anamorphic, Kodak grain, golden hour",
        "num_frames": 81, "sample_steps": 25, "sample_guide_scale": 6.0,
        "suffix": ", anamorphic 2.39:1, Kodak 5219 film grain, golden hour, cinematic depth of field, photorealistic",
    },
    "aerial": {
        "description": "Drone pullback — facility establishing shot",
        "num_frames": 81, "sample_steps": 25, "sample_guide_scale": 6.5,
        "suffix": ", aerial drone pullback, volumetric haze, wide angle, photorealistic, high altitude",
    },
    "macro": {
        "description": "Component closeup — bolts, tolerances, machined detail",
        "num_frames": 49, "sample_steps": 30, "sample_guide_scale": 7.0,
        "suffix": ", extreme macro photography, shallow depth of field, studio lighting, 8K detail",
    },
    "facility": {
        "description": "Ground-level facility walkthrough — processing plant",
        "num_frames": 81, "sample_steps": 25, "sample_guide_scale": 6.0,
        "suffix": ", ground level dolly shot, industrial facility, operational machinery, cinematic",
    },
    "quick": {
        "description": "Fast preview — lower steps, good for prompt testing",
        "num_frames": 33, "sample_steps": 15, "sample_guide_scale": 5.5,
        "suffix": "",
    },
    "custom": {
        "description": "Custom — uses your exact parameters",
        "num_frames": 81, "sample_steps": 25, "sample_guide_scale": 6.0,
        "suffix": "",
    },
}

# ── Image style presets ────────────────────────────────────────────────────────
IMAGE_STYLES = {
    "cinematic":      ", cinematic photography, anamorphic lens, golden hour, photorealistic, 8K",
    "institutional":  ", corporate photography, clean lighting, professional, high-end, editorial",
    "aerial":         ", aerial drone photography, wide angle, volumetric atmosphere, photorealistic",
    "macro":          ", extreme macro photography, studio lighting, shallow DOF, ultra-sharp detail",
    "concept":        ", concept art, detailed illustration, dramatic lighting, epic composition",
    "blueprint":      ", technical blueprint style, white lines on dark blue, engineering diagram, precise",
    "raw":            "",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _h():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


async def _predict(client, model: str, inp: dict) -> dict:
    r = await client.post(f"{API}/models/{model}/predictions",
                          headers=_h(), json={"input": inp}, timeout=90.0)
    r.raise_for_status()
    return r.json()


async def _get(client, pid: str) -> dict:
    r = await client.get(f"{API}/predictions/{pid}", headers=_h(), timeout=30.0)
    r.raise_for_status()
    return r.json()


def _cost(secs):
    return f"~${secs * 0.00140:.3f}" if secs else ""


def _out(pred):
    o = pred.get("output")
    if not o:
        return None
    return o if isinstance(o, str) else (o[0] if isinstance(o, list) else str(o))


# ── MCP Server ────────────────────────────────────────────────────────────────

server = Server("specter-vision")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [

        # ── STATUS ────────────────────────────────────────────────────────────
        types.Tool(
            name="specter_status",
            description="Check Replicate API connection and account status. Always call first.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── IMAGE GENERATION ─────────────────────────────────────────────────
        types.Tool(
            name="specter_image",
            description=(
                "Generate a photorealistic or stylized still image using Flux 1.1 Pro or Recraft v3. "
                "Flux Pro = cinematic photorealism (think: The Garden Arrival quality, architectural, "
                "product hero shots, environments). Recraft = brand/design/illustration. "
                "Returns image URL immediately — typically under 30 seconds.\n\n"
                "Styles: cinematic, institutional, aerial, macro, concept, blueprint, raw."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Detailed image description. More detail = better result."},
                    "style": {
                        "type": "string",
                        "enum": ["cinematic", "institutional", "aerial", "macro", "concept", "blueprint", "raw"],
                        "description": "Visual style preset. Default: cinematic.",
                        "default": "cinematic",
                    },
                    "model": {
                        "type": "string",
                        "enum": ["flux_pro", "flux_dev", "recraft"],
                        "description": "Model: flux_pro (best quality), flux_dev (faster), recraft (brand/design). Default: flux_pro.",
                        "default": "flux_pro",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": ["1:1", "16:9", "21:9", "4:3", "3:4", "9:16"],
                        "description": "Output aspect ratio. Default: 16:9.",
                        "default": "16:9",
                    },
                    "width": {"type": "integer", "description": "Width in pixels (flux_dev only). Default 1280."},
                    "height": {"type": "integer", "description": "Height in pixels (flux_dev only). Default 720."},
                },
                "required": ["prompt"],
            },
        ),

        # ── VIDEO GENERATION ─────────────────────────────────────────────────
        types.Tool(
            name="specter_generate",
            description=(
                "Generate a cinematic video using Wan 2.1 14B I2V/T2V on Replicate H100s. "
                "Returns prediction_id — poll with specter_job_status every 20s. "
                "Takes 3–6 minutes. Tip: generate a still with specter_image first, then animate it.\n\n"
                "Presets: institutional_hero, aerial, macro, facility, quick, custom."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Cinematic prompt."},
                    "image_url": {"type": "string", "description": "Input image URL for I2V mode. If omitted: T2V."},
                    "preset": {
                        "type": "string",
                        "enum": ["institutional_hero", "aerial", "macro", "facility", "quick", "custom"],
                        "default": "institutional_hero",
                    },
                    "seconds": {"type": "number", "minimum": 1, "maximum": 8},
                    "steps": {"type": "integer", "minimum": 10, "maximum": 50},
                    "guidance_scale": {"type": "number", "minimum": 1.0, "maximum": 10.0},
                },
                "required": ["prompt"],
            },
        ),

        # ── UPSCALE ───────────────────────────────────────────────────────────
        types.Tool(
            name="specter_upscale",
            description=(
                "Upscale any image to 4K using Real-ESRGAN. "
                "Perfect for taking a Flux-generated still or video frame and making it "
                "boardroom-presentation ready. Returns upscaled image URL in ~15 seconds."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "URL of the image to upscale."},
                    "scale": {
                        "type": "integer",
                        "enum": [2, 4],
                        "description": "Upscale factor: 2× or 4×. Default: 4.",
                        "default": 4,
                    },
                    "face_enhance": {
                        "type": "boolean",
                        "description": "Apply face enhancement (GFPGAN). Default: false.",
                        "default": False,
                    },
                },
                "required": ["image_url"],
            },
        ),

        # ── JOB STATUS ────────────────────────────────────────────────────────
        types.Tool(
            name="specter_job_status",
            description="Poll a Replicate prediction (video or slow image). Returns status + output URL when done.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prediction_id": {"type": "string", "description": "Prediction ID from specter_generate."},
                },
                "required": ["prediction_id"],
            },
        ),

        # ── PRESETS ───────────────────────────────────────────────────────────
        types.Tool(
            name="specter_list_presets",
            description="List all Director presets (video) and image styles.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    async with httpx.AsyncClient(timeout=120.0) as client:

        # ── STATUS ────────────────────────────────────────────────────────────
        if name == "specter_status":
            if not TOKEN:
                return [types.TextContent(type="text", text=(
                    "❌ REPLICATE_API_TOKEN not set.\n"
                    "Add it to ~/.claude.json under mcpServers.specter-vision.env"
                ))]
            try:
                r = await client.get(f"{API}/account", headers=_h(), timeout=15.0)
                if r.status_code == 401:
                    return [types.TextContent(type="text", text="❌ Invalid API token — 401 Unauthorized.")]
                r.raise_for_status()
                acct = r.json()
                return [types.TextContent(type="text", text=(
                    f"✅ Specter-Vision v3.0 ONLINE\n"
                    f"Account: {acct.get('username', 'unknown')}\n\n"
                    f"Tools available:\n"
                    f"  specter_image    — Flux 1.1 Pro / Recraft v3 (stills)\n"
                    f"  specter_generate — Wan 2.1 14B (video)\n"
                    f"  specter_upscale  — Real-ESRGAN 4× (4K upscale)\n"
                    f"  specter_job_status — poll video predictions\n\n"
                    f"Ready. What are we making?"
                ))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Cannot reach Replicate: {e}")]

        # ── IMAGE GENERATION ──────────────────────────────────────────────────
        elif name == "specter_image":
            if not TOKEN:
                return [types.TextContent(type="text", text="❌ REPLICATE_API_TOKEN not set.")]

            prompt    = arguments["prompt"]
            style     = arguments.get("style", "cinematic")
            model_key = arguments.get("model", "flux_pro")
            ar        = arguments.get("aspect_ratio", "16:9")

            suffix     = IMAGE_STYLES.get(style, "")
            full_prompt = prompt.rstrip(".,") + suffix
            model      = MODELS[model_key]

            # Build input per model
            if model_key == "flux_pro":
                inp = {
                    "prompt":       full_prompt,
                    "aspect_ratio": ar,
                    "output_format": "webp",
                    "output_quality": 95,
                    "safety_tolerance": 5,
                }
            elif model_key == "flux_dev":
                w = arguments.get("width", 1280)
                h = arguments.get("height", 720)
                inp = {
                    "prompt":          full_prompt,
                    "width":           w,
                    "height":          h,
                    "num_outputs":     1,
                    "output_format":   "webp",
                    "output_quality":  95,
                    "guidance_scale":  3.5,
                    "num_inference_steps": 28,
                }
            else:  # recraft
                inp = {
                    "prompt":       full_prompt,
                    "style":        "realistic_image",
                    "size":         "1820x1024",
                }

            try:
                pred = await _predict(client, model, inp)
            except httpx.HTTPStatusError as e:
                return [types.TextContent(type="text", text=f"❌ API error {e.response.status_code}: {e.response.text[:300]}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Failed: {e}")]

            pid    = pred.get("id")
            status = pred.get("status")
            out    = _out(pred)

            # If already done (fast models return immediately)
            if status == "succeeded" and out:
                t = pred.get("metrics", {}).get("predict_time", 0)
                return [types.TextContent(type="text", text=(
                    f"✅ IMAGE READY\n"
                    f"URL: {out}\n"
                    f"Model: {model_key} | Style: {style} | AR: {ar}\n"
                    f"Time: {t:.1f}s {_cost(t)}\n\n"
                    f"Use specter_upscale(image_url='{out}') to go 4K.\n"
                    f"Use specter_generate(prompt='...', image_url='{out}') to animate it."
                ))]

            # Async — poll needed
            return [types.TextContent(type="text", text=(
                f"🎨 Generating image...\n"
                f"Prediction: {pid}\n"
                f"Poll with specter_job_status(prediction_id='{pid}')"
            ))]

        # ── VIDEO GENERATION ──────────────────────────────────────────────────
        elif name == "specter_generate":
            if not TOKEN:
                return [types.TextContent(type="text", text="❌ REPLICATE_API_TOKEN not set.")]

            prompt      = arguments["prompt"]
            image_url   = arguments.get("image_url")
            preset_name = arguments.get("preset", "institutional_hero")
            preset      = VIDEO_PRESETS.get(preset_name, VIDEO_PRESETS["custom"])

            if "seconds" in arguments:
                num_frames = max(17, min(121, int(float(arguments["seconds"]) * 24)))
                if num_frames % 2 == 0: num_frames += 1
                seconds = round(num_frames / 24, 1)
            else:
                num_frames = preset["num_frames"]
                seconds    = round(num_frames / 24, 1)

            steps    = arguments.get("steps", preset["sample_steps"]) if preset_name == "custom" else preset["sample_steps"]
            guidance = arguments.get("guidance_scale", preset["sample_guide_scale"]) if preset_name == "custom" else preset["sample_guide_scale"]

            full_prompt = prompt.rstrip(".,") + preset["suffix"]
            neg_prompt  = "blurry, distorted, low quality, watermark, text, deformed"

            mode  = "i2v" if image_url else "t2v"
            model = MODELS["wan_i2v"] if mode == "i2v" else MODELS["wan_t2v"]
            inp   = {
                "prompt": full_prompt, "negative_prompt": neg_prompt,
                "num_frames": num_frames, "sample_steps": steps,
                "sample_guide_scale": guidance, "fps": 16,
            }
            if image_url:
                inp["image"] = image_url

            try:
                pred = await _predict(client, model, inp)
            except httpx.HTTPStatusError as e:
                return [types.TextContent(type="text", text=f"❌ API error {e.response.status_code}: {e.response.text[:300]}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Failed: {e}")]

            pid = pred.get("id")
            return [types.TextContent(type="text", text=(
                f"🎬 Video queued on H100!\n"
                f"Prediction: {pid}\n"
                f"Mode: {'I2V' if mode == 'i2v' else 'T2V'} | Preset: {preset_name}\n"
                f"Frames: {num_frames} (~{seconds}s) | Steps: {steps}\n"
                f"Prompt: {full_prompt[:100]}{'...' if len(full_prompt)>100 else ''}\n\n"
                f"Poll: specter_job_status(prediction_id='{pid}') every 20s\n"
                f"ETA: 3–6 minutes on H100."
            ))]

        # ── UPSCALE ───────────────────────────────────────────────────────────
        elif name == "specter_upscale":
            if not TOKEN:
                return [types.TextContent(type="text", text="❌ REPLICATE_API_TOKEN not set.")]

            image_url    = arguments["image_url"]
            scale        = arguments.get("scale", 4)
            face_enhance = arguments.get("face_enhance", False)

            inp = {"image": image_url, "scale": scale, "face_enhance": face_enhance}

            try:
                pred = await _predict(client, MODELS["upscale"], inp)
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Upscale failed: {e}")]

            pid    = pred.get("id")
            status = pred.get("status")
            out    = _out(pred)

            if status == "succeeded" and out:
                return [types.TextContent(type="text", text=(
                    f"✅ UPSCALE COMPLETE\n"
                    f"URL: {out}\n"
                    f"Scale: {scale}× | Face enhance: {face_enhance}"
                ))]

            return [types.TextContent(type="text", text=(
                f"⏳ Upscaling...\nPrediction: {pid}\n"
                f"Poll: specter_job_status(prediction_id='{pid}')"
            ))]

        # ── JOB STATUS ────────────────────────────────────────────────────────
        elif name == "specter_job_status":
            pid = arguments["prediction_id"]
            try:
                pred = await _get(client, pid)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return [types.TextContent(type="text", text=f"❌ Prediction `{pid}` not found.")]
                return [types.TextContent(type="text", text=f"❌ API error: {e.response.status_code}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ Error: {e}")]

            status  = pred.get("status")
            out     = _out(pred)
            logs    = (pred.get("logs") or "").strip().splitlines()
            log_tail = "\n".join(logs[-4:]) if logs else "No logs yet."
            t       = pred.get("metrics", {}).get("predict_time", 0)
            error   = pred.get("error")

            if status == "succeeded" and out:
                return [types.TextContent(type="text", text=(
                    f"✅ COMPLETE\n"
                    f"URL: {out}\n"
                    f"Time: {t:.0f}s {_cost(t)}\n\n"
                    f"Note: Replicate URLs expire after 24h — save the file."
                ))]
            elif status == "failed":
                return [types.TextContent(type="text", text=f"❌ FAILED\nError: {error}\nLogs:\n{log_tail}")]
            elif status == "canceled":
                return [types.TextContent(type="text", text=f"🚫 Canceled.")]
            else:
                icon = {"starting": "🔵", "processing": "⏳"}.get(status, "⏳")
                return [types.TextContent(type="text", text=(
                    f"{icon} {status.upper()}\nID: `{pid}`\nLogs:\n{log_tail}\n\nPoll again in 20s."
                ))]

        # ── PRESETS ───────────────────────────────────────────────────────────
        elif name == "specter_list_presets":
            lines = ["=== SPECTER-VISION v3.0 — Full Creative Suite ===\n"]
            lines.append("IMAGE STYLES (specter_image):")
            for k, v in IMAGE_STYLES.items():
                lines.append(f"  {k:15} {v[:60] or '(no suffix)'}")
            lines.append("\nVIDEO PRESETS (specter_generate):")
            for k, p in VIDEO_PRESETS.items():
                lines.append(f"  {k:20} {p['description']}")
            lines.append("\nMODELS:")
            lines.append("  flux_pro   — Flux 1.1 Pro  (best image quality)")
            lines.append("  flux_dev   — Flux Dev      (fast, customizable size)")
            lines.append("  recraft    — Recraft v3    (brand / design / illustration)")
            lines.append("  wan_i2v    — Wan 2.1 I2V   (image → cinematic video)")
            lines.append("  wan_t2v    — Wan 2.1 T2V   (text → cinematic video)")
            lines.append("  upscale    — Real-ESRGAN   (4K upscale)")
            return [types.TextContent(type="text", text="\n".join(lines))]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
