# local-GW, first step: threshold the distance matrices (Step 5) — 2026-10-23

Plan: `tasks/todo.md` Step 5. After mean normalization (mean 1, as for all GW runs), for each language take
τ = the q-quantile of the off-diagonal distances and replace every d > τ by a large finite value v
(`localgw.preprocess.threshold_distances`, `run_gwtune.py --threshold-quantile q --threshold-value v`).
Which pairs are cut does not depend on the normalization; the order matters only for the scale of v.

Setting: EN→ES, K=20000, init p qᵀ, GPU standard setting (float32 + `sinkhorn_log`, warm start, Sinkhorn
stopThr 3.16e-5, outer tol 1e-4 + `--min-iter 10`), one RTX PRO 6000 per run. Logs:
`data/processed/gwtune/logs/gpu_K20000_thrq0.5v10*.log`.

## q = 50 % (τ = 1.012 in both languages), v = 10: which ε converges

| ε | Sinkhorn inner iterations | ‖ΔΓ‖ | outcome |
|---|---|---|---|
| 2e-4 (the no-threshold setting) | 1000 (cap) every iteration | ≈ 6e-3, flat | stopped at iteration 20 (18 s / iteration) |
| 2e-3 | 1000 (cap) | ≈ 5.9e-3 at iteration 10 | stopped at iteration 10 |
| 2e-2 | 350–370 | ≈ 5.1–5.3e-3 from iteration 10 to 60, flat | stopped at iteration 60 (7 s / iteration; 1000 iterations would take ~2 h) |
| **2e-1** | 10–100 | 7e-5 → 1e-3 → **3.1e-5 at iteration 60** | **converged: 61 iterations, GW 100 s** (0.70 + 0.90 s / iteration), GPU 13.8 GB |

Why: with v = 10 the square loss of a cut pair against a kept pair is ≈ (10 − 1)² ≈ 81, against ≈ 0.01 between
kept distances, so the gradient spans a much wider range and ε = 2e-4 is effectively a tiny regularization.

## Accuracy (P@1; coupling / proj / proj+CSLS)

| run | GW vocab dict 0-5000 | GW vocab full dict | 200k dict 0-5000: proj / CSLS | 200k dict 5000-6500: proj / CSLS |
|---|---|---|---|---|
| threshold q 50 %, v 10, ε 2e-1 | 70.24 / 82.55 / 85.69 | 64.90 / 78.61 / 82.31 | 79.46 / 82.64 | 79.27 / 81.33 |
| no threshold, ε 2e-4 (GPU standard, `logs/gwtune_gpu.md`) | 67.61 / 81.25 / 84.48 | 62.84 / 76.83 / 80.40 | 78.46 / 81.32 | 76.73 / 80.07 |

- The threshold run is 1–2.5 pt higher everywhere (full dict: coupling +2.1, proj+CSLS +1.9; MUSE standard
  200k / dict 5000-6500: proj +2.5, CSLS +1.3)
- **Caveat: ε differs (2e-1 vs 2e-4), so this does not separate the effect of the threshold from that of ε.**
  The no-threshold run at ε = 2e-1 is needed for that
- gw_dist (26.36) is not comparable to the no-threshold value: the cost matrices differ
