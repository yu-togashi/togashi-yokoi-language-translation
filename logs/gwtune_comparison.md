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
