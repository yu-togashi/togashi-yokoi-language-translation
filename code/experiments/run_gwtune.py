"""Solve the Conneau/MUSE GW-BLI problem with GWTune's entropic GW, then evaluate.

Uses localgw.gwtune_ext.GWTuneSolver (GWTune's loop + optional Sinkhorn stopThr / warm start).
Same setting as otalign: top-K words per language, otalign normalization ('both'),
cosine distance / mean, uniform p, q, init T = p qᵀ ("uniform"), fixed epsilon, no optuna.
Note the loss scale: POT/GWTune use (a-b)^2, otalign (a-b)^2/2, so GWTune eps = 2 * otalign λ.

Usage:
  poetry run python code/experiments/run_gwtune.py en es 2000 2e-4 --max-iter 1000 \
      [--tol 1e-8] [--sinkhorn sinkhorn|sinkhorn_log] [--sinkhorn-stopthr 3.16e-5] [--warmstart]
      [--backend numpy|torch] [--threads 16] [--tag TAG]
Outputs: data/processed/gwtune/<src>-<trg>_K<K>_eps<eps>_<sinkhorn>_stop<thr>[_warm]_<backend>_t<threads>[_TAG]/
  result.json (timings, per-iteration times, Sinkhorn inner iterations, P@1 rows), coupling.npy
"""

from __future__ import annotations

import argparse
import os

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("trg")
ap.add_argument("K", type=int)
ap.add_argument("eps", type=float)
ap.add_argument("--max-iter", type=int, default=1000)
ap.add_argument("--tol", type=float, default=1e-8)
ap.add_argument("--numitermax", type=int, default=1000, help="Sinkhorn inner iterations")
ap.add_argument("--sinkhorn", default="sinkhorn")
ap.add_argument("--sinkhorn-stopthr", type=float, default=1e-9,
                help="Sinkhorn stopThr on ||marginal err||_2 (GWTune default 1e-9; otalign ~ 3.16e-5)")
ap.add_argument("--warmstart", action="store_true", help="warm-start Sinkhorn across GW iterations")
ap.add_argument("--first-stopthr", type=float, default=None,
                help="Sinkhorn stopThr for the first GW iteration only (otalign: 1e-9)")
ap.add_argument("--backend", default="numpy", choices=["numpy", "torch"])
ap.add_argument("--threads", type=int, default=16)
ap.add_argument("--tag", default="")
ap.add_argument("--no-eval", action="store_true")
args = ap.parse_args()

for var in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ[var] = str(args.threads)

import json  # noqa: E402
import resource  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

from localgw.bli import evaluate_coupling  # noqa: E402
from localgw.data import REPO_ROOT, load_vectors  # noqa: E402
from localgw.gwtune_ext import GWTuneSolver  # noqa: E402
from localgw.preprocess import distance_matrix, normalize_embeddings  # noqa: E402

if args.backend == "torch":
    import torch  # noqa: E402

    torch.set_num_threads(args.threads)


def main() -> None:
    name = (f"{args.src}-{args.trg}_K{args.K}_eps{args.eps:g}_{args.sinkhorn}"
            f"_stop{args.sinkhorn_stopthr:g}"
            f"{f'_first{args.first_stopthr:g}' if args.first_stopthr is not None else ''}"
            f"{'_warm' if args.warmstart else ''}_{args.backend}"
            f"_t{args.threads}{'_' + args.tag if args.tag else ''}")
    outdir = REPO_ROOT / "data" / "processed" / "gwtune" / name
    outdir.mkdir(parents=True, exist_ok=True)
    timings = {}

    t0 = time.perf_counter()
    _, xs, _ = load_vectors(args.src, args.K)
    _, xt, _ = load_vectors(args.trg, args.K)
    c1 = distance_matrix(normalize_embeddings(xs))
    c2 = distance_matrix(normalize_embeddings(xt))
    timings["prep_s"] = time.perf_counter() - t0

    gw = GWTuneSolver(
        c1, c2, device="cpu", to_types=args.backend, data_type="double",
        max_iter=args.max_iter, numItermax=args.numitermax, tol=args.tol,
        sinkhorn_method=args.sinkhorn, sinkhorn_stopThr=args.sinkhorn_stopthr,
        warmstart=args.warmstart, sinkhorn_stopThr_first=args.first_stopthr)
    T0 = gw.init_mat_builder.make_initial_T("uniform")

    t0 = time.perf_counter()
    logv = gw.entropic_gw_computation(args.eps, T0)
    timings["gw_s"] = time.perf_counter() - t0

    G = logv["ot"]
    G = G.cpu().numpy() if hasattr(G, "cpu") else np.asarray(G)
    gw_dist = float(logv["gw_dist"])
    valid = np.isfinite(gw_dist) and np.isfinite(G).all() and G.sum() > 0.5
    print(f"{name}: GW {timings['gw_s']:.1f}s, {logv['cpt']} iters, gw_dist {gw_dist:.4g}, valid {valid}",
          flush=True)

    result = {"args": vars(args), "name": name, "timings": timings, "n_iter": int(logv["cpt"]),
              "gw_dist": gw_dist, "valid": bool(valid),
              **{k: logv[k] for k in ["err", "grad_s", "sinkhorn_s", "sinkhorn_niter"]}}
    if valid:
        np.save(outdir / "coupling.npy", G)
        if not args.no_eval:
            t0 = time.perf_counter()
            rows, info = evaluate_coupling(G, args.src, args.trg, args.K)
            timings["eval_s"] = time.perf_counter() - t0
            result.update(info)
            result["accuracy"] = rows
            for r in rows:
                print(f"  {r['candidates']:>14} {r['dict']:>9} {r['score']:>9}  "
                      f"n={r['n_queries']:5d}  P@1 {100 * r['P@1']:.2f}", flush=True)
    result["peak_rss_GB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2
    (outdir / "result.json").write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
