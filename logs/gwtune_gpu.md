# GWTune on GPU (server 69) — 2026-10-22

Goal: speed up the provisional standard GW run (EN→ES, K=20000, ε=2e-4 ≡ λ=1e-4, init p qᵀ, setting B =
warm start + Sinkhorn stopThr 3.16e-5; 53 min on the 64-thread CPU of server 58, `logs/gwtune_comparison.md`).

## Environment
- Server 69 (rx1000): 4× NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition (96 GB, sm_120), driver 580.95.05. One GPU used (`CUDA_VISIBLE_DEVICES=0`)
- torch 2.7.1+cu128 (CUDA 12.8), POT 0.9.4, numpy 1.26.4, Python 3.10.11. pyproject/poetry.lock for this are on the `gpu` branch only
- Runner: `code/experiments/run_gwtune.py ... --backend torch --device cuda --dtype {float,double}`; timers call `torch.cuda.synchronize()`
- Run logs (verbose ‖ΔΓ‖ every 10 iterations): `data/processed/gwtune/logs/gpu_*.log`

## Results (EN→ES, ε=2e-4, setting B, init p qᵀ)
P@1 order: coupling / proj / proj+CSLS. GPU rows: float32 + `sinkhorn_log`, `--max-iter 1000`.

| run | outer iters | GW solve | per iter (grad + Sinkhorn) | peak GPU mem | gw_dist | GW vocab dict 0-5000 | GW vocab full dict | 200k dict 0-5000: proj / CSLS | 200k dict 5000-6500: proj / CSLS |
|---|---|---|---|---|---|---|---|---|---|
| K=5000 GPU float, tol 1e-8 | 1000 (cap; ‖ΔΓ‖ ≈ 2.5e-5) | 17 s | 0.011 + 0.004 s | 1.0 GB | 0.005641 | 68.00 / 80.65 / 82.29 | 68.00 / 80.65 / 82.29 | 74.76 / 77.36 | 72.20 / 75.33 |
| K=5000 CPU double numpy 16 thr, tol 1e-8 | 501 | 875 s | ≈ 1.75 s | — | 0.00564 | 68.00 / 80.74 / 82.29 | — | — | — |
| K=20000 GPU float, tol 1e-5 | 1000 (cap; ‖ΔΓ‖ ≈ 7.2e-5) | 982 s (16 min) | 0.74 + 0.24 s | 13.8 GB | 0.005897 | 67.65 / 80.82 / 84.11 | 62.94 / 76.72 / 80.42 | 78.04 / 81.20 | 77.00 / 80.33 |
| **K=20000 GPU float, tol 1e-4, `--min-iter 10`** | **101** | **126 s (2.1 min)** | 0.72 + 0.52 s | 13.8 GB | 0.005893 | 67.61 / 81.25 / 84.48 | 62.84 / 76.83 / 80.40 | 78.46 / 81.32 | 76.73 / 80.07 |
| K=20000 CPU double numpy 64 thr, tol 1e-5 | 121 | 53 min | 19.5 + 4.4 s | (RAM 45 GB) | — | 67.69 / 80.97 / 84.19 | 62.93 / 76.70 / 80.31 | 78.04 / 81.04 | 76.73 / 80.20 |

Double precision on GPU, K=20000, `--max-iter 10 --no-eval` (3.3):

| run | per iter: grad | per iter: Sinkhorn (inner 10–90) | peak GPU mem |
|---|---|---|---|
| GPU double, `sinkhorn` | 21.1 s | 0.16–0.43 s | 29.8 GB |
| GPU double, `sinkhorn_log` | 21.1 s | 0.65–4.0 s | 27.1 GB |
| GPU float, `sinkhorn_log` (first 10 iters of the run above) | 0.71 s | 0.35–1.6 s | 13.8 GB |
| CPU double numpy 64 thr | 19.5 s | 4.4 s (mean) | — |

Other: prep (load + distance matrices, CPU) 87 s at K=20000; evaluation 96 s; peak RSS 25 GB (K=20000 float run).

## Findings
- **float32 + log-domain Sinkhorn gives the CPU accuracy**: all P@1 within ±0.3 pt of the CPU runs (noise: 1500 queries → 1 word = 0.07 pt), same gw_dist, no NaN / invalid plans
- **Per-iteration time at K=20000: 24 s → 0.98 s (≈ 24×).** The first 121 iterations (the CPU stopping point) take 2.4 min
- **But in float32 ‖ΔΓ‖ stops decreasing**: K=20000 plateaus at ≈ 7.2e-5 from ~iteration 100 (CPU double reached 1e-5 at 121); K=5000 at ≈ 2.5e-5 (Sinkhorn inner = 0 iterations from ~iteration 50). So tol 1e-5 / 1e-8 are never reached and the runs go to the 1000 cap (16 min at K=20000). Cause not checked; likely float32 rounding in the gradient amplified by 1/ε, which jitters Γ every iteration
- **Double precision on GPU does not help the gradient**: 21 s/iter, the same as the 64-thread CPU (Blackwell FP64 is slow), as expected. Only Sinkhorn gets faster
- **Stopping rule for float32: tol 1e-4 with `--min-iter 10`** stops at iteration 101 (‖ΔΓ‖ 7.7e-5): **GW solve 2.1 min vs 53 min on CPU (25×)**, P@1 within −0.13 / +0.42 pt of the CPU run (the CPU tol sweep varied by ±0.15 pt). The plateau value depends on K, so re-check tol when K or ε changes
  - `--min-iter` is needed because the check at iteration 0 (from p qᵀ) sees ‖ΔΓ‖ = 2.8e-5: plain tol 1e-4 stopped after 1 iteration (P@1 ≈ 0). With min_iter the first stop is the check at iteration min_iter (default 0 = old behaviour)
- Caveat: run names do not contain tol. The first tol 1e-4 run (no min-iter) overwrote `result.json` / `coupling.npy` of the 1000-iteration K=20000 float run; its numbers above come from the printed output (`data/processed/gwtune/logs/gpu_K20000_float_log.log`). Use `--tag` when only tol differs
