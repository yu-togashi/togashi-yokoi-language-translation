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
- **評価**：P@1 は MUSE 標準テスト `en-xx.5000-6500.txt` で出す。otalign デフォルトの `.0-5000.txt`（train fold）で出した値は必ず「train-fold」と明記して区別する
- **P@1 の取り方**（Γ の argmax / NN / CSLS）を結果に必ず書く。otalign と GWTune の比較では同じ取り方にそろえる
- **比較の条件をそろえる**：コサイン距離、mean 正規化、一様な p,q。初期値の違い（otalign は T=pqᵀ、GWTune はランダム・多点）は別の要因として切り分ける
- **ε/λ の選択**は教師なし（GW 目的値）で行う。辞書を使ったハイパラ選択はしない
- **`+inf` を距離行列に直接入れない**（square-loss GW で NaN になる）。閾値処理を正規化の前後どちらに入れたかを必ず記録する
- **すべての実行で K（maxs/maxt）、λ、反復回数、wall-clock、ピークメモリを記録する**
- 大きなデータ（`.vec`、辞書、距離行列、Γ）はコミットしない。`data/raw/` と `data/processed/` に置く
- 結果が論文と合わなくても、合わないと報告する

## Lessons learned

@tasks/lessons.md
