# GWTune vs otalign (Step 3) — 2026-10-14

Runner: `code/experiments/run_gwtune.py` (calls `MainGromovWasserstainComputation.entropic_gw_computation`
directly: one init, no optuna). Evaluation for both: `localgw.bli.evaluate_coupling`.
Shared preprocessing/mapping validated against otalign (`localgw.preprocess`, `localgw.mapping`:
distance stats identical, 1977 anchors, max|P − P_otalign| = 3e-8).

## Matching the settings
| item | otalign | GWTune | matched? |
|---|---|---|---|
| vocab / distances | top-K, centre+unit, cosine / mean | same matrices passed in | yes |
| p, q / init | uniform / p qᵀ | uniform / "uniform" = p qᵀ | yes |
| loss | (a−b)²/2 | (a−b)² (POT) | **ε = 2λ** to match |
| outer stop | ‖ΔΓ‖ < 1e-8 checked every 10 iters, maxiter | same rule (tol=1e-8 passed), max_iter | yes |
| Sinkhorn | own `sinkhorn_knopp`, numItermax 1000, stopThr 1e-9, **warm start** (u, v from previous iter) | `ot.bregman.sinkhorn`, 1000, 1e-9, **no warm start** | no (GWTune has no warm-start option) |

POT's own `ot.gromov.entropic_gromov_wasserstein` has `warmstart=True`; GWTune re-implements the loop without it.

## K=2000, EN→ES, ε=2e-4 (≡ λ=1e-4), numpy, 16 threads

| | otalign | GWTune |
|---|---|---|
| outer iterations | 1000 (hit maxiter, ‖ΔΓ‖ ≈ 1.9e-8) | 491 (‖ΔΓ‖ < 1e-8) |
| Sinkhorn inner iterations / outer iter | (warm start, not logged) | **975–999 = hits numItermax, "did not converge" warnings** |
| time per outer iter | 0.17–0.49 s (time_G) | 0.98 s (grad 0.12 + Sinkhorn 0.86) |
| GW solve | 245 s | 481 s |
| argmax(Γ) agreement with otalign | — | 72.3% |
| P@1 GW vocab, full dict: coupling / proj / proj+CSLS | 62.4 / 74.2 / 74.4 | 63.5 / 74.4 / 74.6 |
| P@1 200k, dict 5000-6500: proj / proj+CSLS | 60.3 / 66.9 | 61.5 / 66.9 |

(At K=2000 the GW-vocab queries are the same 1263 words for dict 0-5000 and full.)
→ Accuracy is equivalent (within ~1 pt) although the couplings differ in detail.

## Per-iteration time of other Sinkhorn variants (K=2000, ε=2e-4, 16 threads)

| backend / Sinkhorn | grad [s] | Sinkhorn [s] | inner iters |
|---|---|---|---|
| numpy / sinkhorn | 0.12 | 0.86 | ~1000 |
| torch / sinkhorn | 0.06 | 3.4 | ~1000 |
| numpy / sinkhorn_log | 0.11 | **112** | ~1000 |
| torch / sinkhorn_log | 0.06 | 8.2 | 20–980 (first 5 iters) |

## Extrapolation to K=20000 (Sinkhorn ∝ K² × inner iters, grad ≈ K^2.3–K³)
- numpy / sinkhorn, 150 outer iters: ~1.5–4 min per iter → **≈ 4–10 h** (otalign: 1.5 h)
- torch / sinkhorn_log: ~15 min per iter → **≈ 1.5 days** for 150 iters
- numpy / sinkhorn_log: infeasible

## Sinkhorn stopping rule and warm start (K=2000, EN→ES, ε=2e-4, numpy, 16 threads, max_iter 1000, tol 1e-8)

`localgw.gwtune_ext.GWTuneSolver` = GWTune's loop + `sinkhorn_stopThr`, `warmstart`, `sinkhorn_stopThr_first`
(defaults reproduce GWTune exactly; tested). otalign's inner rule ‖err‖₂² < 1e-9 ⇔ POT stopThr = 3.16e-5;
otalign solves the FIRST outer iteration with POT's cold Sinkhorn at 1e-9, later ones warm-started at 3.16e-5.

| run | 1st iter stopThr | later stopThr | warm | outer iters | s / outer iter (grad + Sinkhorn) | mean inner iters | GW solve | gw_dist | argmax agree w/ otalign | P@1 GW vocab full: coupling / proj / proj+CSLS | P@1 200k dict 5000-6500: proj / CSLS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| otalign | 1e-9 | 3.16e-5 | yes | 1000 | 0.17–0.49 (time_G) | — | 245 s | — | — | 62.4 / 74.2 / 74.4 | 60.3 / 66.9 |
| GWTune default | 1e-9 | 1e-9 | no | 491 | 0.98 (0.12 + 0.86) | 994 | 481 s | 0.00590 | 72% | 63.5 / 74.3 / 74.6 | 61.5 / 66.9 |
| A | 3.16e-5 | 3.16e-5 | no | 481 | 1.06 (0.12 + 0.94) | 985 | 511 s | 0.00591 | 75% | 64.0 / 74.5 / 74.3 | 61.4 / 67.1 |
| B | 3.16e-5 | 3.16e-5 | yes | 1000 | 0.19 (0.12 + 0.08) | 10 | 194 s | **0.00703** | 13% | **10.1 / 12.3 / 12.0** | 4.6 / 5.6 |
| **C (= otalign recipe)** | 1e-9 | 3.16e-5 | yes | 1000 | **0.21 (0.13 + 0.08)** | 36 | **210 s** | 0.00587 | 73% | 62.5 / 73.7 / 73.9 | 60.6 / 66.2 |
| D | 1e-9 | 1e-9 | yes | 221 | 1.09 (0.13 + 0.96) | 988 | 240 s | **0.00705** | 12% | **9.3 / 11.6 / 11.1** | 3.3 / 4.1 |

Findings:
- **Speed:** without warm start, Sinkhorn hits the 1000-iteration cap almost every outer iteration even with the
  loose threshold (A) → ~1 s / iter. Warm start + loose threshold (C) cuts the Sinkhorn part 12× (0.94 → 0.08 s)
  and the whole iteration 5× (→ 0.21 s, same as otalign). With the strict threshold, warm start does not help (D).
- **Robustness:** from the deterministic init p qᵀ, 2 of 5 variants (B, D) converge to a bad stationary point
  (P@1 ≈ 10%), while the others go through the usual plateau (~250–300 iters) and jump to the good solution.
  The outcome depends on fine details of the inexact Sinkhorn solves, not only on λ.
- **The GW objective identifies the bad runs** (gw_dist 0.0070 vs 0.0059), i.e. unsupervised selection by GW loss —
  which is what GWTune does over multiple random inits — would reject them.
- Outer iteration counts differ only through the inner solver (the outer rule is identical); all good runs are
  effectively converged after ~300–400 iterations.

## Stability w.r.t. the initial plan (K=2000, EN→ES, ε=2e-4, warm start) — 2026-10-15

`code/experiments/stability_k2000.sh` → `analysis/tables/gwtune_stability_k2000.csv`.
"good" = coupling P@1 > 40% (GW vocab, full dict). Times are not comparable to earlier runs
(16 jobs ran concurrently with 6 threads each).

| setting | init | good / runs | coupling P@1 of good runs | of bad runs |
|---|---|---|---|---|
| B (loose everywhere) | p qᵀ | 0 / 1 | — | 10.1 |
| B | p qᵀ + 1e-6 noise | 1 / 8 | 63.0 | 9.2–10.1 |
| C (otalign recipe) | p qᵀ | 1 / 1 | 62.5 | — |
| C | p qᵀ + 1e-6 noise | **1 / 8** | 62.5 | 9.3–11.4 |
| C | GWTune random plan | **0 / 8** | — | 0.3–15.8 |
| D (strict everywhere) | p qᵀ | 0 / 1 | — | 9.3 |
| D | p qᵀ + 1e-6 noise | 0 / 8 | — | 9.3 (all identical) |
| GWTune default, A | p qᵀ | 2 / 2 | 63.5, 64.0 | — |

- At K=2000, λ=1e-4 the good solution is reached only occasionally: a relative perturbation of 1e-6 of the
  init flips C (the otalign recipe) from good to bad in 7 of 8 seeds. The good otalign / C results from p qᵀ
  were largely luck. D washes the perturbation out and always lands on the same bad point.
- GWTune's random initial plans (far from p qᵀ) never found the good solution (0/8).
- **gw_dist separates good and bad runs perfectly**: good 0.00586–0.00591, bad 0.00692–0.00748.
  Selecting by GW loss (unsupervised) is therefore reliable — the problem is reaching the good basin, not recognizing it.
- Open: is this specific to small K? (otalign K=5000/10000/20000 from p qᵀ were all good, one run each.)

## Was otalign's loose Sinkhorn criterion the POT behaviour at the time? — checked 2026-10-15

POT `ot/bregman.py` (`sinkhorn_knopp`) at each release tag on GitHub:

| POT | release | marginal error checked against stopThr (default 1e-9) |
|---|---|---|
| 0.4.0 | 2017 | `np.linalg.norm((np.sum(transp, axis=0) - b))**2` — **squared** |
| 0.5.0 / 0.5.1 | Sep 2018 | `np.linalg.norm(tmp2 - b)**2` — **squared** |
| 0.6.0 | Jul 2019 | `np.linalg.norm(tmp2 - b)` — not squared (no release-note entry) |
| 0.7–0.9.4 | 2020– | `nx.norm(tmp2 - b)` — not squared |

- otalign's ported `sinkhorn_knopp` has exactly the POT 0.4.0 expression → copied from POT ≤ 0.5.
- The paper (arXiv Aug 2018, EMNLP 2018) predates POT 0.6, so with the POT of that time **both** the first
  (POT `bregman.sinkhorn`) and later (ported) Sinkhorn calls used the squared criterion, i.e. ≡ stopThr 3.16e-5
  everywhere = setting **B**. The strict first iteration (setting C) only appears with POT ≥ 0.6.
- otalign's last commit (Jun 2020) is after POT 0.6/0.7 and `setup.py` does not pin POT, so the mixed behaviour
  is what a user installing it since mid-2019 gets.
