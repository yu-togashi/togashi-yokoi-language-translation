"""Figures for k=12 clusterings (run step4_k12.py first).

  step4_k12_flows_K<K>.png      EN clusters (left) ↔ ES clusters (right) through the one-to-one pairs,
                                ribbon width ∝ number of pairs; full-vocabulary and matched-only clusterings
  step4_k12_pca_{full,matched}_K<K>.png   PCA small multiples, one panel per cluster
  step4_k12_rdm_K<K>.png        sorted distance matrices: full (each language by its own clusters) and
                                matched (EN and ES pairs in the same order, sorted by EN cluster)
Colours: 8 validated palette hues + 4 darker shades; every cluster is also labelled by name.
ES clusters take the colour of their best-matching EN cluster (Hungarian matching on the pair counts).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from scipy.optimize import linear_sum_assignment  # noqa: E402

from localgw.data import load_vectors  # noqa: E402
from localgw.preprocess import normalize_embeddings  # noqa: E402
from step4_plots import BLUE_RAMP, DATA, FIG, INK, K, MUTED, SLOT, SURFACE, style  # noqa: E402

COLORS = SLOT + ["#104281", "#9c3a12", "#0b6b49", "#8f6100"]
GREY = "#d9d8d2"
NAMES = {
    ("en", "full"): ["function words & discourse", "talk-page / opinion", "institutions & society",
                     "story actions", "sports, dates & symbols", "geography & nature",
                     "media & entertainment", "wiki markup & codes", "anglophone places",
                     "anglophone person names", "science & technology", "foreign names & places"],
    ("es", "full"): ["function words & descriptive verbs", "institutions & society", "talk-page / opinion",
                     "technical & processes", "markup & codes", "story actions",
                     "sports, dates & countries", "past-tense verbs", "geography & nature",
                     "hispanic names & places", "English words & media", "anglophone names & places"],
    ("en", "matched"): ["talk-page / opinion", "institutions & organizations", "places, routes & dates",
                        "function words & discourse", "conflict & story actions", "countries & nationalities",
                        "media & entertainment", "anglophone person names", "history, religion & culture",
                        "technology", "biology & nature", "foreign person names"],
    ("es", "matched"): ["career & event verbs (past)", "hispanic first names", "towns & settlements",
                        "literature, arts & scholarship", "technical & abstract", "government & politics",
                        "talk-page / opinion", "family & emotional story", "countries & nationalities",
                        "English strings & media", "biology & physical description",
                        "anglophone names & English words"],
}


def load():
    return np.load(DATA / f"k12_K{K}.npz")


def pair_labels(d, setting):
    """EN and ES cluster labels of the one-to-one pairs."""
    pairs = d["pairs"]
    if setting == "full":
        return d["en_full_labels"][pairs[:, 0]], d["es_full_labels"][pairs[:, 1]]
    return d["en_matched_labels"], d["es_matched_labels"]


def matching(le, ls, k=12):
    ct = np.zeros((k, k), int)
    np.add.at(ct, (le, ls), 1)
    _, es_to_en = linear_sum_assignment(-ct.T)
    return ct, es_to_en


def ribbon(ax, x0, x1, y0a, y0b, y1a, y1b, color):
    xm = (x0 + x1) / 2
    verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a), (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", alpha=0.45))


def flows_panel(ax, d, setting):
    le, ls = pair_labels(d, setting)
    n = len(le)
    ct, es_to_en = matching(le, ls)
    en_order = list(range(12))
    es_order = sorted(range(12), key=lambda c: es_to_en[c])
    gap, x0, x1, w = 0.012, 0.0, 1.0, 0.025
    scale = (1 - 11 * gap) / n

    def stack(order, sizes):
        pos, y = {}, 1.0
        for c in order:
            h = sizes[c] * scale
            pos[c] = (y - h, y)
            y -= h + gap
        return pos

    en_pos = stack(en_order, ct.sum(1))
    es_pos = stack(es_order, ct.sum(0))
    en_cursor = {c: en_pos[c][1] for c in en_order}
    es_cursor = {c: es_pos[c][1] for c in es_order}
    for i in en_order:  # ribbons, partner order top→bottom to limit crossings
        for j in es_order:
            f = ct[i, j]
            if f == 0:
                continue
            h = f * scale
            ribbon(ax, x0 + w, x1 - w, en_cursor[i], en_cursor[i] - h, es_cursor[j], es_cursor[j] - h,
                   COLORS[i])
            en_cursor[i] -= h
            es_cursor[j] -= h
    for c in en_order:
        lo, hi = en_pos[c]
        ax.add_patch(plt.Rectangle((x0, lo), w, hi - lo, color=COLORS[c]))
        ax.text(x0 - 0.01, (lo + hi) / 2, f"{NAMES['en', setting][c]} ({ct[c].sum()})", ha="right",
                va="center", fontsize=8, color=INK)
    for c in es_order:
        lo, hi = es_pos[c]
        ax.add_patch(plt.Rectangle((x1 - w, lo), w, hi - lo, color=COLORS[es_to_en[c]]))
        share = ct[es_to_en[c], c] / ct[:, c].sum()
        ax.text(x1 + 0.01, (lo + hi) / 2, f"{NAMES['es', setting][c]} ({ct[:, c].sum()}; "
                f"{share:.0%} from matched EN)", ha="left", va="center", fontsize=8, color=INK)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.01, 1.01)
    ax.axis("off")
    title = {"full": f"clusters of all top-{K} words", "matched": "clusters of matched words only"}[setting]
    ax.set_title(f"EN (left) ↔ ES (right): {title}; {n} one-to-one pairs", fontsize=11, color=INK, loc="center")


def flows_figure(d):
    fig, axes = plt.subplots(1, 2, figsize=(26, 9.5), facecolor=SURFACE)
    for ax, setting in zip(axes, ["full", "matched"]):
        flows_panel(ax, d, setting)
    fig.tight_layout()
    fig.subplots_adjust(left=0.1, right=0.85, wspace=0.9)
    fig.savefig(FIG / f"step4_k12_flows_K{K}.png", dpi=150, facecolor=SURFACE)


def pca_figure(d, setting):
    le, ls = pair_labels(d, "matched" if setting == "matched" else "full")
    _, es_to_en = matching(*pair_labels(d, setting))
    fig, axes = plt.subplots(4, 6, figsize=(19, 13.5), facecolor=SURFACE)
    for row0, lang in [(0, "en"), (2, "es")]:
        xy = d[f"{lang}_{setting}_coords"]
        lab = d[f"{lang}_{setting}_labels"]
        for c in range(12):
            ax = axes[row0 + c // 6, c % 6]
            style(ax)
            col = COLORS[c] if lang == "en" else COLORS[es_to_en[c]]
            ax.scatter(*xy.T, s=1, color=GREY, linewidths=0, rasterized=True)
            ax.scatter(*xy[lab == c].T, s=2, color=col, alpha=0.7, linewidths=0, rasterized=True)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"{lang.upper()}: {NAMES[lang, setting][c]} ({(lab == c).sum()})", fontsize=8.5,
                         color=INK, loc="left")
    what = {"full": f"all top-{K} words", "matched": "dictionary-matched words only"}[setting]
    fig.suptitle(f"PCA (PC1 × PC2), k-means k=12 on {what}; ES colours = best-matching EN cluster",
                 fontsize=12, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / f"step4_k12_pca_{setting}_K{K}.png", dpi=150, facecolor=SURFACE)


def rdm_panel(fig, ax, x, groups, names, colors, title):
    """x: normalized vectors in display order; groups: list of (start, size, name index)."""
    dist = 1 - x @ x.T
    dist /= dist[np.triu_indices(len(x), 1)].mean()
    np.fill_diagonal(dist, np.nan)
    vmin, vmax = np.nanpercentile(dist, [2, 98])
    style(ax)
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    im = ax.imshow(dist, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest", rasterized=True)
    for start, size, c in groups:
        if start:
            ax.axhline(start - 0.5, color=SURFACE, lw=1)
            ax.axvline(start - 0.5, color=SURFACE, lw=1)
        ax.add_patch(plt.Rectangle((-len(x) * 0.02, start), len(x) * 0.012, size, color=colors[c], clip_on=False))
        ax.text(-len(x) * 0.025, start + size / 2, names[c], ha="right", va="center", fontsize=7.5, color=INK)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, len(x) - 0.5)
    ax.set_title(title, fontsize=10, color=INK, loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("distance (mean = 1)", color=MUTED, fontsize=8)
    cb.ax.tick_params(colors=MUTED, labelsize=7)
    cb.outline.set_visible(False)


def rdm_figure(d, per=150):
    rng = np.random.default_rng(0)
    vec = {lang: normalize_embeddings(load_vectors(lang, K)[1]) for lang in ["en", "es"]}
    fig, axes = plt.subplots(2, 2, figsize=(17, 14.5), facecolor=SURFACE)

    # full: each language sorted by its own clusters (ES in the order of matched EN clusters)
    _, es_to_en = matching(*pair_labels(d, "full"))
    for ax, lang in zip(axes[0], ["en", "es"]):
        lab = d[f"{lang}_full_labels"]
        order = list(range(12)) if lang == "en" else sorted(range(12), key=lambda c: es_to_en[c])
        idx, groups, start = [], [], 0
        for c in order:
            sel = np.sort(rng.choice(np.flatnonzero(lab == c), per, replace=False))
            idx.append(sel)
            groups.append((start, per, c))
            start += per
        colors = COLORS if lang == "en" else {c: COLORS[es_to_en[c]] for c in range(12)}
        rdm_panel(fig, ax, vec[lang][np.concatenate(idx)], groups, NAMES[lang, "full"], colors,
                  f"{lang.upper()}, all top-{K}: sorted by own k=12 clusters ({per} random words each)")

    # matched: the same pairs in the same order (sorted by EN matched cluster) in both languages
    pairs = d["pairs"]
    le = d["en_matched_labels"]
    idx, groups, start = [], [], 0
    for c in range(12):
        sel = np.sort(rng.choice(np.flatnonzero(le == c), per, replace=False))
        idx.append(sel)
        groups.append((start, per, c))
        start += per
    idx = np.concatenate(idx)
    for ax, (li, lang) in zip(axes[1], enumerate(["en", "es"])):
        x = normalize_embeddings(load_vectors(lang, K)[1][pairs[:, li]])[idx]
        rdm_panel(fig, ax, x, groups, NAMES["en", "matched"], COLORS,
                  f"{lang.upper()}, matched pairs: same pairs, same order (sorted by EN cluster)")
    fig.tight_layout()
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.02, wspace=0.45, hspace=0.08)
    fig.savefig(FIG / f"step4_k12_rdm_K{K}.png", dpi=130, facecolor=SURFACE)


UNMATCHED = [("lost in one-to-one (translation taken)", "#c9c8c0"),
             ("translation only outside other top-K", "#a3a29a"),
             ("not in dictionary", "#e9e8e2")]


def unmatched_reason(words, other_words, d, matched_idx):
    """Per word: -1 = matched pair, 0/1/2 = index into UNMATCHED."""
    other = set(other_words)
    out = np.full(len(words), 2)
    for i, w in enumerate(words):
        golds = d.get(w)
        if golds is None:
            continue
        out[i] = 0 if any(g in other for g in golds) else 1
    out[matched_idx] = -1
    return out


def flows_full_all_figure(d):
    from localgw.data import load_dictionary

    pairs = d["pairs"]
    lab = {"en": d["en_full_labels"], "es": d["es_full_labels"]}
    words = {"en": list(d["en_words"]), "es": list(d["es_words"])}
    reason = {"en": unmatched_reason(words["en"], words["es"], load_dictionary("en", "es", "full"), pairs[:, 0]),
              "es": unmatched_reason(words["es"], words["en"], load_dictionary("es", "en", "full"), pairs[:, 1])}
    le, ls = lab["en"][pairs[:, 0]], lab["es"][pairs[:, 1]]
    ct, es_to_en = matching(le, ls)
    order = {"en": list(range(12)), "es": sorted(range(12), key=lambda c: es_to_en[c])}
    color = {"en": {c: COLORS[c] for c in range(12)}, "es": {c: COLORS[es_to_en[c]] for c in range(12)}}

    fig, ax = plt.subplots(figsize=(17, 11), facecolor=SURFACE)
    gap, x0, x1, w = 0.008, 0.0, 1.0, 0.03
    scale = (1 - 11 * gap) / K
    pos, cursor = {}, {}
    for lang, x in [("en", x0), ("es", x1 - w)]:
        y = 1.0
        for c in order[lang]:
            m = lab[lang] == c
            n, n_match = m.sum(), (reason[lang][m] == -1).sum()
            top = y
            pos[lang, c] = (top - n * scale, top)
            cursor[lang, c] = top
            ax.add_patch(plt.Rectangle((x, top - n_match * scale), w, n_match * scale, color=color[lang][c]))
            yy = top - n_match * scale
            for r, (_, col) in enumerate(UNMATCHED):
                h = (reason[lang][m] == r).sum() * scale
                ax.add_patch(plt.Rectangle((x, yy - h), w, h, facecolor=col, edgecolor="#a3a29a", lw=0.4))
                yy -= h
            label = f"{NAMES[lang, 'full'][c]} ({n}; {n_match / n:.0%} paired)"
            if lang == "en":
                ax.text(x - 0.01, top - n * scale / 2, label, ha="right", va="center", fontsize=8.5, color=INK)
            else:
                ax.text(x + w + 0.01, top - n * scale / 2, label, ha="left", va="center", fontsize=8.5, color=INK)
            y = top - n * scale - gap
    for i in order["en"]:
        for j in order["es"]:
            f = ct[i, j]
            if f:
                h = f * scale
                ribbon(ax, x0 + w, x1 - w, cursor["en", i], cursor["en", i] - h, cursor["es", j],
                       cursor["es", j] - h, COLORS[i])
                cursor["en", i] -= h
                cursor["es", j] -= h
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=col, edgecolor="#a3a29a", lw=0.4, label=name)
               for name, col in UNMATCHED]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.005), ncol=3, frameon=False,
              fontsize=9, labelcolor=INK, title="part of a cluster without a one-to-one partner",
              title_fontsize=9)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.01, 1.01)
    ax.axis("off")
    ax.set_title(f"EN (left) ↔ ES (right) k=12 clusters of all top-{K} words; bar height ∝ cluster size, "
                 f"ribbons = {len(pairs)} one-to-one pairs", fontsize=11, color=INK)
    fig.subplots_adjust(left=0.2, right=0.78, top=0.95, bottom=0.07)
    fig.savefig(FIG / f"step4_k12_flows_full_all_K{K}.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    import sys

    d = load()
    which = sys.argv[1:] or ["flows", "pca", "rdm"]
    if "flows" in which:
        flows_figure(d)
    if "flows_all" in which or not sys.argv[1:]:
        flows_full_all_figure(d)
    if "pca" in which:
        pca_figure(d, "full")
        pca_figure(d, "matched")
    if "rdm" in which:
        rdm_figure(d)
