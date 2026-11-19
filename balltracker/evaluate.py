"""Compare analysed bounces / calls with ground truth.

Two ground-truth sources are supported:

1. Synthetic (``ground_truth.json`` from ``bt synth``): exact contact times and
   positions. Bounces are matched by time.
2. Field measurements (CSV) from the chalk drill, one row per bounce mark::

       bounce,t_s,x_m,y_m,line,signed_distance_cm,notes
       1,,,,baseline_B,3.5,"mark fully outside"
       2,12.84,1.20,6.71,,,

   Provide either x_m/y_m (court frame) or line + signed_distance_cm
   from the line's outer edge to the nearest edge of the chalk mark (positive =
   outside, <= 0 = touching/inside = IN). ``t_s``
   is optional; without it bounces are matched in order.

Call metrics are computed from the TRUE contact using the same rules, so the
question "would the system's call match the truth?" is answered directly.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .events import AnalysisResult, CallResult
from .geometry.court import CourtSpec, Side


@dataclass
class MatchedBounce:
    true_t: float | None
    true_x: float | None
    true_y: float | None
    true_signed_cm: float | None
    pred_t: float | None
    pred_x: float | None
    pred_y: float | None
    pred_signed_cm: float | None
    pred_sigma_cm: float | None
    true_call: str | None
    pred_call: str | None
    p_out: float | None


def _truth_call(court: CourtSpec, x: float, y: float) -> tuple[str, float]:
    side = Side.B if y >= 0 else Side.A
    rect = court.half_rect(side)
    d = float(rect.distance_outside(np.array(x), np.array(y)))
    sd = float(rect.signed_distance(np.array(x), np.array(y))) - court.contact_patch_radius
    return ("OUT" if d > court.contact_patch_radius else "IN"), sd


def load_truth(path: str | Path, court: CourtSpec) -> list[dict]:
    path = Path(path)
    rows: list[dict] = []
    if path.suffix == ".json":
        gt = json.loads(path.read_text())
        for b in gt["bounces"]:
            call, sd = _truth_call(court, b["x"], b["y"])
            rows.append({"t": b["t"], "x": b["x"], "y": b["y"], "signed_m": sd, "call": call})
        return rows
    with open(path) as f:
        for r in csv.DictReader(f):
            row: dict = {"t": float(r["t_s"]) if r.get("t_s") else None, "x": None, "y": None, "signed_m": None, "call": None}
            if r.get("x_m") and r.get("y_m"):
                row["x"], row["y"] = float(r["x_m"]), float(r["y_m"])
                row["call"], row["signed_m"] = _truth_call(court, row["x"], row["y"])
            elif r.get("signed_distance_cm"):
                # Measured from the line's outer edge to the NEAREST EDGE of the chalk
                # mark, i.e. the same quantity as LineCallEvent.signed_distance_m.
                sd = float(r["signed_distance_cm"]) / 100
                row["signed_m"] = sd
                row["call"] = "OUT" if sd > 0 else "IN"
                row["line"] = r.get("line")
            rows.append(row)
    return rows


def match(result: AnalysisResult, truth: list[dict], max_dt: float = 0.06, visible_only: bool = True) -> list[MatchedBounce]:
    calls_by_bounce = {c.bounce_id: c for c in result.calls}
    preds = sorted(result.bounces, key=lambda b: b.t)
    used: set[int] = set()
    out: list[MatchedBounce] = []
    by_time = all(t.get("t") is not None for t in truth)
    for i, tr in enumerate(truth):
        j_best = None
        if by_time:
            dts = [abs(p.t - tr["t"]) if k not in used else 1e9 for k, p in enumerate(preds)]
            if dts and min(dts) <= max_dt:
                j_best = int(np.argmin(dts))
        elif i < len(preds):
            j_best = i
        p = preds[j_best] if j_best is not None else None
        if j_best is not None:
            used.add(j_best)
        c = calls_by_bounce.get(p.id) if p else None
        sig = float(np.sqrt(max(np.linalg.eigvalsh(np.array(p.cov_xy)).max(), 0))) * 100 if p else None
        out.append(
            MatchedBounce(
                true_t=tr.get("t"), true_x=tr.get("x"), true_y=tr.get("y"),
                true_signed_cm=tr["signed_m"] * 100 if tr.get("signed_m") is not None else None,
                pred_t=p.t if p else None, pred_x=p.position.x if p else None, pred_y=p.position.y if p else None,
                pred_signed_cm=c.signed_distance_m * 100 if c else None,
                pred_sigma_cm=sig,
                true_call=tr.get("call"),
                pred_call=c.result.value if c else None,
                p_out=c.p_out if c else None,
            )
        )
    # Unmatched predictions = false bounces.
    for k, p in enumerate(preds):
        if k not in used:
            c = calls_by_bounce.get(p.id)
            out.append(MatchedBounce(None, None, None, None, p.t, p.position.x, p.position.y,
                                     c.signed_distance_m * 100 if c else None, None, None,
                                     c.result.value if c else None, c.p_out if c else None))
    return out


def summarise(matches: list[MatchedBounce], close_cm: float = 10.0) -> dict:
    truth = [m for m in matches if m.true_call is not None]
    detected = [m for m in truth if m.pred_t is not None]
    false_bounces = [m for m in matches if m.true_call is None]
    pos_err = [
        100 * float(np.hypot(m.pred_x - m.true_x, m.pred_y - m.true_y))
        for m in detected if m.true_x is not None and m.pred_x is not None
    ]
    line_err = [abs(m.pred_signed_cm - m.true_signed_cm) for m in detected
                if m.pred_signed_cm is not None and m.true_signed_cm is not None]
    t_err = [1000 * abs(m.pred_t - m.true_t) for m in detected if m.true_t is not None]
    judged = [m for m in detected if m.pred_call is not None]

    def counts(ms):
        c = {"true_out": 0, "true_in": 0, "out_called_out": 0, "out_silent_uncertain": 0, "out_called_in": 0,
             "in_called_out": 0, "in_uncertain": 0, "in_called_in": 0}
        for m in ms:
            if m.true_call == "OUT":
                c["true_out"] += 1
                c[{"OUT": "out_called_out", "UNCERTAIN": "out_silent_uncertain", "IN": "out_called_in"}[m.pred_call]] += 1
            else:
                c["true_in"] += 1
                c[{"OUT": "in_called_out", "UNCERTAIN": "in_uncertain", "IN": "in_called_in"}[m.pred_call]] += 1
        return c

    def stats(xs):
        if not xs:
            return None
        a = np.array(xs)
        return {"n": len(a), "median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(a.max())}

    close = [m for m in judged if m.true_signed_cm is not None and abs(m.true_signed_cm) <= close_cm]
    return {
        "true_bounces": len(truth),
        "detected": len(detected),
        "recall": len(detected) / len(truth) if truth else None,
        "false_bounces": len(false_bounces),
        "position_error_cm": stats(pos_err),
        "line_distance_error_cm": stats(line_err),
        "timing_error_ms": stats(t_err),
        "calls_all": counts(judged),
        f"calls_within_{close_cm:g}cm_of_line": counts(close),
        "WRONG_OUT_CALLS": sum(1 for m in judged if m.true_call == "IN" and m.pred_call == "OUT"),
        "MISSED_OUT_CALLS": sum(1 for m in judged if m.true_call == "OUT" and m.pred_call != "OUT"),
    }


def visible_truth(truth: list[dict], gt_json: dict, court: CourtSpec) -> list[dict]:
    """Keep synthetic true bounces whose contact point projects inside the image."""
    from .geometry.camera import Camera

    cam = Camera.from_dict(gt_json["camera_true"])
    w, h = cam.image_size
    keep = []
    for t in truth:
        P = np.array([[t["x"], t["y"], court.ball_radius]])
        if cam.depth(P)[0] <= 0:
            continue
        u, v = cam.project(P)[0]
        if 0 <= u < w and 0 <= v < h:
            keep.append(t)
    return keep
