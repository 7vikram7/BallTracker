#!/usr/bin/env python3
"""Copy local data that is safe to publish into the repo, so other people and agents can work on it.

    .venv/bin/python scripts/export_for_repo.py            # field sessions + conversations
    .venv/bin/python scripts/export_for_repo.py --check    # only report what would be written

What it writes:
  data/field/<session>/     every recorded live session WITHOUT camera images (no frames.bin /
                            index.csv / previews): court.json, session.json, events.jsonl,
                            calibration/, replays/, report.md, <camera>/dets.jsonl[.gz]
                            (detections of every frame: `bt replay data/field/<session>` works).
  docs/conversations/       the Claude Code conversations that built this project: the user's
                            requests and the assistant's replies (no tool calls/outputs, no
                            hidden reasoning), with personal details replaced.

Privacy rules (the repo is public):
  * no camera images (people may be in them), no TLS keys, no credentials;
  * personal names in camera names are replaced (see RENAME), e-mail addresses removed;
  * the output is scanned for e-mail addresses, tokens and the replaced names; any hit aborts.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSIONS = ROOT / "data" / "live" / "sessions"
OUT_FIELD = ROOT / "data" / "field"
OUT_CONV = ROOT / "docs" / "conversations"
TRANSCRIPTS = Path.home() / ".claude" / "projects" / "-Users-macbookpro-Vikram-BallTracker"

# Camera / device names that contain a person's name -> neutral names. Applied to file names,
# folder names and file contents.
RENAME = {"samsung": "samsung", "<user>": "<user>"}
# Words that must not appear in anything exported (checked case-insensitively after renaming).
FORBIDDEN = [re.compile(r"<name>", re.I)]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAILS = {"noreply@anthropic.com", "7568724+7vikram7@users.noreply.github.com"}
TOKEN = re.compile(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9-]{30,})")
# Phone hardware identifiers (iOS UDID, CoreDevice UUID).
DEVICE_ID = re.compile(r"\b[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\b|\b[0-9]{8}-[0-9A-F]{16}\b")
GZIP_ABOVE = 5 * 1024 * 1024
KEEP_FILES = {"court.json", "session.json", "events.jsonl", "report.md"}
KEEP_DIRS = {"calibration", "replays"}


def scrub(text: str) -> str:
    for a, b in RENAME.items():
        text = text.replace(a, b)
    text = EMAIL.sub(lambda m: m.group() if m.group() in ALLOWED_EMAILS else "<email>", text)
    text = re.sub(r"~/\s\"']+/", "~/", text)
    text = DEVICE_ID.sub("<device-id>", text)
    return text


def check(text: str, where: str) -> list[str]:
    bad = [f"{where}: forbidden name" for f in FORBIDDEN if f.search(text)]
    bad += [f"{where}: e-mail {e}" for e in set(EMAIL.findall(text)) if e not in ALLOWED_EMAILS]
    bad += [f"{where}: token-like string" for _ in TOKEN.findall(text)[:1]]
    return bad


FIELD_README = """# Real field sessions (no images)

Recorded live sessions, exported by `scripts/export_for_repo.py`: every frame's ball detections
from app phones (`<camera>/dets.jsonl[.gz]`), events, calibrations, live decisions and replays.
Camera images are not included (people are visible in them).

    bt replay data/field/20261119-070916      # field test 2: re-run the pipeline with current code

What each session is, and what to do with it: [docs/HANDOFF.md](../../docs/HANDOFF.md#3-data-in-the-repo).
"""


def export_sessions(dry: bool, secrets: list[str]) -> list[str]:
    problems, written = [], []
    for s in sorted(p for p in SESSIONS.iterdir() if p.is_dir()):
        ev = s / "events.jsonl"
        n_events = len(ev.read_text().splitlines()) if ev.exists() else 0
        if n_events < 5 and not any((d / "dets.jsonl").exists() for d in s.iterdir() if d.is_dir()):
            continue  # server started and stopped with nothing recorded
        dst = OUT_FIELD / s.name
        for src in sorted(s.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(s)
            top = rel.parts[0]
            if len(rel.parts) == 1 and rel.name not in KEEP_FILES:
                continue
            if len(rel.parts) > 1 and top not in KEEP_DIRS and rel.name != "dets.jsonl":
                continue  # frames.bin, index.csv (camera images) and anything else
            text = scrub(src.read_text(errors="replace"))
            out = dst / Path(scrub(str(rel)))
            problems += check(text, str(out.relative_to(ROOT))) + [f"{out}: secret" for x in secrets if x in text]
            data = text.encode()
            if len(data) > GZIP_ABOVE:
                out, data = out.with_name(out.name + ".gz"), gzip.compress(data, 9, mtime=0)
            written.append((out, len(data)))
            if not dry:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
    if not dry:
        (OUT_FIELD / "README.md").write_text(FIELD_README)
    total = sum(n for _, n in written)
    print(f"field sessions: {len(written)} files, {total / 1e6:.1f} MB "
          f"(largest {max(written, key=lambda w: w[1])[0].relative_to(ROOT)} {max(n for _, n in written) / 1e6:.1f} MB)")
    return problems


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")


SYSTEM_BLOCK = re.compile(r"<(system-reminder|task-notification|ide_selection|ide_opened_file|command-[a-z-]+|local-command-[a-z-]+)>.*?</\1>", re.S)


def export_conversations(dry: bool, secrets: list[str]) -> list[str]:
    problems = []
    def started(p: Path) -> str:
        for raw in p.open():
            ts = json.loads(raw).get("timestamp")
            if ts:
                return ts
        return ""

    files = sorted(TRANSCRIPTS.glob("*.jsonl"), key=started)
    index = ["# Conversations that built BallTracker", "",
             "Exported by `scripts/export_for_repo.py`: the user's requests and the assistant's replies, in order.",
             "Tool calls, tool outputs and hidden reasoning are left out; personal details are replaced.",
             "Context-compaction summaries (\"This session is being continued...\") are kept: they list what",
             "was done in the part before them. Request/outcome pairs in short form: `docs/evolution/LOG.md`.", ""]
    for n, f in enumerate(files, 1):
        lines, first_ts = [], None
        for raw in f.open():
            try:
                r = json.loads(raw)
            except ValueError:
                continue
            if r.get("type") not in ("user", "assistant") or r.get("isSidechain") or r.get("isMeta"):
                continue
            msg = r.get("message") or {}
            text = SYSTEM_BLOCK.sub("", _text_of(msg.get("content", ""))).strip()
            if not text or text.startswith("[Request interrupted"):
                continue
            first_ts = first_ts or r.get("timestamp", "")[:16].replace("T", " ")
            who = "User" if r["type"] == "user" else "Assistant"
            ts = r.get("timestamp", "")[:16].replace("T", " ")
            lines.append(f"### {who} · {ts} UTC\n\n{text}\n")
        if not lines:
            continue
        body = scrub(f"# Conversation {n} (started {first_ts} UTC)\n\n" + "\n".join(lines))
        name = f"{n:02d}-{(first_ts or 'unknown')[:10]}.md"
        problems += check(body, f"docs/conversations/{name}") + [f"{name}: secret" for x in secrets if x in body]
        users = sum(l.startswith("### User") for l in lines)
        index.append(f"- [{name}]({name}): {users} requests, {len(lines) - users} replies, {len(body) / 1e3:.0f} kB")
        print(f"conversation {name}: {users} user / {len(lines) - users} assistant messages, {len(body) / 1e3:.0f} kB")
        if not dry:
            OUT_CONV.mkdir(parents=True, exist_ok=True)
            (OUT_CONV / name).write_text(body)
    if not dry:
        (OUT_CONV / "README.md").write_text("\n".join(index) + "\n")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="write nothing, only report")
    a = ap.parse_args()
    secrets = []
    sf = ROOT / "Secrets"
    if sf.exists():
        secrets = [x.strip() for x in sf.read_text().splitlines() if len(x.strip()) >= 12]
    if not a.check:
        shutil.rmtree(OUT_FIELD, ignore_errors=True)
    problems = export_sessions(a.check, secrets) + export_conversations(a.check, secrets)
    if problems:
        print("PRIVACY CHECK FAILED:", *problems[:30], sep="\n  ")
        if not a.check:
            shutil.rmtree(OUT_FIELD, ignore_errors=True)
            shutil.rmtree(OUT_CONV, ignore_errors=True)
            print("exported files removed")
        sys.exit(1)
    print("privacy check passed")


if __name__ == "__main__":
    main()
