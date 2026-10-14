"""Orthogonal map from a GW coupling (otalign's get_mapping with mutual-NN anchors)."""

from __future__ import annotations

import numpy as np


def mutual_nn_pairs(scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Index pairs (i, j) that are each other's argmax in the score matrix."""
    best_t = np.asarray(scores.argmax(axis=1))
    best_s = np.asarray(scores.argmax(axis=0))
    i = np.flatnonzero(best_s[best_t] == np.arange(len(best_t)))
    return i, best_t[i]


def orth_procrustes(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """P minimizing ||X - Y Pᵀ||_F over orthogonal P (otalign convention: map target with Y @ P.T)."""
    u, _, vh = np.linalg.svd(x.T @ y)
    return u @ vh


def projection_from_coupling(coupling: np.ndarray, xs: np.ndarray, xt: np.ndarray) -> tuple[np.ndarray, int]:
    """Orthogonal map P from mutual nearest neighbours of the coupling. Returns (P, n_anchors)."""
    i, j = mutual_nn_pairs(coupling)
    return orth_procrustes(xs[i], xt[j]), len(i)
