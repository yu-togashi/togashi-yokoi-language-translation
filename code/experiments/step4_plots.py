"""Step 4 figures from data/processed/step4/<lang>_K<K>.npz (run step4_structure.py first).

  analysis/figures/step4_pca_K<K>.png      PC1–PC2 per language: k-means clusters | frequency rank
  analysis/figures/step4_distance_K<K>.png sorted cosine-distance matrix (300 words per cluster)

Cluster names were assigned by reading analysis/tables/step4_clusters_<lang>_K<K>.md.
Colours follow the theme / referent, so corresponding clusters share a colour across languages.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from localgw.data import REPO_ROOT, load_vectors  # noqa: E402
from localgw.preprocess import normalize_embeddings  # noqa: E402

K = 20000
SEED = 0
DATA = REPO_ROOT / "data" / "processed" / "step4"
FIG = REPO_ROOT / "analysis" / "figures"

# validated categorical palette (dataviz reference, light mode), fixed slot order
SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
INK, MUTED, SURFACE = "#1f1f1e", "#6b6a63", "#fcfcfb"

# cluster id -> (name, colour slot)
CLUSTERS = {
    "en": {0: ("talk-page / opinion", 0), 1: ("politics & events", 1), 2: ("geography & physical", 2),
           3: ("science & technical", 3), 4: ("pop culture & symbols", 4), 5: ("wiki markup & codes", 5),
           6: ("anglophone names", 6), 7: ("foreign names & places", 7)},
    "es": {0: ("function words & abstract", 3), 1: ("institutions & society", 1),
           2: ("narrative verbs (past)", 4), 3: ("talk-page / opinion", 0), 4: ("geography & nature", 2),
           5: ("English words & symbols", 5), 6: ("hispanic names & places", 7),
           7: ("anglophone names & places", 6)},
}
LANG_NAME = {"en": "English", "es": "Spanish"}


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)


def pca_figure(langs):
    fig, axes = plt.subplots(len(langs), 2, figsize=(17, 6.2 * len(langs)), facecolor=SURFACE)
    for row, lang in zip(np.atleast_2d(axes), langs):
        d = np.load(DATA / f"{lang}_K{K}.npz")
        xy, labels, ev = d["coords"][:, :2], d["labels"], d["explained"]
        names = CLUSTERS[lang]

        ax = row[0]
        style(ax)
        for c, (name, slot) in names.items():
            m = labels == c
            ax.scatter(*xy[m].T, s=2, color=SLOT[slot], alpha=0.35, linewidths=0, rasterized=True)
        handles = []
        for c, (name, slot) in sorted(names.items(), key=lambda kv: kv[1][1]):  # medians + legend
            cx, cy = np.median(xy[labels == c], axis=0)
            ax.scatter(cx, cy, s=70, color=SLOT[slot], edgecolors=SURFACE, linewidths=2, zorder=3)
            handles.append(plt.Line2D([], [], marker="o", ls="", ms=8, color=SLOT[slot],
                                      label=f"{name} ({(labels == c).sum()})"))
        ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False,
                  fontsize=8.5, labelcolor=INK, title="cluster (size); ● = median",
                  title_fontsize=8.5)
        ax.set_title(f"{LANG_NAME[lang]} top-{K}: k-means clusters (k=8)", fontsize=11, color=INK, loc="left")
        ax.set_xlabel(f"PC1 ({ev[0]:.1%})", color=MUTED, fontsize=9)
        ax.set_ylabel(f"PC2 ({ev[1]:.1%})", color=MUTED, fontsize=9)

        ax = row[1]
        style(ax)
        bins = [(10000, 20000, "#86b6ef"), (5000, 10000, "#5598e7"), (1000, 5000, "#256abf"),
                (0, 1000, "#0d366b")]  # ordinal ramp (step 250 → 700); frequent drawn last, on top
        handles = []
        for lo, hi, col in bins:
            ax.scatter(*xy[lo:hi].T, s=2, color=col, alpha=0.6, linewidths=0, rasterized=True)
            handles.append(plt.Line2D([], [], marker="o", ls="", ms=8, color=col,
                                      label=f"rank {lo + 1:,}–{hi:,}"))
        ax.legend(handles=handles[::-1], loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False,
                  fontsize=8.5, labelcolor=INK, title="frequency rank", title_fontsize=8.5)
        ax.set_title(f"{LANG_NAME[lang]} top-{K}: frequency rank", fontsize=11, color=INK, loc="left")
        ax.set_xlabel(f"PC1 ({ev[0]:.1%})", color=MUTED, fontsize=9)
        ax.set_ylabel(f"PC2 ({ev[1]:.1%})", color=MUTED, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / f"step4_pca_K{K}.png", dpi=150, facecolor=SURFACE)


def distance_figure(langs, per_cluster=300):
    rng = np.random.default_rng(SEED)
    fig, axes = plt.subplots(1, len(langs), figsize=(7.2 * len(langs), 6.6), facecolor=SURFACE)
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)  # near = light, far = dark
    for ax, lang in zip(np.atleast_1d(axes), langs):
        d = np.load(DATA / f"{lang}_K{K}.npz")
        labels = d["labels"]
        names = CLUSTERS[lang]
        order = sorted(names, key=lambda c: names[c][1])  # same colour order in both languages
        idx = np.concatenate([np.sort(rng.choice(np.flatnonzero(labels == c), per_cluster, replace=False))
                              for c in order])
        _, x, _ = load_vectors(lang, K)
        x = normalize_embeddings(x)[idx]
        dist = 1 - x @ x.T
        dist /= dist[np.triu_indices(len(idx), 1)].mean()
        np.fill_diagonal(dist, np.nan)
        block = np.repeat(np.arange(len(order)), per_cluster)
        same = block[:, None] == block[None, :]
        print(f"{lang}: mean distance within clusters {np.nanmean(dist[same]):.3f}, "
              f"between {np.nanmean(dist[~same]):.3f}; per cluster within: "
              + ", ".join(f"{names[c][0]} {np.nanmean(dist[np.ix_(block == i, block == i)]):.3f}"
                          for i, c in enumerate(order)))
        vmin, vmax = np.nanpercentile(dist, [2, 98])
        style(ax)
        im = ax.imshow(dist, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest", rasterized=True)
        for i, c in enumerate(order):
            name, slot = names[c]
            lo = i * per_cluster
            if i:
                ax.axhline(lo - 0.5, color=SURFACE, lw=1.5)
                ax.axvline(lo - 0.5, color=SURFACE, lw=1.5)
            ax.add_patch(plt.Rectangle((-28, lo), 20, per_cluster, color=SLOT[slot], clip_on=False))
            ax.text(-34, lo + per_cluster / 2, name, ha="right", va="center", fontsize=8.5, color=INK)
        ax.set_xlim(-0.5, len(idx) - 0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{LANG_NAME[lang]}: cosine distance / mean\n({per_cluster} random words per cluster)",
                     fontsize=11, color=INK, loc="left")
        cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
        cb.set_label("distance (mean = 1)", color=MUTED, fontsize=9)
        cb.ax.tick_params(colors=MUTED, labelsize=8)
        cb.outline.set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(left=0.13, wspace=0.45)
    fig.savefig(FIG / f"step4_distance_K{K}.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    pca_figure(["en", "es"])
    distance_figure(["en", "es"])
