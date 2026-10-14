"""Embedding normalization and intra-language distance matrices (as in otalign)."""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist


def normalize_embeddings(x: np.ndarray, k: int | None = None) -> np.ndarray:
    """otalign's normalize_vecs='both': mean-centre, then unit length.

    otalign centres the GW vocabulary (first k rows) and the remaining rows
    separately; pass k to reproduce that for the 200k out-of-sample step.
    """
    x = np.asarray(x, dtype=np.float64).copy()
    blocks = [slice(0, len(x))] if k is None or k >= len(x) else [slice(0, k), slice(k, None)]
    for b in blocks:
        x[b] -= x[b].mean(axis=0)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def distance_matrix(x: np.ndarray, metric: str = "cosine", normalize: str = "mean") -> np.ndarray:
    """Intra-language distance matrix, normalized as otalign's normalize_dists."""
    c = cdist(x, x, metric=metric)
    if normalize == "mean":
        c /= c.mean()
    elif normalize == "max":
        c /= c.max()
    elif normalize == "median":
        c /= np.median(c)
    elif normalize != "none":
        raise ValueError(f"unknown normalize {normalize!r}")
    return c
