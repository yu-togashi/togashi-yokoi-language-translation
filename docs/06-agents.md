# 06 — The Six Agents in Detail

**Read time:** ~15 minutes.

Each of the six agents lives in `.claude/agents/<name>.md`. Each file
is short and you are encouraged to read the actual spec whenever you
need to debug an agent. This chapter is the human-readable tour.

For each agent you will see:

- **Job** — one line
- **Runs on** — model and effort level
- **Tools** — what it can and cannot touch
- **Inputs** — files it reads on startup
- **Outputs** — files it writes
- **Workflow** — what it does, in order
- **Hard rules** — must nots
- **Common pitfalls** — what to watch for when it runs

---

## 1. Surveyor — literature review

**Job.** Find relevant prior work, produce structured notes, populate
the bibliography, find open datasets.

**Runs on.** `sonnet`, effort `high`.

**Tools.** `WebSearch`, `WebFetch`, `Read`, `Write`, `Edit`, `Glob`,
`Grep`. Web access is restricted by global settings to an allowlist:
arxiv.org, github.com, raw.githubusercontent.com, scholar.google.com,
docs.anthropic.com.

**Inputs.**
- `GOAL.md`, `STATUS.md`
- `survey/` — to avoid duplicating work from prior runs
- `meetings/feedback.md` — PI guidance on which literature to
  emphasize or avoid
- Source papers in `documents/`

**Outputs.**
- `survey/<author_year_slug>.md` — one file per paper, structured
  (citation, one-paragraph summary, key result, relevance to us)
- `paper/references.bib` — appends new entries with descriptive keys
- `PROGRESS.md` — one paragraph
- `logs/literature_survey_<topic>.md` — descriptive log

**Workflow.**

1. Read `GOAL.md` and `STATUS.md` to understand scope.
2. Read existing `survey/` to avoid duplication.
3. Read `meetings/feedback.md` for PI guidance.
4. Use `WebSearch` and `WebFetch` (allowlist only) to find sources.
5. For each relevant paper, write `survey/<slug>.md` and append to
   `paper/references.bib`.
6. Append to `PROGRESS.md` and write a descriptive log.
7. Flag anything uncertain in `DECISIONS.md`.

**Hard rules.**
- Never fetch URLs outside the lab allowlist.
- Never invent citations — if a paper cannot be verified, flag it in
  `DECISIONS.md` rather than making up a citation.
- Never commit or push directly — `post-agent-commit.sh` handles git.

**Common pitfalls.**
- **Hallucinated citations.** If the surveyor cannot find a paper it
  "remembers", it may be tempted to guess. The spec forbids this, but
  you should still spot-check citations in `paper/references.bib`
  against the actual PDFs.
- **Too narrow a search.** If `GOAL.md` is vague, the surveyor may
  focus on too narrow a slice. Fix by editing `GOAL.md` or leaving a
  `meetings/feedback.md` note.
- **Runs forever.** If the surveyor keeps finding more and more
  tangentially related papers, the scope is too open. Tighten
  `GOAL.md` scope-in / scope-out.

---

## 2. Theorist — mathematical verification

**Job.** Verify every key equation and derivation in the source
paper(s). Identify missing steps, hidden assumptions, potential
extensions.

**Runs on.** `opus`, effort `max`. (The theorist works on hard math;
the best model earns its cost here.)

**Tools.** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`. No web
access — theorist works from `documents/` and its own derivations.

**Inputs.**
- `GOAL.md`, `STATUS.md`
- `theory/` (existing files)
- Source papers in `documents/`
- `meetings/feedback.md`

**Outputs.**
- `theory/<topic_slug>.md` — step-by-step derivations in
  LaTeX-compatible Markdown
- `PROGRESS.md` and `logs/<descriptive_name>.md`
- `DECISIONS.md` entries for suspected errors

**Workflow.**

1. Read `GOAL.md`, `STATUS.md`, existing `theory/`, source papers.
2. Read `meetings/feedback.md`.
3. For each theorem / key equation:
   - Rewrite the derivation step by step
   - Check every step against the source
   - Note assumptions and where they are used
   - Mark any suspected error for PI review in `DECISIONS.md`
4. Save derivations to `theory/<topic_slug>.md`.
5. Append to `PROGRESS.md` and write a descriptive log.

**Hard rules.**
- Never guess at a derivation. If the theorist cannot verify a step,
  it flags the step in `DECISIONS.md` with the specific equation
  number and the reason for uncertainty.
- Never touch `paper/` — that is the writer's job.

**Common pitfalls.**
- **Disagreement with source paper.** The theorist often finds
  "errors" that turn out to be a different convention (index-from-0
  vs index-from-1, column-major vs row-major matrix convention, etc.).
  When you see a flagged error, always check the convention before
  concluding the paper is wrong.
- **Assumptions left implicit.** Papers often rely on "technical
  conditions" like finite-dimensional invariant subspaces, persistent
  excitation, etc. The theorist should list these explicitly. If a
  `theory/*.md` file has no assumptions list, it is incomplete.

---

## 3. Coder — implementation and tests

**Job.** Implement the algorithms described in `theory/` and the source
papers. Write unit tests. Run the test suite.

**Runs on.** `sonnet`, effort `high`.

**Tools.** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`. Bash is
needed for `poetry run pytest` etc.

**Inputs.**
- `GOAL.md`, `STATUS.md`
- `theory/` — this is where the coder learns *what* to implement
- `code/src/` (existing)
- `meetings/feedback.md`

**Outputs.**
- `code/src/<module>.py` — source code, type-hinted, documented
- `code/tests/test_<module>.py` — pytest unit tests
- `code/experiments/<name>.py` — experiment harnesses (sometimes;
  usually the analyst writes these)
- `PROGRESS.md` and `logs/<descriptive_name>.md`

**Workflow.**

1. Read `GOAL.md`, `STATUS.md`, `theory/`, `meetings/feedback.md`.
2. Identify the next coding task from `STATUS.md`.
3. Write source under `code/src/`.
4. Write tests under `code/tests/` — one test file per module.
5. Run `poetry run pytest -v` and verify all tests pass.
6. Append to `PROGRESS.md` and write a descriptive log.
7. Flag anything uncertain in `DECISIONS.md`.

**Conventions.**
- Python 3.11+, PEP 8, type hints everywhere.
- Docstrings: short one-line summary + Args/Returns sections.
- Fixed random seeds in every experiment
  (`np.random.default_rng(seed=0)`).
- Every Python command runs via `poetry run`, never bare `python`.
- Never call `rm` — use the `trash-file` skill or `/trash`.

**Hard rules.**
- Never modify `paper/`.
- For computations expected to exceed ~10 minutes, print a one-line
  warning with an estimate and the cost driver, then proceed. Never
  pause for PI approval.
- Never commit or push directly.

**Common pitfalls.**
- **Tests that pass but check the wrong thing.** Read new test files
  before you trust their output. A test that asserts
  `assert result is not None` passes but proves nothing.
- **Silent numerical instability.** The coder may implement something
  that "runs" but returns NaNs on slightly different inputs. The
  analyst usually catches this later; the coder should include a
  numerical stability test.
- **Using `pip install`.** Global and project settings block it, but
  if you see an agent try, flag the agent spec for improvement.

---

## 4. Analyst — experiments and figures

**Job.** Run benchmark experiments, parameter sweeps, and real-data
analysis. Generate figures and tables for the paper.

**Runs on.** `sonnet`, effort `high`.

**Tools.** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`.

**Inputs.**
- `GOAL.md`, `STATUS.md`
- `code/src/` — this is what it exercises
- `theory/` — for interpreting results
- `meetings/feedback.md`

**Outputs.**
- `code/experiments/<descriptive_name>.py` — experiment scripts
- `analysis/<experiment>/results.csv` or `.npz` — raw results
- `analysis/figures/<descriptive>.pdf` and `.png`
- `analysis/tables/<descriptive>.tex` or `.csv`
- `PROGRESS.md` and `logs/<descriptive_name>.md`

**Workflow.**

1. Read `GOAL.md`, `STATUS.md`, `code/src/`, `theory/`,
   `meetings/feedback.md`.
2. Identify the next analysis task from `STATUS.md`.
3. Write an experiment script under `code/experiments/`.
4. Fix the random seed. Document the sweep design at the top of the
   file.
5. Run the experiment via `poetry run python`.
6. Save raw results under `analysis/<experiment_name>/`.
7. Generate figures under `analysis/figures/` with **descriptive
   filenames**. Never `fig1.pdf`.
8. Write a descriptive log summarizing findings.
9. Flag anything uncertain in `DECISIONS.md`.

**Figure conventions.**
- Save as PDF (for LaTeX) plus PNG (for preview).
- Filename describes content: `auroc_vs_noise.pdf`, not `fig1.pdf`.
- Consistent color palette across figures — define once, reuse.
- Always include axis labels, units, and a legend.
- Figure *captions* go in the paper, not the filename.

**Hard rules.**
- Never modify `paper/`.
- Never fabricate or fudge results — if a number looks wrong,
  investigate and flag it.
- For experiments expected to exceed ~10 minutes, print a one-line
  warning with an estimate, then proceed. Never pause.

**Common pitfalls.**
- **Plotting without checking raw results first.** An analyst that
  plots results before eyeballing the raw CSV can miss obvious
  corruption.
- **Seed not pinned.** If a result varies between runs, the seed is
  not pinned. Fix and re-run.
- **Figure numbered instead of described.** If you see `fig1.pdf`,
  edit the agent spec — this is a persistent failure mode.

---

## 5. Writer — the paper

**Job.** Draft and revise every section of the paper in LaTeX.
Incorporate reviewer feedback.

**Runs on.** `opus`, effort `max`. Paper quality is the single most
expensive output to get wrong, so the best model is assigned here.

**Tools.** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`. `Bash` is
scoped by `.claude/settings.json` to the LaTeX build pipeline
(`./compile_paper.sh`, `pdflatex`, `bibtex`, `latexmk`) plus a few
file ops — **not** a general-purpose shell. The writer uses Bash
**only** to run `./compile_paper.sh` after editing the LaTeX source.
Everything else (tests, git, pytest, poetry) is out of scope.

This was `D15` in the Sekizawa and predinfo dogfood runs: earlier
versions of the template omitted Bash from the writer's tool list,
forcing the orchestrator to compile on the writer's behalf. Both runs
flagged the friction. The writer now owns compilation end to end.

**Inputs.**
- `GOAL.md`, `STATUS.md`
- `theory/` — paraphrases derivations into paper prose
- `analysis/figures/`, `analysis/tables/` — references them from LaTeX
- `paper/` (existing source and prior versions)
- `survey/`, `paper/references.bib` — for citations
- `review/` — pending reviews to address
- `meetings/feedback.md`

**Outputs.**
- `paper/main.tex` and section files
- `paper/versions/main_v<NN>_<YYYY-MM-DD>.pdf` — dated snapshot
- `PROGRESS.md` and `logs/<descriptive_name>.md`

**Workflow.**

1. Read `GOAL.md`, `STATUS.md`, `theory/`, `analysis/`, `paper/`,
   `survey/`, `review/` (pending), `meetings/feedback.md`.
2. Identify the section(s) to work on from `STATUS.md`.
3. Draft or revise the LaTeX. Use:
   - `\includegraphics{../analysis/figures/FILENAME.pdf}` for figures
   - `\ref{}` for cross-references, `\label{}` on every figure/table/section
   - `\cite{key}` for citations, where `key` is in `references.bib`
4. Compile via `./compile_paper.sh`.
5. Verify compilation succeeds. Fix LaTeX errors if any.
6. Save the successful PDF to
   `paper/versions/main_v<NN>_<YYYY-MM-DD>.pdf`.
7. Append to `PROGRESS.md` and write a descriptive log.

**Style.**
- Academic English, third person, active voice.
- Define every symbol before use.
- Every claim in Results must be supported by a figure, table, or
  cited result.
- Oxford commas.
- No emojis, no exclamation marks.

**Hard rules.**
- Never modify `theory/`, `code/`, or `analysis/`. If you need a new
  number or figure, flag it in `DECISIONS.md` and stop.
- Never invent results or citations.
- Never overwrite old versions in `paper/versions/` — always a new
  filename.

**Common pitfalls.**
- **LaTeX compile loop.** Sometimes the writer introduces an error
  in `main.tex`, compile fails, writer tries to "fix" it, introduces
  another error, etc. Interrupt if you see three consecutive failed
  compiles.
- **Missing `\cite{}`.** The writer may reference a paper by name in
  prose but forget `\cite{}`. Compile will warn about undefined
  references — check the log.
- **Figure path wrong.** `\includegraphics{../analysis/figures/...}`
  is relative to `paper/`, not the project root.

---

## 6. Reviewer — critical peer review

**Job.** Read the latest paper draft plus all supporting materials.
Produce a structured review listing issues by severity. Give a
verdict. Be harsh but fair.

**Runs on.** `opus`, effort `max`. Same reason as the writer — review
quality matters.

**Tools.** `Read`, `Write`, `Glob`, `Grep`. No `Bash`, no web — the
reviewer only reads the project and writes reviews.

**Inputs.**
- `GOAL.md`
- `paper/main.pdf` (latest versioned PDF)
- `paper/main.tex`
- `analysis/figures/`, `analysis/tables/`
- `theory/`
- `code/src/` — yes, the reviewer reads the code too, to check
  reproducibility
- `meetings/feedback.md`
- Prior reviews in `review/`

**Outputs.**
- `review/review_v<N>.md` — structured review with these sections:
  - **Verdict** (Accept / Minor / Major / Reject)
  - **Summary of the contribution** (2-3 sentences)
  - **Strengths** (bullets)
  - **Major issues** (P0 — must fix)
  - **Minor issues** (P1 — should fix)
  - **Nits** (P2 — typos, formatting)
  - **Specific comments** (inline, with section / equation / figure
    references)
- `PROGRESS.md` and `logs/<descriptive_name>.md`

**Workflow.**

1. Read all inputs above.
2. Produce a review file `review/review_v<N>.md`.
3. For each issue, suggest a concrete fix.
4. Be specific: cite section numbers, equation numbers, figure
   numbers.
5. Append to `PROGRESS.md` and write a descriptive log.

**Review criteria.**
- **Claims vs evidence** — does each claim have a figure, table, or
  derivation?
- **Methodology** — are baselines fair? seeds fixed? datasets
  appropriate?
- **Theory** — are derivations correct? assumptions stated?
- **Writing** — is the structure clear? are symbols defined? typos?
- **Reproducibility** — could a reader re-run the experiments from
  the code?
- **Novelty and positioning** — does related work cover the right
  landscape?

**Hard rules.**
- Never be nice. Harsh-but-fair is the goal.
- Never edit `paper/`. The writer handles revisions.
- Never commit or push.
- Never declare `Accept` unless there are genuinely no P0 issues.

**Common pitfalls.**
- **Too-early `Accept`.** If the reviewer returns Accept on the first
  review, the spec may be too lenient. Edit `.claude/agents/reviewer.md`
  to tighten the criteria.
- **Vague comments.** A good review says "Eq. (7) has a sign error
  — the minus should be plus, see Arbabi-Mezic 2017 Eq. (12)". A bad
  review says "equations look off". If you see vague comments, push
  back and re-run with explicit instructions.
- **Reviewing old PDF.** If `paper/versions/` has multiple PDFs, the
  reviewer should read the **newest**. Check that the review mentions
  the right version number.

---

## 7. Cost and model assignment

Quick recap of who runs on what:

| Agent | Model | Effort | Why |
|---|---|---|---|
| surveyor | sonnet | high | Lots of short reads, not hard reasoning |
| theorist | opus | max | Math verification — best model earns its cost |
| coder | sonnet | high | Code generation is sonnet's strong suit |
| analyst | sonnet | high | Mostly scripting + interpreting numerical results |
| writer | opus | max | Paper quality is the most expensive mistake |
| reviewer | opus | max | Review quality matters as much as paper quality |

If a project is cost-constrained, the obvious tradeoffs are to drop
theorist or reviewer to sonnet. You can do this by editing the
`model:` field in the agent frontmatter. Do not ship these changes
back to the template unless the lab decides to make it the default.

---

## 8. Editing an agent spec

The agent specs are under `.claude/agents/<name>.md`. Each is about
30–60 lines. To edit one:

1. Open the file in your editor.
2. Change the body (instructions) or the frontmatter (model / tools /
   effort) as needed.
3. Save and commit — project-specific edits stay in your project
   repo, they do not affect the template or other projects.
4. Type `continue` to dispatch the next agent with the new spec.

If you make an edit that seems useful for every lab project (not just
yours), open a PR against `lab-research-template` to merge it upstream.

---

## What to read next

- When something breaks: [`07-troubleshooting.md`](07-troubleshooting.md)
