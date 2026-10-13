# TODO — local-GW 単語アラインメント

詳細は `documents/local_gw_plan.md`。締切：**2026-10-19 MTG**（togashi, yokoi）。
MTG までの最低ライン：K=2000 EN-ES の P@1（otalign か GWTune）＋ Step 4 の図数枚。

## Step 0：環境
- [ ] `poetry install`（pyproject に POT, tqdm, scikit-learn などを追加）
- [ ] GWTune を submodule として追加（他プロジェクトと同様）
- [ ] otalign を `external/otalign/` に clone（`.gitignore` するか submodule にするかを決める）
- [ ] GitHub に個人の private repo を作って push

## Step 1：word embedding・辞書の取得
- [ ] `https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.{lang}.vec` が生きているか確認（en, es, fr, de, it, ru）
- [ ] 上位 20 万語だけ取得（`curl ... | head -n 200001`）→ `data/raw/MUSE/wiki.{lang}.vec`
  - 事前アライン済みの `wiki.multi.*.vec` ではなく、非アラインの `wiki.{lang}.vec` を使う
- [ ] MUSE の `data/get_evaluation.sh` で辞書を取得 → `data/raw/MUSE/crosslingual/dictionaries/`
- [ ] 上位 K 語（K=2000/5000/10000/20000）と辞書（`.0-5000` / `.5000-6500`）の突き合わせ表を作る（カバレッジ確認）

## Step 2：原論文コード（otalign）で動かす
- [ ] 既知の問題を fix（`logs/otalign_fixes.md` に記録）
  - [ ] 評価辞書の fold：`load_vectors()` の `dict_fold = 'train'` ハードコード → 引数化、標準テスト `.5000-6500` で評価
  - [ ] （必要なら）Dinu タスクの `args.home_dir` 未定義
  - [ ] （任意）`--no_entropy` が `solve()` で効かない問題
  - GPU パスは触らない（CPU 前提）
- [ ] 現行 POT（0.9.x）で全体が動くか確認。動かない箇所を直す
- [ ] K=2000 で EN-ES を実行し、P@1 を論文の傾向（約 0.8）と比較
- [ ] 1 反復あたり時間とピークメモリを K=2000, 5000, 10000 で計測 → K=20000 を外挿
- [ ] 可能そうなら K=20000 で実行

## Step 3：GWTune で実行・比較
- [ ] otalign の `compute_distances` 相当（コサイン距離＋mean 正規化）を `code/src/` に切り出す
- [ ] MUSE 辞書による P@1 評価関数を `code/src/` に移植（argmax / CSLS の両方）
- [ ] 条件をそろえる：コサイン距離、mean 正規化、一様な p,q、ε は GW 目的値で選ぶ
- [ ] GWTune で EN-ES（K=2000）を実行
- [ ] otalign と P@1・計算時間を比較。差が出たら初期化（T=pqᵀ vs ランダム・多点）の影響を切り分ける

## Step 4：基礎解析・可視化（Step 1 が終われば Step 2・3 と並行で進められる）
- [ ] 上位 K 語の中身の確認（品詞・固有名詞・記号の割合など）
- [ ] 全体的な距離構造の可視化（ソートした距離行列、MDS/UMAP）
- [ ] 意味クラスターに分かれているかの確認
- [ ] 各言語の距離分布（ヒストグラム）
- [ ] 辞書ペアでの local vs global のずれ
  - [ ] 1 対多の対応の扱いを先に決める（例：先頭の訳語を採る）
  - [ ] |d_s(i,k) − d_t(i′,k′)| を、i から見た k の近傍順位の関数としてプロット
  - local で小さく global で大きければ閾値 GW の動機づけになる

## Step 5：local-GW（Step 2〜4 の後）
- [ ] 閾値処理の方式を実装：大きな有限値で置換 / 単調変換（tan, sigmoid⁻¹）/ 損失側でマスク
- [ ] 閾値を正規化の前後どちらに入れるかを決めて記録
- [ ] 閾値（または近傍数 k）をスイープして P@1 を比較。K への依存も確認
- [ ] （後で）unbalanced GW との関係を検討

## MTG（10/19）準備
- [ ] 結果のまとめ（P@1 の表、計算時間、Step 4 の図）を `analysis/` に置く

---

## Review
（各ステップ完了時に結果と気づきをここに追記）
