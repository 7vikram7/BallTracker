"""Remove personal details from text before it goes into the (public) repository.

Used by the evolution-log hook and by scripts/export_for_repo.py. Generic patterns are here:
e-mail addresses, home-folder paths, phone hardware IDs, token-like strings. Names and other
words specific to the owner live in ``.private_words`` at the repo root, which is gitignored
(so the list itself is never published). One entry per line: ``word`` (replaced by
``<redacted>``) or ``word=replacement``; matching ignores case; ``#`` starts a comment.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_WORDS = ROOT / ".private_words"
ALLOWED_EMAILS = {"noreply@anthropic.com", "7568724+7vikram7@users.noreply.github.com"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HOME = re.compile(r"/Users/[^/\s\"'`]+/")
DEVICE_ID = re.compile(r"\b[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\b|\b[0-9]{8}-[0-9A-F]{16}\b")
TOKEN = re.compile(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9-]{30,})")


def private_words() -> list[tuple[str, str]]:
    out = []
    try:
        lines = PRIVATE_WORDS.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for ln in lines:
        ln = ln.split("#", 1)[0].strip()
        if not ln:
            continue
        word, _, rep = ln.partition("=")
        out.append((word.strip(), rep.strip() or "<redacted>"))
    # longest first, so "name-phone=samsung" wins over "name"
    return sorted(out, key=lambda w: -len(w[0]))


def scrub(text: str) -> str:
    for word, rep in private_words():
        text = re.sub(re.escape(word), rep, text, flags=re.I)
    text = EMAIL.sub(lambda m: m.group() if m.group() in ALLOWED_EMAILS else "<email>", text)
    text = HOME.sub("~/", text)
    text = DEVICE_ID.sub("<device-id>", text)
    return TOKEN.sub("<token>", text)


def problems(text: str) -> list[str]:
    """What would still be private in ``text`` (empty list = clean)."""
    bad = [f"private word '{w[:2]}…'" for w, _ in private_words() if re.search(re.escape(w), text, re.I)]
    bad += [f"e-mail {e}" for e in set(EMAIL.findall(text)) if e not in ALLOWED_EMAILS]
    bad += ["token-like string"] if TOKEN.search(text) else []
    return bad
