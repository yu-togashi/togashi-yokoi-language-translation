"""Evaluate an otalign run inside the GW vocabulary (candidates = target top-K words).

Scores: coupling (argmax of Γ), proj (orthogonal map, NN) and proj+CSLS, each with the
MUSE dictionaries 0-5000, 5000-6500 and full. Only queries with a gold translation inside
the GW vocabulary are counted. P@1 of coupling is also broken down by source frequency rank.

Usage: poetry run python code/experiments/eval_otalign_gwvocab.py <run_dir_name>
  e.g. en-es_K20000_ereg1e-4_t64
Output: analysis/tables/otalign_gwvocab_<run>.csv
"""

from __future__ import annotations

import argparse
import pickle
import re

import numpy as np
import pandas as pd

from localgw.data import REPO_ROOT, load_dictionary, load_vectors
from localgw.evaluate import bli_accuracy, score_accuracy

RUN_DIR = REPO_ROOT / "data" / "processed" / "otalign"
OUT_DIR = REPO_ROOT / "analysis" / "tables"
DICTS = ["0-5000", "5000-6500", "full"]
RANK_BINS = [(0, 5000), (5000, 10000), (10000, 20000)]


def normalize(x: np.ndarray) -> np.ndarray:
    """otalign 'both' on the GW vocabulary: centre, then unit length."""
    x = x.astype("float64") - x.mean(axis=0)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    args = ap.parse_args()
    m = re.match(r"(\w+)-(\w+)_K(\d+)_", args.run)
    src, trg, k = m[1], m[2], int(m[3])

    out = RUN_DIR / args.run / "out"
    (pkl,) = out.rglob("results.pkl")
    (coupling_path,) = out.rglob("coupling.npy")
    P = pickle.load(open(pkl, "rb"))["P"]
    G = np.load(coupling_path, mmap_mode="r")

    ws, xs, _ = load_vectors(src, k)
    wt, xt, _ = load_vectors(trg, k)
    xs, xt = normalize(xs), normalize(xt)
    t_set = set(wt)

    rows = []
    for name in DICTS:
        d = load_dictionary(src, trg, name)
        rows.append({"run": args.run, "dict": name, "score": "coupling",
                     **score_accuracy(G, ws, wt, d)})
        # same reachable-query convention as score_accuracy
        d_in = {w: [g for g in gs if g in t_set] for w, gs in d.items()}
        d_in = {w: gs for w, gs in d_in.items() if gs}
        for method in ["nn", "csls"]:
            acc = bli_accuracy(xs, xt @ P.T, ws, wt, d_in, method=method)
            acc.pop("coverage")
            rows.append({"run": args.run, "dict": name,
                         "score": "proj" if method == "nn" else "proj_csls", **acc})
        if name == "full":
            for lo, hi in RANK_BINS:
                if lo >= k:
                    continue
                in_bin = set(ws[lo:hi])
                d_bin = {w: gs for w, gs in d.items() if w in in_bin}
                rows.append({"run": args.run, "dict": f"full, en rank {lo}-{hi}", "score": "coupling",
                             **score_accuracy(G, ws, wt, d_bin)})
    df = pd.DataFrame(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / f"otalign_gwvocab_{args.run}.csv", index=False)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
