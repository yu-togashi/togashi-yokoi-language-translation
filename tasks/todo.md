# TODO — local-GW 単語アラインメント

詳細は `documents/local_gw_plan.md`。締切：**2026-10-19 MTG**（togashi, yokoi）。
MTG までの最低ライン：K=2000 EN-ES の P@1（otalign か GWTune）＋ Step 4 の図数枚。

## Step 0：環境
- [x] `poetry install`（Python 3.10.11、POT 0.9.4、torch 2.4.1 CPU 版など）
- [x] GWTune を submodule として追加（他プロジェクトと同様に sys.path で `from GWTune.src... import`）
- [x] otalign を `external/otalign/` に clone（git 管理外。`external/setup_otalign.sh` でコミット固定＋`external/otalign.patch` を適用）
- [x] 自分たちのパッケージ名を `localgw`（`code/localgw/`）に変更（otalign もトップレベル `src` を使うため衝突回避）
- [x] GitHub に個人の private repo を作って push（yu-togashi/togashi-yokoi-language-translation）

## Step 1：word embedding・辞書の取得
- [x] `https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.{lang}.vec` が生きているか確認（en, es, fr, de, it, ru）
- [x] 上位 20 万語だけ取得（`curl ... | head -n 200001`）→ `data/raw/MUSE/wiki.{lang}.vec`
  - 事前アライン済みの `wiki.multi.*.vec` ではなく、非アラインの `wiki.{lang}.vec` を使う
- [x] MUSE 辞書を取得 → `data/raw/MUSE/crosslingual/dictionaries/`（en↔xx の辞書を直接取得）
- [x] 上位 K 語（K=2000/5000/10000/20000）と辞書（`.0-5000` / `.5000-6500`）の突き合わせ表を作る → `analysis/tables/dictionary_coverage.md`

## Step 2：原論文コード（otalign）で動かす
- [ ] 既知の問題を fix（`logs/otalign_fixes.md` に記録）
  - [x] 評価辞書の fold：`load_vectors()` の `dict_fold = 'train'` ハードコード → `--dict_fold` で引数化（既定は train ＝ 辞書 0-5000 のまま）
  - [ ] （必要なら）Dinu タスクの `args.home_dir` 未定義
  - [ ] （任意）`--no_entropy` が `solve()` で効かない問題
  - GPU パスは触らない（CPU 前提）
- [x] 現行 POT（0.9.4）で全体が動くか確認。重心写像の 1 か所だけ修正（`logs/otalign_fixes.md`）
- [x] K=2000 で EN-ES を実行（λ=1e-4：Γ argmax 62.4%、proj+CSLS 74.4%。λ=5e-5, 1e-5 は数値破綻）
- [x] 1 反復あたり時間とピークメモリを K=2000, 5000, 10000 で計測 → K=20000 を外挿（`logs/otalign_scaling.md`：maxiter=100 で約 2 時間、メモリ約 37 GB）
- [x] K=20000 で実行（1 時間 33 分、45 GB。Γ argmax 67.6%、proj 80.9%、proj+CSLS 84.1% vs 論文 78.3%）

## Step 3：GWTune で実行・比較
- [ ] otalign の `compute_distances` 相当（コサイン距離＋mean 正規化）を `code/localgw/` に切り出す
- [ ] MUSE 辞書による P@1 評価関数を `code/localgw/` に移植（argmax / CSLS の両方）
- [ ] 条件をそろえる：コサイン距離、mean 正規化、一様な p,q、ε は GW 目的値で選ぶ
- [ ] GWTune で EN-ES（K=2000）を実行
- [ ] otalign と P@1・計算時間を比較。差が出たら初期化（T=pqᵀ vs ランダム・多点）の影響を切り分ける

## Step 4：基礎解析・可視化（Step 1 が終われば Step 2・3 と並行で進められる）
- [x] 上位 K 語の中身の確認（k-means のクラスタの中身で確認 → `logs/step4_structure.md`。品詞などの割合の集計はまだ）
- [x] 全体的な距離構造の可視化（PCA ＝ 古典 MDS、クラスタ順に並べた距離行列。`analysis/figures/step4_*`）
- [x] 意味クラスターに分かれているかの確認（k-means k=8。明確な分離はない：シルエット 0.02〜0.03、クラスタ内距離はクラスタ間より約 10% 小さいだけ）
- [ ] 各言語の距離分布（ヒストグラム）
- [ ] 辞書ペアでの local vs global のずれ
  - [ ] 1 対多の対応の扱いを先に決める（例：先頭の訳語を採る）
  - [ ] |d_s(i,k) − d_t(i′,k′)| を、i から見た k の近傍順位の関数としてプロット
  - local で小さく global で大きければ閾値 GW の動機づけになる

## Step 5：local-GW（Step 2〜4 の後）
- [ ] **まず一番シンプルな形で閾値を何通りか試す**：距離 d > τ を大きな有限値（または τ）に置き換え、τ を数通り（例：距離の分布の 5% / 25% / 50% / 75% 点）にして GW を解き、P@1 を比べる（K=5000 程度から）
  - 背景：距離の分布は平均付近にピークがあり、小さい側に長く裾を引く形で、自然な切れ目がない（`logs/step4_structure.md`）。τ の選び方で残る組の割合が大きく変わる
  - 結果を見てから次を検討：単語ごとの k 近傍で切る、切った部分を測地距離で埋める、滑らかな変換（exp(−d²/σ²) など）
- [ ] 閾値処理の方式を実装：大きな有限値で置換 / 単調変換（tan, sigmoid⁻¹）/ 損失側でマスク
- [ ] 閾値を正規化の前後どちらに入れるかを決めて記録
- [ ] 閾値（または近傍数 k）をスイープして P@1 を比較。K への依存も確認
- [ ] （後で）unbalanced GW との関係を検討

## GPU 高速化（69 番、2026-10-22。手順は引き継ぎ書 `handoff_gpu69.md`）
- [x] 環境：pyenv 3.10.11 ＋ poetry 2.5.1、torch 2.7.1+cu128（RTX PRO 6000 Blackwell ×4）。pyproject.toml と poetry.lock の変更は `gpu` ブランチ
- [x] `run_gwtune.py` に `--device {cpu,cuda}` と `--dtype {double,float}` を足す。実行名に device と dtype を入れる（cpu・double のときは今までと同じ名前）。最大 GPU メモリを result.json に記録
- [x] `gwtune_ext.py` の時間の計測の前後で `torch.cuda.synchronize()`（CPU では何もしない）
- [x] pytest を通し、GPU で小さい K の動作確認をしてから main にコミット → `gpu` ブランチに取り込む
- [x] 実験 3.1：K=5000、単精度＋log 領域の Sinkhorn（CPU の値と精度を比べる）
- [x] 実験 3.2：K=20000 の暫定の標準設定、単精度＋log 領域の Sinkhorn（CPU の 53 分と比べる）
- [x] 実験 3.3：K=20000 の倍精度（普通の Sinkhorn と log 領域）の 1 回あたりの時間（`--max-iter 10 --no-eval`）
- [x] 記録：`logs/gwtune_gpu.md` に表、Review に 1〜2 行
- [ ] 単精度での外側の止め方を決める（‖ΔΓ‖ が K=20000 で 7.2e-5、K=5000 で 2.5e-5 で下げ止まり、tol 1e-5 に届かない）

## MTG（10/19）準備
- [ ] 結果のまとめ（P@1 の表、計算時間、Step 4 の図）を `analysis/` に置く

---

## Review
（各ステップ完了時に結果と気づきをここに追記）

### Step 0–1（2026-10-14）
- 6言語の埋め込み（各 20 万語）と en↔xx 辞書を取得。詳細は `logs/data_acquisition.md`
- **重要**：MUSE の辞書 5000-6500 の英語側の単語は頻度順位 5474〜7136。K ≤ 5000 では辞書 5000-6500 の語が上位 K に 1 語も入らない（K=10000 でも en-es で 66%）
  - → 辞書 5000-6500 の P@1 は、Procrustes などで 20 万語に写像を広げた後でしか測れない。上位 K の Γ の argmax だけで測れるのは辞書 0-5000
  - otalign が `dict_fold = 'train'` を固定しているのは、これが理由の可能性がある
- 辞書は 1 対多が多い（en-es の辞書 5000-6500 で平均 1.98 訳、56% が複数訳）
- en-ru は K=20000 でも辞書 5000-6500 のカバレッジが 57% で、最も難しい

### Step 2 途中（2026-10-14）
- otalign は 2 か所の修正で動作。論文の評価方法の調査は `logs/evaluation_protocol.md`
- EN→ES, λ=1e-4, 辞書 0-5000・GW 語彙内の P@1：Γ argmax 62.4 / 68.0 / 68.8（K=2000/5000/10000）、proj+CSLS 74.4 / 82.3 / 84.7。論文 Table 1 の G-W は 78.3（λ=1e-4）/ 81.7（λ=1e-5）
- 時間は ≈ K^2.3 でスケール（Sinkhorn 内ループ律速、スレッドを増やしてもあまり速くならない）。K=20000 は maxiter=100 で約 2 時間、メモリ約 37 GB の見込み
- K=20000 実行結果：論文の 78.3（λ=1e-4）に 6 通りのどれも一致しない。Γ argmax は約 11 pt 低く、直交写像は +2.6（NN）/ +5.8（CSLS）pt 高い。詳細は `logs/otalign_scaling.md`
- 20 万語での評価（K=20000 の直交写像 P、MUSE 方式）：辞書 0-5000：NN 78.1 / CSLS 81.2、辞書 5000-6500：NN 76.7 / CSLS 80.3。論文の 78.3 にほぼ一致 → 再現は成立とみなす
- GW 語彙内の評価を full 辞書に変更（0-5000 に絞る必要はない）。K=20000：coupling 62.9 / proj 76.7 / proj+CSLS 80.3（13,032 語）。頻度の低い語ほど P@1 が下がる（上位 5000 語 67.5 → 1 万〜2 万位 56.3）
- 論文は MUSE 標準（候補 20 万語・辞書 5000-6500）で評価した可能性が高い。Γ の argmax による P@1 は低めに出る（一様な周辺分布の容量の制約で多対一の正解を満たせないのが一因。多対一の語で 53.6 vs 直交写像 70.2、一対一の語でも 75.9 vs 85.8）
- GW 語彙（各言語の上位 K 語を独立に取る）は一対一でない：K=20000 で英語の 65% しか相手側に訳語がない、スペイン語の 32% は多対一（`analysis/tables/vocab_bijectivity.md`）

## 保留中の疑問
- [ ] 一対一に揃えようがない語集合で一様な質量の GW を解いているのに、なぜ精度が高いのか（`logs/replication_summary.md`「保留中の疑問」）
  - 候補：一対一が保証された oracle 設定（辞書から一対一ペアを N 組）との比較、unbalanced / partial / semi-relaxed GW
- **Step 3 の結論**：GWTune＋ウォームスタート＋緩い Sinkhorn の判定（設定 B）で、otalign と同じ精度・同じ 1 反復あたりの時間（K=5000〜20000）。そのままの GWTune は 1 反復 4〜5 倍遅い。ε = 2λ。K=2000 は不安定
- 外側の tol を緩めても精度は変わらない（K=20000：tol 1e-5 で 121 回・53 分、精度は tol 1e-8 と ±0.15 pt 以内）。tol は絶対値なので K を変えたら再確認
- **GPU（69 番、2026-10-22）**：単精度＋log 領域の Sinkhorn で精度は CPU と ±0.3 pt 以内、K=20000 の 1 回あたり 24 秒 → 0.98 秒。ただし単精度では ‖ΔΓ‖ が 7.2e-5 で下げ止まり tol 1e-5 に届かず 1000 回（16 分）まで回る。倍精度は勾配が 21 秒/回で CPU と同じ（`logs/gwtune_gpu.md`）
