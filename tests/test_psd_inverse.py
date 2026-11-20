"""Velocity covariances must stay positive definite (field test 2 replay produced negative variances)."""

import numpy as np

from balltracker.bounce import psd_inverse


def test_regular_matrix_is_a_plain_inverse():
    A = np.random.default_rng(1).normal(size=(20, 3))
    N = A.T @ A
    assert np.allclose(psd_inverse(N), np.linalg.inv(N))


def test_near_singular_matrix_gives_large_positive_variance():
    # A camera that sees x and y moving together only: the x-y difference is unmeasured.
    M = np.array([[1e8, 1e8 - 1e-3, 0], [1e8 - 1e-3, 1e8, 0], [0, 0, 4.0]])
    C = psd_inverse(M)
    assert np.all(np.linalg.eigvalsh(C) > 0)
    d = np.array([1.0, -1.0, 0.0]) / np.sqrt(2)
    assert d @ C @ d > 100 * (np.array([0, 0, 1.0]) @ C @ np.array([0, 0, 1.0]))  # unmeasured >> measured
    assert np.all(np.isfinite(C))


def test_fusion_never_gives_a_camera_negative_weight():
    from types import SimpleNamespace

    from balltracker.live.playstate import flight

    def rep(v, cov):
        ph = {"v_in": v, "v_out": v, "v_in_cov": cov, "v_out_cov": cov}
        return SimpleNamespace(provenance=SimpleNamespace(params={"physics": ph}))

    good = rep([3.0, 0.0, -9.0], (np.eye(3) * 0.01).tolist())
    # A broken report: a negative variance along y with a wild y velocity.
    bad = rep([3.0, 40.0, -9.0], np.diag([0.01, -0.5, 0.01]).tolist())
    f = flight([good, bad])
    assert abs(f["v_in"][1]) < 1.0, f["v_in"]  # the bad camera must not drag y (or push it the other way)
