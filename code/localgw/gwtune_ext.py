"""GWTune's entropic GW loop with a configurable Sinkhorn stopping threshold and warm start.

GWTune (`MainGromovWasserstainComputation.entropic_gw_computation`) calls
`ot.bregman.sinkhorn` with POT's default stopThr=1e-9 (on ‖marginal error‖₂) and restarts
Sinkhorn from u = v = 1 at every outer GW iteration. This subclass keeps the same loop and
adds two options (defaults reproduce GWTune exactly):

  sinkhorn_stopThr : stopping threshold passed to Sinkhorn (otalign's criterion
                     ‖err‖₂² < 1e-9 corresponds to stopThr = sqrt(1e-9) ≈ 3.16e-5)
  warmstart        : start each Sinkhorn from the previous outer iteration's scalings
  sinkhorn_stopThr_first : stopThr for the first outer iteration only (otalign solves the
                     first, cold-started Sinkhorn with POT's 1e-9 and only later ones loosely)
  min_iter         : ignore tol at the ‖ΔΓ‖ checks before iteration min_iter (checks are every 10
                     iterations; the one at iteration 0 sees a tiny ‖ΔΓ‖ when starting from p qᵀ)
  snapshot_tols    : when ‖ΔΓ‖ first drops below each of these values, keep a copy of Γ in
                     log["snapshots"] (lets one run show what larger outer tolerances would give)

It also records per-iteration timings and Sinkhorn inner-iteration counts in the returned log.
On CUDA the timers call torch.cuda.synchronize() first (kernels run asynchronously).
"""

from __future__ import annotations

import sys
import time
import warnings
from typing import Any, Dict

import ot

from localgw.data import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
from GWTune.src.gw_alignment import MainGromovWasserstainComputation  # noqa: E402


class GWTuneSolver(MainGromovWasserstainComputation):
    def __init__(self, *args, sinkhorn_stopThr: float = 1e-9, warmstart: bool = False,
                 sinkhorn_stopThr_first: float | None = None, min_iter: int = 0,
                 snapshot_tols: tuple[float, ...] = (), **kwargs):
        super().__init__(*args, **kwargs)
        self.snapshot_tols = sorted(snapshot_tols, reverse=True)
        self.sinkhorn_stopThr = sinkhorn_stopThr
        self.sinkhorn_stopThr_first = sinkhorn_stopThr_first
        self.warmstart = warmstart
        self.min_iter = min_iter
        if self.back_end.to_types == "torch" and self.back_end.device.startswith("cuda"):
            import torch

            self._sync = torch.cuda.synchronize
        else:
            self._sync = lambda: None

    def _now(self) -> float:
        self._sync()
        return time.perf_counter()

    def entropic_gw_computation(self, eps: float, T: Any) -> Dict[str, Any]:
        C1, C2, p, q, T = self.back_end(self.source_dist, self.target_dist, self.p, self.q, T)
        nx = self.back_end.nx  # set by the Backend call above
        constC, hC1, hC2 = ot.gromov.init_matrix(C1, C2, p, q, loss_fun="square_loss")

        cpt, err = 0, 1
        t_start = self._now()
        logv = {"err": [], "grad_s": [], "sinkhorn_s": [], "sinkhorn_niter": [], "snapshots": []}
        pending = list(self.snapshot_tols)
        warm = None
        while (err > self.tol or cpt <= self.min_iter) and cpt < self.max_iter:
            Tprev = T
            t0 = self._now()
            tens = ot.gromov.gwggrad(constC, hC1, hC2, T)
            t1 = self._now()
            stop_thr = self.sinkhorn_stopThr
            if cpt == 0 and self.sinkhorn_stopThr_first is not None:
                stop_thr = self.sinkhorn_stopThr_first
            T, slog = ot.bregman.sinkhorn(p, q, tens, eps, method=self.sinkhorn_method,
                                          numItermax=self.numItermax, stopThr=stop_thr,
                                          warmstart=warm, log=True)
            t2 = self._now()
            if self.warmstart:
                warm = (slog["log_u"], slog["log_v"]) if "log_u" in slog else \
                    (nx.log(slog["u"]), nx.log(slog["v"]))
            logv["grad_s"].append(t1 - t0)
            logv["sinkhorn_s"].append(t2 - t1)
            logv["sinkhorn_niter"].append(int(slog.get("niter", -1)))

            if cpt % 10 == 0:
                err = nx.norm(T - Tprev)
                logv["err"].append(float(err))
                while pending and err < pending[0]:
                    logv["snapshots"].append({"tol": pending.pop(0), "n_iter": cpt + 1, "err": float(err),
                                              "gw_s": self._now() - t_start,
                                              "ot": nx.to_numpy(T).copy()})
                if self.verbose:
                    print(f"iter {cpt:5d}  |dG| {float(err):.3e}  inner {logv['sinkhorn_niter'][-1]:4d}  "
                          f"elapsed {self._now() - t_start:8.1f}s", flush=True)
            cpt += 1

        # same post-processing as GWTune
        logv["gw_dist"] = ot.gromov.gwloss(constC, hC1, hC2, T)
        logv["ot"] = T
        logv["cpt"] = cpt
        if abs(nx.sum(T) - 1) > 1e-5:
            warnings.warn("Solver failed to produce a transport plan (checked by original POT). ")
            logv["gw_dist"], logv["acc"] = float("nan"), float("nan")
            return logv
        if self.back_end.check_zeros(logv["ot"]):
            logv["gw_dist"], logv["acc"] = float("nan"), float("nan")
            return logv
        pred = nx.argmax(logv["ot"], 1)
        logv["acc"] = (pred == nx.arange(len(logv["ot"]), type_as=logv["ot"])).sum() / len(logv["ot"])
        return logv
