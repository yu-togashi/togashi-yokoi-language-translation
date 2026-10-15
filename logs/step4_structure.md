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

## Translation coverage per cluster (`analysis/tables/step4_cluster_coverage_K20000.md`)
MUSE full dictionary. "partner" = a gold translation inside the other language's top-20000.

| EN cluster | partner in ES top-K | only outside | not in dict | same-theme ES cluster | | ES cluster | partner in EN top-K | only outside | not in dict | same-theme EN cluster |
|---|---|---|---|---|---|---|---|---|---|---|
| talk-page / opinion | 59% | 22% | 19% | 46% | | talk-page / opinion | 78% | 4% | 18% | 32% |
| politics & events | 77% | 14% | 9% | 53% | | institutions & society | 83% | 8% | 10% | 49% |
| geography & physical | 71% | 18% | 11% | 61% | | geography & nature | 82% | 8% | 10% | 52% |
| science & technical | 74% | 18% | 9% | 62% | | function words & abstract | 83% | 3% | 14% | 55% |
| pop culture & symbols | 66% | 23% | 11% | 5% | | narrative verbs (past) | 56% | 3% | 41% | 15% |
| wiki markup & codes | 15% | 18% | 68% | 57% | | English words & symbols | 52% | 6% | 42% | 4% |
| anglophone names | 52% | **47%** | 2% | 76% | | anglophone names & places | **94%** | 2% | 5% | 71% |
| foreign names & places | 62% | 28% | 9% | 29% | | hispanic names & places | 41% | **53%** | 6% | 48% |
| all | 65% | 23% | 12% | | | all | 72% | 10% | 18% | |

- **Own-culture names are the least matchable**: about half of EN anglophone names and ES hispanic names have
  their translation (usually the same string) only outside the other language's top-20000 — they are frequent
  at home but rare abroad. Foreign names that make it into a top-K are almost always matchable (ES anglophone 94%).
- Topical clusters (politics, geography, technical) are the most matchable (71–83%).
- Unmatchable mainly through the dictionary: EN wiki markup (68% not in dict), ES narrative past-tense verbs (41%;
  inflected forms are sparse in MUSE), ES English words & symbols (42%).
- Only ~50–60% of matchable words land in the "same-theme" cluster of the other language (names ~75%):
  the clusters are not well aligned across languages (also depends on my naming; pop culture ↔ narrative verbs
  was a loose pairing → 5% / 15%).

## Restricted to dictionary-matched words (`code/experiments/step4_matched.py`, `step4_matched_plots.py`)
One-to-one pairs: EN top-20000 in frequency order, first MUSE full-dictionary translation inside the ES
top-20000 not used yet → **11,128 pairs (56% of each top-K), 27% identical strings**.
Table `analysis/tables/step4_matched_K20000.md`, figure `analysis/figures/step4_matched_pca_K20000.png`.

- **Restricting to matched words does not make the structure stronger**: PCA PC1 3.6–3.7%, 50 PCs 42–43%;
  silhouette 0.024 in both languages; mean cosine distance within clusters / overall = 0.91 (same as before).
- Clusters (k=8), named from the table:
  EN — events & organizations, talk-page / opinion, geography & physical, society/history/religion,
  media & entertainment, science & technical, anglophone person names, countries & foreign places.
  ES — dates & hispanic first names, technical & abstract, government & politics, talk / mental verbs,
  English strings & media, geography & physical, countries & nationalities, anglophone names & English words.
- **EN and ES clusterings agree only moderately through the pairs: ARI 0.25, NMI 0.34.**
  Share of an EN cluster that goes to its best-matching ES cluster: anglophone names 75%, geography 64%,
  technical 63%, countries 57%, society 54%, media 43%, talk 42%, events & organizations 28%.
- So names, places and physical/technical vocabulary keep their neighbourhood across languages, whereas
  general/event and conversational vocabulary is organized differently in the two spaces (EN "events" splits
  over ES politics, English strings, talk and technical). Note PCA axes are only defined up to sign/rotation,
  so the EN and ES scatter plots should be compared through the colours, not the positions.

## Choosing k (`code/experiments/step4_k_sweep.py`, table `analysis/tables/step4_k_sweep_K20000.md`, figure `analysis/figures/step4_k_sweep_K20000.png`)
k=8 was chosen only because 8 colours are distinguishable; silhouette is flat (0.02–0.03) for all k.
Consistency (ARI) for k = 6…20:

| k | EN↔ES matched-only | EN↔ES full (on pairs) | full vs matched EN | full vs matched ES | seed stability EN | seed stability ES |
|---|---|---|---|---|---|---|
| 6 | 0.24 | 0.19 | 0.70 | 0.48 | 0.87 | 0.98 |
| 8 | 0.25 | 0.23 | 0.52 | 0.51 | 0.77 | **0.97** |
| 10 | 0.26 | **0.30** | 0.55 | 0.43 | 0.74 | 0.64 |
| 12 | 0.23 | **0.30** | 0.49 | 0.44 | **0.82** | 0.72 |
| 14 | 0.24 | 0.27 | 0.44 | 0.48 | 0.62 | 0.65 |
| 16 | 0.26 | 0.22 | 0.53 | 0.48 | 0.75 | 0.64 |
| 20 | 0.26 | 0.24 | 0.51 | 0.44 | 0.72 | 0.69 |

- Cross-lingual agreement is low (ARI 0.2–0.3) for every k; no k makes the two languages' clusters align well.
- Clustering all 20000 words vs only the matched words gives moderately similar clusters (ARI 0.4–0.7):
  the unmatched words shift the partition but do not change its character.
- k-means itself is not very stable for k ≥ 10 (seed ARI 0.6–0.8), consistent with the absence of real clusters.
- Candidates: **k=8** (most stable, ES 0.97) or **k=12** (best cross-lingual agreement of full clusterings, 0.30,
  reasonably stable, still interpretable). k=12 adds clusters that correspond across languages, e.g. sports/teams
  (EN "championship sprint teams" ↔ ES "bundesliga juventus") and story actions (EN "enraged confronted flee" ↔
  ES "vengarse huir escapar"), and separates English place names and discourse/function words.
- Different k for the full and matched clusterings (`analysis/tables/step4_k_grid_full_vs_matched_K20000.md`):
  the agreement is highest on or next to the diagonal (same k), e.g. EN ARI full 6/matched 6 0.70, 10/10 0.55,
  16/16 0.53; ES is flatter (best 0.57 at full 20/matched 16, 0.51 at 8/8 and 10/8). There is no systematic
  preference for a smaller k on the smaller (matched) set → using the same k for both is reasonable, but nothing
  singles out 12; any k in 8–12 is defensible.
