# 02 — Project Anatomy: Every Folder, Every Key File

**Read time:** ~20 minutes. This is the longest chapter. It is the one
you will come back to most often.

Every folder and every file at the project root has a specific job.
This chapter walks through every one of them in the order a beginner
usually encounters them. For each, you will learn:

- **Purpose** — what the thing is for in one sentence
- **Who writes it** — you (the PI), an agent, or the template
- **What's inside** — typical contents you will see
- **Why it's designed that way** — so you can make good judgment calls
  when a situation is not in the manual

Use this as a reference. You are not expected to memorize it.

---

## 1. The big picture — a map of the project root

When you bootstrap a new project, the directory tree looks like this
(trimmed to things a beginner cares about):

```
my_first_project/
├── CLAUDE.md                 ← orchestrator rules (Part 1 framework + Part 2 your project)
├── GOAL.md                   ← research question and deliverables (PI writes)
├── STATUS.md                 ← pipeline state table (orchestrator maintains)
├── PROGRESS.md               ← running log, newest first (every agent appends)
├── DECISIONS.md              ← pending PI questions (blocks /continue until resolved)
├── HEARTBEAT.md              ← dispatch counter, health checks
├── RESUME.md                 ← session-handoff document (refreshed by `/resume`)
├── README.md                 ← project-level reference sheet
│
├── .claude/                  ← ALL Claude Code configuration
│   ├── agents/               ← six agent specs
│   ├── commands/             ← five slash commands
│   ├── skills/               ← three reusable capability packs
│   ├── hooks/                ← two event hooks (auto-commit, progress check)
│   └── settings.json         ← project-local permissions
│
├── documents/                ← source papers, reference materials (PI drops in)
├── survey/                   ← literature review notes (surveyor writes)
├── theory/                   ← derivations and proofs (theorist writes)
├── code/
│   ├── src/                  ← source code (coder writes)
│   ├── tests/                ← unit tests (coder writes)
│   └── experiments/          ← experiment scripts (analyst + coder)
├── analysis/
│   ├── figures/              ← generated figures (analyst writes)
│   └── tables/               ← generated tables (analyst writes)
├── paper/
│   ├── main.tex              ← paper source (writer writes)
│   ├── references.bib        ← bibliography (surveyor + writer)
│   └── versions/             ← dated PDF snapshots (writer appends)
├── review/                   ← reviewer feedback files, numbered
│
├── meetings/
│   ├── raw/                  ← PI drops transcripts here
│   ├── summaries/            ← Claude-generated summaries
│   └── feedback.md           ← accumulated agent guidance
│
├── logs/                     ← descriptive per-stage logs
│   └── trash.md              ← record of every file moved to .trash/
│
├── .trash/                   ← safe delete staging (gitignored)
│
├── pyproject.toml            ← Python dependencies (poetry)
├── .python-version           ← pinned Python version (pyenv)
├── compile_paper.sh          ← LaTeX build script
└── .venv/                    ← poetry virtualenv (gitignored)
```

You will spend most of your time looking at the files at the very top
(`CLAUDE.md`, `GOAL.md`, `STATUS.md`, `PROGRESS.md`) and the outputs in
`paper/`, `analysis/figures/`, and `logs/`. The rest you only visit
when something specific needs attention.

---

## 2. The state files — the project's brain

These six root-level Markdown files are **the single source of truth**
for the project. The orchestrator reads and updates them; you can too.
If you want to know where the project stands, read these files in this
order: `STATUS.md`, `PROGRESS.md`, `DECISIONS.md`.

### 2.1 `CLAUDE.md` — orchestrator rules

**Purpose.** Tells Claude how to behave when you type `continue`. Split
in two parts:

- **Part 1 — Common framework.** Reusable across projects.
  Workflow rules, verification requirements, core principles. **Do not
  edit** — changes here affect every lab project.
- **Part 2 — Project-specific.** *You* fill this in once at the start of
  a project. Contains: the problem statement, the pipeline diagram, and
  any domain-specific conventions that do not belong in a general-purpose
  agent file.

**Who edits it.** Part 1: template maintainer only. Part 2: the PI (you)
once, at project setup.

**Why split this way.** It lets the same framework run many different
projects without each project re-inventing the coordination rules.
Project-specific knowledge is isolated in Part 2, so updating the
framework in Part 1 is safe for everyone.

> **When to edit Part 2 later.** Rarely. If your pipeline structure
> changes — e.g., you add a new stage after a meeting — edit Part 2.
> Most day-to-day guidance goes in `meetings/feedback.md` instead.

### 2.2 `GOAL.md` — what are you trying to do

**Purpose.** The answer to the question "why does this project exist".
Contains the research question, starting materials, deliverables,
success criteria, scope in, scope out, and known constraints.

**Who writes it.** The PI. Once, at setup. You may revise after a
meeting if the goal shifts.

**Why it matters.** Every agent reads `GOAL.md` on startup. A vague
`GOAL.md` produces vague agent work. **Write specifics:** "reproduce
Figure 3 within 5% using the same seeds" beats "verify the paper".

**What's in it.** A filled-in `GOAL.md` typically runs 100–300 lines.
Short `GOAL.md` files are a warning sign — the orchestrator will have
to guess.

### 2.3 `STATUS.md` — the pipeline state table

**Purpose.** A table showing every pipeline stage, which agent owns it,
its current status, and where the output will go.

**Who edits it.** The orchestrator, automatically, after every agent
run. You rarely touch it directly, though you *may* re-order rows or
add new ones after a meeting.

**What's inside.** A pipeline table like this:

```markdown
| Stage | Agent | Status | Output | Notes |
|---|---|---|---|---|
| 1. Foundation — survey | surveyor | done | survey/ | |
| 2. Foundation — theory | theorist | in_progress | theory/ | |
| 3. Foundation — code | coder | pending | code/src/ | |
| 4. Validation | analyst | pending | analysis/ | |
...
```

Statuses are one of: `pending`, `in_progress`, `done`, `blocked`.

**Why it matters.** This is *what the orchestrator reads first* every
time you type `continue`. Changing `STATUS.md` is how you change what
happens next.

### 2.4 `PROGRESS.md` — the narrative log

**Purpose.** A running log of everything that happened in the project,
with the **newest entry at the top**.

**Who writes it.** Every agent appends a one-paragraph summary of what
it just did. The orchestrator also logs its own dispatches. A hook
(`stop-progress-check.sh`) refuses to end a session if `PROGRESS.md`
has not been updated in the last 15 minutes.

**What's inside.** Time-stamped paragraphs, newest first. Each entry
says: what was done, what files were written, anything noteworthy.

**Why it matters.** This is the file a human reads to catch up after a
day away. Skim the top 5 entries and you know what happened.

### 2.5 `DECISIONS.md` — pending PI questions

**Purpose.** A list of open questions that need PI input before the
pipeline can proceed.

**Who writes it.** Agents append when they hit something they cannot
decide on their own. The PI resolves by filling in the **Resolution**
field and adding initials + date.

**What's inside.** Numbered decision blocks with: title, who raised it,
date, impact (low/med/high), context, options considered, the agent's
recommendation, and (empty until resolved) the resolution.

**Why it matters.** `/continue` refuses to dispatch any agent if
`DECISIONS.md` has any pending item. This is a safety rail: it forces
human-in-the-loop on anything an agent flagged as uncertain.

> **How to resolve a decision.** Open `DECISIONS.md`, find the block,
> fill in `Resolution: <your choice>. — <initials> YYYY-MM-DD`, save,
> then type `continue`. The orchestrator will proceed.

### 2.6 `HEARTBEAT.md` — dispatch counter and health check

**Purpose.** Tracks how many agents have been dispatched in the current
`continue` invocation (hard cap: 20) and a per-agent health table.

**Who edits it.** The orchestrator. You read it but do not usually
write to it.

**What's inside.** Start time, dispatch count, last agent, per-agent
idle/running status, and a checklist of health checks (`no stale
agents`, `no unresolved decisions`, `no unprocessed transcripts`, etc.).

**Why it matters.** The 20-dispatch cap prevents runaway loops. If a
buggy pipeline keeps re-running the same agent, `HEARTBEAT.md` will
hit 20 and the orchestrator will stop and ask you.

### 2.7 `RESUME.md` — session-handoff document

**Purpose.** A snapshot of "where is this project and how do I pick it
up" designed to be read at the **start of a new Claude Code session**
— after a laptop restart, a day off, or handing the project to a
labmate. Think of it as a targeted cover letter for the state files:
if `STATUS.md` / `PROGRESS.md` / `DECISIONS.md` are the raw data,
`RESUME.md` is the executive summary.

**Who writes it.** The `/resume` slash command. Never written by hand
unless the PI wants to add a personal note.

**What's inside.** Project problem statement (from GOAL.md), current
pipeline stage, next action, open blockers, what has been delivered,
a numbered resume procedure ("cd, launch claude, /status, resolve
decisions, continue"), key conventions reminders, and pointers to the
most important files to read first.

**Why it exists.** `/status` is a dashboard for during-session checks;
`/resume` is a cold-start document for after-break restarts. The two
overlap but optimise for different audiences — `/status` is shown in
the conversation, `/resume` is a committed file that survives across
restarts.

**When to refresh it.** Before stopping for the day, or whenever you
want to hand the project off. The command is idempotent — you can run
it as many times as you like; each run overwrites the previous
`RESUME.md` with a fresh snapshot.

### 2.8 `README.md` — project-level reference

**Purpose.** A short reference sheet specific to this project.
`{{PROJECT_NAME}}` is substituted at bootstrap time.

**Who edits it.** The PI. Keep it short.

---

## 3. `.claude/` — all Claude Code configuration

Everything Claude Code needs to run this project lives under `.claude/`.
There are **five subfolders**, each with a distinct role.

### 3.1 `.claude/agents/` — the six agent specs

One Markdown file per agent: `surveyor.md`, `theorist.md`, `coder.md`,
`analyst.md`, `writer.md`, `reviewer.md`.

**Each file has the same shape:**

```markdown
---
name: surveyor                           # machine-readable agent name
description: Literature survey, ...      # one line, shown in menus
tools: WebSearch, WebFetch, Read, ...    # which tools this agent can use
model: sonnet                            # sonnet | opus
effort: high                             # low | med | high | max
---

You are the SURVEYOR for this project.

## Job
- ...

## Workflow
1. ...

## Must not
- ...
```

The frontmatter (the block between `---` lines) controls model and tool
access. The body is the agent's instructions.

**Who edits it.** Template maintainer by default. A project may override
an agent spec by editing the file under `.claude/agents/` directly — that
override stays in the project repo and does not affect other projects.

**Why this design.** Each agent is a separate prompt file so you can
debug and tune it in isolation. If the surveyor is producing low-quality
summaries, you can rewrite `surveyor.md` without touching anything else.

See [`06-agents.md`](06-agents.md) for what each of the six agents does
in detail.

### 3.2 `.claude/commands/` — slash commands

One Markdown file per slash command: `continue.md`, `checkpoint.md`,
`meeting.md`, `status.md`, `resume.md`, `trash.md`.

A command file is a prompt Claude uses when you type the matching slash
command inside Claude Code. For example, typing `/continue` runs
`.claude/commands/continue.md`, which tells Claude to act as the
orchestrator.

**The six commands:**

| Command | What it does |
|---|---|
| `/continue` | Dispatch the next pending agent (the main loop) |
| `/status` | Print a pipeline status report without dispatching anything |
| `/resume` | Generate or refresh `RESUME.md` — a session-handoff document for picking the project back up after a break or restart |
| `/meeting` | Process unprocessed transcripts in `meetings/raw/` |
| `/checkpoint` | Merge agent branches into `main`, compile, push, summarize |
| `/trash <path>` | Safely remove a file by moving it to `.trash/YYYY-MM-DD/` |

**Why commands live in files.** Same reason agents do — you can read
and edit the exact prompt without guessing what Claude is doing
internally. For a worked walk-through of how slash commands are
executed and how to write your own, see
[`05-daily-workflow.md`](05-daily-workflow.md) §11.

### 3.3 `.claude/skills/` — reusable capability packs

Three skills live here: `orchestrate/`, `incorporate-meeting/`,
`trash-file/`. Each folder contains one `SKILL.md` file.

A skill is like a slash command but smaller and more focused — it is
typically invoked by an agent, not by the user. For example, the
`trash-file` skill is what the coder agent calls when it needs to
"delete" a file safely.

**Who edits them.** Template maintainer. You rarely need to touch these.

### 3.4 `.claude/hooks/` — event scripts

Two shell scripts that fire automatically on Claude Code events:

| Hook | When it fires | What it does |
|---|---|---|
| `post-agent-commit.sh` | After a writer-class subagent (coder, analyst, writer) finishes | Stages changes (excluding forbidden paths like `.env`), runs Python syntax check, commits to `agent/auto/<date>` branch, pushes best-effort |
| `stop-progress-check.sh` | When Claude Code tries to end a session | Refuses to stop if `PROGRESS.md` has not been updated in the last 15 minutes |

**Why hooks.** They enforce safety and hygiene without Claude having to
remember to do it every time. You get auto-commit for free; you cannot
forget to update the progress log.

**Important.** The `post-agent-commit.sh` hook **will not commit** files
under `data/`, `meetings/raw/`, or any path matching `.env`, `*.pem`,
`id_rsa*`, or `credentials*`. This is the safety net that prevents an
agent from leaking secrets or large data into git. If you see the hook
refuse to commit because it found a forbidden path, that is working as
designed.

### 3.5 `.claude/settings.json` — project-local permissions

A JSON file that lists shell commands and URLs Claude Code is allowed
to run without prompting you. The template pre-allows common dev tools
(`poetry run`, `python`, `pytest`, `git add/commit/push origin`,
`pdflatex`, `./compile_paper.sh`, `mkdir -p`, `mv * .trash/`).

**Who edits it.** You, when Claude stops to ask permission for a legit
command. Add it to the `permissions.allow` list, commit, continue.

**Do not remove** the `hooks` section — that is what wires up
`post-agent-commit.sh` and `stop-progress-check.sh`.

---

## 4. `documents/` — source materials (PI drops in)

**Purpose.** Everything the project starts with. Papers you are
reproducing, datasets you have downloaded, reference implementations.

**Who writes it.** The PI. Agents may *read* from `documents/` but must
not *write* to it.

**What goes in.** A typical theory-paper project has
`documents/main.pdf` (the paper being reproduced). A data project might
also have `documents/dataset_description.pdf`, `documents/sample.csv`,
etc.

**Why read-only for agents.** `documents/` is the project's ground
truth. If an agent could overwrite a source paper, you would not be
able to trust anything.

---

## 5. `survey/` — literature review notes

**Purpose.** Structured notes on prior work, one file per paper.

**Who writes it.** The surveyor agent.

**What's inside.** Files like `survey/sugihara_2012_ccm.md` or
`survey/arbabi_2017_koopman.md`, each containing:

- The citation
- A one-paragraph summary
- Key result
- Relevance to *this* project
- A citation key that matches `paper/references.bib`

**Why one file per paper.** Easy to diff, easy to Ctrl-F, no merge
conflicts. The alternative — one big `literature.md` — becomes
unmergeable after three surveyor runs.

---

## 6. `theory/` — derivations and proofs

**Purpose.** Step-by-step derivations of every key equation in the
source paper, plus any extensions the project develops.

**Who writes it.** The theorist agent.

**What's inside.** Markdown files with LaTeX-compatible math notation,
one per topic: `theory/hankel_factorization.md`,
`theory/koopman_krylov.md`, etc.

**Each file typically contains:**

- What theorem or equation it covers
- The full derivation, step by step
- Assumptions used and where they are used
- A **verdict**: holds / conditional / fails
- Any errors or suspicious steps flagged for PI review

**Why a separate folder.** The theorist's job is to produce rigorous
notes the writer can paraphrase for the paper. Keeping theory separate
from `paper/` means the writer can cite it without worrying about
accidentally turning a derivation into half-formed prose.

---

## 7. `code/` — source code, tests, experiments

Three subfolders with different purposes.

### 7.1 `code/src/`

**Purpose.** The implementation of the method(s). Importable as a
Python package. `pyproject.toml` is configured with
`packages = [{include = "src", from = "code"}]` so `import src.hankel`
works.

**Who writes it.** The coder agent.

**Conventions.** Python 3.11+, type hints everywhere, 100-character line
limit, docstrings with Args/Returns sections, formatted with `black`
and linted with `ruff` (both pre-configured in `pyproject.toml`).

### 7.2 `code/tests/`

**Purpose.** Unit tests for everything in `code/src/`. One test file per
source module. Pytest-based, fixed random seeds, fully deterministic.

**Who writes it.** The coder agent.

**How to run.** `poetry run pytest -v` (or `-q` for quiet mode). The
`/checkpoint` command runs tests before merging to `main`; if tests
fail, the checkpoint stops.

### 7.3 `code/experiments/`

**Purpose.** Reproducible experiment scripts. One script per experiment,
each with a fixed random seed and a short docstring describing what the
experiment tests.

**Who writes it.** The analyst agent, sometimes the coder.

**Conventions.**
- Filenames describe the content: `benchmark_vs_granger_causality.py`,
  not `exp1.py`.
- Every script starts with `rng = np.random.default_rng(seed=0)` — seed
  values are reported in figure captions.
- Results save to `analysis/<experiment_name>/results.csv` or `.npz`.

---

## 8. `analysis/` — experiment results

Two subfolders plus loose result files.

### 8.1 `analysis/figures/`

**Purpose.** Every figure the paper references, as PDF (for LaTeX) plus
PNG (for quick preview).

**Filename rule.** Describes the content, never the figure number.
`auroc_vs_noise.pdf` is good; `fig3.pdf` is forbidden. Rationale: figure
numbers change during revision, filenames should not.

**Who writes it.** The analyst agent.

### 8.2 `analysis/tables/`

**Purpose.** LaTeX-formatted or CSV-formatted tables for the paper.

**Who writes it.** The analyst agent.

### 8.3 Loose files under `analysis/`

Each experiment script produces one or more result files
(`.csv`, `.npz`, `.json`) under a subfolder named after the experiment.
Example layout after a run:

```
analysis/
├── figures/
│   └── rho_vs_coupling.pdf
├── tables/
│   └── benchmark_summary.tex
└── rho_vs_coupling/
    ├── results.csv
    └── config.json        (the seed and parameter set used)
```

**Why separate raw results from figures.** If you need to re-plot a
figure with a different color palette later, the raw `.csv` is still
there. You do not have to re-run the experiment.

---

## 9. `paper/` — the LaTeX paper

**Purpose.** The writeup itself. LaTeX source plus versioned PDF
snapshots.

**Who writes it.** Only the writer agent. Coder, analyst, theorist,
reviewer, and surveyor all must **not** touch `paper/`. This is enforced
in each agent spec.

### 9.1 `paper/main.tex` and section files

The usual layout — `main.tex` is the master document, section files
(`introduction.tex`, `methods.tex`, `results.tex`, `discussion.tex`,
`related_work.tex`) are included with `\input{}`.

The writer references figures with paths like
`\includegraphics{../analysis/figures/auroc_vs_noise.pdf}` — note the
`../` because LaTeX is compiled from inside `paper/`.

### 9.2 `paper/references.bib`

Bibliography. The surveyor populates this as it finds citations; the
writer uses the keys. One citation key per paper, descriptive (e.g.,
`sugihara2012ccm` not `sugihara1`).

### 9.3 `paper/versions/` — dated PDF snapshots

Every successful compile saves a snapshot named
`main_v<NN>_<YYYY-MM-DD>.pdf` to this folder. **Never overwrite
existing versions** — the history is evidence for the PI that the paper
improved over time.

**Why versioned PDFs.** LaTeX source is already in git, but a reviewer
or PI who wants to see "what did the draft look like last Friday?" does
not want to check out a git commit. They want to click a PDF. This
folder gives them that.

---

## 10. `review/` — reviewer feedback

**Purpose.** Numbered review files, one per review cycle.

**Who writes it.** The reviewer agent.

**What's inside.** Files named `review_v01.md`, `review_v02.md`, etc.
Each review contains:

- Verdict (Accept / Minor / Major / Reject)
- Summary of the contribution
- Strengths
- Major issues (P0 — must fix)
- Minor issues (P1 — should fix)
- Nits (P2 — typos, formatting)
- Specific comments with section/equation/figure references

**Why numbered, not overwritten.** Same reason as `paper/versions/` —
the full review history proves the paper improved. Also, the next
review can explicitly check whether the prior P0 issues were addressed.

---

## 11. `meetings/` — the PI feedback loop

Three parts, all working together. This is the **main way a PI steers a
project** without having to launch Claude Code.

### 11.1 `meetings/raw/`

**Purpose.** A drop folder for raw meeting transcripts. Otter exports,
Zoom transcripts, plain text notes — anything goes.

**Who writes it.** The PI.

**Naming.** Use `YYYY-MM-DD_<short-slug>.md` (or `.txt`). Example:
`2026-04-18_pipeline-review.md`.

**What happens next.** The orchestrator **refuses to run `/continue`**
while any file in `meetings/raw/` is unprocessed. This forces the PI's
new guidance to be absorbed before the pipeline proceeds on stale
instructions.

### 11.2 `meetings/summaries/`

**Purpose.** Claude-generated structured summaries of each transcript.
One summary file per raw transcript, same basename.

**Who writes it.** The `/meeting` command.

**What's inside.** Each summary has these sections:
- **TL;DR** (2–3 sentences)
- **Key points discussed**
- **Decisions made** (explicit PI choices with rationale)
- **Open questions** (things the PI did *not* decide)
- **Feedback for agents** (guidance to change how agents work)
- **Next actions** (concrete pipeline steps, tagged with agent name and
  priority HIGH/MED/LOW)
- **Reconsideration** (given current `STATUS.md`, what changes?)
- **Verbatim quotes** (if the transcript is multilingual)

Alongside the summaries there is a hidden `.hashes` file recording the
SHA-256 of every processed raw transcript so nothing is processed
twice.

### 11.3 `meetings/feedback.md`

**Purpose.** The **canonical store of agent guidance** — accumulated
bullets from every meeting, growing over time.

**Who writes it.** The `/meeting` command appends to it. The PI may
edit it directly if needed.

**Why this matters.** Every agent reads `meetings/feedback.md` on
startup. If you told the writer "use the word 'Hankel regression' not
'Koopman causality'" three weeks ago, that rule lives in
`feedback.md` and is honored forever — or until the PI removes it.

`feedback.md` is checked into git so it is visible to teammates who
clone the repo. It is NOT auto-memory (auto-memory is machine-local and
invisible to teammates).

---

## 12. `logs/` — descriptive per-stage logs

**Purpose.** One file per agent run, describing what that run did in
enough detail that the PI can audit it later.

**Who writes it.** Every agent writes one at the end of each run.

**Naming rule (important).** Descriptive, never numbered. Good:
`logs/literature_survey_koopman.md`, `logs/hankel_regression_impl.md`,
`logs/benchmark_vs_ccm.md`. Bad: `logs/phase1.md`, `logs/run_042.md`.
Rationale: numbered logs decay — you cannot tell `phase1.md` from
`phase2.md` three months later. Descriptive filenames are self-documenting.

### `logs/trash.md`

Special file. One line per file ever moved to `.trash/`, with
timestamp, original path, new path, and reason. This is how the PI
audits what agents "deleted" and recovers anything that should not
have been.

### `logs/checkpoint_<date>.md`

Written by `/checkpoint`. Contains the list of merged agent branches,
test status, paper version produced, any open decisions, and the next
stage. The PI reads this to get a one-page digest of the session.

---

## 13. `.trash/` — safe delete staging

**Purpose.** Agents never call `rm`. When something needs to be
"deleted", it is moved to `.trash/YYYY-MM-DD/` and logged in
`logs/trash.md`. Only the PI ever permanently deletes files from
`.trash/`.

**Who writes it.** Any agent, via the `trash-file` skill or the
`/trash` slash command. Also `compile_paper.sh`, which moves LaTeX
build artifacts (`.aux`, `.log`, `.bbl`, etc.) to
`.trash/latex-build/YYYY-MM-DD/`.

**Gitignored.** `.trash/` is not committed. If you want to permanently
free the space, you — the PI — manually clear it after confirming the
contents are safe to lose.

**Why this exists.** A single `rm` in a research project can destroy
weeks of work. The trash box gives you a chance to undo. Global Claude
hooks installed by `lab-claude-dotfiles` additionally block `rm` at the
shell level.

---

## 14. Python environment files

### 14.1 `pyproject.toml`

**Purpose.** Poetry project definition. Lists every Python dependency
and every dev tool (pytest, black, ruff, mypy) with pinned versions.

**Who writes it.** PI at setup, coder agent when adding a new
dependency (via `poetry add <package>`). **Never run `pip install`
directly** — poetry tracks everything, pip does not.

### 14.2 `.python-version`

**Purpose.** Pins the Python interpreter version for pyenv.

**What's inside.** A single line like `3.11.0`. pyenv reads this
automatically when you `cd` into the directory.

### 14.3 `.venv/`

**Purpose.** The poetry-managed virtualenv. Gitignored.

**How to use.** Never activate manually. Run Python through poetry:
`poetry run python script.py`, `poetry run pytest`, etc.

---

## 15. Build scripts

### 15.1 `compile_paper.sh`

**Purpose.** Build `paper/main.pdf` from `paper/main.tex` +
`paper/references.bib`.

**What it does.**
1. Run `pdflatex` pass 1
2. Run `bibtex`
3. Run `pdflatex` pass 2 and 3 (to resolve cross-references)
4. Check the log for undefined references; warn if any
5. **Trash-aware cleanup:** move temporary LaTeX files (`.aux`, `.log`,
   `.bbl`, `.blg`, `.out`, `.toc`, `.fdb_latexmk`, `.fls`, `.synctex.gz`)
   to `.trash/latex-build/<date>/` instead of deleting them. Logs the
   move to `logs/trash.md`.

**Who runs it.** The writer agent runs it every time it finishes a
draft. `/checkpoint` runs it as part of the merge process.

### 15.2 `bootstrap.sh`

**Purpose.** Creates a new project from this template. Lives in the
template repo, not in your project — you do not see it after bootstrap.

**What it does.** Copies the template to `../<project-name>/`,
substitutes `{{PROJECT_NAME}}` in the seed files, copies the chosen
variant's Part 2 skeleton, resets git history, creates the initial
commit. See [`03-setup.md`](03-setup.md) for usage.

---

## 16. Quick lookup table

When you don't remember where something lives, search this table for a
keyword.

| I want to… | Look at |
|---|---|
| see what the project is trying to do | `GOAL.md` |
| see what happened yesterday | `PROGRESS.md` (top few entries) |
| see what will happen next | `STATUS.md` (first `pending` row) |
| see why `/continue` is blocked | `DECISIONS.md` |
| see which agents have run | `HEARTBEAT.md` |
| find a specific literature note | `survey/` |
| find a derivation | `theory/` |
| run the tests | `poetry run pytest -q` from the project root |
| find the figure the paper references | `analysis/figures/` |
| rebuild the paper PDF | `./compile_paper.sh` |
| see the latest review | `review/review_v<highest>.md` |
| see the latest PDF | `paper/versions/` (newest file) |
| drop a meeting transcript | `meetings/raw/<date>_<slug>.md` |
| see the agent guidance that shaped the last month's work | `meetings/feedback.md` |
| audit what files were "deleted" | `logs/trash.md` |
| change how the surveyor behaves | `.claude/agents/surveyor.md` |
| allow a new shell command without being asked | `.claude/settings.json` |
| change the pipeline for this project | `CLAUDE.md` Part 2 and `STATUS.md` |

---

## What to read next

You now know where everything lives. Next:

- If you are ready to set up a project, go to [`03-setup.md`](03-setup.md).
- If you want to understand each agent's behavior more deeply before
  you start, go to [`06-agents.md`](06-agents.md).
