"""The Stop hook commits and pushes the evolution log after every response, tested or not."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "autocommit.py"


def _run(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    remote, work = tmp_path / "remote.git", tmp_path / "work"
    _run(tmp_path, "init", "-q", "--bare", str(remote))
    _run(tmp_path, "init", "-q", "-b", "main", str(work))
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid"), ("commit.gpgsign", "false")):
        _run(work, "config", k, v)
    (work / "docs" / "evolution").mkdir(parents=True)
    (work / "docs" / "evolution" / "LOG.md").write_text("# log\n")
    (work / "code.py").write_text("x = 1\n")
    _run(work, "add", "-A")
    _run(work, "commit", "-q", "-m", "init")
    _run(work, "remote", "add", "origin", str(remote))
    _run(work, "push", "-q", "-u", "origin", "main")
    spec = importlib.util.spec_from_file_location("autocommit_under_test", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ROOT", work)
    monkeypatch.setattr(mod, "MARKER", work / ".bt_tests_ok")
    (work / ".gitignore").write_text(".bt_tests_ok\n")
    _run(work, "add", ".gitignore")
    _run(work, "commit", "-q", "-m", "ignore marker")
    _run(work, "push", "-q")
    return mod, work, remote


def _append_log(work, text="\n## request\n\n> something\n"):
    with open(work / "docs" / "evolution" / "LOG.md", "a") as f:
        f.write(text)


def test_log_is_committed_and_pushed_even_without_a_test_run(repo):
    mod, work, remote = repo
    _append_log(work)
    msg = mod.stop({})
    assert "Evolution log committed" in msg and "pushed" in msg
    assert _run(work, "status", "--porcelain") == ""
    assert _run(remote, "log", "-1", "--format=%s", "main").startswith("Evolution log")


def test_untested_code_stays_out_while_the_log_goes_out(repo):
    mod, work, remote = repo
    mod.record_pass(1)
    (work / "code.py").write_text("x = 2  # edited after the tests ran\n")
    _run(work, "add", "code.py")  # even when staged
    _append_log(work)
    assert "Evolution log committed" in mod.stop({})
    assert _run(work, "show", "--name-only", "--format=", "HEAD") == "docs/evolution/LOG.md"
    assert _run(work, "diff", "--cached", "--name-only") == "code.py"  # still staged, not committed
    assert _run(remote, "rev-parse", "main") == _run(work, "rev-parse", "HEAD")


def test_tested_code_and_the_log_go_out_together(repo):
    mod, work, _ = repo
    (work / "code.py").write_text("x = 3\n")
    mod.record_pass(5)
    _append_log(work)  # written by the hook after the tests: not part of the fingerprint
    assert "Tests passed" in mod.stop({})
    assert set(_run(work, "show", "--name-only", "--format=", "HEAD").split()) == {"code.py", "docs/evolution/LOG.md"}


def test_nothing_to_do_when_the_log_is_unchanged(repo):
    mod, work, _ = repo
    (work / "code.py").write_text("x = 4\n")  # untested, no log change
    head = _run(work, "rev-parse", "HEAD")
    assert mod.stop({}) is None
    assert _run(work, "rev-parse", "HEAD") == head


def test_main_reports_through_a_system_message(repo, monkeypatch, capsys):
    mod, work, _ = repo
    _append_log(work)
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps({"session_id": "x"})))
    mod.main()
    assert "Evolution log committed" in json.loads(capsys.readouterr().out)["systemMessage"]


def test_commit_subjects_never_carry_conversation_text(repo, tmp_path):
    mod, work, remote = repo
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"type": "user", "message": {"content": "Sleepy, going to bed now, please fix it"}}) + "\n")
    mod.record_pass(1)  # tested tree, but only the log changed: still a log commit
    _append_log(work)
    assert "Evolution log committed" in mod.stop({"transcript_path": str(t)})
    assert _run(work, "log", "-1", "--format=%B").splitlines()[0] == "Evolution log update"
    (work / "code.py").write_text("x = 5\n")
    mod.record_pass(1)
    _append_log(work)
    mod.stop({"transcript_path": str(t)})
    msg = _run(work, "log", "-1", "--format=%B")
    assert msg.splitlines()[0] == "Auto: update code.py" and "Sleepy" not in msg


def test_the_log_is_filtered_before_it_is_committed(repo):
    mod, work, remote = repo
    _append_log(work, "\n> the token in the keychain can push\n\nA normal line about bounces.\n")
    mod.stop({})
    pushed = _run(remote, "show", "main:docs/evolution/LOG.md")
    assert "keychain" not in pushed and "A normal line about bounces." in pushed
    assert "> [line removed: it mentioned credentials]" in pushed


def test_credential_lines_are_dropped_and_the_filter_is_idempotent():
    import sys

    sys.path.insert(0, str(HOOK.parent))
    from privacy import drop_credential_lines, public_text

    text = ("Keep this.\n- Your fine-grained token is stored somewhere\n> git takes its login from the CLI\n"
            "The OAuth scope lacked workflow.\nCalibration RMS 0.8 px.")
    out = drop_credential_lines(text)
    assert out.splitlines() == ["Keep this.", "- [line removed: it mentioned credentials]",
                                "> [line removed: it mentioned credentials]",
                                "[line removed: it mentioned credentials]", "Calibration RMS 0.8 px."]
    assert public_text(out) == out
