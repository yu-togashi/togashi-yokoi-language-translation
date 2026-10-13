# 05 — Daily Workflow

**Read time:** ~12 minutes.

You have run your first agent (see [`04-first-run.md`](04-first-run.md)).
Now: how do you actually work with this template day after day? This
chapter covers the recurring operations — checking status, handling
meetings, checkpointing, resuming the next morning, and the
review-revise loop at the end of a project.

---

## 1. A typical day in one picture

```
   morning                                                     evening
   ───────                                                     ───────
   launch                                      /checkpoint
   claude        continue          continue    (merge, push)
     │              │                  │              │
     ▼              ▼                  ▼              ▼
  read /status   dispatch loop     dispatch loop    close session
                 (agents run,      (more agents,
                  you read         more reading)
                  summaries,
                  answer
                  decisions)
                              ^
                              │
                      /meeting here if you
                      drop a new transcript
```

Most days you type three things: `continue`, maybe `/meeting`, then
`/checkpoint`.

---

## 2. Starting the day: `/status`

After launching `claude`, the first command most people type is
**not** `continue`. It is `/status`:

```
> /status
```

`/status` reads `STATUS.md`, `HEARTBEAT.md`, the top of `PROGRESS.md`,
and any pending decisions, then prints a one-page summary **without
dispatching any agents**. Example output:

```
## Pipeline
| Stage | Agent | Status | Output |
| 1. Foundation — survey | surveyor | done | survey/ |
| 2. Foundation — theory | theorist | done | theory/ |
| 3. Foundation — code   | coder    | in_progress | code/src/ |
| 4. Validation          | analyst  | pending | analysis/ |
...

## Recent progress (last 5 entries)
- 2026-04-11  theorist: verified Eqs. (3)-(8) of main.pdf, flagged one issue in D02
- 2026-04-11  coder: implemented Hankel matrix builder + truncated SVD pseudoinverse
- 2026-04-11  surveyor: literature survey, 14 references added
- 2026-04-10  orchestrator: pipeline initialized

## Open decisions
- D02: Finite-dimensional Koopman assumption — how strict should the check be?

## Unprocessed transcripts
none

## Health
- Dispatches this invocation: 0 / 20
- Last agent: theorist
- Working tree: clean
- Last commit: 2a3f4d1 auto(coder): ...

## Next action
If you /continue: the orchestrator will first pause on D02 (open decision).
```

**Why start with `/status`:** before you dispatch anything new, you
want to know what is blocking the pipeline. D02 in the example above
would block `/continue`. Better to resolve it *first*, then run
`continue` and let the loop proceed.

---

## 3. Resolving decisions in `DECISIONS.md`

Open `DECISIONS.md` in your editor. Find the block for the decision
you want to resolve. It looks like this:

```markdown
### D02 — Finite-dimensional Koopman assumption
- **Raised by:** theorist
- **Date:** 2026-04-11
- **Impact:** high
- **Context:** The source paper's Proposition 2 relies on a
  finite-dimensional Koopman invariant subspace. In practice this
  is approximated by a finite Krylov basis of size m. How strict
  should we be when verifying this assumption in the proof?
- **Options considered:**
  - A: Treat as approximate, accept with caveat in paper
  - B: Demand explicit bound on approximation error
  - C: Drop the proof, replace with empirical verification only
- **Recommendation:** B — we should have an explicit error bound.
- **Resolution:** (empty)
```

Fill in the `Resolution` field with your choice, add initials and date,
save:

```markdown
- **Resolution:** B — insist on explicit error bound; theorist should
  derive one following Arbabi-Mezic 2017 Section 4. — MO 2026-04-11
```

Now `/continue` will un-block on this item and proceed.

**Bulk-resolving.** If there are several decisions at once, resolve
them all before typing `continue`. Each one you leave open will trigger
a stop.

---

## 4. Running the dispatch loop: `continue`

Same command, every day:

```
> continue
```

The orchestrator reads state, runs guards, dispatches agents, and
loops until a guard stops it. You do not have to type `continue` for
each agent — one `continue` runs the whole chain until it stops for a
reason.

**When to skim, when to read:**

- Skim `STATUS.md` and `PROGRESS.md` after every 2–3 agent dispatches.
- Read the latest `logs/<descriptive_name>.md` in full for any agent
  whose output you are going to build on (e.g., read the theorist log
  before the coder runs).
- Read agent prints in the live session for anything theorist or
  reviewer says — these two agents often produce judgment calls that
  are worth attention.

---

## 5. The meeting workflow

This is the **main mechanism** for steering a project. If the PI tells
the student something in a meeting, the student does not need to type
that guidance into Claude by hand. They drop the transcript into
`meetings/raw/`, and `/meeting` does the rest.

### 5.1 Drop the transcript

```bash
cp ~/Downloads/zoom_transcript.vtt meetings/raw/2026-04-18_pipeline-review.md
```

Naming convention: `YYYY-MM-DD_<short-slug>.md` (or `.txt`). The date
matters — summaries are stored alongside with the same basename.

Any format works. Otter exports, Zoom `.vtt`, plain text, Japanese,
English, or a mix. The `/meeting` command is built to handle
multilingual, messy transcripts.

### 5.2 Run `/meeting`

```
> /meeting
```

Claude will:

1. Find every file in `meetings/raw/` that has no matching summary in
   `meetings/summaries/` (tracked via a hidden `.hashes` file of
   SHA-256 sums, so nothing gets processed twice).
2. For each one, read it (chunking if it is very long), load context
   from `GOAL.md`, `STATUS.md`, `PROGRESS.md`, `DECISIONS.md`, and
   `meetings/feedback.md`.
3. Produce a structured summary at
   `meetings/summaries/<same-basename>.md` with sections:
   **TL;DR**, **Key points**, **Decisions**, **Open questions**,
   **Feedback for agents**, **Next actions**, **Reconsideration**,
   **Verbatim quotes** (if multilingual).
4. **Apply the summary** to the project:
   - Each Decision → appended to `DECISIONS.md` as a new pending item
     (until the PI resolves it)
   - Each Feedback bullet → appended to `meetings/feedback.md`
   - Each Next action → added to `STATUS.md` as a new row or
     re-prioritization
5. **Stop.** `/meeting` refuses to dispatch further agents — it wants
   the PI to review the changes first.

### 5.3 Review the diff

After `/meeting` finishes, Claude will print a short summary of what
changed in `STATUS.md`, `DECISIONS.md`, and `meetings/feedback.md`.
Read it. If anything is wrong, edit the files by hand. Then type
`continue` to resume the pipeline with the new guidance applied.

> **Why `meetings/feedback.md` is versioned in git.**
> Auto-memory (the `~/.claude/` memory system) is machine-local. If
> your labmate pulls the repo on their laptop, auto-memory will not
> follow. `meetings/feedback.md` is a normal git-tracked file, so it
> does follow. Use it for anything teammates need to see.

---

## 6. Ending the day: `/checkpoint`

When you are done working for the day (or whenever you want a clean
`main` to share), run:

```
> /checkpoint
```

`/checkpoint` does seven things:

1. **Verifies `main` is clean.** If there are uncommitted changes, it
   stops and asks you to deal with them.
2. **Lists and merges agent branches.** For each `agent/auto/<date>`
   branch, it squash-merges into `main` with a commit message like
   `checkpoint: merge agent/auto/2026-04-11`.
3. **Runs tests.** `poetry run pytest -q`. If any test fails,
   `/checkpoint` stops. It will not push broken code.
4. **Compiles the paper** (if `paper/main.tex` exists). Saves the
   output to `paper/versions/main_v<NN>_<YYYY-MM-DD>.pdf`.
5. **Pushes to `main`.** `git push origin main`.
6. **Writes a checkpoint summary** at `logs/checkpoint_<date>.md`:
   what was merged, test status, paper version produced, open
   decisions, next stage.
7. **Resets the dispatch counter** in `HEARTBEAT.md` back to 0.

**Read the checkpoint summary.** It is a one-page digest of
everything that happened in the session. Forwarding its content to
your PI is faster than waiting for them to read `PROGRESS.md`.

### 6.1 What if `/checkpoint` stops mid-way?

If tests fail or a merge conflict appears, `/checkpoint` stops and
tells you. Fix the issue and run `/checkpoint` again. The parts that
succeeded are idempotent (merge is skipped if the branch is already
merged, etc.), so re-running is safe.

Do **not** use `git reset --hard` or `git push --force` to "make it
go away". That is the fastest way to lose a day of agent work.

---

## 7. Resuming the next day

```bash
cd ~/Documents/Claude/Projects/my_first_project
claude

> /status          # see where things stand
> continue         # pick up where it left off
```

The orchestrator reads the state files and continues. No setup, no
configuration, no "where was I?". That is the whole point of the state
files.

If you have a new meeting transcript from the night before, drop it in
`meetings/raw/` before `continue`. The orchestrator will block on it
and prompt you to run `/meeting` first.

---

## 8. The review-revise loop

Once the writer has produced a first draft, the pipeline enters an
iterative loop:

```
            ┌──────────────┐
            │   reviewer   │
            │  writes review/review_v<NN>.md
            └──────┬───────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
 writer fixes  analyst fixes  coder fixes
 prose         figures/data   bugs
      │            │            │
      └────────────┼────────────┘
                   │
            ┌──────▼───────┐
            │ compile_paper.sh
            │ save PDF to paper/versions/
            └──────┬───────┘
                   │
                   ▼
              next iteration
                   │
         (until reviewer says ACCEPT)
```

Each cycle:

1. The reviewer writes `review/review_v<NN>.md` with a verdict
   (Accept / Minor / Major / Reject) and a numbered list of P0 (must
   fix), P1 (should fix), and P2 (nits) issues.
2. The orchestrator dispatches the appropriate agent for each issue
   class: writer for prose, analyst for new figures or numbers, coder
   for bug fixes.
3. Each agent's work is auto-committed to its side branch as usual.
4. The writer runs `compile_paper.sh` and saves a new dated PDF to
   `paper/versions/`.
5. The reviewer runs again on the new PDF.

Repeat until `review/review_v<NN>.md` says **Accept** with no P0
issues. At that point, `/checkpoint` one more time and the project is
submission-ready.

**Rules of the loop:**

- Never overwrite `review/review_v<NN>.md` — start `v<NN+1>`.
- Never overwrite old PDFs in `paper/versions/` — always a new filename.
- The reviewer must not "be nice" — harsh but fair is the goal. If the
  reviewer keeps returning Accept too quickly, the agent spec at
  `.claude/agents/reviewer.md` may need tightening.

---

## 9. What *you* should never do

- **Do not edit `CLAUDE.md` Part 1.** Part 2 only.
- **Do not run `rm` directly.** Use `/trash <path>` or the
  `trash-file` skill. Global hooks will block `rm` anyway.
- **Do not `git push origin main` manually while agents are running.**
  Let `/checkpoint` handle it.
- **Do not dispatch agents yourself by hand** unless you are debugging
  an agent spec. The state files will drift.
- **Do not edit `paper/main.tex` by hand** unless fixing something
  tiny (a typo the writer is unlikely to re-introduce). The writer is
  the source of truth for `paper/`.
- **Do not re-run `poetry install` randomly.** It is only needed when
  `pyproject.toml` changes.
- **Do not commit `.env`, credentials, or large datasets.** The hook
  blocks this by default, but do not test the safety net.

---

## 10. What *you* should do every session

1. Start with `/status`.
2. Resolve any pending decisions first.
3. Run `continue`. Read summaries as agents complete.
4. Drop new transcripts in `meetings/raw/` when meetings happen; run
   `/meeting`; review the diff.
5. End with `/checkpoint`.

That is the whole daily workflow.

---

## 11. Slash command reference

You have seen the six template slash commands in the daily-flow
sections above. This section is the consolidated catalog you can come
back to. Each command is a Markdown prompt file under
`.claude/commands/<name>.md`, which means you can read (and tune) the
exact instructions the command gives Claude.

| Command | One-line purpose | Dispatches agents? | When to use |
|---|---|---|---|
| `continue` or `/continue` | The main orchestrator loop — pick the next pending agent from `STATUS.md` and dispatch it | **Yes** | Once per day (or more) to advance the pipeline |
| `/status` | Pipeline dashboard — current stage, last 5 entries of `PROGRESS.md`, open decisions, health check | No | At the start of every session, before anything else |
| `/resume` | Session-handoff document — generate or refresh `RESUME.md` at the project root so a fresh session can pick up cleanly | No | Before stopping for the day, or before handing off to a labmate / another machine |
| `/meeting` | Process every unprocessed transcript in `meetings/raw/` into a structured summary + updates to `DECISIONS.md` / `meetings/feedback.md` / `STATUS.md` | No (but updates state) | After a PI meeting, before the next `continue` |
| `/checkpoint` | Merge agent side branches into `main`, run tests, compile the paper, push, write a checkpoint log, reset the dispatch counter | No (runs tests) | At the end of a work session, or when you need a clean `main` |
| `/trash <path>` | Safely "remove" a file by moving it to `.trash/YYYY-MM-DD/` and logging the move in `logs/trash.md`. Replaces `rm` everywhere in a lab project | No | Whenever you or an agent wants to delete a file |

### How slash commands work (using `/resume` as the walked-through example)

The slash-command mechanism is simple enough that you can understand
it from a single example. When you type `/resume` at the Claude Code
prompt:

1. **Claude Code looks for a file at `.claude/commands/resume.md`.**
   If the file exists, the command is defined for this project. If
   not, you get an "unknown command" error.
2. **Claude Code loads the contents of `.claude/commands/resume.md`
   as a prompt** and sends it to Claude (the assistant) as if you had
   typed it yourself. The top of the file looks like this:
   ```markdown
   ---
   description: Generate or refresh RESUME.md — a session-handoff document…
   ---

   You are producing or updating `RESUME.md` at the project root. …
   ```
   The frontmatter (`---` block) is metadata. The rest of the file is
   the actual prompt.
3. **Claude executes the prompt** — in `/resume`'s case, that means
   reading `STATUS.md`, `HEARTBEAT.md`, `PROGRESS.md`, `DECISIONS.md`,
   `GOAL.md`, `CLAUDE.md` Part 2, `meetings/feedback.md`, and a few
   `git` queries, distilling them into a `RESUME.md` at the project
   root, and committing the result.
4. **The result is shown in your Claude Code conversation.** For
   `/resume` specifically, Claude tells you where the new `RESUME.md`
   lives and which state files it was generated from. For `/status`,
   it prints the dashboard directly to the conversation.

Because the command is just a Markdown file, you can **read the exact
prompt Claude will run** without any guessing. Open
`.claude/commands/resume.md` in your editor. You will see the same
"Steps" section that Claude follows. If you disagree with a step, edit
the file and commit — the next `/resume` will use your edited version.

### Writing your own slash command

You can add project-specific commands by dropping a new Markdown file
under `.claude/commands/`. For example, a `/lint` command would live at
`.claude/commands/lint.md` and start with:

```markdown
---
description: Run project-wide linters and report the results.
---

Run the following commands in order and summarise the output:

1. `poetry run ruff check .`
2. `poetry run black --check .`
3. `poetry run mypy code/src/`

If any step fails, list the failing files and return the error
verbatim. Do not fix anything — just report.
```

Commit the file, relaunch `claude`, and `/lint` is available. This is
how the template's six commands were written; there is no magic.

### When to use each command (decision table)

| Situation | Command |
|---|---|
| I just launched `claude` and want to know where I am | `/status` |
| I want the orchestrator to advance the pipeline | `continue` or `/continue` |
| A new meeting transcript is in `meetings/raw/` | `/meeting` |
| An agent wrote a file that shouldn't exist | `/trash <path>` |
| End of work session; I want `main` clean and pushed | `/checkpoint` |
| I'm about to stop for the day (or hand off to a labmate) and want the next session to pick up without confusion | `/resume` |
| I want to run one of my own project-specific workflows | write a new command under `.claude/commands/` |

### The `/resume` vs `/status` distinction

Both read the state files, but they optimise for different audiences:

- **`/status`** is a *dashboard*. Short. Shown in the conversation.
  Updated every time you type the command. Good for "am I blocked
  right now?".
- **`/resume`** is a *handoff*. Longer. Written to `RESUME.md` on
  disk, committed, and pushed. Good for "a fresh session needs to pick
  up this project from scratch". Survives across laptop restarts,
  Claude Code restarts, and student-to-student handoffs.

Use both. `/status` during a session for quick checks, `/resume`
before you close the laptop for the day.

---

## What to read next

- Deeper understanding of each agent: [`06-agents.md`](06-agents.md)
- When something breaks: [`07-troubleshooting.md`](07-troubleshooting.md)
