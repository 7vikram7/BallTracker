#!/usr/bin/env python3
"""Claude Code hook: keep an evolution log of the product in docs/evolution/LOG.md.

* ``UserPromptSubmit``: appends the request (substantive prompts only: short replies such as
  "done" or "ok" are skipped).
* ``Stop``: appends Claude's final message of the turn (its summary of what was decided,
  built and concluded), when it is substantive.

Usage (from .claude/settings.json):  python3 scripts/hooks/evolution_log.py prompt|stop
Reads the hook's JSON input on stdin. Never fails the turn: any error is swallowed.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "docs" / "evolution" / "LOG.md"
MIN_PROMPT_WORDS = 8       # shorter prompts are acknowledgements, not requests
MIN_ANSWER_CHARS = 400     # shorter final messages are status updates, not conclusions
MAX_ANSWER_CHARS = 6000


def _last_assistant_text(transcript: str) -> str | None:
    """Text of the last assistant message in the session transcript (JSONL)."""
    try:
        lines = Path(transcript).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines[-400:]):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant":
            continue
        content = (d.get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            text = "\n".join(t for t in texts if t.strip())
            if text.strip():
                return text
    return None


def _append(block: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with open(LOG, "a", encoding="utf-8") as f:
        if new:
            f.write("# Product evolution log\n\nWritten automatically by `scripts/hooks/evolution_log.py`"
                    " (Claude Code hooks): each request, then the conclusions of the work on it.\n")
        f.write(block)


def main() -> None:
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    data = json.loads(sys.stdin.read() or "{}")
    stamp = time.strftime("%Y-%m-%d %H:%M")
    session = str(data.get("session_id", ""))[:8]
    if kind == "prompt":
        prompt = (data.get("prompt") or "").strip()
        # Automated messages (background-task notifications, system reminders) are not requests.
        if prompt.startswith("<") and any(t in prompt[:200] for t in ("<task-notification", "<system-reminder", "<command-")):
            return
        if len(prompt.split()) < MIN_PROMPT_WORDS:
            return
        quoted = "\n".join("> " + ln for ln in prompt.splitlines())
        _append(f"\n## {stamp} · request (session {session})\n\n{quoted}\n")
    elif kind == "stop":
        if data.get("stop_hook_active"):
            return
        text = data.get("last_assistant_message") or _last_assistant_text(data.get("transcript_path") or "")
        if not text or len(text) < MIN_ANSWER_CHARS:
            return
        if len(text) > MAX_ANSWER_CHARS:
            text = text[:MAX_ANSWER_CHARS] + "\n\n… (truncated)"
        _append(f"\n### {stamp} · outcome\n\n{text.strip()}\n")


if __name__ == "__main__":
    try:
        if os.environ.get("BT_EVOLUTION_LOG", "1") != "0":
            main()
    except Exception:  # a logging hook must never break the session
        pass
