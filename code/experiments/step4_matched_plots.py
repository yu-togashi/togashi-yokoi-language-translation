"""Figure for step4_matched.py: PCA of the dictionary-matched EN/ES words.

  analysis/figures/step4_matched_pca_K<K>.png
    top:    EN by EN clusters | ES by ES clusters (ES clusters coloured like their best-matching EN cluster)
    bottom: EN by the ES cluster of its partner | ES by the EN cluster of its partner
Cluster names were assigned by reading analysis/tables/step4_matched_K<K>.md.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import linear_sum_assignment  # noqa: E402

from step4_plots import DATA, FIG, INK, K, MUTED, SLOT, SURFACE, style  # noqa: E402

NAMES = {
    "en": ["events & organizations", "talk-page / opinion", "geography & physical",
           "society, history & religion", "media & entertainment", "science & technical",
           "anglophone person names", "countries & foreign places"],
    "es": ["dates & hispanic first names", "technical & abstract", "government & politics",
           "talk / mental verbs", "English strings & media", "geography & physical",
           "countries & nationalities", "anglophone names & English words"],
}


def main() -> None:
    d = np.load(DATA / f"matched_K{K}.npz")
    le, ls = d["en_labels"], d["es_labels"]
    ct = np.zeros((8, 8), int)
    np.add.at(ct, (le, ls), 1)
    _, es_to_en = linear_sum_assignment(-ct.T)  # es cluster c ↔ en cluster es_to_en[c]
    colour = {"en": {c: SLOT[c] for c in range(8)},
              "es": {c: SLOT[es_to_en[c]] for c in range(8)}}

    fig, axes = plt.subplots(2, 2, figsize=(17, 12.5), facecolor=SURFACE)
    panels = [("en", "en", "EN words, coloured by EN cluster"),
              ("es", "es", "ES words, coloured by ES cluster (colour = best-matching EN cluster)"),
              ("en", "es", "EN words, coloured by the ES cluster of their partner"),
              ("es", "en", "ES words, coloured by the EN cluster of their partner")]
    for ax, (where, by, title) in zip(axes.flat, panels):
        style(ax)
        xy = d[f"{where}_coords"][:, :2]
        lab = d[f"{by}_labels"]
        for c in range(8):
            m = lab == c
            ax.scatter(*xy[m].T, s=3, color=colour[by][c], alpha=0.4, linewidths=0, rasterized=True)
        handles = [plt.Line2D([], [], marker="o", ls="", ms=8, color=colour[by][c],
                              label=f"{NAMES[by][c]} ({(lab == c).sum()})")
                   for c in sorted(range(8), key=lambda c: colour[by][c] and SLOT.index(colour[by][c]))]
        ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False,
                  fontsize=8.5, labelcolor=INK, title=f"{by.upper()} cluster (size)", title_fontsize=8.5)
        ev = d[f"{where}_explained"]
        ax.set_xlabel(f"PC1 ({ev[0]:.1%})", color=MUTED, fontsize=9)
        ax.set_ylabel(f"PC2 ({ev[1]:.1%})", color=MUTED, fontsize=9)
        ax.set_title(title, fontsize=11, color=INK, loc="left")
    fig.suptitle(f"Dictionary-matched one-to-one EN–ES pairs inside both top-{K} ({len(le)} pairs)",
                 fontsize=12, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / f"step4_matched_pca_K{K}.png", dpi=150, facecolor=SURFACE)
    print("ES→EN cluster matching:", {f"es{c}": f"en{es_to_en[c]}" for c in range(8)})


if __name__ == "__main__":
    main()
