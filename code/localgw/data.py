"""Loading fastText .vec embeddings and MUSE bilingual dictionaries."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
MUSE_DIR = REPO_ROOT / "data" / "raw" / "MUSE"
DICT_DIR = MUSE_DIR / "crosslingual" / "dictionaries"

# MUSE dictionary folds: "train" = .0-5000, "test" = .5000-6500, "full" = no suffix
DICT_SUFFIX = {"train": ".0-5000", "test": ".5000-6500", "full": ""}


def vec_path(lang: str) -> Path:
    return MUSE_DIR / f"wiki.{lang}.vec"


def load_vectors(
    lang: str, max_words: int | None = None, path: Path | None = None
) -> tuple[list[str], np.ndarray, dict]:
    """Read a fastText .vec file in frequency order.

    Lines whose field count does not match the header dimension (e.g. tokens
    containing whitespace) and repeated words are skipped, as in MUSE.

    Returns (words, vectors[n, dim] float32, stats).
    """
    path = path or vec_path(lang)
    words: list[str] = []
    vecs: list[np.ndarray] = []
    seen: set[str] = set()
    n_malformed = n_duplicate = 0
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        _, dim = map(int, f.readline().split())
        for line in f:
            if max_words is not None and len(words) >= max_words:
                break
            parts = line.rstrip("\n").rstrip(" ").split(" ")
            if len(parts) != dim + 1:
                n_malformed += 1
                continue
            word = parts[0]
            if word in seen:
                n_duplicate += 1
                continue
            seen.add(word)
            words.append(word)
            vecs.append(np.asarray(parts[1:], dtype=np.float32))
    stats = {"n_words": len(words), "dim": dim, "n_malformed": n_malformed,
             "n_duplicate": n_duplicate}
    return words, np.vstack(vecs), stats


def load_vocab(lang: str, max_words: int | None = None, path: Path | None = None) -> list[str]:
    """Words of a .vec file in frequency order, without parsing the vectors."""
    path = path or vec_path(lang)
    words: list[str] = []
    seen: set[str] = set()
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        _, dim = map(int, f.readline().split())
        for line in f:
            if max_words is not None and len(words) >= max_words:
                break
            parts = line.rstrip("\n").rstrip(" ").split(" ")
            if len(parts) != dim + 1 or parts[0] in seen:
                continue
            seen.add(parts[0])
            words.append(parts[0])
    return words


def dict_path(src: str, trg: str, fold: str) -> Path:
    return DICT_DIR / f"{src}-{trg}{DICT_SUFFIX[fold]}.txt"


def load_dictionary(src: str, trg: str, fold: str, path: Path | None = None) -> dict[str, list[str]]:
    """MUSE dictionary as {source word: [translations in file order]} (one-to-many)."""
    path = path or dict_path(src, trg, fold)
    pairs: dict[str, list[str]] = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            s, t = parts
            if t not in pairs[s]:
                pairs[s].append(t)
    return dict(pairs)
