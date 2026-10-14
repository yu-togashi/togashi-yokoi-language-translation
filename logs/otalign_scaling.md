# otalign runtime / memory scaling and K=20000 estimate — 2026-10-14

EN→ES, λ=1e-4, mean distance normalization, uniform p/q, CPU only (OpenBLAS via numpy 1.26).
Raw numbers: `analysis/tables/otalign_runs.md` (from `code/experiments/summarize_otalign_runs.py`).

## Measured

| K | threads | iters run | time_G iters 0–99 [s] | time_G steady [s] | GW solve [min] | wall [min] | peak RSS [GB] | P@1 coupling | P@1 proj+CSLS |
|---|---|---|---|---|---|---|---|---|---|
| 2000 | 16 | 1000 | 0.71 | 0.17 | 4.1 | 5.6 | 3.3 | 62.4 | 74.4 |
| 5000 | 16 | 200 | 3.48 | 1.5 | 7.1 | 8.9 | 3.5 | 68.0 | 82.3 |
| 10000 | 16 | 100 | 13.5 | 7.2 | 17.8 | 21.7 | 11.7 | 68.8 | 84.7 |
| 10000 | 64 | 100 | 11.8 | 5.3 | 14.9 | 18.7 | 11.7 | 68.8 | 84.7 |

(P@1 = train fold, dictionary pairs inside top-K, so the denominator changes with K.)

- time_G = gradient + warm-started Sinkhorn per GW iteration; it drops over iterations (warm start), so early iterations are 2–4× slower.
- Every 10th iteration additionally computes loss + accuracy (time_total − time_G ≈ 8 s at K=10000).
- Effective scaling of steady time_G: ×8.6 for 2000→5000, ×4.8 for 5000→10000 → **≈ K^2.3** (not K³).
  16→64 threads gives only ×1.35 at K=10000, and a 4000×4000 matmul is no faster with 64 than 16 threads →
  cost is dominated by the Sinkhorn inner loop (element-wise exp / K² mat-vec, memory-bound), not by C_s Γ C_tᵀ.
- Convergence (P@1 and obj stable): K=2000 ≈ 300 iters (plateau, then jump at ~250), K=5000 ≈ 30–60, K=10000 ≈ 60.
  Note: otalign stops only when ‖ΔΓ‖ < tol (1e-8) or maxiter (default 1000); at K≥5000 ΔΓ stays ~1e-6–1e-7,
  so `--maxiter` must be set explicitly or it runs all 1000 iterations.
- Memory: ~3.2 GB baseline (200k-word vectors for the out-of-sample step) + K-dependent part (~8.4 GB at K=10000, ∝ K²).
- λ=5e-5 and 1e-5 fail numerically at K=2000 (see `logs/otalign_fixes.md`).

## Estimate for K=20000 (EN→ES, λ=1e-4, 64 threads)

| item | estimate |
|---|---|
| time_G iters 0–99 | 11.8 × 2^2.3 ≈ 58 s (pessimistic K³: 94 s) |
| time_G steady | 5.3 × 2^2.3 ≈ 26 s (K³: 42 s) |
| eval overhead | ≈ 32 s every 10 iters ≈ +3 s/iter |
| fixed cost (load, distances, final eval, 200k export) | ≈ 10–15 min |
| **total, maxiter=100** | **≈ 1.9 h** (K³: ≈ 3 h) |
| **total, maxiter=150** | **≈ 2.3 h** (K³: ≈ 3.7 h) |
| peak memory | ≈ 3.2 + 4 × 8.4 ≈ 37 GB (machine: 1 TB) |

Paper reports 37–70 min per pair on a quad-core CPU for K=20000; our estimate is 2–3× slower.
Possible reasons: fewer iterations in the paper, faster BLAS/exp (MKL), or different stopping.

## K=20000 actual run (EN→ES, λ=1e-4, 64 threads, maxiter=150) — 2026-10-14

| item | estimate | actual |
|---|---|---|
| time_G iters 0–99 | 58 s | 47 s |
| time_G steady | 26 s | 24.5 s |
| GW solve | — | 84 min (150 iters) |
| wall total | 2.3 h | **1 h 33 min** |
| peak memory | 37 GB | **45 GB** |

- Dynamics: plateau (P@1 9→42%) until ~60 iters, jump at ~80, P@1 stable from ~100 iters (ΔΓ ~3e-6 at 140).
- P@1 (train fold, pairs inside top-20000; coverage 97.3%):
  coupling 67.58, coupling+CSLS 67.58, bary 67.21, bary+CSLS 67.17, **proj 80.92, proj+CSLS 84.09**.
- Paper Table 1 G-W EN→ES: 78.3 (λ=1e-4), 81.7 (λ=1e-5). None of the six matches exactly:
  Γ argmax is ~11 pt lower; orthogonal projection is +2.6 pt (NN) / +5.8 pt (CSLS) higher.
- Γ-based P@1 did not improve from K=10000 (68.8) to K=20000 (67.6); projection-based stayed ~84%.
