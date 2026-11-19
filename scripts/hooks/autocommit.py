#!/usr/bin/env python3
"""Commit and push automatically once the tests pass (Claude Code ``Stop`` hook).

Two halves:

* ``tests/conftest.py`` calls :func:`record_pass` when a **full** pytest run passes (no file
  selection, no ``-k``/``-m``/``--lf``). It writes ``.bt_tests_ok``: a fingerprint of the exact
  working tree that was tested (a git tree hash, ignored files excluded).
* This script, run at the end of every Claude response, commits and pushes if the working tree
  still has that fingerprint. Anything edited after the tests ran is *not* committed until the
  tests pass again, so nothing untested is ever pushed.

The evolution log (docs/evolution/LOG.md) is written by the hooks themselves after the tests,
so it is left out of the fingerprint but included in the commit.

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


def _last_request(transcript: str) -> str:
    """First line of the user's latest real request in this session (for the commit subject)."""
    try:
        lines = Path(transcript).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for line in reversed(lines[-2000:]):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "user":
            continue
        c = (d.get("message") or {}).get("content")
        if isinstance(c, list):
            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
        if not isinstance(c, str):
            continue
        c = re.sub(r"<[^>]+>.*?</[^>]+>", "", c, flags=re.S).strip()
        if len(c.split()) >= 4:
            return c.splitlines()[0][:72]
    return ""


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


def stop(data: dict) -> str | None:
    """-> message for the user, or None when there was nothing to do."""
    if not MARKER.exists():
        return None
    gitdir = Path(_git("rev-parse", "--git-dir"))
    gitdir = gitdir if gitdir.is_absolute() else ROOT / gitdir
    if any((gitdir / n).exists() for n in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD")):
        return None
    tested = json.loads(MARKER.read_text())
    if not _git("status", "--porcelain"):
        return None  # nothing to commit
    if fingerprint() != tested["tree"]:
        return None  # changed since the last passing run: wait for the next one
    _git("add", "-A")
    staged = [p for p in _git("diff", "--cached", "--name-only").splitlines() if p]
    bad = _unsafe(staged)
    if bad:
        _git("reset", "-q")
        return "Auto-commit skipped, review these files: " + "; ".join(bad)
    subject = _last_request(data.get("transcript_path") or "") or "Update"
    stat = _git("diff", "--cached", "--stat", "--stat-width=100").splitlines()
    body = (f"Auto-commit after a passing full test run ({tested['passed']} passed, {tested['at']}).\n\n"
            + "\n".join(stat[-25:]) + f"\n\n{TRAILER}\n")
    _git("commit", "-q", "-m", f"Auto: {subject}", "-m", body)
    sha = _git("rev-parse", "--short", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if not _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False):
        return f"Committed {sha} ({len(staged)} files); not pushed: {branch} has no upstream."
    r = subprocess.run(["git", "push", "-q"], cwd=ROOT, capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        return f"Committed {sha}; push failed: {r.stderr.strip()[-300:]}"
    return f"Tests passed: committed {sha} ({len(staged)} files) and pushed {branch}."


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
