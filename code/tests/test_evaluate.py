import numpy as np

from localgw.evaluate import bli_accuracy


def test_bli_accuracy_identity_mapping():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(50, 8))
    words = [f"w{i}" for i in range(50)]
    trg = [f"v{i}" for i in range(50)]
    d = {f"w{i}": [f"v{i}"] for i in range(20)}
    for method in ["nn", "csls"]:
        acc = bli_accuracy(x, x, words, trg, d, method=method, knn=3)
        assert acc["P@1"] == 1.0 and acc["n_queries"] == 20


def test_bli_accuracy_one_to_many_and_oov():
    x = np.eye(4)
    src = ["a", "b", "c", "d"]
    trg = ["A", "B", "C", "D"]
    # "a" has a wrong first gold but a correct second one; "zz" is not in the source vocab
    d = {"a": ["B", "A"], "b": ["C"], "zz": ["A"]}
    acc = bli_accuracy(x, x, src, trg, d, method="nn", ks=(1,))
    assert acc["n_queries"] == 2
    assert acc["P@1"] == 0.5
    assert acc["coverage"] == 2 / 3
