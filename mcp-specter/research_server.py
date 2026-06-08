#!/usr/bin/env python3
"""
Specter-Research MCP Server — v1.0
Deep research engine. No API key. No card. Completely free.

Sources:
  • DuckDuckGo Instant Answers API (free, no key)
  • DuckDuckGo HTML search scraper (free, no key)
  • Full page fetch + extraction
  • Multi-source synthesis

Tools:
  research_search   — web search via DuckDuckGo
  research_fetch    — fetch and extract full page content
  research_deep     — multi-query deep research on a topic
"""

import asyncio
import os
import re
import json
import urllib.parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

server = Server("specter-research")


def _clean_html(html: str, max_chars: int = 4000) -> str:
    """Strip HTML tags and clean up text."""
    # Remove scripts and styles
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove common boilerplate patterns
    text = re.sub(r'(Cookie Policy|Privacy Policy|Terms of Service|Accept Cookies)[^\n]*', '', text)
    return text[:max_chars]


async def _ddg_search(query: str, max_results: int = 8) -> list[dict]:
    """Search DuckDuckGo and return results."""
    results = []

    # Try DuckDuckGo Instant Answer API first
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }
            r = await client.get("https://api.duckduckgo.com/", params=params)
            data = r.json()

            # Abstract (featured snippet)
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data["AbstractText"],
                    "source": "DDG Instant Answer",
                })

            # Related topics
            for topic in data.get("RelatedTopics", [])[:4]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "DDG Related",
                    })
    except Exception:
        pass

    # DuckDuckGo HTML search for more results
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            params = {"q": query, "kl": "us-en", "kp": "-2"}
            r = await client.get("https://html.duckduckgo.com/html/", params=params)
            html = r.text

            # Extract result blocks
            blocks = re.findall(
                r'<a class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a class="result__snippet"[^>]*>(.*?)</a>',
                html, re.DOTALL
            )

            for url, title, snippet in blocks[:max_results]:
                title   = re.sub(r'<[^>]+>', '', title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                if url and title and url not in [r["url"] for r in results]:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "DDG Web",
                    })
    except Exception:
        pass

    return results[:max_results]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="research_search",
            description=(
                "Search the web using DuckDuckGo. Free, no API key. "
                "Returns titles, URLs, and snippets for a query. "
                "Good for: current events, technical docs, company info, market research, ZK ecosystem, mining industry."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query. Be specific for better results.",
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 15,
                        "description": "Number of results to return. Default: 8.",
                        "default": 8,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="research_fetch",
            description=(
                "Fetch and extract the full readable content of any web page. "
                "Use after research_search to read the actual content of a result. "
                "Good for: reading full articles, papers, docs, forum threads."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the page to fetch.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Max characters to return. Default: 4000.",
                        "default": 4000,
                    },
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="research_deep",
            description=(
                "Deep research on a topic. Runs multiple targeted searches, "
                "fetches top results, and synthesizes findings. "
                "Use for: competitor analysis, ZK ecosystem mapping, mining regulation research, "
                "researcher background checks, institutional due diligence. "
                "Takes 20-40 seconds — thorough by design."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to research in depth.",
                    },
                    "angles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific angles or sub-questions to cover. Optional — auto-generated if omitted.",
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "thorough"],
                        "description": "Research depth. Quick=2 queries, Standard=4, Thorough=6. Default: standard.",
                        "default": "standard",
                    },
                },
                "required": ["topic"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    # ── SEARCH ────────────────────────────────────────────────────────────────
    if name == "research_search":
        query       = arguments["query"]
        max_results = arguments.get("max_results", 8)

        results = await _ddg_search(query, max_results)

        if not results:
            return [types.TextContent(type="text", text=f"No results found for: {query}")]

        lines = [f"Search: {query}\n{len(results)} results\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r['title']}")
            lines.append(f"    {r['url']}")
            lines.append(f"    {r['snippet'][:200]}")
            lines.append("")

        return [types.TextContent(type="text", text="\n".join(lines))]

    # ── FETCH ─────────────────────────────────────────────────────────────────
    elif name == "research_fetch":
        url       = arguments["url"]
        max_chars = arguments.get("max_chars", 4000)

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                content_type = r.headers.get("content-type", "")

                if "json" in content_type:
                    text = json.dumps(r.json(), indent=2)[:max_chars]
                else:
                    text = _clean_html(r.text, max_chars)

                return [types.TextContent(type="text", text=(
                    f"URL: {url}\n"
                    f"Status: {r.status_code}\n"
                    f"---\n{text}"
                ))]
        except httpx.HTTPStatusError as e:
            return [types.TextContent(type="text", text=f"HTTP {e.response.status_code}: {url}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Fetch failed: {e}")]

    # ── DEEP RESEARCH ─────────────────────────────────────────────────────────
    elif name == "research_deep":
        topic  = arguments["topic"]
        angles = arguments.get("angles", [])
        depth  = arguments.get("depth", "standard")

        query_count = {"quick": 2, "standard": 4, "thorough": 6}[depth]

        # Auto-generate angles if not provided
        if not angles:
            angles = [
                topic,
                f"{topic} latest news 2025 2026",
                f"{topic} technical details how it works",
                f"{topic} criticism problems challenges",
                f"{topic} market analysis companies",
                f"{topic} research papers academic",
            ]

        queries = angles[:query_count]
        all_results = []
        seen_urls   = set()

        # Run all searches
        for q in queries:
            results = await _ddg_search(q, 4)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)

        if not all_results:
            return [types.TextContent(type="text", text=f"No results found for topic: {topic}")]

        # Fetch top 3 pages for full content
        fetched = []
        async with httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
            for r in all_results[:3]:
                if not r["url"] or r["url"].startswith("#"):
                    continue
                try:
                    resp = await client.get(r["url"])
                    content = _clean_html(resp.text, 2000)
                    fetched.append({"title": r["title"], "url": r["url"], "content": content})
                except Exception:
                    fetched.append({"title": r["title"], "url": r["url"], "content": r["snippet"]})

        # Build report
        lines = [
            f"DEEP RESEARCH: {topic}",
            f"Depth: {depth} | Queries: {len(queries)} | Sources: {len(all_results)}",
            "=" * 60,
            "",
            "ALL SOURCES FOUND:",
        ]
        for i, r in enumerate(all_results[:12], 1):
            lines.append(f"  [{i}] {r['title']}")
            lines.append(f"      {r['url']}")
            lines.append(f"      {r['snippet'][:150]}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("FULL CONTENT FROM TOP SOURCES:")
        lines.append("")
        for f in fetched:
            lines.append(f"--- {f['title']} ---")
            lines.append(f"URL: {f['url']}")
            lines.append(f['content'])
            lines.append("")

        return [types.TextContent(type="text", text="\n".join(lines))]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
