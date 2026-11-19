"""Session log, replay comparison and report (bt replay / bt report / bt sessions)."""

import csv
import json

import pytest

from balltracker.live.replay import compare
from balltracker.live.report import score_marks


def _d(t, x=0.0, y=7.0, result="IN", announce=False, dist=-10.0, suppressed=None):
    return {"t": t, "x": x, "y": y, "result": result, "announce": announce, "text": "OUT" if announce else None,
            "distance_cm": dist, "suppressed": suppressed, "cameras": ["a", "b"], "p_out": 1.0 if announce else 0.0}


def test_compare_finds_changed_moved_gone_and_new():
    old = [_d(1.0), _d(2.0, result="OUT", announce=True, dist=5), _d(3.0), _d(4.0)]
    new = [_d(1.0), _d(2.01, result="UNCERTAIN", dist=1), _d(3.0, x=0.05), _d(5.0)]
    c = compare(old, new)
    assert c["matched"] == 3 and not c["identical"]
    assert [r["t"] for r in c["changed"]] == [2.0] and c["changed"][0]["old"] == "OUT (spoken)"
    assert [r["t"] for r in c["moved"]] == [3.0] and c["moved"][0]["moved_cm"] == 5.0
    assert [r["t"] for r in c["only_live"]] == [4.0] and [r["t"] for r in c["only_replay"]] == [5.0]
    assert compare(old, old)["identical"]


def test_score_marks_in_order_with_errors_and_wrong_out():
    decisions = [_d(1, dist=-11), _d(2, result="OUT", announce=True, dist=2.0), _d(3, suppressed="secondary bounce"),
                 _d(4, result="OUT", announce=True, dist=14)]
    marks = [{"bounce": "1", "line": "baseline_B", "signed_cm": -12.0, "notes": ""},
             {"bounce": "2", "line": "baseline_B", "signed_cm": -1.0, "notes": ""},  # in, but called OUT
             {"bounce": "3", "line": "sideline_right", "signed_cm": 12.0, "notes": ""}]
    s = score_marks(decisions, marks)
    assert s["matched"] == 3 and not s["count_mismatch"]  # the suppressed 2nd bounce isn't a drill bounce
    assert s["wrong_out_spoken"] == 1
    assert s["clear_out_called"] == 1 and s["clear_out_total"] == 1
    assert s["median_abs_err_cm"] == pytest.approx(2.0)


@pytest.mark.slow
def test_recorded_session_manifest_replay_and_report(tmp_path):
    from balltracker.live.fakephone import run_live_demo
    from balltracker.live.replay import read_events, replay, save_replay
    from balltracker.live.report import build_report, list_sessions

    r = run_live_demo(["behind_baseline_high", "side_mid"], seed=11, shots=4, width=960, height=540, fps=60,
                      data_dir=tmp_path, port=8196, clock_offsets=[0.0, 21.0], drift_ppm=[0.0, 0.0], verbose=False,
                      edge=True, record=True)
    sd = tmp_path / "sessions" / r["session_dir"].split("/")[-1]
    man = json.loads((sd / "session.json").read_text())
    # Manifest: what ran and how it went.
    assert man["versions"]["phone_detector"].startswith("edge_color_motion") and "commit" in man["git"]
    s = man["summary"]
    assert s is not None and len(s["cameras"]) == 2 and s["decisions"] == len(r["decisions"])
    assert all(c["mode"] == "edge" and c["frames_in"] > 100 and c["drops"] == 0 for c in s["cameras"])
    # Event log: connections with app details and detector config, periodic health, calibration snapshots.
    ev = read_events(sd)
    con = [e for e in ev if e["type"] == "camera_connected"]
    assert len(con) == 2 and all(e["mode"] == "edge" and e["detector_config"]["fps"] == 60 for e in con)
    assert any(e["type"] == "camera_stats" for e in ev)
    assert {p.name for p in (sd / "calibration").iterdir()} == {"sim-behind_baseline_high.json", "sim-side_mid.json"}
    # Replay with the same code reproduces the live calls.
    res = replay(sd)
    assert res["comparison"]["matched"] == len(r["decisions"]) and not res["comparison"]["changed"]
    assert res["comparison"]["max_moved_cm"] < 0.1
    save_replay(res)
    # Report, scored against a marks sheet built from the synthetic truth.
    marks = tmp_path / "marks.csv"
    with open(marks, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bounce", "t_s", "x_m", "y_m", "line", "signed_distance_cm", "notes"])
        for i, row in enumerate([x for x in r["rows"] if x["first"]], 1):
            w.writerow([i, "", "", "", "", round(row["truth_dist_cm"], 1), ""])
    text, out = build_report(sd, marks)
    assert "## Accuracy against the chalk marks" in text and "## Replays with later code" in text
    assert out["marks"]["wrong_out_spoken"] == 0 and out["marks"]["median_abs_err_cm"] < 2.0
    assert [x["session"] for x in list_sessions(tmp_path)] == [sd.name]
