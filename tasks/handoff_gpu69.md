# 引き継ぎ：69 番 GPU サーバーでの GW 高速化実験

作成：2026-10-22（58 番 ubuntu-server-58 / 192.168.201.58 のセッションから）
対象リポジトリ：`git@github.com:yu-togashi/togashi-yokoi-language-translation.git`（private）

このファイルを読んだら、まずリポジトリの `CLAUDE.md`（毎回自動で読み込まれる。用語、評価方法、パラメータの換算の注意点、暫定の標準設定が書いてある）と `tasks/lessons.md` を確認すること。経緯は `logs/gwtune_comparison.md` と `logs/replication_summary.md`。

---

## 0. 目的

CPU（58 番、64 スレッド）で 53 分かかっている暫定の標準設定の GW を、GPU で速くできるかを確かめる。

**暫定の標準設定**（`CLAUDE.md` に記載、CPU で検証済み）
- EN→ES、K=20000（各言語の頻度上位 2 万語）、ε=2e-4（＝ otalign の λ=1e-4）、初期値 pqᵀ
- `localgw.gwtune_ext.GWTuneSolver`、設定 B：Sinkhorn のウォームスタートあり、内側の判定 stopThr=3.16e-5
- 外側の判定 tol=1e-5（121 回で停止）
- CPU（58 番）での結果：GW の求解 53 分、1 回あたり約 24 秒（勾配 19.5 秒＋Sinkhorn 4.4 秒）、最大メモリ 45 GB
- 精度（P@1、GW 語彙内・辞書 0-5000）：Γ の argmax 67.69 / 直交写像 80.97 / 直交写像＋CSLS 84.19。候補 20 万語・辞書 5000-6500：直交写像 76.73 / ＋CSLS 80.20

## 1. 環境構築

### 1.1 GPU の確認
```bash
nvidia-smi
```
- GPU の型番、メモリ、ドライバが対応する CUDA のバージョンを記録する。
- **RTX PRO 6000 Blackwell の場合**：Blackwell（sm_120）は torch 2.7 以上と CUDA 12.8 以上の wheel が必要。今の pyproject の torch 2.4.1 では動かない（2.2 を参照）。
- 他の人が GPU を使っていないかも確認する（共有サーバーの場合）。

### 1.2 コードの取得
69 番から GitHub に SSH で入れるか確認する（`ssh -T git@github.com`）。
- 入れる場合：
  ```bash
  git clone git@github.com:yu-togashi/togashi-yokoi-language-translation.git
  cd togashi-yokoi-language-translation
  git submodule update --init   # GWTune（oizumi-lab/GWTune、private の可能性あり）
  ```
- 入れない場合：58 番から取得する（58 番への SSH が通る前提）。
  ```bash
  git clone togashi@192.168.201.58:togashi-yokoi-language-translation
  rsync -a togashi@192.168.201.58:togashi-yokoi-language-translation/GWTune/ togashi-yokoi-language-translation/GWTune/
  ```

`external/otalign/` は今回の実験には不要（必要なら `external/setup_otalign.sh`）。

### 1.3 データ（約 3 GB、git 管理外）
58 番からコピーするのが一番早い。
```bash
rsync -a togashi@192.168.201.58:togashi-yokoi-language-translation/data/raw/ data/raw/
```
58 番に入れない場合は、`logs/data_acquisition.md` の手順で取得し直す（fastText の `wiki.{en,es}.vec` の先頭 200,001 行と MUSE 辞書）。今回の実験に必要なのは `en` と `es` だけ。

### 1.4 Python 環境
- Python 3.10.11（pyenv）＋ poetry。`pip install` を直接使わない（CLAUDE.md のルール）。
- **torch の指定を GPU 用に変える必要がある。** 今の `pyproject.toml` は CPU 版の torch を明示的に指定している：
  ```toml
  torch = {version = "2.4.1", source = "pytorch-cpu"}
  [[tool.poetry.source]]
  name = "pytorch-cpu"
  url = "https://download.pytorch.org/whl/cpu"
  ```
  69 番では、source を GPU とドライバに合う CUDA 版（例：`https://download.pytorch.org/whl/cu121`、Blackwell なら `cu128` ＋ torch 2.7 以上）に変えてから `poetry lock --no-update && poetry install` する。
  - **この変更（pyproject.toml と poetry.lock）は main にコミットしない**（58 番の CPU 環境が壊れる）。69 番のローカルの変更のままにするか、`gpu` ブランチにする。どちらにするかはユーザーに確認する。
  - torch のバージョンを上げる場合、POT 0.9.4 と numpy 1.26 はそのままで動くはずだが、`poetry run pytest -q` で確認する。
- 確認：
  ```bash
  poetry run python -c "import torch, ot; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0), ot.__version__)"
  poetry run pytest -q
  ```

## 2. 実行スクリプトの GPU 対応（コードの変更が必要）

`code/experiments/run_gwtune.py` は今 CPU 専用：`GWTuneSolver(..., device="cpu", to_types=args.backend, data_type="double", ...)` と固定されている。次を足す。
- `--device {cpu,cuda}` と `--dtype {double,float}` の引数（GWTune の `Backend` は device="cuda" と data_type="float"/"double" に対応している）。
- **GPU では計算が非同期なので、`code/localgw/gwtune_ext.py` の時間の計測の前後で `torch.cuda.synchronize()` を呼ぶ**（呼ばないと勾配と Sinkhorn の時間が正しく測れない）。CPU のときは何もしないようにする。
- 結果の Γ は `.cpu().numpy()` で取り出して評価に渡す（今のスクリプトは既に対応済み）。
- ファイル名に device と dtype を入れる（今は `_numpy_t64` のように backend とスレッド数だけ）。
- 変更したら `poetry run pytest -q` を通し、コミットする（この変更は CPU 側に影響しないので main で良い）。

## 3. 実験の手順

すべて EN→ES、ε=2e-4、設定 B（`--warmstart --sinkhorn-stopthr 3.16e-5`）、初期値 pqᵀ。

### 3.1 動作確認：K=5000、torch・cuda・倍精度
CPU での結果と同じ精度が出るかを見る。K=5000 は初期値 pqᵀ から安定して良い解に行くことを確認済み（K=2000 は不安定なので確認には使わない）。
```bash
poetry run python code/experiments/run_gwtune.py en es 5000 2e-4 --max-iter 1000 --tol 1e-8 \
  --sinkhorn-stopthr 3.16e-5 --warmstart --backend torch --device cuda --dtype double --verbose
```
CPU（numpy、16 スレッド）での結果（`logs/gwtune_comparison.md`）：501 回で停止、GW 875 秒、P@1（GW 語彙内・辞書 0-5000）Γ の argmax 68.00 / 直交写像 80.74 / ＋CSLS 82.29、gw_dist 0.00564。

### 3.2 本番：K=20000 の暫定の標準設定、倍精度
```bash
poetry run python code/experiments/run_gwtune.py en es 20000 2e-4 --max-iter 1000 --tol 1e-5 \
  --sinkhorn-stopthr 3.16e-5 --warmstart --backend torch --device cuda --dtype double --verbose
```
CPU の 53 分（1 回あたり 24 秒）と、時間・精度（0 節の値）を比べる。メモリは CPU で 45 GB だったので、GPU メモリに収まるかを先に見積もる（K×K の倍精度の行列 1 枚が 3.2 GB）。

### 3.3 単精度
3.2 を `--dtype float` で。
- 注意：ε=2e-4 では Sinkhorn の exp(−M/ε) が単精度でアンダーフローしやすい（単精度で表せるのは約 exp(−87) まで、倍精度は約 exp(−745) まで）。結果が `valid False` になったり gw_dist が NaN になったりしたら失敗。
- 失敗した場合は `--sinkhorn sinkhorn_log` を試す（log 領域の Sinkhorn。CPU では遅すぎて使えなかったが、GPU なら現実的な可能性がある）。

### 3.4 記録
- 結果は `data/processed/gwtune/<実行名>/result.json`（時間、反復ごとの時間、内側の反復回数、精度）。
- `logs/gwtune_gpu.md` に、GPU の型番、torch/CUDA のバージョン、各実行の「外側の反復回数、GW の求解時間、1 回あたり（勾配＋Sinkhorn）、最大 GPU メモリ、gw_dist、P@1」の表を書き、CPU の値と並べる。
- `tasks/todo.md` に結果を 1〜2 行で追記。

## 4. 注意（CLAUDE.md / lessons より抜粋）
- 指示された範囲だけを実行する。追加でやると良さそうなことは、実行せずに最後に 1 行で提案する。
- 解析や図はシンプルなものから。
- 長時間の実行は、所要時間の見積もりを伝えてから始める。
- GWTune の ε ＝ 2 × otalign の λ。Sinkhorn の stopThr は 3.16e-5（otalign の判定 ‖誤差‖² < 1e-9 に相当）。
- 大きなデータ（`.vec`、Γ の `.npy`）はコミットしない（`data/` は git 管理外）。
