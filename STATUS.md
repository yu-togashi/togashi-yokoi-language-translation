# Pipeline Status — togashi-yokoi-language-translation

**Last updated:** 2026-10-14
**Current stage:** `data`
**Next agent:** coder — Step 1（埋め込み・辞書の取得）

## Pipeline state

| Stage | Agent | Status | Output | Notes |
|-------|-------|--------|--------|-------|
| 1. Data — embeddings + MUSE dictionaries | coder | pending | data/raw/MUSE/, logs/data_acquisition.md | Step 1 |
| 2. Reproduction — otalign fix + K=2000 EN-ES | coder | pending | external/otalign/, logs/otalign_fixes.md | Step 2 |
| 3. Reproduction — runtime/memory scaling | analyst | pending | analysis/tables/ | Step 2, K=2k/5k/10k → 20k |
| 4. Basic analysis — distance structure | analyst | pending | analysis/figures/ | Step 4, Step 2・3 と並行 |
| 5. GWTune — port preprocessing + P@1 eval | coder | pending | code/src/ | Step 3 |
| 6. GWTune — compare with otalign | analyst | pending | analysis/ | Step 3 |
| 7. Local-GW — thresholded distance variants | coder → analyst | pending | code/src/, analysis/ | 閾値スイープ |
| 8. MTG report (2026-10-19) | analyst | pending | analysis/ | |

## Blockers

(none)

## How to advance

`tasks/todo.md` のチェックリストに沿って進める。`continue` で orchestrator がこの表の最初の pending 行を dispatch する。

(Live dispatch state lives in `HEARTBEAT.md` — do not duplicate it here.)
