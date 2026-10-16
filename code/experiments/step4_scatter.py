"""Step 4: EN distance vs ES distance for all dictionary-matched word pairs (11,128 one-to-one pairs).

  (a) density of all 62M word pairs (i<k): d_EN(i,k) on x, d_ES(i',k') on y (log colour)
  (b) the same density in grey, with the pairs where k is among i's 10 nearest EN neighbours as points
Distances as in step4_local_global.py (normalized for GW, mean 1 per language).
Output: analysis/figures/step4_scatter_K<K>.png
Usage: poetry run python code/experiments/step4_scatter.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm  # noqa: E402
from scipy.stats import pearsonr, spearmanr  # noqa: E402

from step4_local_global import distances, ranks  # noqa: E402
from step4_plots import BLUE_RAMP, DATA, FIG, INK, K, MUTED, SLOT, SURFACE, style  # noqa: E402

NN = 10


def main() -> None:
    rng = np.random.default_rng(0)
    pairs = np.load(DATA / f"k12_K{K}.npz")["pairs"]
    n = len(pairs)
    ds, dt = distances("en", pairs[:, 0]), distances("es", pairs[:, 1])
    edges = np.linspace(0, 1.4, 281)
    hist = np.zeros((len(edges) - 1, len(edges) - 1))
    for s in range(0, n, 1000):  # upper triangle in chunks
        rows = np.arange(s, min(s + 1000, n))
        mask = np.arange(n)[None, :] > rows[:, None]
        hist += np.histogram2d(ds[rows][mask], dt[rows][mask], bins=[edges, edges])[0]
    iu = np.triu_indices(n, 1)
    pick = rng.choice(len(iu[0]), 2_000_000, replace=False)
    a, b = ds[iu[0][pick], iu[1][pick]], dt[iu[0][pick], iu[1][pick]]
    r_all, rho_all = pearsonr(a, b)[0], spearmanr(a, b)[0]
    r_en = ranks(ds)
    loc = r_en < NN
    la, lb = ds[loc], dt[loc]
    r_loc, rho_loc = pearsonr(la, lb)[0], spearmanr(la, lb)[0]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6), facecolor=SURFACE)
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    for ax in axes:
        style(ax)
        ax.plot([0, 1.4], [0, 1.4], color=MUTED, lw=1, ls="--")
        ax.set_xlim(0, 1.4)
        ax.set_ylim(0, 1.4)
        ax.set_aspect("equal")
        ax.set_xlabel("distance in English  d_EN(i, k)", color=MUTED, fontsize=9)
        ax.set_ylabel("distance in Spanish  d_ES(i', k')", color=MUTED, fontsize=9)
    im = axes[0].imshow(hist.T, origin="lower", extent=[0, 1.4, 0, 1.4], cmap=cmap, norm=LogNorm(vmin=1),
                        interpolation="nearest", aspect="equal")
    cb = fig.colorbar(im, ax=axes[0], fraction=0.045, pad=0.02)
    cb.set_label("word pairs per cell", color=MUTED, fontsize=8)
    cb.ax.tick_params(colors=MUTED, labelsize=7)
    cb.outline.set_visible(False)
    axes[0].set_title(f"(a) all {n * (n - 1) // 2 / 1e6:.0f}M word pairs: Pearson r {r_all:.2f}, "
                      f"Spearman ρ {rho_all:.2f}", fontsize=10.5, color=INK, loc="left")

    axes[1].imshow(np.where(hist.T > 0, 1, np.nan), origin="lower", extent=[0, 1.4, 0, 1.4],
                   cmap=LinearSegmentedColormap.from_list("g", ["#e6e5df", "#e6e5df"]), aspect="equal")
    sel = rng.choice(len(la), min(40000, len(la)), replace=False)
    axes[1].scatter(la[sel], lb[sel], s=2, color=SLOT[0], alpha=0.25, linewidths=0, rasterized=True)
    axes[1].set_title(f"(b) k among i's {NN} nearest EN neighbours ({loc.sum() / 1e3:.0f}k pairs; "
                      f"40k shown): r {r_loc:.2f}, ρ {rho_loc:.2f}", fontsize=10.5, color=INK, loc="left")
    axes[1].text(0.02, 1.36, "grey = support of all pairs", fontsize=8, color=MUTED, va="top")
    fig.suptitle(f"EN vs ES distances of the same word pairs ({n} dictionary-matched words, top-{K}; "
                 "distances / mean)", fontsize=12, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / f"step4_scatter_K{K}.png", dpi=150, facecolor=SURFACE)
    print(f"all pairs: r {r_all:.3f} rho {rho_all:.3f}; EN {NN}-NN pairs ({loc.sum()}): r {r_loc:.3f} rho {rho_loc:.3f}")
    marginal_figure(hist, edges, a, b, r_all, rho_all, n)


def marginal_figure(hist, edges, a, b, r_all, rho_all, n):
    """Density of (d_EN, d_ES) with the marginal distributions on top (EN) and right (ES)."""
    fig = plt.figure(figsize=(8.5, 8.5), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[4, 1.2], height_ratios=[1.2, 4], wspace=0.04, hspace=0.04)
    ax = fig.add_subplot(gs[1, 0])
    top = fig.add_subplot(gs[0, 0], sharex=ax)
    right = fig.add_subplot(gs[1, 1], sharey=ax)
    for x in (ax, top, right):
        style(x)
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    ax.imshow(hist.T, origin="lower", extent=[edges[0], edges[-1], edges[0], edges[-1]], cmap=cmap,
              norm=LogNorm(vmin=1), interpolation="nearest", aspect="auto")
    ax.plot([0, 1.4], [0, 1.4], color=MUTED, lw=1, ls="--")
    ax.set_xlim(0, 1.4)
    ax.set_ylim(0, 1.4)
    ax.set_xlabel("distance in English  d_EN(i, k)  (mean = 1)", color=MUTED, fontsize=9)
    ax.set_ylabel("distance in Spanish  d_ES(i', k')  (mean = 1)", color=MUTED, fontsize=9)
    ax.text(0.03, 1.36, f"r {r_all:.2f}, ρ {rho_all:.2f}", fontsize=9, color=INK, va="top")
    centers = (edges[:-1] + edges[1:]) / 2
    w = edges[1] - edges[0]
    en, es = hist.sum(1), hist.sum(0)
    top.bar(centers, en / en.sum() / w, width=w, color=SLOT[0], linewidth=0)
    right.barh(centers, es / es.sum() / w, height=w, color=SLOT[0], linewidth=0)
    top.tick_params(labelbottom=False)
    right.tick_params(labelleft=False)
    top.set_ylabel("density", color=MUTED, fontsize=8)
    right.set_xlabel("density", color=MUTED, fontsize=8)
    top.text(0.02, 0.95, f"EN: sd {a.std():.3f}, 1% quantile {np.quantile(a, 0.01):.2f}", transform=top.transAxes,
             fontsize=8.5, color=INK, va="top")
    right.text(0.95, 0.02, f"ES: sd {b.std():.3f}\n1% quantile {np.quantile(b, 0.01):.2f}",
               transform=right.transAxes, fontsize=8.5, color=INK, ha="right", va="bottom")
    fig.suptitle(f"EN vs ES distances with marginal distributions ({n} matched words, "
                 f"{n * (n - 1) // 2 / 1e6:.0f}M word pairs)", fontsize=11, color=INK, x=0.02, ha="left")
    fig.savefig(FIG / f"step4_scatter_marginals_K{K}.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")


if __name__ == "__main__":
    main()
