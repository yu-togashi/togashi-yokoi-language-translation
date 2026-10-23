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

## ε = 2e-1: no threshold and q = 5 / 25 / 50 / 75 % (v = 10)

P@1: coupling / proj / proj+CSLS (200k: proj / CSLS). One GPU per run, run in parallel.

| threshold | τ (EN / ES) | outer iters | GW solve | gw_dist | GW vocab dict 0-5000 | GW vocab full dict | 200k dict 0-5000 | 200k dict 5000-6500 |
|---|---|---|---|---|---|---|---|---|
| none | — | 11 | 10 s | 0.01382 | 0.00 / 0.02 / 0.00 | 0.00 / 0.01 / 0.00 | 0.02 / 0.00 | 0.00 / 0.00 |
| q 5 % | 0.850 / 0.847 | 31 | 37 s | 5.615 | 0.39 / 0.51 / 0.60 | 0.29 / 0.35 / 0.41 | 0.44 / 0.42 | 0.40 / 0.53 |
| **q 25 %** | 0.961 / 0.959 | 21 | 44 s | 18.34 | 69.78 / 82.65 / 85.65 | 64.87 / 79.05 / 82.66 | 79.70 / 82.58 | **79.13 / 81.47** |
| **q 50 %** | 1.012 / 1.012 | 61 | 100 s | 26.36 | 70.24 / 82.55 / 85.69 | 64.90 / 78.61 / 82.31 | 79.46 / 82.64 | **79.27 / 81.33** |
| q 75 % | 1.054 / 1.056 | 91 | 97 s | 23 | 0.08 / 0.06 / 0.02 | 0.05 / 0.05 / 0.02 | 0.02 / 0.08 | 0.07 / 0.00 |
| (no threshold, ε 2e-4, for reference) | — | 101 | 126 s | 0.005893 | 67.61 / 81.25 / 84.48 | 62.84 / 76.83 / 80.40 | 78.46 / 81.32 | 76.73 / 80.07 |

- **No threshold at ε = 2e-1 fails trivially**: Γ stays at p qᵀ (‖ΔΓ‖ 2.5e-8 at iteration 0, gw_dist = the p qᵀ value).
  ε = 2e-1 is far too large for the unthresholded cost, so the same-ε comparison does not isolate the threshold either.
  The fair comparison is each cost at its own (unsupervised) best ε, i.e. an ε sweep for each
- q 25 % and 50 % succeed and agree with each other (±0.4 pt); both beat the no-threshold ε 2e-4 run by 1–2.5 pt
- q 5 % and 75 % fail (P@1 < 1 %, valid plans, converged). Not checked whether ε = 2e-1 is simply wrong for them
  (the share of cut pairs, hence the gradient scale, changes with q) or the threshold itself destroys the signal
- gw_dist is not comparable across thresholds (different cost matrices)

## ε sweep per setting (2026-10-23)

K=20000, v = 10, GPU standard setting; 4 GPUs in parallel, each run capped at 20 min (`timeout`).
Runner: `data/processed/gwtune/logs/sweep_eps_threshold.sh`, logs `data/processed/gwtune/logs/sweep_K20000_*.log`.
Rule (CLAUDE.md): choose ε without the dictionary, by the lowest gw_dist among converged runs **within one setting**
(gw_dist is not comparable across settings). P@1 for reference: GW vocab full dict (coupling / proj / proj+CSLS),
200k dict 5000-6500 (proj / CSLS).

**No threshold**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| 5e-5 | not converged (20 min cap at iteration ~950, ‖ΔΓ‖ 1.3e-4) | | | | |
| 1e-4 | 1000 (cap; ‖ΔΓ‖ plateau 1.1e-4, just above tol 1e-4) | 1002 s | **0.005797** | 61.98 / 76.59 / 80.26 | 76.47 / 79.60 |
| **2e-4** | 101 | 126 s | 0.005893 | 62.84 / 76.83 / 80.40 | 76.73 / 80.07 |
| 5e-4 | 21 | 24 s | 0.008227 | 2.53 / 7.58 / 9.99 | 5.27 / 7.33 |
| 1e-3 | 11 | 12 s | 0.009979 | 0.22 / 0.30 / 0.44 | 0.07 / 0.20 |
| 2e-3 | 11 | 12 s | 0.01200 | 0.10 / 0.03 / 0.04 | 0.00 / 0.07 |
| 5e-3 | 11 | 10 s | 0.01380 | 0.02 / 0.02 / 0.02 | 0.00 / 0.00 |
| 2e-1 | 11 | 10 s | 0.01382 (= p qᵀ) | 0.00 / 0.01 / 0.00 | 0.00 / 0.00 |

**q 25 % (τ ≈ 0.96)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| 5e-2 | not converged (20 min cap at iteration ~830, ‖ΔΓ‖ 6.8e-4) | | | | |
| **1e-1** | 21 | 66 s | **18.279** | 64.15 / 78.92 / 82.46 | 78.67 / 81.73 |
| 2e-1 | 21 | 44 s | 18.338 | 64.87 / 79.05 / 82.66 | 79.13 / 81.47 |
| 5e-1 | 21 | 30 s | 18.762 | 65.96 / 79.14 / 82.58 | 78.73 / 81.73 |
| 1 | 11 | 13 s | 23.438 | 1.24 / 4.37 / 6.18 | 2.53 / 2.73 |

**q 50 % (τ ≈ 1.01)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| 2e-2 | not converged (stopped at iteration 60, ‖ΔΓ‖ 5.3e-3) | | | | |
| 5e-2 | not converged (20 min cap at iteration ~430, ‖ΔΓ‖ 1.7e-3) | | | | |
| **1e-1** | 71 | 167 s | **26.321** | 64.46 / 78.69 / 82.25 | 78.87 / 80.93 |
| 2e-1 | 61 | 100 s | 26.363 | 64.90 / 78.61 / 82.31 | 79.27 / 81.33 |
| 5e-1 | 91 | 93 s | 28.53 | 27.04 / 64.86 / 70.59 | 60.20 / 65.33 |
| 1 | 11 | 13 s | 31.59 | 0.17 / 0.21 / 0.23 | 0.07 / 0.07 |

**Each setting at its selected ε**

| setting | ε | GW vocab full dict proj+CSLS | 200k dict 5000-6500 proj / CSLS |
|---|---|---|---|
| no threshold | 2e-4 (1e-4 if the run that hit the iteration cap counts) | 80.40 (80.26) | 76.73 / 80.07 (76.47 / 79.60) |
| q 25 % | 1e-1 | 82.46 | 78.67 / 81.73 |
| q 50 % | 1e-1 | 82.25 | 78.87 / 80.93 |

- **The threshold helps by about 1–2 pt at each setting's own ε**: q 25 % +2.1 (full dict CSLS) / +1.7 (MUSE standard CSLS),
  q 50 % +1.9 / +0.9 (vs no threshold at ε 2e-4). Single runs, no repeats (1500 queries: 1 word = 0.07 pt)
- q 25 % is flat over ε = 1e-1 … 5e-1 (82.5 ± 0.1 full dict CSLS); q 50 % degrades already at 5e-1
- Each setting works only in a narrow ε window: no threshold 1e-4 … 2e-4 (≥ 5e-4 collapses towards p qᵀ, ≤ 5e-5 does
  not converge in float32 within 20 min); thresholded 1e-1 … 2e-1 (5e-1 for q 25 %)
- Within a setting, gw_dist grows with ε, so "lowest gw_dist" picks the smallest ε that converges

## ε sweep for q 5 % and 75 % (2026-10-23)

Same setting and runner as above. q is the share of pairs kept: distances **above** the q-quantile become 10,
so q 5 % keeps only the closest 5 % of pairs and q 75 % cuts only the farthest 25 %.

**q 5 % (τ ≈ 0.85)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| 2e-2 | not converged (20 min cap at iteration ~410, ‖ΔΓ‖ 3.3e-3) | | | | |
| 5e-2 | 111 | 139 s | 5.233 | 0.13 / 0.08 / 0.09 | 0.07 / 0.00 |
| 1e-1 | 41 | 53 s | 5.336 | 0.34 / 0.24 / 0.30 | 0.00 / 0.00 |
| 2e-1 | 31 | 37 s | 5.615 | 0.29 / 0.35 / 0.41 | 0.40 / 0.53 |
| 5e-1 | 11 | 14 s | 6.901 | 0.02 / 0.00 / 0.02 | 0.00 / 0.00 |
| 1 | 11 | 11 s | 7.636 | 0.06 / 0.02 / 0.03 | 0.00 / 0.00 |
| 2 | 11 | 10 s | 8.083 | 0.02 / 0.03 / 0.02 | 0.00 / 0.00 |

**q 75 % (τ ≈ 1.055)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| 2e-2 | not converged (20 min cap at iteration ~160, ‖ΔΓ‖ 7.0e-3) | | | | |
| 5e-2 | not converged (20 min cap at iteration ~320, ‖ΔΓ‖ 6.0e-3) | | | | |
| 1e-1 | not converged (20 min cap at iteration ~650, ‖ΔΓ‖ 3.5e-3) | | | | |
| 2e-1 | 91 | 97 s | 23.00 | 0.05 / 0.05 / 0.02 | 0.07 / 0.00 |
| 5e-1 | 21 | 23 s | 24.20 | 0.06 / 0.07 / 0.08 | 0.07 / 0.13 |
| 1 | 11 | 12 s | 26.18 | 0.02 / 0.02 / 0.03 | 0.00 / 0.00 |
| 2 | 11 | 12 s | 28.13 | 0.01 / 0.02 / 0.02 | 0.00 / 0.00 |

- **q 5 % and q 75 % fail at every ε tried** (2e-2 … 2): converged runs give P@1 < 1 %, smaller ε does not converge in 20 min.
  So with v = 10 only q 25–50 % works in this ε range
- Not checked: whether this is a bad stationary point reached from p qᵀ (GW is non-convex) or the thresholded
  structure itself not matching across languages

## ε sweep for q 10 % and 15 %, and q 75 % at ε 2e-4 (2026-10-23)

**q 10 % (τ ≈ 0.90)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| **5e-2** | 81 | 171 s | **8.678** | 50.05 / 71.45 / 75.89 | 67.73 / 71.00 |
| 1e-1 | 41 | 78 s | 8.721 | 50.48 / 71.94 / 76.40 | 67.87 / 72.20 |
| 2e-1 | 31 | 49 s | 8.766 | 52.92 / 75.09 / 78.72 | 72.13 / 74.93 |
| 5e-1 | 31 | 33 s | 9.682 | 49.35 / 73.52 / 77.82 | 72.27 / 74.60 |
| 1 | 11 | 12 s | 12.89 | 0.09 / 0.06 / 0.11 | 0.00 / 0.07 |

**q 15 % (τ ≈ 0.925)**

| ε | outer iters | GW solve | gw_dist | GW vocab full dict | 200k dict 5000-6500 |
|---|---|---|---|---|---|
| **5e-2** | 51 | 186 s | **12.108** | 61.99 / 78.51 / 82.26 | 78.53 / 81.53 |
| 1e-1 | 51 | 116 s | 12.132 | 62.62 / 78.77 / 82.31 | 78.60 / 81.53 |
| 2e-1 | 51 | 79 s | 12.213 | 63.57 / 78.69 / 82.34 | 78.60 / 81.00 |
| 5e-1 | 21 | 28 s | 12.86 | 60.83 / 78.68 / 82.27 | 78.67 / 80.87 |
| 1 | 11 | 13 s | 16.61 | 1.76 / 7.06 / 10.97 | 4.20 / 6.73 |

**q 75 %, ε 2e-4**: not converged — Sinkhorn at its 1000 cap every iteration, only 50 outer iterations in the 20 min
cap (‖ΔΓ‖ 6.9e-3), like q 50 % at 2e-4.

## Summary: each q at its selected ε (lowest gw_dist among converged runs)

| kept share q | selected ε | GW vocab full dict proj+CSLS | 200k dict 5000-6500 proj / CSLS |
|---|---|---|---|
| no threshold | 2e-4 | 80.40 | 76.73 / 80.07 |
| 5 % | — (all fail) | < 1 | < 1 |
| 10 % | 5e-2 | 75.89 | 67.73 / 71.00 |
| **15 %** | 5e-2 | **82.26** | 78.53 / **81.53** |
| **25 %** | 1e-1 | **82.46** | 78.67 / **81.73** |
| 50 % | 1e-1 | 82.25 | 78.87 / 80.93 |
| 75 % | — (all fail) | < 1 | < 1 |

- q 15–50 % all beat no threshold by about 2 pt (full dict CSLS 82.3–82.5 vs 80.4) and are flat across ε where they converge
- Sharp edges on both sides: q 10 % is already 5–10 pt below no threshold (75.9 / 71.0), q 5 % and q 75 % fail entirely
