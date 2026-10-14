"""Evaluate an otalign run's orthogonal map on the full 200k vocabulary (MUSE protocol).

Reproduces otalign's preprocessing ("both": centre the top-K block and the remaining
block separately, then unit length), maps the target with the learned P
(score = cos(xs, xt @ P.T), as otalign's 'projected' score), and retrieves among all
200k target words with NN and CSLS, for MUSE dictionaries 0-5000 and 5000-6500.

Usage: poetry run python code/experiments/eval_otalign_200k.py <run_dir_name> [--K 20000]
  e.g. en-es_K20000_ereg1e-4_t64
Output: analysis/tables/otalign_200k_<run>.csv
"""

from __future__ import annotations

import argparse
import pickle
import re

import pandas as pd

from localgw.data import REPO_ROOT, load_dictionary, load_vectors
from localgw.evaluate import bli_accuracy

RUN_DIR = REPO_ROOT / "data" / "processed" / "otalign"
OUT_DIR = REPO_ROOT / "analysis" / "tables"


def otalign_normalize(x, k):
    x = x.astype("float64").copy()
    x[:k] -= x[:k].mean(axis=0)
    x[k:] -= x[k:].mean(axis=0)
    x /= (x**2).sum(axis=1, keepdims=True) ** 0.5
    return x


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    args = ap.parse_args()
    m = re.match(r"(\w+)-(\w+)_K(\d+)_", args.run)
    src, trg, k = m[1], m[2], int(m[3])

    (pkl,) = (RUN_DIR / args.run / "out").rglob("results.pkl")
    P = pickle.load(open(pkl, "rb"))["P"]

    ws, xs, _ = load_vectors(src)
    wt, xt, _ = load_vectors(trg)
    xs, xt = otalign_normalize(xs, k), otalign_normalize(xt, k)
    xt_mapped = xt @ P.T

    rows = []
    for fold in ["0-5000", "5000-6500"]:
        d = load_dictionary(src, trg, fold)
        for method in ["nn", "csls"]:
            acc = bli_accuracy(xs, xt_mapped, ws, wt, d, method=method)
            rows.append({"run": args.run, "dict": fold, "method": method, **acc})
            print(rows[-1])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_DIR / f"otalign_200k_{args.run}.csv", index=False)


if __name__ == "__main__":
    main()
