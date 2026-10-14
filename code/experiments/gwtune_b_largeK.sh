#!/usr/bin/env bash
# Setting B (warm start, Sinkhorn stopThr 3.16e-5 everywhere ≡ otalign with POT ≤ 0.5), init p qᵀ,
# eps=2e-4 (≡ λ=1e-4), outer rule as otalign (tol 1e-8, max 1000 iterations).
# K=5000 and K=10000 in parallel, then K=20000 alone (64 threads, as the otalign K=20000 run).
# Logs: data/processed/gwtune/logs/B_K<K>.log
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p data/processed/gwtune/logs
run() {  # K threads
  poetry run python code/experiments/run_gwtune.py en es "$1" 2e-4 --max-iter 1000 --tol 1e-8 \
    --sinkhorn-stopthr 3.16e-5 --warmstart --threads "$2" --verbose \
    > "data/processed/gwtune/logs/B_K$1.log" 2>&1
  echo "done K=$1 $(date '+%F %T')"
}
run 5000 16 &
run 10000 32 &
wait
run 20000 64
