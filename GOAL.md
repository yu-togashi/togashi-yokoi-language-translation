# Research Goal — togashi-yokoi-language-translation

## The question

GWOT（Gromov–Wasserstein Optimal Transport）による教師なし単語対訳抽出で、
**言語内の距離行列をいじって local な距離構造だけを残すと**、アラインメント精度や得られる対応がどう変わるかを調べる。
出発点は 2026-09-14 の議論での yokoi の提案「距離の閾値を超えたらコストを +∞ にする？」。
第一段階として、Alvarez-Melis & Jaakkola (EMNLP 2018) の結果を、原論文と同じデータ・同じアルゴリズムで再現できるかを確認する。

## Starting point

- `documents/local_gw_plan.md` — 計画メモ（2026-10-14 作成）。論文の要点、公式コードの構造と既知のバグ、データ取得方法、Step 1〜4 の手順
- 対象論文：D. Alvarez-Melis, T. S. Jaakkola, "Gromov-Wasserstein Alignment of Word Embedding Spaces", EMNLP 2018（arXiv:1809.00013）
- 著者公式実装：https://github.com/dmelis/otalign （最終コミット 2020-06-16）
- ラボの GW ライブラリ：GWTune（oizumi-lab）
- データ（リポジトリには含めない）：fastText `wiki.{lang}.vec`（上位 20 万語）、MUSE 対訳辞書、（任意）VecMap の Dinu データ

## Deliverables

1. **データ**（Step 1）：`wiki.{en,es,fr,de,it,ru}.vec` の上位 20 万語と MUSE 辞書を `data/raw/MUSE/` に取得。上位 K 語の辞書カバレッジを表にまとめる
2. **otalign での再現**（Step 2）：最低限のバグ修正（評価辞書 fold など）を入れたうえで EN-ES を K=2000 で実行し P@1 を出す。K=2000/5000/10000 の 1 反復あたり時間とメモリから K=20000 のコストを外挿し、可能なら K=20000 で実行
3. **GWTune での実行と比較**（Step 3）：コサイン距離＋mean 正規化、一様な p,q、P@1 評価をそろえて GWTune で同じタスクを解き、otalign と精度・計算時間を比較する
4. **基礎解析・可視化**（Step 4）：上位 K 語の中身、距離分布、クラスター構造、辞書ペアでの |d_s(i,k) − d_t(i′,k′)| と近傍順位の関係のプロット
5. **local-GW の初期実験**：閾値処理した距離行列（大きな有限値で置換、単調変換、マスクなど）で GW を解き、閾値ごとに P@1 を比較する
6. 2026-10-19 の MTG 用に「簡単な設定の GW 実験結果」を用意（最低限 K=2000 EN-ES の P@1 と Step 4 のプロット数枚）

## Success criteria

- EN-ES で、論文 Table 1 の傾向（P@1 がおおむね 0.7〜0.8）に近い値を otalign か GWTune のどちらかで再現できる。差が出る場合は原因（K、λ、評価 fold、初期化）を切り分けて説明できる
- 辞書ペアの距離ずれについて、local（近傍）と global で振る舞いが違うかどうかを図で答えられる
- 閾値 GW について、少なくとも 1 つの閾値処理方式で、閾値と P@1 の関係を図で示せる

## Quality bar

- 再現：比較する条件（K、λ、正規化、評価 fold、P@1 の取り方）を必ず明記。論文の数値と合わないときは合わないと報告する
- 解析：すべての図に生成スクリプトとシードを対応させる（`code/experiments/` → `analysis/figures/`）
- 評価には MUSE 標準テスト（`.5000-6500.txt`）を使う。otalign デフォルトの `.0-5000.txt` で出した値は区別して記録する

## Scope — in

- Conneau/MUSE タスク（EN↔ES を主に、余裕があれば FR/DE/IT/RU）
- otalign の最小限のバグ修正と実行
- GWTune への前処理・評価関数の移植
- 距離行列の閾値処理・単調変換・マスクによる local-GW の変種
- 距離構造の基礎解析・可視化

## Scope — out

- 埋め込み自体の再学習（公開の fastText ベクトルを使う）
- otalign の GPU パスの修正（CPU で回す）
- 教師ありの BLI 手法との網羅的な比較
- 論文執筆（当面は MTG 用の結果作りが目的。執筆は後で判断）
- Dinu タスク（Table 2）は余裕があれば。必須ではない

## Known constraints

- メモリ：K=20000 では距離行列 1 枚で約 3.2 GB（float64）、solve() 全体では数十 GB の見込み。K=2000 から段階的に上げる
- 計算時間：論文では CPU で 1 言語対あたり 37〜70 分（K=20000）。K³ のスケーリングに加え、λ が小さいと Sinkhorn の反復が増える
- 文字通りの `+inf` は square-loss GW で inf−inf → NaN になるので、有限値や変換で代用する
- 大きなデータ（`.vec`、辞書、距離行列）はコミットしない（`data/raw/` は .gitignore 済み）
- 締切：2026-10-19 の MTG（togashi, yokoi）
