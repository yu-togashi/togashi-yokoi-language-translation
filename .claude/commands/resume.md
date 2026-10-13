---
description: Generate or refresh RESUME.md — a session-handoff document for picking the project back up after a break or restart.
---

You are producing or updating `RESUME.md` at the project root. This is
a **session-handoff document** — it should let a fresh Claude Code
session (you tomorrow, a labmate, or yourself after a laptop restart)
pick the project back up with a single read.

`/status` is a *dashboard* ("where are we right now"). `/resume` is a
*handoff* ("how do I pick this up"). The two overlap but optimise for
different audiences: `/status` is for the PI during a session;
`/resume` is for the next session.

## Steps

1. **Read state.** In order:
   - `GOAL.md` (full) — what the project is trying to do
   - `CLAUDE.md` Part 2 — the project-specific rules and pipeline
   - `STATUS.md` — pipeline table + blockers
   - `HEARTBEAT.md` — dispatch counter + agent status
   - `PROGRESS.md` (top 20 lines) — what just happened
   - `DECISIONS.md` Pending section — what is blocking `/continue`
   - `meetings/feedback.md` — accumulated PI guidance
   - `ls meetings/raw/` + `ls meetings/summaries/` — unprocessed transcripts
   - `git log --oneline -5` on `main` and any recent `agent/auto/*` branches
   - `git status --short`

2. **Distill into a RESUME.md with this structure:**

```markdown
# RESUME — <project-name>

Context hand-off document. Read this at the start of every new
Claude Code session before typing `continue`.

## The problem

(1 paragraph from GOAL.md + CLAUDE.md Part 2: what is this project
trying to accomplish, and what is the source material.)

## Current state (as of <date>)

- **Pipeline stage:** <current stage from STATUS.md>
- **Next action:** <what /continue would do next>
- **Open blockers:** <bulleted list from DECISIONS.md Pending + any
  meetings/raw/ unprocessed transcripts + any HEARTBEAT health-check
  failures>
- **Dispatch counter:** <N / 30>
- **Last agent dispatched:** <name, date, status>
- **Test status:** <"not checked" or "N passing" from last pytest run>

## What has been delivered so far

(1–3 bullets per completed stage, pulled from STATUS.md Notes column.
Short. Full narrative is in PROGRESS.md and logs/.)

## What to do on resume

Numbered procedure, concrete and sequenced:

1. `cd <project-root>`
2. Launch `claude`
3. First action: `/status` (confirms state hasn't drifted)
4. If there are pending decisions, resolve them in `DECISIONS.md`
5. Run `continue`
6. <any project-specific notes, e.g., "background agents from the
   prior session may still be running — check task-notification
   output">

## Key conventions (reminders for the next session)

(A handful of bullets from CLAUDE.md Part 2 that are easy to forget:
seeds, units, honesty clause, never `rm`, `poetry run` discipline.
Three-to-six bullets max.)

## Files to read first

- `STATUS.md` — the authoritative pipeline state
- `PROGRESS.md` top entry — what just happened
- `DECISIONS.md` Pending — what is blocking advance
- <1–2 recent log files that matter, e.g., the last agent's log>

## Links

- Project repo: <git remote -v | head -1>
- Source paper / data / starting artifact: <pointer to documents/>
```

3. **Write the result to `RESUME.md` at the project root.** If
   `RESUME.md` already exists, overwrite it — it is always a snapshot
   of the current state, never an append-only log.

4. **Commit + push.** After writing, `git add RESUME.md && git commit
   -m "Refresh RESUME.md for session handoff"`. Push to `origin main`
   if the remote is configured. The commit is orchestrator-level, not
   agent work — it does NOT go on an `agent/auto/<date>` branch.

5. **Tell the PI where the file is and which state files it was
   generated from.** Do not dispatch any other agent.

## Must not

- Do NOT invent state that is not in the source files. If
  `STATUS.md` says the pipeline is at Foundation, do not write RESUME
  saying it is at Validation.
- Do NOT duplicate `PROGRESS.md` narrative — link to it instead.
- Do NOT include anything secret (look at `git status --short` before
  committing; if any file under `data/`, `.env`, `secrets/` etc. is
  mentioned in RESUME.md by accident, remove it).
- Do NOT dispatch any agents. `/resume` is a state-capture command,
  not a dispatch command. Use `/continue` for dispatch.
