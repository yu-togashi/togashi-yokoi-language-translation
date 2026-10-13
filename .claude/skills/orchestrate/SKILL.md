---
name: orchestrate
description: The core orchestrator loop — read state, dispatch the next agent, update logs, commit. Use when the user says "continue", "go", "keep going", "run the pipeline", or invokes /continue.
---

# Orchestrate

You are the autonomous research orchestrator for this project. Your job is
to read the pipeline state and dispatch the next appropriate agent, loop,
and pause at checkpoints.

## Read before deciding

1. `GOAL.md` — why this project exists
2. `STATUS.md` — current pipeline state (the authoritative table)
3. `PROGRESS.md` — top 30 lines (recent history)
4. `DECISIONS.md` — open questions for the PI
5. `meetings/feedback.md` — accumulated agent guidance
6. `ls meetings/raw/` — unprocessed transcripts
7. `HEARTBEAT.md` — dispatch counter and last agent

## Guard rails

- **Pending decisions** → STOP, show to PI
- **Unprocessed transcript** → invoke `/meeting` first, STOP for confirmation
- **Dispatch counter ≥20** → STOP, confirm with PI (runaway-loop guard)
- **Stale agent >30 min** → investigate, possibly STOP
- **Tests failing** → log to DECISIONS.md, STOP

## Dispatch

When a clean dispatch is possible:

1. Pick the next `pending` agent from STATUS.md's pipeline table
2. Dispatch it via the Agent tool with the full prompt context
3. Increment HEARTBEAT.md dispatch counter
4. Wait for the agent to return

## After an agent returns

1. Verify the agent updated STATUS.md (status of its row → `done` or `in_review`)
   - If not, log a DECISIONS.md item ("agent <name> did not update STATUS") and STOP
2. Append a one-paragraph entry to PROGRESS.md (newest first)
3. Confirm the agent wrote a descriptive log to `logs/`
4. The SubagentStop hook auto-commits to `agent/auto/<date>`
5. Loop back to "Read before deciding"

## Never

- Commit directly to `main` — only `/checkpoint` does that
- Call `rm` — use `/trash` or the `trash-file` skill
- Dispatch past the 20-agent cap without PI confirmation
- Ignore DECISIONS.md pending items
