"""Readable summary of a live session, optionally scored against the chalk-marks sheet.

    bt report data/live/sessions/20261118-101500 [--marks docs/field_test_marks.csv]

Writes ``report.md`` into the session folder (and prints its path). Works for
sessions recorded before session.json existed (with less detail).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .replay import read_events


def _fmt(v, d=1, unit=""):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{v:.{d}f}{unit}" if isinstance(v, (int, float)) else str(v)


def load_marks(path: Path | str) -> list[dict]:
    """Field-test sheet (docs/field_test_marks.csv); rows without a measurement are skipped."""
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            sd = (r.get("signed_distance_cm") or "").strip()
            if not sd:
                continue
            rows.append({"bounce": r.get("bounce"), "line": (r.get("line") or "").strip(), "signed_cm": float(sd),
                         "notes": r.get("notes", "")})
    return rows


def score_marks(decisions: list[dict], marks: list[dict]) -> dict:
    """Match drill bounces to decisions in order (the drill has one bounce at a time).

    Error = system signed distance - measured signed distance (both: line's outer edge to the
    ball's nearest edge, positive = out).
    """
    ds = [d for d in decisions if not d.get("suppressed") and d.get("distance_cm") is not None]
    rows = []
    for i, m in enumerate(marks):
        d = ds[i] if i < len(ds) else None
        truth = "OUT" if m["signed_cm"] > 0 else "IN"
        row = {"bounce": m["bounce"], "line": m["line"], "measured_cm": m["signed_cm"], "truth": truth}
        if d is not None:
            row.update(t=d["t"], system_cm=d["distance_cm"], system_line=d.get("line"), result=d.get("result"),
                       spoken=bool(d.get("announce")), p_out=d.get("p_out"), cams=len(d.get("cameras") or []),
                       err_cm=d["distance_cm"] - m["signed_cm"])
        rows.append(row)
    matched = [r for r in rows if "err_cm" in r]
    errs = np.abs([r["err_cm"] for r in matched]) if matched else np.array([])
    return {
        "rows": rows,
        "marks": len(marks), "decisions": len(ds), "matched": len(matched),
        "count_mismatch": len(ds) != len(marks),
        "median_abs_err_cm": float(np.median(errs)) if len(errs) else None,
        "p90_abs_err_cm": float(np.percentile(errs, 90)) if len(errs) else None,
        "wrong_out_spoken": sum(1 for r in matched if r["spoken"] and r["result"] == "OUT" and r["truth"] == "IN"),
        "clear_out_called": sum(1 for r in matched if r["measured_cm"] > 10 and r["spoken"]),
        "clear_out_total": sum(1 for r in rows if r["measured_cm"] > 10),
        "uncertain": sum(1 for r in matched if r["result"] == "UNCERTAIN"),
    }


def build_report(session: Path | str, marks_csv: Path | str | None = None) -> tuple[str, dict]:
    session = Path(session)
    events = read_events(session)
    man = json.loads((session / "session.json").read_text()) if (session / "session.json").exists() else {}
    summ = man.get("summary") or {}
    decisions = [e for e in events if e.get("type") == "decision"]
    reports = [e for e in events if e.get("type") == "report"]
    L: list[str] = [f"# Session {session.name}", ""]
    if man:
        g = man.get("git", {})
        v = man.get("versions", {})
        L += [f"* **When:** {man.get('started_at', '?')} → {man.get('ended_at', 'not closed cleanly')}"
              f" ({_fmt(summ.get('duration_s'), 0, ' s')})",
              f"* **Code:** commit `{g.get('commit', '?')}`{' + ' + str(g.get('changed_files')) + ' uncommitted files' if g.get('changed_files') else ''};"
              f" bounce {v.get('bounce')}, fusion {v.get('fusion')}, phone detector {v.get('phone_detector')}, protocol {v.get('protocol')}",
              f"* **Command:** `{man.get('command', '')}`",
              f"* **Court:** {man.get('court', {}).get('name', '?')}, "
              f"{_fmt(man.get('court', {}).get('width'), 2)} × {_fmt(man.get('court', {}).get('length'), 2)} m",
              f"* **Settings:** {json.dumps(man.get('settings', {}))}", ""]
    else:
        L += ["*(no session.json: recorded before session manifests existed)*", ""]

    # Cameras
    connects = {}
    for e in events:
        if e.get("type") == "camera_connected":
            connects.setdefault(e["camera"], e)
    last_stats = {}
    worst = {}
    for e in events:
        if e.get("type") == "camera_stats":
            last_stats[e["camera"]] = e
            w = worst.setdefault(e["camera"], {"min_fps_in": None, "max_latency_ms": None})
            # The phone's capture rate when it reports one: a phone that skips still frames
            # (data reduction) sends fewer frames than it captures.
            fps = (e.get("phone") or {}).get("fps_capture") or e.get("fps_in")
            if fps and fps > 0 and e.get("connected", True):
                w["min_fps_in"] = fps if w["min_fps_in"] is None else min(w["min_fps_in"], fps)
            if e.get("latency_ms") is not None:
                w["max_latency_ms"] = max(w["max_latency_ms"] or 0, e["latency_ms"])
    cams = summ.get("cameras") or list(last_stats.values())
    names = sorted(set(connects) | {c["camera"] for c in cams})
    L += ["## Cameras", "", "| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        c = next((x for x in cams if x["camera"] == n), {})
        con = connects.get(n, {})
        clk = c.get("clock") or {}
        frames = c.get("frames_in") or 0
        drop_pct = 100 * (c.get("drops") or 0) / frames if frames else None
        disc = sum(1 for e in events if e.get("type") == "camera_disconnected" and e.get("camera") == n)
        L.append(f"| {n} | {con.get('mode', c.get('mode', '?'))} | {con.get('device', c.get('device', ''))[:40]} | {frames} | "
                 f"{c.get('drops', '–')} ({_fmt(drop_pct, 1, '%')}) | {_fmt(clk.get('rtt_ms'), 0)} / ±{_fmt(clk.get('uncertainty_ms'), 1)} ms | "
                 f"{_fmt(c.get('calib_rms_px'), 2, ' px')} | {_fmt(worst.get(n, {}).get('min_fps_in'), 0)} | "
                 f"{_fmt(worst.get(n, {}).get('max_latency_ms'), 0, ' ms')} | {disc} |")
    L.append("")

    # Calls
    by: dict[str, int] = {}
    for d in decisions:
        k = "suppressed (2nd bounce)" if d.get("suppressed") else str(d.get("result"))
        by[k] = by.get(k, 0) + 1
    lat = [d["latency_s"] for d in decisions if d.get("latency_s") is not None]
    multi = sum(1 for d in decisions if len(d.get("cameras") or []) > 1)
    L += ["## Calls", "",
          f"{len(reports)} single-camera reports → {len(decisions)} decisions ({multi} seen by 2+ cameras): "
          + ", ".join(f"{k} {v}" for k, v in sorted(by.items())),
          f"Spoken: {sum(1 for d in decisions if d.get('announce'))}. "
          f"Delay bounce → call: median {_fmt(float(np.median(lat)) if lat else None, 2, ' s')}, "
          f"max {_fmt(max(lat) if lat else None, 2, ' s')}.", "",
          "| t (s) | call | spoken | p(out) | line | distance | cameras | note |", "|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        note = d.get("suppressed") or (f"unconfirmed by {', '.join(d['unconfirmed_by'])}" if d.get("unconfirmed_by") else "")
        if d.get("cameras_disagree"):
            note = (note + "; " if note else "") + f"cameras disagree (chi2 {d.get('chi2', 0):.0f})"
        L.append(f"| {d['t']:.2f} | {d.get('result', '–')} | {'**' + str(d.get('text')) + '**' if d.get('announce') else ''} | "
                 f"{_fmt(d.get('p_out'), 2)} | {d.get('line') or ''} | {_fmt(d.get('distance_cm'), 1, ' cm')} | "
                 f"{len(d.get('cameras') or [])} | {note} |")
    L.append("")

    result: dict = {"decisions": len(decisions), "reports": len(reports), "calls": by}
    if marks_csv:
        sc = score_marks(decisions, load_marks(marks_csv))
        result["marks"] = sc
        L += ["## Accuracy against the chalk marks", "",
              f"{sc['marks']} measured marks, {sc['decisions']} decisions (matched in order"
              f"{'; **counts differ: check the table for a shifted match**' if sc['count_mismatch'] else ''}).", "",
              f"* Median error {_fmt(sc['median_abs_err_cm'], 1, ' cm')}, 90 % within {_fmt(sc['p90_abs_err_cm'], 1, ' cm')}",
              f"* Spoken OUT on a ball that was in: **{sc['wrong_out_spoken']}**",
              f"* Clear outs (> 10 cm) called: {sc['clear_out_called']} of {sc['clear_out_total']}",
              f"* Unsure (silent): {sc['uncertain']}", "",
              "| # | line | measured | system | error | call | spoken | p(out) | cameras |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sc["rows"]:
            L.append(f"| {r['bounce']} | {r['line']} | {r['measured_cm']:+.1f} cm | {_fmt(r.get('system_cm'), 1, ' cm')} | "
                     f"{_fmt(r.get('err_cm'), 1, ' cm')} | {r.get('result', 'no decision')} | {'yes' if r.get('spoken') else ''} | "
                     f"{_fmt(r.get('p_out'), 2)} | {r.get('cams', '')} |")
        L.append("")

    warns = [e for e in events if e.get("type") == "warning"]
    if warns:
        L += ["## Warnings", ""] + [f"* {_fmt(e.get('t'), 1)} s {e.get('camera', '')}: {e.get('text')}" for e in warns[:50]] + [""]
    calib = [e for e in events if e.get("type") == "calibrated"]
    if calib:
        L += ["## Calibrations", ""]
        for e in calib:
            worst_pt = max((e.get("per_point_px") or {}).items(), key=lambda kv: kv[1], default=None)
            L.append(f"* {e['camera']} at {e['t']:.0f} s: RMS {e['rms_px']:.2f} px from {e['points']} points"
                     + (f"; worst point {worst_pt[0]} {worst_pt[1]:.1f} px" if worst_pt else ""))
        L.append("")
    replays = sorted((session / "replays").glob("replay-*.json")) if (session / "replays").exists() else []
    if replays:
        L += ["## Replays with later code", ""]
        for p in replays:
            r = json.loads(p.read_text())
            c = r.get("comparison", {})
            L.append(f"* {p.name}: commit `{r.get('git', {}).get('commit', '?')}` → "
                     + ("identical" if c.get("identical") else
                        f"{len(c.get('changed', []))} changed, {len(c.get('moved', []))} moved, "
                        f"{len(c.get('only_live', []))} gone, {len(c.get('only_replay', []))} new"))
        L.append("")
    return "\n".join(L), result


def write_report(session: Path | str, marks_csv: Path | str | None = None) -> Path:
    text, _ = build_report(session, marks_csv)
    p = Path(session) / "report.md"
    p.write_text(text)
    return p


def list_sessions(data_dir: Path | str = "data/live") -> list[dict]:
    out = []
    root = Path(data_dir) / "sessions"
    for d in sorted(root.glob("*")) if root.exists() else []:
        if not d.is_dir():
            continue
        man = json.loads((d / "session.json").read_text()) if (d / "session.json").exists() else {}
        s = man.get("summary") or {}
        ev = read_events(d) if not s else []
        out.append({"session": d.name, "duration_s": s.get("duration_s"),
                    "cameras": len(s.get("cameras") or []) or len({e["camera"] for e in ev if e.get("type") == "camera_connected"}),
                    "decisions": s.get("decisions", sum(1 for e in ev if e.get("type") == "decision")),
                    "spoken": s.get("announced"), "commit": (man.get("git") or {}).get("commit", "?")[:10],
                    "recorded": any((x / "index.csv").exists() or (x / "dets.jsonl").exists() for x in d.iterdir() if x.is_dir())})
    return out
