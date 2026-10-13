# 03 — Setup: From Empty Laptop to a Bootstrapped Project

**Read time:** ~10 minutes (plus ~20 minutes of actual installation the
first time, less if you have pyenv and poetry already).

By the end you will have:

1. `lab-claude-dotfiles` installed (global Claude rules and safety hooks)
2. `pyenv` and `poetry` installed
3. `lab-research-template` cloned
4. A new project bootstrapped from the template, with `GOAL.md` and
   `CLAUDE.md` Part 2 filled in
5. A private GitHub repo for the project, pushed

You will **not yet** have run any agents. That is [`04-first-run.md`](04-first-run.md).

---

## 1. One-time machine setup

You do these steps **once per laptop**. If you already did them for a
previous project, skip ahead to section 2.

### 1.1 Install `lab-claude-dotfiles`

This is a companion repo that sets up global Claude Code rules, hooks,
and permission defaults. Without it, the safety rails that block `rm`,
`sudo`, `git push --force`, and writes to `.env` files do not exist.

```bash
git clone git@github.com:<lab>/lab-claude-dotfiles.git \
  ~/Documents/Claude/Projects/lab-claude-dotfiles
cd ~/Documents/Claude/Projects/lab-claude-dotfiles
./setup.sh
```

The setup script creates symlinks under `~/.claude/` for rules, hooks,
and skills.

**Verify it worked:**

```bash
ls ~/.claude/rules                                              # should list rule files
~/.claude/hooks/pre-destructive.sh < /dev/null ; echo exit=$?   # should print "exit=0"
```

If either command fails, stop and ask a labmate. The rest of this
tutorial assumes the dotfiles are installed.

### 1.2 Install `pyenv` and `poetry`

Research projects pin an exact Python version (`pyenv`) and track
dependencies without touching system Python (`poetry`). On macOS:

```bash
brew install pyenv poetry
```

Install a recent Python 3.11:

```bash
pyenv install 3.11.0
```

Any recent 3.11.x works. The template's `.python-version` file tells
pyenv which one to use when you `cd` into the project.

> **Why not `pip` and the system Python?**
> System Python on macOS changes without warning when you update macOS,
> and `pip install` without a virtualenv pollutes a shared namespace.
> Both lead to "works on my laptop, broken everywhere else" bugs.
> Poetry + pyenv give you reproducible, locked environments. **Never
> run `pip install` directly in a project.**

### 1.3 Clone the template

```bash
git clone git@github.com:<lab>/lab-research-template.git \
  ~/Documents/Claude/Projects/lab-research-template
```

This is the template itself. You do **not** edit files here when you
start a project. You bootstrap a new directory from it (section 2).

---

## 2. Bootstrap a new project

From the template directory, run `bootstrap.sh` with a project name.
Pick a descriptive snake_case name — it will become the folder name
and the Python package name.

```bash
cd ~/Documents/Claude/Projects/lab-research-template
./bootstrap.sh my_first_project --variant theory-paper
```

**What `bootstrap.sh` does, in order:**

1. Creates `~/Documents/Claude/Projects/my_first_project/` by copying
   the template (excluding `.git`, `.trash`, and `bootstrap.sh` itself).
2. Makes an empty `.trash/.gitkeep`.
3. Substitutes `{{PROJECT_NAME}}` in the seed files
   (`CLAUDE.md`, `GOAL.md`, `STATUS.md`, `PROGRESS.md`, `DECISIONS.md`,
   `HEARTBEAT.md`, `pyproject.toml`, `README.md`).
4. If the chosen variant has a `CLAUDE_part2.md` skeleton, copies it
   next to `CLAUDE.md` as `CLAUDE_part2_variant.md` for you to paste
   into `CLAUDE.md` Part 2.
5. Makes `compile_paper.sh` and `.claude/hooks/*.sh` executable.
6. Resets git history (`rm -rf .git`, `git init`), stages everything,
   and creates the initial commit.

**Variants available today:** only `theory-paper` ships a skeleton
Part 2. More may be added (`data-analysis`, `wet-lab`). If you omit
`--variant`, the default is `theory-paper`.

After `bootstrap.sh` finishes, move into the new project:

```bash
cd ~/Documents/Claude/Projects/my_first_project
```

From here on, every path in this tutorial is relative to
`my_first_project/` unless stated otherwise.

---

## 3. Install Python dependencies

```bash
poetry install
```

This reads `pyproject.toml`, creates `.venv/`, and installs numpy,
scipy, matplotlib, pandas, pytest, black, ruff, mypy, and a few other
common tools. Expect it to take 1–3 minutes the first time.

**Verify:**

```bash
poetry run python -c "import numpy; print(numpy.__version__)"
```

Should print a version like `1.26.4`. If you get `ModuleNotFoundError`,
check that you are in the project directory and that `poetry install`
completed without errors.

**Important rule going forward:** every Python command runs through
poetry. Not `python script.py`, but `poetry run python script.py`. Not
`pytest`, but `poetry run pytest`. The coder and analyst agents know
this; you should too.

---

## 4. Drop in your starting materials

Whatever your project starts from goes in `documents/`.

- **Reproducing a paper?** Put the PDF at `documents/main.pdf`.
- **Extending a method?** Put the paper, plus any related papers you
  already know you need, in `documents/`.
- **Working from a dataset?** Put a sample file or the dataset
  description in `documents/`. Do not commit large datasets — see the
  note below.

```bash
cp ~/Downloads/the_paper.pdf documents/main.pdf
```

> **Do not commit large datasets.** Git is not built for files larger
> than a few MB. The `post-agent-commit.sh` hook refuses to commit
> anything under `data/` by default, but you should also add your
> dataset patterns to `.gitignore` to be safe. Large files belong in
> lab shared storage, not in the project repo.

---

## 5. Fill in `GOAL.md`

This is where you actually tell Claude what you want. A well-written
`GOAL.md` is the single biggest factor in whether the project runs
smoothly. A two-sentence `GOAL.md` will produce two-sentence agent work.

**Sections to fill in** (the template has these as blockquoted
placeholders):

1. **The question** — one paragraph. What are you trying to find out,
   prove, build, or reproduce?
2. **Starting point** — what artifacts exist on day 1? List the files
   in `documents/` and one line about each.
3. **Deliverables** — a numbered list. Be concrete.
4. **Success criteria** — how do you know the project is done?
5. **Quality bar** — what counts as "good enough" at each stage?
6. **Scope — in** — bulleted list of things that are IN scope.
7. **Scope — out** — bulleted list of things explicitly OUT of scope.
   Equally important.
8. **Known constraints** — compute budget, data access, deadlines.

**Example of a good vs bad deliverable list:**

| Bad | Good |
|---|---|
| "Implement the method" | "Implement Hankel regression and the two baselines (Granger causality, CCM) as a Python package under `code/src/` with unit tests for each component" |
| "Reproduce the paper" | "Reproduce Section III Example 1 (target: `rho_0→2 ≈ 0.97`, `rho_2→0 ≈ 0.60`) and Example 2 (target: `rho_0→2 ≈ 0.31`, `rho_2→0 ≈ 0.21`) on the same systems described in the source paper" |

Open `GOAL.md` in your editor and fill it in. Aim for 100–300 lines of
real specifics.

---

## 6. Fill in `CLAUDE.md` Part 2

Open `CLAUDE.md`. The top half (Part 1 — Common Framework) is **do not
edit**. Scroll to Part 2.

If you used `--variant theory-paper`, you will also see a sibling file
`CLAUDE_part2_variant.md` with a starting skeleton. Copy its contents
into `CLAUDE.md` Part 2, then edit.

**Three sub-sections to fill in:**

### 6.1 The problem (one paragraph)

State the research question, the starting materials, and the expected
final artifact. Agents read this on every startup — the more specific
it is, the less they have to guess.

### 6.2 Pipeline stages (ASCII diagram)

An ASCII tree showing which agents run in which order, with parallelism
made explicit. The `theory-paper` variant ships this default:

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
  └─ reviewer → writer/analyst/coder → compile → reviewer → ...
```

Tune this for your project. Add or remove stages. The `STATUS.md` table
should have one row per stage in this diagram.

### 6.3 Domain-specific conventions

Project-unique rules that do not belong in a general-purpose agent
file. Examples:

- Naming conventions ("call the method 'X', never 'Y'")
- Baseline fairness rules ("all baselines run on the same seed")
- Score conventions ("always report `rho_X→Y` and `rho_Y→X` together")
- Honesty clauses ("if the method loses on system X, report it")

If you have nothing project-unique, you can delete this sub-section.

---

## 7. Commit your setup edits

```bash
git add GOAL.md CLAUDE.md
git commit -m "PI setup: fill GOAL.md and CLAUDE.md Part 2"
```

If the bootstrap left `CLAUDE_part2_variant.md` behind and you have
already merged it into `CLAUDE.md`, safely remove it with:

```
> /trash CLAUDE_part2_variant.md
```

(That is typed at the Claude Code prompt, not at the shell — see
[`05-daily-workflow.md`](05-daily-workflow.md) for the `/trash` command.)

---

## 8. Create a private GitHub repo and push

**Important: private, not public.** Research projects contain
unpublished results. Until the paper is out, keep the repo private.

```bash
# Replace <lab> with your lab org name on GitHub
git remote add origin git@github.com:<lab>/my_first_project.git
git push -u origin main
```

If you prefer using the `gh` CLI, you can create the repo from the
command line in one step:

```bash
gh repo create <lab>/my_first_project --private --source=. --push
```

---

## 9. Sanity check

Before your first agent run, confirm a few things are in place.
Copy-paste each command and look at the output.

```bash
poetry run python -c "import numpy, scipy, matplotlib; print('ok')"
# Expected: ok

poetry run pytest -q
# Expected: "no tests ran" or a very small number (template ships no tests)

ls documents/
# Expected: whatever you dropped in (at minimum a .gitkeep)

cat GOAL.md | wc -l
# Expected: 100+ if you filled it in thoroughly

git status
# Expected: clean, on branch main
```

Everything good? Great — you are ready for the first agent run.

---

## What to read next

Go to [`04-first-run.md`](04-first-run.md). It walks through your first
`continue` command step by step, with screenshots of what to expect at
each stage.
