# local-GW 単語アラインメント実験：計画メモ

作成日：2026-10-14
関連 MTG：2026-10-19（togashi, yokoi）

## 背景・目的

- 議事メモ（2026-09-14）より：「初手：距離の閾値を超えたらコストを +∞ にする？？」(yokoi)
- 目的：GWOT による教師なし単語対訳抽出において、**距離行列をいじる（local な距離構造だけを残す）とどうなるか**を調べる
- 第一段階として、原論文と同じデータ・同じアルゴリズムで結果が再現できるかを確認する
- 10/19 の MTG で「簡単な設定の GW 実験結果」があると議論が進みそう

## 対象論文

David Alvarez-Melis, Tommi S. Jaakkola, "Gromov-Wasserstein Alignment of Word Embedding Spaces", EMNLP 2018.
arXiv:1809.00013, https://arxiv.org/abs/1809.00013
ACL Anthology: D18-1214, https://aclanthology.org/D18-1214/

※ 本文（arXiv HTML 版）は原典で直接確認済み。

### 手法の要点（論文本文より）

- 言語内コサイン距離行列 C_s, C_t を作り、square loss の entropic GW を解く（Peyré, Cuturi & Solomon, ICML 2016 の反復法）
  - 各反復：擬似コスト Ĉ_Γ = C_st − 2 C_s Γ C_tᵀ → Sinkhorn（K = exp(−Ĉ_Γ/λ)）で Γ を更新
  - λ = エントロピー正則化係数
- p, q は一様分布
- 距離行列は平均値などで正規化。正規化すれば λ にほぼ鈍感になる、と記載
- λ：本文では 5×10⁻⁵（だめなら 1×10⁻⁴）。ただし Table 1 の行ラベルは λ=10⁻⁴ と 10⁻⁵ で、論文内でも記述が揃っていない
- 頻度上位 K 語のみで GW を解く（Table 1 は K=20,000、メモリ上限で決定）。残りの語は Γ から Procrustes で直交写像を作って射影
- Table 1（Conneau/MUSE データ、EN↔ES/FR/DE/IT/RU）：P@1 はおおむね 7〜8 割（EN-RU は低い）。CPU で 1 言語対あたり 37〜70 分
- Table 2（Dinu データ、EN↔IT/DE/FI/ES）：より難しいタスク。距離行列の正規化で大きく改善

## コード

著者公式実装：https://github.com/dmelis/otalign （README・中身をクローンして直接確認済み。最終コミット 2020-06-16）

```
git clone https://github.com/dmelis/otalign.git
cd otalign && pip install -e ./
python scripts/main_gw_bli.py --task conneau --src_lang en --trg_lang es --maxiter 50
```

- 依存：numpy, POT (Python Optimal Transport), tqdm, matplotlib。GPU 用に cupy（任意）
- `from ot.gromov import gwggrad, gwloss` は現行 POT 0.9.7 でも import 可能なことを確認済み（全体の動作は未確認）

### コード構造メモ

- `scripts/main_gw_bli.py`：メイン。`load_vectors()` がデータを読み込み、`gromov_bilind` で GW を解いて評価
- `src/gw_optim.py`
  - `gromov_wass_solver.compute_distances()`：`scipy.spatial.distance.cdist` でコサイン距離を計算 → mean/max/median で正規化。**距離行列をいじる差し込み口はここ**
  - `gromov_wass_solver.solve()`：初期値 T = pqᵀ、`gwggrad` で勾配 → `sinkhorn` で射影、のループ
- `src/bilind.py`：`gromov_bilind` クラス。`solve_gromovwass(entropic=False)` という非正則化 GW の別経路あり（POT の `ot.gromov.gromov_wasserstein` を呼ぶ）

### 主な引数

| 引数 | デフォルト | 論文の値 | 備考 |
|---|---|---|---|
| `--maxs` / `--maxt` | 2000 | 20000 | 上位 K 語 |
| `--entreg` | 5e-4 | 5e-5 / 1e-4（Table では 1e-4 / 1e-5） | λ |
| `--metric` | cosine | cosine | |
| `--normalize_dists` | mean | 平均などで正規化 | |
| `--distribs` | uniform | uniform | p, q |
| `--maxiter` | 1000 | — | |

### 既知の問題（fix 候補）

1. **評価辞書の fold**：`load_vectors()` 内で `dict_fold = 'train'` がハードコード。MUSE の `.0-5000.txt` で評価している。標準テストは `.5000-6500.txt`。論文の数値がどちらで出されたかは本文から判別できず
2. **Dinu タスク**：パスが `args.home_dir/pkg/vecmap/data` だが、`home_dir` が argparse に未定義
3. **`--no_entropy` が効かない**：`self.entropic` に保存されるが、`solve()` 内で分岐せず常に Sinkhorn を呼ぶ
4. **GPU パスが壊れている**：README 自身に、POT の cudamat→cupy 移行で壊れたと記載。CPU で回す前提
5. README の `--src` / `--trg` は argparse の省略形として通る（正式名は `--src_lang` / `--trg_lang`）

### 距離行列のサイズ・メモリ

- C_s：maxs × maxs、C_t：maxt × maxt（float64）。Γ や擬似コストは maxs × maxt
- K=2,000：1 枚あたり約 32 MB
- K=20,000：1 枚あたり約 3.2 GB。solve() 内で C1, C2, constC, hC1, hC2, T, 勾配, Sinkhorn カーネルなどが同時に乗るため、合計で数十 GB 規模の見込み（コードからの概算、未実測）
- 評価時（step 2）は `maxs = max(200000, maxs)` として上位 20 万語まで読み込み、Procrustes で射影

## データ

リポジトリにデータは含まれないので、自分で取得する必要がある。

### Conneau タスク（Table 1）

- 埋め込み：fastText Wikipedia ベクトル `wiki.{lang}.vec`
  - URL 形式：`https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.{lang}.vec`（MUSE README に記載。**現在もアクセスできるかは未確認**）
  - テキスト形式・頻度順・1 行目がヘッダ。上位 20 万語あれば足りるので、全体（英語版は数GB級）は不要：
    ```
    curl -sL https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.en.vec | head -n 200001 > wiki.en.vec
    ```
  - 注意：MUSE の事前アライン済み `wiki.multi.*.vec` ではなく、非アラインの `wiki.{lang}.vec` を使う
- 辞書：MUSE（https://github.com/facebookresearch/MUSE ）の `data/get_evaluation.sh` で `crosslingual/dictionaries/` に取得
- 配置先：`data/raw/MUSE/wiki.{lang}.vec`、`data/raw/MUSE/crosslingual/dictionaries/`

### Dinu タスク（Table 2）

- VecMap（https://github.com/artetxem/vecmap ）の `get_data.sh` で取得（スクリプトの存在は確認済み）
- 上記の `home_dir` 問題のため、パスの修正が必要

## 手順

### Step 1：word embedding の取得

- [ ] `wiki.{en,es,fr,de,it,ru}.vec` の URL が生きているか確認
- [ ] 上位 20 万語だけ取得（上の `head` 方式）
- [ ] MUSE 辞書の取得
- [ ] 上位 K 語と辞書の突き合わせ（カバレッジ確認）

### Step 2：原論文コードで動かす

- [ ] 上記の既知の問題を fix（最低限：評価辞書の fold、必要なら Dinu のパス）
- [ ] K=2000 で EN-ES を回し、論文の傾向（P@1 が 8 割前後）に近い値が出るか確認
- [ ] 計算時間の見積もり：1 反復あたりの時間を K=2000, 5000, 10000 で測って外挿
  - 支配項は C_s Γ C_tᵀ の密行列積で K³ のはず
  - λ を小さくすると Sinkhorn の内部反復が増えるため、単純な K³ より悪化しうる
  - メモリは K² で増えるので、20000 では先にメモリが詰まる可能性あり
- [ ] 可能そうなら K=20000 で実行
- 古いコードなので、そのままでは動かない可能性大。fix で動くかは場合による

### Step 3：GWTune で実行・比較

- Step 2 がダメなら GWTune で実行。Step 2 が動いた場合も、結果と計算時間を比較する
- 理想的には基本 GWTune に移行したい
- 公平な比較のために揃える条件：
  - [ ] コスト行列：コサイン距離、mean 正規化
  - [ ] p, q：一様分布
  - [ ] 初期値：otalign は T = pqᵀ から開始。GWTune のランダム初期化・多点探索とは異なるので、差が出たら初期化の影響を切り分ける
  - [ ] ε の選び方：論文は「教師なし目的関数のみでモデル選択」の立場。GWTune でも GW 目的値で ε を選ぶ設定にする
  - [ ] 評価：P@1 を Γ の argmax で取るか CSLS 込みで取るかを揃える。MUSE 辞書による P@1 評価関数を GWTune 側に移植
- 移行の方針案：otalign の `compute_distances` 相当の前処理と評価関数だけ切り出して GWTune に持っていく

### Step 4：基礎解析・可視化（Step 2・3 が全然ダメでもやる）

Step 1 さえできれば、Step 2・3 と独立に進められる。閾値の決め方にも直接効くので、並行して早めに着手するのがよさそう。

- [ ] どんな word が入っているかの確認（上位 K 語の中身）
- [ ] 全体的な距離構造の可視化
- [ ] いくつかの意味クラスターに分かれているかの確認
- [ ] 各言語で距離の分布を出す
- [ ] 言語間で supervised にマッチさせた語同士で、距離のずれが local vs global で変わるかを見る
  - 具体案：辞書でペアになった語 (i, i′) と (k, k′) について、|d_s(i,k) − d_t(i′,k′)| を、d_s(i,k) の近傍順位（i から見て k が何番目に近いか）の関数としてプロット
  - local で小さく global で大きくなれば、閾値 GW の動機づけになる
  - 注意：MUSE 辞書は 1 対多の対応を含むので、ペアの選び方（先頭の訳語を採る、など）を先に決める

## 距離行列をいじる際の注意（今後）

- square loss の GW は内部で C² や C·Γ·C′ を計算するため、文字通り `+inf` を入れると inf−inf で NaN になる
- 候補（2026-09-14 の議論より）：
  - 大きな有限値で置き換える
  - tan や sigmoid⁻¹ で単調変換する（ishimine）
  - 損失側でペアをマスクする
  - unbalanced GW（ishimine）
- 閾値処理を正規化の前後どちらに入れるかで λ の実効スケールが変わる
- K が小さいと上位語しか入らないので、「近傍」の密度も K に依存する。閾値の効き方が K で変わる可能性あり
