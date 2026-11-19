"""Record a passing full test run for the auto-commit hook (scripts/hooks/autocommit.py)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _full_run(config) -> bool:
    """The whole suite was selected: no test files picked, no -k / -m / --lf / --deselect."""
    o = config.option
    if getattr(o, "keyword", "") or getattr(o, "markexpr", "") or getattr(o, "lf", False) \
            or getattr(o, "deselect", None) or getattr(o, "collectonly", False):
        return False
    tests = (ROOT / "tests").resolve()
    for a in config.args:
        p = Path(a.split("::")[0])
        p = (p if p.is_absolute() else Path(config.invocation_params.dir) / p).resolve()
        if p not in (tests, ROOT):
            return False
    return True


def pytest_sessionfinish(session, exitstatus):
    if exitstatus != 0 or not _full_run(session.config):
        return
    try:
        spec = importlib.util.spec_from_file_location("bt_autocommit", ROOT / "scripts/hooks/autocommit.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.record_pass(session.testscollected)
    except Exception:  # never let bookkeeping fail the test run
        pass
