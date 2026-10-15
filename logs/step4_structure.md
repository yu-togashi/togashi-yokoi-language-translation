# Step 4: distance structure of the GW vocabularies (K=20000, EN / ES) — 2026-10-15

Scripts: `code/experiments/step4_structure.py` (PCA, k-means, tables), `code/experiments/step4_plots.py` (figures).
Vectors normalized as for GW (centre, unit length) → PCA = classical MDS of the cosine-distance cost.
Figures: `analysis/figures/step4_pca_K20000.png`, `analysis/figures/step4_distance_K20000.png`.
Cluster tables: `analysis/tables/step4_clusters_{en,es}_K20000.md`.

## No strong low-dimensional or cluster structure
- PCA: PC1 3.5%, PC2 2.5–2.6%; 50 PCs explain only 42% (EN 42.0%, ES 42.8%).
- k-means silhouette is ~0.02–0.03 for every k from 2 to 30 (EN and ES alike).
- Mean normalized distance within k-means clusters 0.90 (EN) / 0.91 (ES) vs between 1.01 — only ~10% closer.
  Tightest clusters: EN wiki markup 0.76, names 0.86; ES anglophone names 0.86, hispanic names 0.88.
- → The space is a continuum with soft topical regions, not separated categories.

## k-means (k=8) categories, named by reading the clusters
| colour slot | EN cluster (size) | ES cluster (size) |
|---|---|---|
| 1 | talk-page / opinion (2052) | talk-page / opinion (2345) |
| 2 | politics & events (3456) | institutions & society (3703) |
| 3 | geography & physical (2572) | geography & nature (2780) |
| 4 | science & technical (2765) | function words & abstract (3047) |
| 5 | pop culture & symbols (3757) | narrative verbs, past tense (1935) |
| 6 | wiki markup & codes (668) | English words & symbols (2732) |
| 7 | anglophone names (2394) | anglophone names & places (1584) |
| 8 | foreign (mostly hispanic) names & places (2336) | hispanic names & places (1874) |

- Most topical regions have a counterpart in the other language (talk, politics/society, geography, technical/abstract, names).
- Names group by referent culture in both languages, but their role differs: in EN, anglophone names are
  "own-language" and form the most separated region (PC1 > 0.3); in ES they sit with English words and
  symbols as a "foreign material" region (PC1 < −0.2). Same referents (e.g. john ↔ john), different neighbourhoods.
- Frequency: in ES the foreign/English region is mostly rare words (rank > 5000) and frequent words lie in the
  centre-right; in EN the anglophone-names region is also mostly rank > 5000. Frequency is a visible direction
  in the PC1–PC2 plane, not an independent axis.
- k-means clusters with k=8 split the frequent function words across clusters (EN "," "the" in politics; ES
  "de" "en" in narrative verbs): high-frequency words are not a cluster of their own.

## Implications for local-GW (to discuss)
- Because global structure is weak (distances concentrated around the mean, ±10%), most of the information
  GW uses may come from the small-distance tail — a direct motivation to look at local vs global next
  (|d_s(i,k) − d_t(i′,k′)| vs neighbour rank on dictionary pairs).
