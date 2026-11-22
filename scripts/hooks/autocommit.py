#!/usr/bin/env python3
"""Commit and push automatically once the tests pass (Claude Code ``Stop`` hook).

Two halves:

* ``tests/conftest.py`` calls :func:`record_pass` when a **full** pytest run passes (no file
  selection, no ``-k``/``-m``/``--lf``). It writes ``.bt_tests_ok``: a fingerprint of the exact
  working tree that was tested (a git tree hash, ignored files excluded).
* This script, run at the end of every Claude response, commits and pushes if the working tree
  still has that fingerprint. Anything edited after the tests ran is *not* committed until the
  tests pass again, so nothing untested is ever pushed.

Commit subjects are built from file names, never from conversation text, and the log is run
through the privacy filter (scripts/hooks/privacy.py) before each commit.

The evolution log (docs/evolution/LOG.md) is written by the hooks themselves after the tests,
so it is left out of the fingerprint. When the rest of the tree is tested it goes into that
commit; otherwise it is committed and pushed **on its own** at the end of every response, so the
log on GitHub is always up to date while untested code still waits for a passing run.

Safety: never commits during a merge/rebase, never commits files that look like credentials
or are larger than 5 MB, pushes only the current branch to its upstream. Off with
``BT_AUTOCOMMIT=0``. Never fails the turn.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = ROOT / ".bt_tests_ok"
UNFINGERPRINTED = ["docs/evolution/LOG.md"]
MAX_FILE_BYTES = 5 * 1024 * 1024
SECRET_NAME = re.compile(r"(^|/)(Secrets?|\.env[^/]*|.*\.(pem|key|p12|keystore|jks|mobileprovision))$", re.I)
SECRET_TEXT = re.compile(rb"github_pat_[A-Za-z0-9_]{20}|ghp_[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}")
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def _git(*args: str, env: dict | None = None, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                       env={**os.environ, **(env or {})}, timeout=120)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def fingerprint() -> str:
    """Tree hash of the working tree as `git add -A` would stage it (minus the hook-written log)."""
    with tempfile.TemporaryDirectory() as d:
        env = {"GIT_INDEX_FILE": os.path.join(d, "index")}
        _git("read-tree", "HEAD", env=env)
        _git("add", "-A", env=env)
        _git("rm", "-q", "--cached", "--ignore-unmatch", "--", *UNFINGERPRINTED, env=env)
        return _git("write-tree", env=env)


def record_pass(n_passed: int) -> None:
    MARKER.write_text(json.dumps({"tree": fingerprint(), "passed": n_passed,
                                  "at": time.strftime("%Y-%m-%d %H:%M:%S")}))


def _filter_log() -> None:
    """Run the whole public log through the privacy filter (personal details, credential lines)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from privacy import public_text

    for rel in UNFINGERPRINTED:
        f = ROOT / rel
        if f.is_file():
            text = f.read_text(encoding="utf-8")
            clean = public_text(text)
            if clean != text:
                f.write_text(clean, encoding="utf-8")


def _subject(paths: list[str]) -> str:
    """A commit subject from the changed file names only: never conversation text."""
    names = sorted({Path(p).name for p in paths if p not in UNFINGERPRINTED}) or ["evolution log"]
    more = f" and {len(names) - 3} more" if len(names) > 3 else ""
    return "Auto: update " + ", ".join(names[:3]) + more


def _unsafe(paths: list[str]) -> list[str]:
    bad = []
    for p in paths:
        f = ROOT / p
        if SECRET_NAME.search(p):
            bad.append(f"{p} (credential-like name)")
        elif f.is_file():
            if f.stat().st_size > MAX_FILE_BYTES:
                bad.append(f"{p} (> 5 MB)")
            elif SECRET_TEXT.search(f.read_bytes()[:2_000_000]):
                bad.append(f"{p} (contains a token or private key)")
    return bad


def _push() -> str | None:
    """-> None when pushed, else why not."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if not _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False):
        return f"not pushed: {branch} has no upstream"
    r = subprocess.run(["git", "push", "-q"], cwd=ROOT, capture_output=True, text=True, timeout=90)
    return None if r.returncode == 0 else f"push failed: {r.stderr.strip()[-300:]}"


def commit_log_only(data: dict) -> str | None:
    """Commit and push just the evolution log (the rest of the tree is untested or unchanged)."""
    _filter_log()
    changed = [p for p in UNFINGERPRINTED if _git("status", "--porcelain", "--", p)]
    if not changed:
        return None
    bad = _unsafe(changed)
    if bad:
        return "Evolution log not committed, review: " + "; ".join(bad)
    # `git commit -- <paths>` commits only those paths and leaves anything else staged as it was
    _git("commit", "-q", "-m", "Evolution log update",
         "-m", f"Written by the Claude Code hooks (scripts/hooks/evolution_log.py).\n\n{TRAILER}\n", "--", *changed)
    sha = _git("rev-parse", "--short", "HEAD")
    why = _push()
    return f"Evolution log committed {sha}" + (f"; {why}." if why else " and pushed.")


def stop(data: dict) -> str | None:
    """-> message for the user, or None when there was nothing to do."""
    gitdir = Path(_git("rev-parse", "--git-dir"))
    gitdir = gitdir if gitdir.is_absolute() else ROOT / gitdir
    if any((gitdir / n).exists() for n in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD")):
        return None
    if not _git("status", "--porcelain"):
        return None  # nothing to commit
    dirty = set((_git("diff", "--name-only", "HEAD") + "\n" + _git("ls-files", "--others", "--exclude-standard")).split())
    tested = json.loads(MARKER.read_text()) if MARKER.exists() else None
    if dirty <= set(UNFINGERPRINTED) or not tested or fingerprint() != tested["tree"]:
        return commit_log_only(data)  # code untested since it changed: only the log goes out
    _filter_log()
    _git("add", "-A")
    staged = [p for p in _git("diff", "--cached", "--name-only").splitlines() if p]
    bad = _unsafe(staged)
    if bad:
        _git("reset", "-q")
        return "Auto-commit skipped, review these files: " + "; ".join(bad)
    stat = _git("diff", "--cached", "--stat", "--stat-width=100").splitlines()
    body = (f"Auto-commit after a passing full test run ({tested['passed']} passed, {tested['at']}).\n\n"
            + "\n".join(stat[-25:]) + f"\n\n{TRAILER}\n")
    _git("commit", "-q", "-m", _subject(staged), "-m", body)
    sha = _git("rev-parse", "--short", "HEAD")
    why = _push()
    if why:
        return f"Committed {sha} ({len(staged)} files); {why}."
    return f"Tests passed: committed {sha} ({len(staged)} files) and pushed."


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active"):
        return
    msg = stop(data)
    if msg:
        print(json.dumps({"systemMessage": msg}))


if __name__ == "__main__":
    try:
        if os.environ.get("BT_AUTOCOMMIT", "1") != "0":
            main()
    except Exception as e:  # a hook must never break the session
        print(json.dumps({"systemMessage": f"Auto-commit hook error: {e}"[:400]}))
