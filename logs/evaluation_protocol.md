# Evaluation protocol: what Alvarez-Melis & Jaakkola (2018) and otalign actually do — 2026-10-14

Terminology (see CLAUDE.md): "dict 0-5000" / "dict 5000-6500" = MUSE dictionaries (Conneau et al. call them train / test); "GW vocabulary" = top-K words fed to GW; "candidates" = target words searched at retrieval.

Sources: `documents/alvarez-melis_jaakkola_2018_gw_alignment.pdf` (arXiv v1),
Conneau et al. 2018 "Word Translation Without Parallel Data" (arXiv:1710.04087),
otalign @ 37e48f8 (`scripts/main_gw_bli.py`, `src/bilind.py`).

## MUSE dictionaries (Conneau et al. 2018, independent of the GW paper)
- Released with MUSE. Split by source-word frequency rank: dict 0-5000 (5000 source words) is what Conneau et al.
  call the training dictionary for supervised methods (Procrustes); dict 5000-6500 (1500 source words) is their test set.
- Standard protocol (Conneau Table 1 caption): 1,500 test source queries, retrieval over **200k target words**,
  P@1 counts a hit if any gold translation is retrieved.

## Alvarez-Melis & Jaakkola, Table 1 (Conneau data)
- States: GW on top K = 20,000 words (memory limit, §4.2); Fig. 2 curves use 15K words.
- States: "Γ* by itself, without any further post-processing, provides high-quality translations" (§3.1);
  CSLS used "whenever nearest neighbor search is required" (§4.1, about mapping-based baselines).
- Does NOT state: which dictionary fold the G-W numbers use, which score (coupling / CSLS / projection),
  or the candidate vocabulary size.
- Minor inconsistency: §4.1 lists ZH among the pairs, Table 1 has IT instead.

Table 1 values (→ = from EN, ← = to EN):

| row | supervision | ES→ | ES← | FR→ | FR← | DE→ | DE← | IT→ | IT← | RU→ | RU← |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Procrustes | 5K words | 77.6 | 77.2 | 74.9 | 75.9 | 68.4 | 67.7 | 73.9 | 73.8 | 47.2 | 58.2 |
| Procrustes + CSLS | 5K words | 81.2 | 82.3 | 81.2 | 82.2 | 73.6 | 71.9 | 76.3 | 75.5 | 51.7 | 63.7 |
| Conneau et al. 2018 | none | 81.7 | 83.3 | 82.3 | 82.1 | 74.0 | 72.2 | 77.4 | 76.1 | 52.4 | 61.4 |
| G-W (λ=1e-4) | none | 78.3 | 79.5 | 79.3 | 78.3 | 69.6 | 66.9 | 75.3 | 74.1 | 26.1 | 35.4 |
| G-W (λ=1e-5) | none | 81.7 | 80.4 | 81.3 | 78.9 | 71.9 | 72.8 | 78.9 | 75.2 | 45.1 | 43.7 |

Comparison with Conneau et al. Table 1:
- "Conneau et al." row = Conneau's Adv-Refine-CSLS, copied exactly (81.7 83.3 82.3 82.1 74.0 72.2 …).
- Procrustes rows are close but not identical to Conneau's (Procrustes-NN 77.4 77.3 74.9 76.1 68.4 67.7;
  Procrustes-CSLS 81.4 82.9 81.1 82.4 73.5 72.4, ru 51.7 63.7) → probably re-run with MUSE code
  (trained on dict 0-5000, "Time 3"), i.e. evaluated with the MUSE protocol: dict 5000-6500, 200k candidates.

## otalign code
- Loads top `maxs`/`maxt` words; dictionary hard-coded to dict 0-5000 (`dict_fold='train'`), restricted to pairs
  whose source and target are both in the loaded top-K; one-to-many → any gold hit counts.
- After GW, prints six P@1 values (labelled "test dictionary" but it is dict 0-5000), candidates = GW vocabulary:
  `coupling` (argmax of Γ), `coupling_csls`, `bary` (barycentric projection, NN), `bary_csls`,
  `proj` (orthogonal map from mutual-NN anchors of Γ, NN), `proj_csls`.
- The 200k "out-of-sample" step only exports mapped vectors; it computes no accuracy.

## Implication
- Most likely the G-W numbers in Table 1 are GW vocabulary 20K, dict 0-5000, one of the six scores (probably `coupling`),
  while the baselines are dict 5000-6500 over 200k candidates — not the same protocol. Not confirmable from the text.
- No leakage issue in evaluating unsupervised GW on dict 0-5000, but it is easier
  (more frequent words, K candidates instead of 200k).
- **Update (2026-10-14):** evaluating the K=20000 orthogonal map on 200k candidates gives 78.1 (dict 0-5000) /
  76.7 (dict 5000-6500) — close to the paper's 78.3, so the Table 1 G-W numbers are most likely projection-based
  over 200k candidates, not Γ-based. See `logs/replication_summary.md`.
- Plan: report all six otalign scores and see which one reproduces Table 1.
