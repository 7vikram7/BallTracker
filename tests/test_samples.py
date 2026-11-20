"""Real field data shipped with the repo (data/samples): the whole live pipeline replays it."""

from pathlib import Path

import pytest

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "samples" / "fieldtest2_60s"


@pytest.mark.slow
@pytest.mark.skipif(not SAMPLE.exists(), reason="sample data missing")
def test_field_test_2_sample_replays_with_play_state(tmp_path):
    import shutil

    from balltracker.live.replay import replay

    s = tmp_path / SAMPLE.name
    shutil.copytree(SAMPLE, s)
    res = replay(s)
    dec = res["decisions"]
    assert len(dec) >= 5, len(dec)  # a rally's worth of bounces in 60 s
    judged = [d for d in dec if not d.get("suppressed")]
    assert all(d.get("play") for d in judged), "every judged bounce has a play-state label"
    # Field test 2 lesson: no OUT may be announced from one camera with poor depth precision,
    # nor for dead balls.
    for d in dec:
        if d.get("announce"):
            assert d["play"] in ("rally", "start of play")  # real reports always carry flight data
            assert len(d["cameras"]) >= 2 or d.get("single_camera_std_cm") is None


@pytest.mark.slow
@pytest.mark.skipif(not SAMPLE.exists(), reason="sample data missing")
def test_gzipped_detections_replay_identically(tmp_path):
    """data/field stores large dets.jsonl as dets.jsonl.gz; replay must give the same decisions."""
    import gzip
    import shutil

    from balltracker.live.replay import replay

    plain, packed = tmp_path / "plain", tmp_path / "packed"
    shutil.copytree(SAMPLE, plain)
    shutil.copytree(SAMPLE, packed)
    for f in packed.glob("*/dets.jsonl"):
        f.with_name("dets.jsonl.gz").write_bytes(gzip.compress(f.read_bytes()))
        f.unlink()
    key = lambda r: [(d["t"], d.get("result"), d.get("suppressed")) for d in r["decisions"]]  # noqa: E731
    a, b = replay(plain), replay(packed)
    assert key(a) == key(b) and len(a["decisions"]) >= 5
