import numpy as np
from scipy.spatial.distance import cdist

from localgw.preprocess import threshold_distances


def test_threshold_distances():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(50, 3))
    c = cdist(x, x)
    t, tau = threshold_distances(c, 0.25, 10.0)
    off = ~np.eye(50, dtype=bool)
    assert np.isclose(np.mean(c[off] <= tau), 0.25, atol=0.01)
    assert (np.diag(t) == 0).all()
    np.testing.assert_array_equal(t[c <= tau], c[c <= tau])
    assert (t[(c > tau) & off] == 10.0).all()
    np.testing.assert_array_equal(t, t.T)
