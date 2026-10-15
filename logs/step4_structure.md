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

## k=12 figures (`code/experiments/step4_k12.py`, `step4_k12_plots.py`; table `analysis/tables/step4_k12_clusters_K20000.md`)
- `analysis/figures/step4_k12_flows_K20000.png`: EN clusters (left) ↔ ES clusters (right) through the 11,128
  one-to-one pairs, ribbon width ∝ pairs; ES clusters coloured/ordered by their best-matching EN cluster
  (Hungarian); each ES label gives the share of its pairs coming from that EN cluster.
  - Full-vocabulary clusterings: best-preserved are anglophone names & places (69%), institutions & society (66%),
    geography & nature (62%), talk-page (61%); weak are story actions (41%), technical (39%) and ES
    hispanic names (4%: hispanic names in ES are mostly paired with EN "foreign names & places", which flows
    into ES "sports, dates & countries"); ES past-tense verbs have only 144 pairs (inflected forms rarely in MUSE).
  - Matched-only clusterings: anglophone names 73%, countries 68%, talk-page 57%, towns 54%, government 53%;
    ES career/event verbs 21% and technical & abstract 29% receive words from many EN clusters.
- `step4_k12_pca_{full,matched}_K20000.png`: one panel per cluster (cluster in colour, rest grey). Names, places,
  markup and talk-page clusters are compact; topical clusters overlap broadly in PC1×PC2.
- `step4_k12_rdm_K20000.png`: top = each language sorted by its own clusters (150 words each); bottom = the same
  matched pairs in the same order (sorted by EN cluster) for EN and ES. In ES, the EN-defined blocks for
  person names, countries, talk-page, technology and biology are still visible (the ES name block is even
  tighter), while institutions, places/routes and media blocks fade — the part of the EN distance structure
  that survives in ES is concentrated in a few semantic fields.
- `analysis/figures/step4_k12_flows_full_all_K20000.png`: same k=12 full clusterings, but bar height ∝ full
  cluster size (20000 words per side) and the part without a one-to-one partner drawn in grey by reason
  (translation taken in one-to-one / translation only outside the other top-K / not in dictionary).
  Least paired: EN wiki markup 13%, anglophone places 39% (towns like northampton: outside ES top-K),
  talk-page 44%, sports/dates/symbols 48%; ES past-tense verbs 16% (mostly not in dictionary), markup 22%,
  hispanic names & places 33% (mostly outside EN top-K), English words & media 41%.
  Most paired: ES anglophone names & places 84%, technical 73%, institutions/geography 61–67% on both sides.
  The imbalance is concentrated in own-culture names/places (partner outside the other top-K), markup and
  inflected verbs (dictionary gaps).

## Local vs global agreement of EN–ES distances (`code/experiments/step4_local_global.py`)
11,128 one-to-one pairs; distances normalized as for GW, mean 1 per language; neighbour ranks inside the
matched set. Table `analysis/tables/step4_local_global_K20000.md`, figure `analysis/figures/step4_local_global_K20000.png`.

- **Neighbour identity is strongly preserved, most strongly at the smallest scale.** Share of EN k-NN whose
  partners are ES k-NN: k=1 0.33, k=10 0.36, k=100 0.40, k=1000 0.48, k=3000 0.57 vs chance k/N
  (0.0001 … 0.27) → enrichment ~3700× at k=1, ~40× at k=100, ~5× at k=1000, 2× at k=3000.
- **Rank agreement of distances is higher locally**: Spearman ρ(d_EN, d_ES) inside EN-rank bins falls from 0.56
  (nearest neighbour) to 0.24 (ranks 1001–3000); the last bin (3001–11127) rises to 0.34 only because it spans
  a wider distance range (range restriction affects all bins).
- **But the distance values themselves mismatch more for close pairs.** Binned by the *average* distance
  (symmetric, avoids regression to the mean): mean |d_EN − d_ES| = 0.097 for the closest 0.1% of word pairs,
  0.084 (1–5%), 0.056 (median), 0.044 (farthest 5%), with no systematic offset (mean d_ES − d_EN within ±0.02).
  Binning by one language's rank (panel a) exaggerates this through regression to the mean
  (EN rank 1: d_EN 0.36 vs d_ES 0.53; ES rank 1: d_ES 0.38 vs d_EN 0.51).
- Relative to no correspondence (random re-assignment), the mismatch is far smaller locally (rank 1: 0.19 vs 0.64,
  ×0.29) than globally (rank > 3000: 0.051 vs 0.076, ×0.67): far pairs all sit near the mean distance in both
  languages, so they agree in value but carry little information about which word is which.
- By EN cluster (overlap@10): countries & nationalities 0.60, foreign person names 0.47, history/religion 0.46,
  biology 0.44 … anglophone person names 0.26, talk-page 0.24. Anglophone names form a tight block in both
  languages but *which* name is next to which is not preserved (names are interchangeable inside the block).
- Implications for local-GW: the informative part of the correspondence is local (who is near whom), while the
  square loss on raw distances weights all 62M word pairs, most of them far pairs whose distances are ≈1 in
  both languages. Emphasizing local pairs (thresholding/masking) keeps the informative part, but because close
  distances disagree more in value, a rank- or neighbourhood-based cost may be preferable to raw local distances.
- Note (discussion 2026-10-16): absolute distance values matter less than the overall structure; the
  value-mismatch result above is kept for reference (it matters for the square-loss cost), but the
  rank/neighbourhood measures are the main description.
- overlap@10 per cluster = for each EN word i: share of its 10 nearest EN neighbours (among matched words)
  whose ES partners are among the 10 nearest ES neighbours of i' (any cluster), averaged over i in the cluster.

## EN vs ES distance scatter (`code/experiments/step4_scatter.py`, `analysis/figures/step4_scatter_K20000.png`)
- All 62M word pairs of the 11,128 matched words: Pearson r 0.60, Spearman ρ 0.52. The mass sits around
  (1, 1) and is elongated along the diagonal; the close-in-both tail follows the diagonal down to ~0.1.
- Pairs that are EN 10-NN (111k): EN distance 0.1–0.75 by construction, ES distance spread over 0.2–1.1
  (r 0.56, ρ 0.55) — many EN neighbours are not close in ES.
- Off-diagonal lobes: pairs much closer in ES than in EN (EN 0.8–1.1, ES 0.5–0.7) and the reverse
  (EN 0.4–0.6, ES 0.8–1.0); candidates are blocks that are tight in only one language (e.g. names /
  English strings in ES) — to check.
