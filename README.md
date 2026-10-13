# togashi-yokoi-language-translation

GWOT による教師なし単語対訳抽出で、言語内の距離行列を local な構造だけに制限する（local-GW）とどうなるかを調べるプロジェクト（togashi, yokoi）。
まず Alvarez-Melis & Jaakkola (EMNLP 2018) を otalign と GWTune で再現する。

- 目標：[`GOAL.md`](GOAL.md)
- 計画メモ：[`documents/local_gw_plan.md`](documents/local_gw_plan.md)
- 作業リスト：[`tasks/todo.md`](tasks/todo.md)

## ディレクトリ

| パス | 中身 |
|---|---|
| `code/` | `localgw/` ライブラリ、`experiments/` 実行スクリプト、`tests/` テスト |
| `analysis/` | 図・表（`code/experiments/` から生成） |
| `documents/` | 入力資料（計画メモ、論文 PDF） |
| `data/` | データ（git 管理外） |
| `logs/` | 作業記録 |
| `meetings/` | MTG の議事メモ（`raw/`）と要約（`summaries/`） |
| `tasks/` | `todo.md` 作業リスト、`lessons.md` |
| `paper/`, `survey/`, `theory/`, `review/` | 論文化用（当面は使わない） |

## セットアップ

```bash
poetry install
```

[oizumi-lab/lab-research-template](https://github.com/oizumi-lab/lab-research-template) から作成（自動エージェント機能は外している）。
