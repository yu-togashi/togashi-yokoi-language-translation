# otalign fixes

Upstream: https://github.com/dmelis/otalign @ 37e48f82 (2020-06-16). Our changes live in
`external/otalign.patch`; `external/setup_otalign.sh` re-creates the patched checkout.
Run via `code/experiments/run_otalign.sh`.

| # | File | Problem | Fix |
|---|---|---|---|
| 1 | `src/bilind.py` `compute_scores` | `score_type='barycentric'` crashes with POT 0.9.4: `EMDTransport.inverse_transform` needs `self.nx` (backend), which is only set by `fit()` | set `ot_emd.nx = ot.backend.get_backend(xs, xt)` before `inverse_transform` |
| 2 | `scripts/main_gw_bli.py` `load_vectors` | evaluation dictionary fold hard-coded to `'train'` (`.0-5000`) | new `--dict_fold {train,test}`, default `train` (= original behaviour) |

## Not fixed (out of scope / not needed yet)
- Dinu task path uses undefined `args.home_dir` (Dinu data not used)
- `--no_entropy` is stored but `solve()` always runs Sinkhorn
- GPU path (cudamat → cupy migration in POT; CPU only here)

## Observed behaviour
- Everything else runs unmodified with Python 3.10 / numpy 1.26 / POT 0.9.4.
- Small λ breaks the plain (non-log-domain) Sinkhorn: at K=2000, λ=5e-5 gives log(0) warnings and stalls at 4.5% P@1;
  λ=1e-5 underflows at iteration 0 (objective 0). λ=1e-4 works. Consistent with the paper's
  "if λ=5e-5 leads to floating point errors, use 1e-4".
- The printed "Results on test dictionary" use whatever `--dict_fold` is (train by default).
