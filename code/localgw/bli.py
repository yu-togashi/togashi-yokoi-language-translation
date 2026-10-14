"""Standard evaluation of a GW coupling for BLI (shared by otalign and GWTune runs).

GW vocabulary (candidates = target top-K): coupling / proj / proj+CSLS with dictionaries
0-5000 and full. 200k candidates (MUSE protocol): proj NN / CSLS with dictionaries
0-5000 and 5000-6500. proj = orthogonal map from mutual-NN anchors of the coupling.
"""

from __future__ import annotations

import numpy as np

from localgw.data import load_dictionary, load_vectors
from localgw.evaluate import bli_accuracy, score_accuracy
from localgw.mapping import projection_from_coupling
from localgw.preprocess import normalize_embeddings


def _reachable(d: dict[str, list[str]], targets: set[str]) -> dict[str, list[str]]:
    d = {w: [g for g in gs if g in targets] for w, gs in d.items()}
    return {w: gs for w, gs in d.items() if gs}


def evaluate_coupling(coupling: np.ndarray, src: str, trg: str, k: int,
                      gwvocab_dicts=("0-5000", "full"),
                      full_dicts=("0-5000", "5000-6500")) -> tuple[list[dict], dict]:
    """Returns (rows, info). Each row: candidates, dict, score, n_queries, P@1/5/10."""
    ws_all, xs_all, _ = load_vectors(src)
    wt_all, xt_all, _ = load_vectors(trg)
    ws, wt = ws_all[:k], wt_all[:k]
    xs, xt = normalize_embeddings(xs_all[:k]), normalize_embeddings(xt_all[:k])
    P, n_anchors = projection_from_coupling(coupling, xs, xt)

    rows = []
    t_set = set(wt)
    for name in gwvocab_dicts:
        d = load_dictionary(src, trg, name)
        rows.append({"candidates": f"GW vocab {k}", "dict": name, "score": "coupling",
                     **score_accuracy(coupling, ws, wt, d)})
        d_in = _reachable(d, t_set)
        for method, score in [("nn", "proj"), ("csls", "proj_csls")]:
            acc = bli_accuracy(xs, xt @ P.T, ws, wt, d_in, method=method)
            acc.pop("coverage")
            rows.append({"candidates": f"GW vocab {k}", "dict": name, "score": score, **acc})

    xs_all = normalize_embeddings(xs_all, k)
    xt_all = normalize_embeddings(xt_all, k)
    for name in full_dicts:
        d = load_dictionary(src, trg, name)
        for method, score in [("nn", "proj"), ("csls", "proj_csls")]:
            acc = bli_accuracy(xs_all, xt_all @ P.T, ws_all, wt_all, d, method=method)
            acc.pop("coverage")
            rows.append({"candidates": f"{len(wt_all)}", "dict": name, "score": score, **acc})
    return rows, {"n_anchors": n_anchors}
