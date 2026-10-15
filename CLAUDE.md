# Project Instructions — togashi-yokoi-language-translation

## Workflow

- **Plan first**: 3 ステップ以上の作業は `tasks/todo.md` にチェックリストで計画を書き、着手前に確認を取る
- **Track progress**: 終わった項目にチェックを付け、各ステップの結果と気づきは `tasks/todo.md` の Review に追記する
- **Lessons**: ユーザーから修正を受けたら `tasks/lessons.md` に再発防止ルールを書く（下の import で毎セッション自動的に読み込まれる）。特定の作業手順にまとまったものは `.claude/skills/` に切り出す
- **Verify before done**: 出力ファイルが実際にあること、スクリプトが実際に動くことを確認してから完了とする
- **Meetings**: 議事メモは `meetings/raw/` に置き、`/meeting` で `meetings/summaries/` に要約する

## Core principles

- **Simplicity first** — fewest files, one source of truth（進捗管理は `tasks/todo.md` だけ）
- **No laziness** — root causes, not workarounds
- **Pinned env** — `pyenv` + `poetry`; never system Python; run via `poetry run python ...`
- **Safe deletes** — no `rm`. Use `/trash`（`.trash/YYYY-MM-DD/` に移し `logs/trash.md` に記録）
- **Fixed seeds** — every experiment pins `numpy.random.default_rng(seed)`
- **Descriptive naming** — `logs/otalign_fixes.md`, not `logs/step2.md`

## Layout

- `code/localgw/` ライブラリコード、`code/experiments/` 実行スクリプト、`code/tests/` テスト
- `analysis/figures/`, `analysis/tables/` 生成物（すべて `code/experiments/` のスクリプトから再生成できること）
- `documents/` 入力資料（計画メモ、論文 PDF）
- `data/raw/`, `data/processed/` データ（git 管理外）、`external/otalign/` 公式実装（git 管理外）
- `logs/` 作業記録、`meetings/` MTG
- `paper/`, `survey/`, `theory/`, `review/`, `compile_paper.sh` 論文化に備えて残している（当面は使わない）

---

## The problem

GWOT による教師なし単語対訳抽出で、言語内の距離行列を閾値処理などで local な構造だけにしたときに、アラインメントがどう変わるかを調べる（local-GW）。
まず Alvarez-Melis & Jaakkola (EMNLP 2018, arXiv:1809.00013) を公式実装 otalign と GWTune の両方で再現し、そのうえで距離行列を変えた変種を試す。
詳細な計画・既知のバグ・データ取得方法は `documents/local_gw_plan.md`、作業リストは `tasks/todo.md`。
当面の成果物は 2026-10-19 の MTG 用の実験結果で、論文化は後で判断する。

## Domain-specific conventions

- **otalign は `external/otalign/` に置いて改変する**。fix はすべて commit メッセージと `logs/otalign_fixes.md` に記録する。`external/` は自分たちのコードとして扱わない
- **用語**（「train / test」は 2 つの意味で混同しやすいので使わない）
  - **GW 語彙（上位 K 語）**：GW の最適化に入れる各言語の頻度上位 K 語。辞書は一切使わない
  - **辞書 0-5000 / 辞書 5000-6500 / full 辞書**：MUSE の対訳辞書（`.0-5000.txt` / `.5000-6500.txt` / 分割なしの `.txt`、約 11 万ペア）。前 2 つは英語側の頻度順位で分かれていて、Conneau et al. は教師あり学習用（train）・評価用（test）と呼ぶ。GW は辞書を評価にしか使わないので、この区別は不要
  - **候補語彙**：訳語を検索する相手側の語（GW 語彙内の K 語 か 20 万語）
- **評価**：結果には必ず「辞書（0-5000 / 5000-6500）・候補語彙（K 語 / 20 万語）・スコア（coupling / bary / proj、CSLS の有無）」を書く。論文・Procrustes との比較の基本は「20 万語・辞書 5000-6500」（MUSE 標準）。GW 語彙内の評価は **full 辞書**で行う（GW 語彙のうち正解が辞書にある語すべて。K=20000 なら 65%）。正解が GW 語彙に 1 つもない語は数えない
- otalign と GWTune の比較では、上の 3 点（辞書・候補語彙・スコア）をそろえる。評価は `localgw.evaluate.bli_accuracy` を使う
- **比較の条件をそろえる**：コサイン距離、mean 正規化、一様な p,q。初期値の違い（otalign は T=pqᵀ、GWTune はランダム・多点）は別の要因として切り分ける
- **ε/λ の選択**は教師なし（GW 目的値）で行う。辞書を使ったハイパラ選択はしない
- **パラメータの換算に注意**（同じ数字でも意味が違う。詳細は `logs/gwtune_comparison.md`）
  - Sinkhorn の stopThr：POT ≤ 0.5（と otalign）は周辺分布の誤差のノルムの 2 乗、POT ≥ 0.6 はノルムと比較 → otalign の 1e-9 ＝ 今の POT の 3.16e-5
  - 正則化：otalign の損失は (a−b)²/2、POT/GWTune は (a−b)² → GWTune の ε ＝ 2 × otalign の λ
  - 外側の tol（‖ΔΓ‖_F）と Sinkhorn の stopThr は絶対値の閾値。Γ・q の要素が約 1/K なので、同じ値でも K によって実質の厳しさが変わる
  - 距離行列の正規化（平均で割るか）で ε の実質的な効き方が変わる
- GW は `localgw.gwtune_ext.GWTuneSolver`（GWTune ＋ Sinkhorn のウォームスタート ＋ stopThr 指定）で解くのを標準にする（設定 B：warmstart、stopThr 3.16e-5）
- **`+inf` を距離行列に直接入れない**（square-loss GW で NaN になる）。閾値処理を正規化の前後どちらに入れたかを必ず記録する
- **すべての実行で K（maxs/maxt）、λ、反復回数、wall-clock、ピークメモリを記録する**
- 大きなデータ（`.vec`、辞書、距離行列、Γ）はコミットしない。`data/raw/` と `data/processed/` に置く
- 結果が論文と合わなくても、合わないと報告する

## Lessons learned

@tasks/lessons.md
