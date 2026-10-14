#!/usr/bin/env bash
# Run the (patched) official otalign GW-BLI script on the Conneau/MUSE task.
# Usage: code/experiments/run_otalign.sh <src> <trg> <K> <entreg> [extra otalign args...]
# Env:   THREADS (BLAS threads, default 16)
# Outputs: data/processed/otalign/<src>-<trg>_K<K>_ereg<entreg>[_<TAG>]/{run.log,time.log,out/...}
#   run.log  : otalign stdout (per-iteration obj / Acc / time_G, final six P@1 values)
#   time.log : GNU time -v (wall clock, peak RSS)
set -euo pipefail

src=$1; trg=$2; K=$3; ereg=$4; shift 4
root="$(cd "$(dirname "$0")/../.." && pwd)"
threads=${THREADS:-16}
name="${src}-${trg}_K${K}_ereg${ereg}${TAG:+_$TAG}"
outdir="$root/data/processed/otalign/$name"
mkdir -p "$outdir"

cd "$root/external/otalign"
env PYTHONPATH=. MPLBACKEND=Agg \
  OMP_NUM_THREADS=$threads OPENBLAS_NUM_THREADS=$threads MKL_NUM_THREADS=$threads \
  /usr/bin/time -v -o "$outdir/time.log" \
  "$root/.venv/bin/python" -u scripts/main_gw_bli.py \
    --task conneau --src_lang "$src" --trg_lang "$trg" \
    --maxs "$K" --maxt "$K" --entreg "$ereg" \
    --data_dir "$root/data/raw" \
    --results_path "$outdir/out" --chkpt_path "$outdir/chkpt" \
    --plot_freq 100000 --print_freq 10 \
    "$@" > "$outdir/run.log" 2>&1
echo "done: $name"
