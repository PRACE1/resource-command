#!/usr/bin/env python3
"""
session_memory.py — Just-in-Time Context Accumulator
Implements the JIT-RL pattern: structured experience logs that compound
over sessions without weight updates or fine-tuning infrastructure.

Usage:
  python session_memory.py log    — append a session entry
  python session_memory.py read   — print current context window
  python session_memory.py prompt — generate a paste-ready context block
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "sovereign_memory.json"
MAX_ENTRIES = 50  # Keep the last 50 sessions in the log


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {"project": "Resource Command", "sessions": []}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(data: dict) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_session(entry: dict) -> None:
    data = load_memory()
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    data["sessions"].append(entry)
    # Trim to max entries
    data["sessions"] = data["sessions"][-MAX_ENTRIES:]
    save_memory(data)
    print(f"Session logged. Total entries: {len(data['sessions'])}")


def read_memory() -> None:
    data = load_memory()
    sessions = data.get("sessions", [])
    if not sessions:
        print("No sessions logged yet.")
        return
    print(f"\n=== Sovereign Memory Log ({len(sessions)} sessions) ===\n")
    for s in sessions[-10:]:  # Show last 10
        print(f"[{s['timestamp'][:10]}] {s.get('domain', 'general').upper()}")
        print(f"  Decision: {s.get('decision', 'N/A')}")
        print(f"  Output:   {s.get('output', 'N/A')}")
        print(f"  Blocker:  {s.get('blocker', 'None')}")
        print()


def generate_prompt() -> str:
    data = load_memory()
    sessions = data.get("sessions", [])
    if not sessions:
        return "No prior session context available."

    lines = ["=== SOVEREIGN MEMORY CONTEXT (JIT-RL) ===\n"]
    lines.append(f"Project: Resource Command | Sessions logged: {len(sessions)}\n")

    # Extract recent decisions by domain
    domains = {}
    for s in sessions:
        domain = s.get("domain", "general")
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(s)

    for domain, entries in domains.items():
        latest = entries[-1]
        lines.append(f"[{domain.upper()}]")
        lines.append(f"  Last decision: {latest.get('decision', 'N/A')}")
        lines.append(f"  Last output:   {latest.get('output', 'N/A')}")
        if latest.get("blocker"):
            lines.append(f"  Active blocker: {latest.get('blocker')}")
        lines.append("")

    lines.append("=== END CONTEXT ===")
    return "\n".join(lines)


# ── Pre-loaded entries from our actual session history ─────────────────────────

BOOTSTRAP_ENTRIES = [
    {
        "domain": "zk_circuits",
        "decision": "Patched royalty_rate_bps soundness gap. Bounded to 5000 bps statutory cap.",
        "output": "compliance.circom v1.1 — SHA-256 fingerprinted and audit-ready.",
        "blocker": None,
    },
    {
        "domain": "audit_engagement",
        "decision": "Submitted audit pack v1.9 to Trail of Bits (Akshith). Cover letter with hash table.",
        "output": "Resource_Command_Audit_Pack_v1.9_SIGNATURE_READY.zip dispatched.",
        "blocker": "Awaiting Trail of Bits response.",
    },
    {
        "domain": "media_engine",
        "decision": "Abandoned local ComfyUI/Docker (AMD RX 6600 incompatible). Pivoted to Replicate cloud.",
        "output": "Specter-Vision MCP server v2.0 — Wan 2.1 14B, Director presets, H100 compute.",
        "blocker": "Replicate credit balance at $0. Video render blocked until purchase confirmed.",
    },
    {
        "domain": "mcp_stack",
        "decision": "Hard-registered specter-vision in .claude.json with absolute Windows paths.",
        "output": "Token forensics confirmed: prace1 account active. Bridge logic validated.",
        "blocker": "Claude Desktop GUI MCP connection not yet confirmed via /mcp command.",
    },
    {
        "domain": "memory_architecture",
        "decision": "Implementing JIT-RL pattern — structured experience logs, no fine-tuning required.",
        "output": "session_memory.py deployed. sovereign_memory.json as the accumulator.",
        "blocker": None,
    },
]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prompt"

    if cmd == "bootstrap":
        # Seed the memory with our actual session history
        data = load_memory()
        for entry in BOOTSTRAP_ENTRIES:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            data["sessions"].append(entry)
        data["sessions"] = data["sessions"][-MAX_ENTRIES:]
        save_memory(data)
        print(f"Memory bootstrapped with {len(BOOTSTRAP_ENTRIES)} real session entries.")

    elif cmd == "log":
        # Interactive log entry
        print("Logging new session entry.")
        entry = {
            "domain": input("Domain (zk_circuits/media_engine/audit/mcp_stack/general): ").strip(),
            "decision": input("Key decision made: ").strip(),
            "output": input("Real output produced: ").strip(),
            "blocker": input("Active blocker (or leave blank): ").strip() or None,
        }
        log_session(entry)

    elif cmd == "read":
        read_memory()

    elif cmd == "prompt":
        print(generate_prompt())

    else:
        print("Commands: bootstrap | log | read | prompt")
