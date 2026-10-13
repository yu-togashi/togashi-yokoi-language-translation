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

> **PI: fill this block before running the orchestrator.** Keep it short — rules
> live in `.claude/agents/*.md` and `compile_paper.sh`. Only put project-unique
> content here: the problem statement, the pipeline stages, and any
> domain-specific conventions that do not belong in any general-purpose file.

## The problem

(One paragraph: research question, starting material in `documents/`, expected
final artifact. Example: "Reproduce and extend Sekizawa & Oizumi 2026 on
Koopman-based causality detection. Starting point: `documents/main.pdf`.")

## Pipeline stages

```
FOUNDATION (parallel)
  ├─ surveyor: literature review
  ├─ theorist: verify derivations from source paper
  └─ coder: implement method + baselines
VALIDATION
  ├─ coder: simulation harness
  └─ analyst: reproduce reference examples
BENCHMARKING
  ├─ analyst: systematic benchmarks vs baselines
  ├─ analyst: parameter sensitivity sweeps
  └─ surveyor: find open datasets
REAL DATA
  └─ analyst: apply to one selected dataset
PAPER (parallel with REAL DATA)
  ├─ writer: draft intro/methods/results/discussion
  └─ surveyor: finalize references.bib
REVIEW-REVISE (iterative)
  └─ reviewer → writer/analyst/coder → compile → reviewer → …
```

## Domain-specific conventions

(Project-specific naming, score conventions, baseline fairness rules, honesty
clauses — only things that do NOT belong in any general-purpose agent file.
Delete this heading if none apply.)
