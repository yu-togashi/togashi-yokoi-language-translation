# 01 — Overview and Mental Model

**Read time:** ~8 minutes. No commands to run. Just read.

By the end of this chapter you will understand: what this template *is*,
what problem it solves, the three concepts you need to hold in your head,
and the life cycle of a typical project. You will not yet know how to do
anything. That is [`03-setup.md`](03-setup.md)'s job.

---

## 1. What problem does this template solve?

Running a full research project — literature survey, theory verification,
implementation, experiments, writing, peer review — is a sequence of
many small tasks. A student doing this alone spends a lot of time on
**coordination** rather than research:

- "What should I work on next?"
- "Did I already try that?"
- "Where did I put those results?"
- "What did my advisor ask me to do last Thursday?"

Claude Code can do most of the small tasks, but if you just chat with it
one question at a time, it has no memory of the project across sessions,
no idea of the overall pipeline, and no consistent place to save its
work. You end up coordinating Claude the same way you would coordinate
yourself — except now there are two of you.

**This template fixes that** by giving Claude a *state machine* that
encodes the project's progress on disk, a set of *specialist agents*
that each own one job, and an *orchestrator loop* that reads the state
and dispatches the next agent automatically. The state is plain
Markdown, so a human can read and edit it too. The agents are plain
Markdown specs, so you can tune them. Nothing is hidden inside a
database or a proprietary format.

The net effect: you spend most of your time on *research direction*
(what to investigate, how to interpret results, when to stop) and very
little on *execution coordination*.

---

## 2. The three concepts

Hold these three ideas in your head and everything else will make sense.

### 2.1 State files

Four plain Markdown files at the project root record **where the project
currently is**:

- `STATUS.md` — a table of pipeline stages, each marked `pending`,
  `in_progress`, `done`, or `blocked`. Think of it as a trello board
  flattened into a single file.
- `PROGRESS.md` — a log of what happened, newest first. Every agent
  appends one paragraph after it runs. You read this to catch up.
- `DECISIONS.md` — questions the agents need the PI to answer. The
  orchestrator refuses to proceed if any decision is pending.
- `HEARTBEAT.md` — a dispatch counter and health check. Caps runaway
  loops at 20 agent dispatches per `continue` invocation.

These files are the **single source of truth**. If `STATUS.md` says a
stage is `done`, it is done. If `PROGRESS.md` says nothing happened, then
nothing happened. Never trust chat history over these files.

> **Why Markdown, not a database?**
> Two reasons. First, a student can read the state directly on GitHub in
> the browser without launching Claude Code — no app to install, no API
> to call. Second, if Claude gets something wrong, you can fix it with
> any text editor. No schema migration, no admin UI.

### 2.2 The six agents

Each specialized job in a research project is owned by exactly one
agent. The six agents and their one-line jobs:

| Agent | Job | Writes to |
|---|---|---|
| **surveyor** | Literature review, related work, find datasets | `survey/`, `paper/references.bib` |
| **theorist** | Verify and extend mathematical derivations | `theory/` |
| **coder** | Implement algorithms, write unit tests | `code/src/`, `code/tests/` |
| **analyst** | Run experiments, sweeps, generate figures | `code/experiments/`, `analysis/` |
| **writer** | Draft and revise the paper in LaTeX | `paper/` |
| **reviewer** | Critical peer review of the draft | `review/` |

Each agent has a spec in `.claude/agents/<name>.md` that says what it
must do, what it must not do, and where it writes. The spec is the
**contract** between you and the agent. You can read and edit it.

Two facts worth absorbing now:

1. **One agent = one job = one output folder.** The writer never touches
   `code/`. The coder never touches `paper/`. This is enforced by the
   specs.
2. **Writer and reviewer run on Claude Opus (best model); the rest on
   Sonnet.** That is a cost/quality tradeoff — paper quality and review
   quality are the most expensive mistakes, so we pay for the best model
   there.

Full details in [`06-agents.md`](06-agents.md).

### 2.3 The orchestrator

The **orchestrator** is not a separate program. It is a *role* Claude
plays when you type `continue` at the Claude Code prompt. When you type
`continue`, Claude:

1. Reads `STATUS.md`, `GOAL.md`, `DECISIONS.md`, `meetings/feedback.md`.
2. Runs **guards**: is there a pending decision? An unprocessed meeting
   transcript? Has the dispatch cap been hit? If yes, stop.
3. Picks the first `pending` row from `STATUS.md` whose prerequisites
   are done.
4. Dispatches the corresponding agent as a subagent.
5. When the agent returns, updates `STATUS.md`, appends to
   `PROGRESS.md`, writes a log to `logs/`, and bumps the dispatch
   counter in `HEARTBEAT.md`.
6. Loops back to step 1. Stops when a guard fails or the pipeline is
   finished.

Every agent run is **auto-committed** to a side branch called
`agent/auto/<date>` by a hook — never directly to `main`. You merge to
`main` later via `/checkpoint`. This keeps `main` clean and gives you a
safe rollback point if an agent makes a mess.

---

## 3. The life cycle of a project

A typical theory-paper project goes through roughly seven phases. You
never have to memorize this — the pipeline is spelled out in your
`STATUS.md` table — but seeing the shape helps.

```
   PHASE                          AGENTS INVOLVED       DURATION
   ─────────────────────────────────────────────────────────────
1. Setup                          (you, once)           30 min
2. Foundation                     surveyor, theorist,   few hours
                                  coder (parallel)
3. Validation                     coder, analyst        few hours
4. Benchmarking                   analyst, surveyor     few hours
5. Real data                      analyst               1-2 hours
6. Paper draft                    writer, surveyor      1-2 hours
7. Review-revise loop             reviewer → writer/    iterative,
                                  analyst/coder →       until the
                                  reviewer → ...        reviewer
                                                        says ACCEPT
```

"A few hours" above is agent clock time — not your time. Your time in
phases 2–7 is reading summaries, answering decisions in `DECISIONS.md`,
and dropping occasional meeting transcripts into `meetings/raw/`.

---

## 4. Your daily job, in two sentences

- **Every day you work:** launch Claude, type `continue`, read the
  summaries, answer any `DECISIONS.md` items. At the end of the session,
  type `/checkpoint`.
- **Whenever you meet with your PI:** drop the transcript into
  `meetings/raw/`, type `/meeting`. From then on, every agent will read
  the new guidance.

Everything else is covered in [`05-daily-workflow.md`](05-daily-workflow.md).

---

## 5. What this template is NOT

To avoid surprises later, here is what the template explicitly does
**not** try to be:

- **Not a framework for production code.** The coder agent writes
  research-quality Python — type-hinted, tested, reproducible — but not
  a deployable product.
- **Not a replacement for your PI.** The orchestrator stops whenever a
  decision needs human judgment. It is designed to coordinate, not to
  decide.
- **Not a pipeline scheduler like Airflow or Snakemake.** It is
  agent-based, not DAG-based. Stages run in the order `STATUS.md` lists
  them; parallelism inside a phase is described in `CLAUDE.md` Part 2.
- **Not a memory system.** The auto-memory in `~/.claude/` is
  machine-local and ephemeral. Persistent knowledge lives in
  `meetings/feedback.md` and `.claude/rules/`, both of which are
  versioned in git.
- **Not a substitute for reading the paper you are reproducing.** You
  still have to understand the science. Agents help you execute faster;
  they do not replace scientific taste.

---

## 6. What to read next

- If you want to understand *what is on disk*, read
  [`02-anatomy.md`](02-anatomy.md) next.
- If you want to jump in and start a project, read
  [`03-setup.md`](03-setup.md).

Most beginners do better reading the anatomy first, because it removes
the "what is this folder?" anxiety before you have to type commands.
