#!/usr/bin/env python3
"""Copy recorded live sessions into the repo without anything private, for other people and agents.

    .venv/bin/python scripts/export_for_repo.py            # write data/field/
    .venv/bin/python scripts/export_for_repo.py --check    # only report what would be written

Writes data/field/<session>/ for every session that recorded something, WITHOUT camera images
(no frames.bin / index.csv / previews): court.json, session.json, events.jsonl, calibration/,
replays/, report.md, <camera>/dets.jsonl[.gz] (detections of every frame, so
`bt replay data/field/<session>` works).

Privacy (the repo is public): personal details are removed with scripts/hooks/privacy.py (names
come from the gitignored .private_words, also applied to folder and file names), and the output
is checked again; any hit aborts and removes what was written. Conversations are not exported:
docs/DECISION_LOG.md is the curated request -> analysis -> decision record.
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "hooks"))
from privacy import problems as privacy_problems, scrub  # noqa: E402

SESSIONS = ROOT / "data" / "live" / "sessions"
OUT_FIELD = ROOT / "data" / "field"
GZIP_ABOVE = 5 * 1024 * 1024
KEEP_FILES = {"court.json", "session.json", "events.jsonl", "report.md"}
KEEP_DIRS = {"calibration", "replays"}


def check(text: str, where: str) -> list[str]:
    return [f"{where}: {p}" for p in privacy_problems(text)]


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
    problems = export_sessions(a.check, secrets)
    if problems:
        print("PRIVACY CHECK FAILED:", *problems[:30], sep="\n  ")
        if not a.check:
            shutil.rmtree(OUT_FIELD, ignore_errors=True)
            print("exported files removed")
        sys.exit(1)
    print("privacy check passed")


if __name__ == "__main__":
    main()
