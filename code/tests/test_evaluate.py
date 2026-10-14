import numpy as np

from localgw.evaluate import bli_accuracy, score_accuracy


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


def test_score_accuracy_drops_unreachable_queries():
    scores = np.array([[0.9, 0.1], [0.2, 0.8], [0.6, 0.4]])
    src, trg = ["a", "b", "c"], ["A", "B"]
    # "c" is wrong; "d" is not a row; "a" has a gold outside the candidates plus a reachable one
    d = {"a": ["Z", "A"], "b": ["B"], "c": ["B"], "d": ["A"], "e": ["Z"]}
    acc = score_accuracy(scores, src, trg, d, ks=(1, 2))
    assert acc["n_queries"] == 3
    assert acc["P@1"] == 2 / 3 and acc["P@2"] == 1.0
