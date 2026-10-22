import warnings

import numpy as np
from scipy.spatial.distance import cdist

from localgw.gwtune_ext import GWTuneSolver, MainGromovWasserstainComputation


def _problem(n=40, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, 5))
    y = x @ np.linalg.qr(rng.normal(size=(5, 5)))[0] + 0.05 * rng.normal(size=(n, 5))
    c1, c2 = cdist(x, x), cdist(y, y)
    return c1 / c1.mean(), c2 / c2.mean()


def test_defaults_reproduce_gwtune():
    c1, c2 = _problem()
    kw = dict(max_iter=50, numItermax=200, tol=1e-9)
    ref = MainGromovWasserstainComputation(c1, c2, **kw)
    ext = GWTuneSolver(c1, c2, **kw)
    T0 = ref.init_mat_builder.make_initial_T("uniform")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        a = ref.entropic_gw_computation(0.05, T0)
        b = ext.entropic_gw_computation(0.05, T0)
    assert a["cpt"] == b["cpt"]
    np.testing.assert_allclose(a["ot"], b["ot"])


def test_warmstart_reduces_inner_iterations():
    c1, c2 = _problem()
    kw = dict(max_iter=100, numItermax=5000, tol=1e-9, sinkhorn_stopThr=1e-6)
    cold = GWTuneSolver(c1, c2, warmstart=False, **kw)
    warm = GWTuneSolver(c1, c2, warmstart=True, **kw)
    T0 = cold.init_mat_builder.make_initial_T("uniform")
    a = cold.entropic_gw_computation(0.01, T0)
    b = warm.entropic_gw_computation(0.01, T0)
    assert sum(b["sinkhorn_niter"][1:]) < sum(a["sinkhorn_niter"][1:])
    # same fixed point up to the Sinkhorn tolerance
    assert np.abs(a["ot"] - b["ot"]).max() < 1e-3


def test_snapshots_record_first_crossing():
    c1, c2 = _problem()
    s = GWTuneSolver(c1, c2, max_iter=200, numItermax=5000, tol=1e-12, sinkhorn_stopThr=1e-6,
                     warmstart=True, snapshot_tols=(1e-4, 1e-6))
    log = s.entropic_gw_computation(0.01, s.init_mat_builder.make_initial_T("uniform"))
    tols = [snap["tol"] for snap in log["snapshots"]]
    assert len(tols) >= 1
    assert tols == sorted(tols, reverse=True)
    for snap in log["snapshots"]:
        assert snap["err"] < snap["tol"] and snap["ot"].shape == (40, 40)


def test_min_iter_delays_tol_stop():
    c1, c2 = _problem()
    kw = dict(max_iter=100, numItermax=5000, tol=0.5, sinkhorn_stopThr=1e-6, warmstart=True)
    s = GWTuneSolver(c1, c2, **kw)
    T0 = s.init_mat_builder.make_initial_T("uniform")
    assert s.entropic_gw_computation(0.01, T0)["cpt"] == 1  # stops at the first check (iteration 0)
    s = GWTuneSolver(c1, c2, min_iter=20, **kw)
    assert s.entropic_gw_computation(0.01, T0)["cpt"] == 21  # stops after the check at iteration 20
