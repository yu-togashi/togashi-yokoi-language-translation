# Autonomous Research Orchestrator

Two parts:
1. **PART 1 — COMMON FRAMEWORK** — reusable across projects. Do NOT edit.
2. **PART 2 — PROJECT-SPECIFIC** — filled in per project.

---

# PART 1: COMMON FRAMEWORK (DO NOT EDIT)

## Workflow Orchestration

### 1. STATUS-Driven Dispatch
- Orchestrator decides the next agent from `STATUS.md`
- Do not wait for the PI; dispatch autonomously
- Hard cap: 30 dispatches per `/continue` (tracked in `HEARTBEAT.md`; projects can override in Part 2)

### 2. Subagent Strategy
- One task per subagent; keep main context clean
- Six agents in `.claude/agents/` own their own rules
- Writer runs on `opus`, `effort: max`; others on `sonnet` (frontmatter, not here)

### 3. Verification Before Done
- Never mark a stage complete without the output file on disk
- After every agent: verify `STATUS.md` row updated, `PROGRESS.md` appended, log in `logs/`
- The `post-agent-commit.sh` hook auto-commits to `agent/auto/<date>`; `main` only via `/checkpoint`
- **Defensive commit:** after every agent return, the orchestrator also runs `./.claude/hooks/post-agent-commit.sh` manually. The hook is idempotent (clean tree → no commit) and covers the case where `SubagentStop` did not fire for a background subagent

### 4. Transparency and Decisions
- Uncertainties → `DECISIONS.md` (agents append, PI resolves)
- Errors → `STATUS.md` + `DECISIONS.md` entry
- Long computations (~10 min+): warn with a wall-clock estimate and the cost driver, then proceed. Do not pause.

### 5. Meeting Feedback Loop
- PI drops transcripts in `meetings/raw/`; unprocessed files block `/continue`
- Invoke `/meeting` to absorb; accumulated guidance in `meetings/feedback.md`

### 6. Autonomous Dispatch
- Fix failing tests, resolve blockers, keep the pipeline moving
- Hand-holding is the exception, not the default

## Task Management

1. Read `STATUS.md`, `GOAL.md`, `DECISIONS.md`, `meetings/feedback.md`
2. Check guards (pending decisions, unprocessed transcripts, dispatch cap)
3. Pick next pending agent from the pipeline in Part 2
4. Dispatch via the Agent tool; increment `HEARTBEAT.md` counter
5. After return: update `STATUS.md`, prepend `PROGRESS.md`, write `logs/<descriptive_name>.md`
6. Loop or stop per guard conditions

## Core Principles

- **Simplicity first** — fewest files, shortest bullets, one source of truth
- **No laziness** — root causes, not workarounds; no temporary fixes
- **Minimal impact** — changes touch only what is necessary
- **Pinned env** — `pyenv` + `poetry`; never system Python; run via `poetry run python ...`
- **Safe deletes** — no `rm`, ever. Use `/trash` or the `trash-file` skill
- **Descriptive naming** — `logs/literature_survey.md`, not `logs/phase1.md`
- **Fixed seeds** — every experiment pins `numpy.random.default_rng(seed)`
- **Version everything** — `paper/versions/`, `review/review_vNN.md`, never overwrite

## Where the rules actually live

- **Agent specs** — `.claude/agents/<name>.md` (surveyor, theorist, coder, analyst, writer, reviewer)
- **Slash commands** — `.claude/commands/<name>.md` (`/continue`, `/status`, `/resume`, `/meeting`, `/checkpoint`, `/trash`)
- **Hooks** — `.claude/hooks/*.sh` (`post-agent-commit.sh`, `stop-progress-check.sh`)
- **Skills** — `.claude/skills/<name>/SKILL.md` (`orchestrate`, `incorporate-meeting`, `trash-file`)
- **Folder/file purposes** — `README.md` "File cheat sheet"
- **LaTeX build** — `compile_paper.sh` inline comments

---

# PART 2: PROJECT-SPECIFIC (fill this in for your project)

## The problem

GWOT による教師なし単語対訳抽出で、言語内の距離行列を閾値処理などで local な構造だけにしたときに、アラインメントがどう変わるかを調べる（local-GW）。
まず Alvarez-Melis & Jaakkola (EMNLP 2018, arXiv:1809.00013) を公式実装 otalign と GWTune の両方で再現し、そのうえで距離行列を変えた変種を試す。
詳細な計画・既知のバグ・データ取得方法は `documents/local_gw_plan.md`、作業リストは `tasks/todo.md`。
当面の成果物は 2026-10-19 の MTG 用の実験結果で、論文化は後で判断する。

## Pipeline stages

```
DATA (Step 1)
  └─ coder: wiki.{lang}.vec 上位20万語 + MUSE 辞書を data/raw/MUSE/ に取得、カバレッジ確認
REPRODUCTION (parallel, after DATA)
  ├─ coder: otalign を external/ に clone、最小限の fix、K=2000 EN-ES 実行 (Step 2)
  ├─ analyst: K=2000/5000/10000 の時間・メモリ計測 → K=20000 の外挿 (Step 2)
  └─ analyst: 基礎解析・可視化 — 語彙、距離分布、クラスター、local vs global のずれ (Step 4)
GWTUNE (Step 3)
  ├─ coder: 距離前処理 + MUSE P@1 評価を code/src/ に切り出し、GWTune から呼べるようにする
  └─ analyst: GWTune vs otalign の P@1・計算時間の比較
LOCAL-GW
  ├─ coder: 距離行列の閾値処理の変種（大きな有限値 / 単調変換 / マスク）
  └─ analyst: 閾値ごとの P@1 スイープ
MTG REPORT
  └─ analyst: analysis/ に MTG 用のまとめ（図＋表）
```

PAPER / REVIEW 段階は当面使わない（surveyor・theorist・writer・reviewer は必要になったら dispatch）。

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
