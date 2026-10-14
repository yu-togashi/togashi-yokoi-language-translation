"""Bilingual lexicon induction (BLI) accuracy, MUSE-style.

Queries are dictionary source words; candidates are ALL target words given.
A query counts as correct at k if any gold translation is in its top-k.
Denominator = dictionary source words present in the source vocabulary
(MUSE convention; with 200k words this is every entry).
"""

from __future__ import annotations

import numpy as np
import torch


def _row_normalize(x: np.ndarray) -> torch.Tensor:
    t = torch.as_tensor(x, dtype=torch.float32)
    return t / t.norm(dim=1, keepdim=True).clamp_min(1e-12)


def _mean_topk_sim(a: torch.Tensor, b: torch.Tensor, knn: int, batch: int) -> torch.Tensor:
    """For each row of a: mean cosine similarity to its knn nearest rows of b."""
    out = torch.empty(a.shape[0])
    for i in range(0, a.shape[0], batch):
        out[i:i + batch] = (a[i:i + batch] @ b.T).topk(knn, dim=1).values.mean(dim=1)
    return out


def score_accuracy(
    scores: np.ndarray,
    src_words: list[str],
    trg_words: list[str],
    dictionary: dict[str, list[str]],
    ks: tuple[int, ...] = (1, 5, 10),
) -> dict:
    """P@k from a dense score matrix over the GW vocabulary (e.g. the coupling Γ).

    Only queries whose source word is a row of `scores` and that have at least one gold
    translation among the columns are counted (otherwise the query is unanswerable).
    """
    s_idx = {w: i for i, w in enumerate(src_words)}
    t_idx = {w: i for i, w in enumerate(trg_words)}
    queries = [(s_idx[w], {t_idx[g] for g in golds if g in t_idx})
               for w, golds in dictionary.items() if w in s_idx]
    queries = [(i, g) for i, g in queries if g]
    rows = np.array([i for i, _ in queries])
    top = torch.as_tensor(np.asarray(scores[rows]), dtype=torch.float32).topk(max(ks), dim=1).indices.numpy()
    hits = {k: sum(bool(g.intersection(t[:k])) for t, (_, g) in zip(top, queries)) for k in ks}
    n = len(queries)
    return {"n_queries": n, **{f"P@{k}": hits[k] / n for k in ks}}


def bli_accuracy(
    xs: np.ndarray,
    xt: np.ndarray,
    src_words: list[str],
    trg_words: list[str],
    dictionary: dict[str, list[str]],
    method: str = "nn",
    knn: int = 10,
    ks: tuple[int, ...] = (1, 5, 10),
    batch: int = 4096,
) -> dict:
    """P@k of retrieving gold translations for dictionary source words.

    xs, xt: source / target vectors in a shared space (target already mapped).
    method: "nn" (cosine) or "csls" (Conneau et al. 2018, with knn neighbours;
            target-side penalty uses all source words as in MUSE).
    """
    s, t = _row_normalize(xs), _row_normalize(xt)
    s_idx = {w: i for i, w in enumerate(src_words)}
    t_idx = {w: i for i, w in enumerate(trg_words)}
    queries = [(s_idx[w], {t_idx[g] for g in golds if g in t_idx})
               for w, golds in dictionary.items() if w in s_idx]

    q = s[[i for i, _ in queries]]
    if method == "csls":
        r_t = _mean_topk_sim(t, s, knn, batch)        # per target: mean sim to its knn sources
        r_s = _mean_topk_sim(q, t, knn, batch)        # per query: mean sim to its knn targets
    elif method != "nn":
        raise ValueError(f"unknown method {method!r}")

    kmax = max(ks)
    hits = {k: 0 for k in ks}
    for i in range(0, len(queries), batch):
        sim = q[i:i + batch] @ t.T
        if method == "csls":
            sim = 2 * sim - r_s[i:i + batch, None] - r_t[None, :]
        top = sim.topk(kmax, dim=1).indices.numpy()
        for row, (_, golds) in zip(top, queries[i:i + batch]):
            for k in ks:
                if golds.intersection(row[:k]):
                    hits[k] += 1
    n = len(queries)
    return {"n_queries": n, "coverage": n / len(dictionary),
            **{f"P@{k}": hits[k] / n for k in ks}}
