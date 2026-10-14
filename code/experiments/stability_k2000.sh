#!/usr/bin/env bash
# Stability of GWTune entropic GW (K=2000, EN-ES, eps=2e-4 ≡ otalign λ=1e-4) w.r.t. the initial plan.
# Settings (see logs/gwtune_comparison.md):
#   B: stopThr 3.16e-5 everywhere, warm start      (fell into a bad solution from p qᵀ)
#   C: 1st iter 1e-9, later 3.16e-5, warm start    (= otalign recipe, good from p qᵀ)
#   D: stopThr 1e-9 everywhere, warm start         (bad from p qᵀ)
# Inits: p qᵀ with relative noise 1e-6 (seeds 1-8) for B, C, D; GWTune random plan (seeds 1-8) for C.
set -euo pipefail
cd "$(dirname "$0")/../.."
common="en es 2000 2e-4 --max-iter 1000 --threads 6 --warmstart --eval-gwvocab-only"
{
  for s in 1 2 3 4 5 6 7 8; do
    echo "$common --sinkhorn-stopthr 3.16e-5 --init perturbed --seed $s"
    echo "$common --sinkhorn-stopthr 3.16e-5 --first-stopthr 1e-9 --init perturbed --seed $s"
    echo "$common --sinkhorn-stopthr 1e-9 --init perturbed --seed $s"
    echo "$common --sinkhorn-stopthr 3.16e-5 --first-stopthr 1e-9 --init random --seed $s"
  done
} | xargs -P 16 -I{} sh -c 'poetry run python code/experiments/run_gwtune.py {} 2>&1 | grep -v -i warn | head -1'
