---
description: Continue the orchestrator loop — dispatch the next appropriate agent.
---

You are the orchestrator. Follow the steps below (authoritative) and the principles in `CLAUDE.md` Part 1.

**Hard dispatch cap:** track the dispatch count in `HEARTBEAT.md`. If you have
already dispatched 30 agents in this `/continue` invocation, STOP and confirm
with the PI. (Projects can override this cap in `CLAUDE.md` Part 2.)

## Steps

1. Read `STATUS.md`, `PROGRESS.md`, `DECISIONS.md`, `meetings/feedback.md`,
   and `ls meetings/raw/` to check for unprocessed transcripts.
2. If `DECISIONS.md` has any pending items → STOP and show them to the PI.
3. If any file in `meetings/raw/` has no matching summary in
   `meetings/summaries/` → invoke `/meeting` first, then STOP for PI confirmation.
4. Check `HEARTBEAT.md` dispatch counter. If ≥30 (or whatever Part 2 sets),
   STOP and confirm with PI.
5. Identify the next agent from the `STATUS.md` pipeline table.
6. Dispatch it via the Agent tool; increment the `HEARTBEAT.md` dispatch counter.
7. After the agent returns:
   a. **Wait-for-wrap-up.** Verify both `STATUS.md` was updated AND the
      agent's descriptive log file exists in `logs/`. If either is missing,
      wait briefly and re-check once (the agent may still be writing its
      final files). If still missing, log the discrepancy to `DECISIONS.md`
      and STOP.
   b. Prepend a one-paragraph entry to `PROGRESS.md` (orchestrator-style,
      not the agent's own summary which the agent already prepended).
   c. Confirm the agent wrote a descriptive log to `logs/`.
   d. **Defensive commit** — run `./.claude/hooks/post-agent-commit.sh`
      manually. The hook is idempotent (clean tree → no commit) and
      covers the case where the automatic `SubagentStop` hook did not
      fire (known failure mode for background-mode subagents).
   e. Check `logs/hook_debug.log` for a recent entry. If the hook is
      failing silently across multiple dispatches, flag a template bug
      in `DECISIONS.md`.
   f. **Defensive paper compile (writer only)** — if the agent that
      just returned is the writer, verify that `paper/main.pdf` exists
      and is newer than every `paper/sections/*.tex` and `paper/main.tex`.
      If not, run `./compile_paper.sh` manually yourself, then copy
      `paper/main.pdf` to `paper/versions/main_v<NN>_<YYYY-MM-DD>.pdf`
      (incrementing `<NN>`). The writer agent spec includes `Bash` and
      `./compile_paper.sh` in its tool list, so a writer dispatched in
      a fresh session should run the compile itself; this defensive
      step catches the case where (a) the session's agent registry was
      cached before a `.claude/agents/writer.md` edit, (b) the compile
      failed mid-writer-dispatch, or (c) the writer forgot. See
      `docs/07-troubleshooting.md` §3.8 for the full story.
8. If `DECISIONS.md` gained new items → STOP and show them to the PI.
9. Otherwise → loop back to step 1 until a checkpoint, a pending decision,
   or the dispatch cap.

## Notes

- Parallel dispatch: if `CLAUDE.md` Part 2 describes a stage with multiple
  agents that can run in parallel (e.g. Foundation = surveyor + theorist +
  coder independently), dispatch them in a single message with multiple
  Agent tool uses. Increment the dispatch counter by the number dispatched.
- Background vs foreground: use `run_in_background=true` for agents that
  typically run longer than ~10 minutes (theorist, writer, long analyst
  sweeps). Handle completion notifications as they arrive. For short
  agents, foreground is simpler.
- Defensive commits happen **per-agent**, not per-dispatch. If you
  dispatch three agents in parallel, run the hook manually three times
  (once after each completes) so each agent's work lands on
  `agent/auto/<date>` under its own commit.
