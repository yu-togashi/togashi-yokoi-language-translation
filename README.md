# togashi-yokoi-language-translation

GWOT による教師なし単語対訳抽出で、言語内の距離行列を local な構造だけに制限する（local-GW）とどうなるかを調べるプロジェクト（togashi, yokoi）。
まず Alvarez-Melis & Jaakkola (EMNLP 2018) を otalign と GWTune で再現する。

- 目標：[`GOAL.md`](GOAL.md)
- 計画メモ：[`documents/local_gw_plan.md`](documents/local_gw_plan.md)
- 作業リスト：[`tasks/todo.md`](tasks/todo.md)

Bootstrapped from `lab-research-template`.

> **New here and wondering how the template works?**
> Read the beginner guide in the template repo:
> [`lab-research-template/docs/README.md`](https://github.com/oizumi-lab/lab-research-template/blob/main/docs/README.md).

---

# lab-research-template (reference sheet)

# lab-research-template

A semi-autonomous multi-agent research project scaffold for the Oizumi lab.
Designed so a freshman with zero Claude Code experience can go from "empty
laptop" to "first agent dispatched" in about 20 minutes.

> **New here? Start with the beginner's guide: [`docs/README.md`](docs/README.md).**
> It is a 7-chapter walkthrough — mental model, full folder/file anatomy,
> setup, first run, daily workflow, the six agents, and troubleshooting.
> This README is the reference sheet; `docs/` is the narrative.

**Companion repo:** [`lab-claude-dotfiles`](../lab-claude-dotfiles) — install
that once per laptop BEFORE bootstrapping a project from this template.

---

## Who is this for?

- Lab members (incl. freshmen) who want to run a theory → code → experiments
  → paper pipeline with minimal manual dispatch.
- PIs who want to monitor and steer projects by pulling a git repo and
  dropping meeting transcripts into `meetings/raw/`.

## What it gives you

- **Opinionated project structure** — `GOAL.md`, `STATUS.md`, `PROGRESS.md`,
  `DECISIONS.md`, `HEARTBEAT.md`, `logs/`, `code/`, `paper/`, `analysis/`,
  `meetings/`, `.trash/`.
- **Six specialized agents** — `surveyor`, `theorist`, `coder`, `analyst`,
  `writer`, `reviewer`. Writer runs on Claude Opus (`effort: max`); others
  on Sonnet.
- **Six slash commands** — `/continue`, `/status`, `/resume`, `/meeting`,
  `/checkpoint`, `/trash`. `/resume` generates a session-handoff
  `RESUME.md` so a fresh Claude Code session can pick the project back
  up with a single read. See
  [`docs/05-daily-workflow.md`](docs/05-daily-workflow.md) §11 for the
  full command catalog and a walked-through example of how commands
  are implemented.
- **Three project skills** — `orchestrate`, `incorporate-meeting`, `trash-file`.
- **Two project hooks** — `post-agent-commit.sh` (auto-commits to
  `agent/auto/<date>`, never `main`), `stop-progress-check.sh` (ensures
  `PROGRESS.md` is current).
- **Trash-box safety** — agents never call `rm`; files move to
  `.trash/YYYY-MM-DD/` and are logged in `logs/trash.md`.
- **Meeting transcript workflow** — drop a raw Otter/Zoom/text transcript in
  `meetings/raw/`, run `/meeting`, and Claude produces a structured summary,
  updates decisions, and re-prioritizes the pipeline.
- **Compiled LaTeX paper pipeline** — `compile_paper.sh` builds
  `paper/main.pdf` and moves temp artifacts into `.trash/latex-build/`.

---

## One-time machine setup

Before using this template, install the lab dotfiles once per laptop:

```bash
git clone git@github.com:<lab>/lab-claude-dotfiles.git \
  ~/Documents/Claude/Projects/lab-claude-dotfiles
cd ~/Documents/Claude/Projects/lab-claude-dotfiles
./setup.sh
# (recommended) ./setup.sh --managed   # requires sudo; adds enterprise-managed layer
```

Verify:
```bash
ls ~/.claude/rules                          # should list 5 rule files
~/.claude/hooks/pre-destructive.sh < /dev/null ; echo exit=$?   # should print exit=0
```

---

## Start a new research project

```bash
# 1. Clone this template next to your other Claude projects
git clone git@github.com:<lab>/lab-research-template.git \
  ~/Documents/Claude/Projects/lab-research-template

# 2. Bootstrap a new project
cd ~/Documents/Claude/Projects/lab-research-template
./bootstrap.sh my_first_project --variant theory-paper

# 3. Move in
cd ../my_first_project

# 4. Fill in the project-specific parts
#    - Edit GOAL.md (research question, deliverables, success criteria)
#    - Edit CLAUDE.md Part 2 (pipeline stages for your problem)

# 5. Put any starting materials (a paper PDF to reproduce, etc.) in documents/

# 6. Create a PRIVATE GitHub repo and push
git remote add origin git@github.com:<lab>/my_first_project.git
git push -u origin main

# 7. Launch Claude Code and start the orchestrator
claude
> continue
```

That's it. The orchestrator will read `STATUS.md`, dispatch the first
pending agent, and keep going until it hits a decision point.

---

## Daily workflow

- **Start work**: launch Claude, type `continue`
- **Check progress**: type `/status`, or read `STATUS.md` / `PROGRESS.md` on GitHub
- **After a meeting**: drop the transcript into `meetings/raw/`, then type `/meeting`
- **Stop for the day**: type `/checkpoint` to merge agent branches into `main`
- **Resume**: type `continue` again. The orchestrator picks up where it left off.

---

## File cheat sheet

| File / folder | Purpose | Who edits it |
|---|---|---|
| `CLAUDE.md` | Orchestrator rules (Part 1 framework + Part 2 project-specific) | PI edits Part 2 once |
| `GOAL.md` | Research question and deliverables | PI writes |
| `STATUS.md` | Pipeline state table | orchestrator maintains |
| `PROGRESS.md` | Running log, newest first | every agent appends |
| `DECISIONS.md` | Pending questions for the PI | agents append; PI resolves |
| `HEARTBEAT.md` | Dispatch counter, agent health | orchestrator maintains |
| `RESUME.md` | Session-handoff document — "how to pick up" snapshot | `/resume` writes, never by hand |
| `meetings/raw/` | Drop meeting transcripts here | PI |
| `meetings/summaries/` | Claude-generated summaries | `/meeting` writes |
| `meetings/feedback.md` | Accumulated agent guidance | `/meeting` appends |
| `logs/` | Descriptive per-stage logs (never numbered) | every agent writes |
| `logs/trash.md` | Record of every file move into `.trash/` | `/trash` and skills |
| `.trash/` | Staging folder for "removed" files | gitignored |
| `documents/` | Source papers and references | PI drops in |
| `survey/` | Literature review notes | surveyor |
| `theory/` | Derivations and proofs | theorist |
| `code/src/` | Source code | coder |
| `code/experiments/` | Experiment scripts | analyst, coder |
| `code/tests/` | Unit tests | coder |
| `analysis/figures/` | Generated figures | analyst |
| `analysis/tables/` | Generated tables | analyst |
| `paper/main.tex` | Paper source | writer |
| `paper/references.bib` | Bibliography | surveyor + writer |
| `paper/versions/` | Versioned PDF snapshots | writer |
| `review/` | Reviewer feedback | reviewer |
| `.claude/agents/` | Agent definitions | (template) |
| `.claude/commands/` | Slash commands | (template) |
| `.claude/skills/` | Reusable capability packs | (template) |
| `.claude/hooks/` | Event scripts (auto-commit, progress check) | (template) |
| `.claude/settings.json` | Project-local permissions | (template) |
| `compile_paper.sh` | LaTeX build (trash-aware) | (template) |

---

## Safety — what's enforced for you

Global settings in `~/.claude/` (installed by `lab-claude-dotfiles`) hard-block:
- Any `rm` or `rmdir` — **use `/trash` instead**
- `sudo`, `git push --force`, `git reset --hard`, `git clean -fdx`
- Outgoing network except `arxiv.org`, `github.com`, `scholar.google.com`,
  `raw.githubusercontent.com`, `docs.anthropic.com`
- Writing to `.env`, credentials, SSH keys

Project-local settings auto-allow common dev tools (poetry, pytest, python,
git add/commit/push origin main, compile_paper.sh) so agents don't interrupt
you for every command.

If an agent tries something dangerous, it's blocked automatically — you don't
need to babysit. If a legitimate command is blocked, you can either:
1. Add it to `.claude/settings.json` allow list and commit, OR
2. Use `/trash` / trash-file skill if it's a removal

---

## Troubleshooting

**Agent asks for permission on a common command**
Add it to `.claude/settings.json` → `permissions.allow`. Commit.

**Agent refuses to delete a file**
That's expected. Use `/trash <path>` instead.

**Push fails**
Check `git remote -v` and that you have access to the private repo.

**Agent stuck in a loop**
Check `HEARTBEAT.md` dispatch counter. If ≥20, `/continue` stops automatically.
If <20, check `DECISIONS.md` — the orchestrator probably flagged a question.

**Paper won't compile**
Look at `paper/main.log`. Common fixes: missing `\cite{key}` in
`references.bib`, missing figure file in `analysis/figures/`, unescaped
special character.

**I want to interrupt a runaway agent**
`Ctrl+C` in the Claude Code terminal. Then check `git status` — any
half-staged changes are still there.

**I dropped a transcript but `/meeting` does nothing**
Check that the filename has the form `YYYY-MM-DD_<slug>.md` and is in
`meetings/raw/`. Also check `meetings/summaries/.hashes` — if the raw
file's SHA-256 is already in the hashes file, Claude thinks it's processed.

---

## Versioning and reproducibility

- Every agent run is auto-committed to `agent/auto/<date>` by the
  `post-agent-commit.sh` hook
- `/checkpoint` merges side branches into `main` and compiles the paper
- `paper/versions/` holds every successful PDF with a date-stamped filename
- `review/` holds every review iteration
- Fixed random seeds are required in every experiment (see `code/experiments/`)

---

## Contributing back to the template

Bug fix or improvement that applies to all lab projects? Send it back to
`lab-research-template`:

```bash
cd ~/Documents/Claude/Projects/lab-research-template
git checkout -b fix/<short-description>
# edit
git push origin fix/<short-description>
gh pr create
```

Project-specific tweaks stay in your project repo, not the template.

---

## License

Internal lab use. Do not publish without PI approval.
