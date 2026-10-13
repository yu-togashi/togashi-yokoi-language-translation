---
description: Show the current pipeline state, recent progress, and open decisions.
---

Give the PI a concise status report. Do NOT dispatch any agents.

## Steps

1. Read `STATUS.md` — show the pipeline table
2. Read `HEARTBEAT.md` — show dispatch count and last agent
3. Read the top 10 lines of `PROGRESS.md` — recent work
4. Read `DECISIONS.md` — list any Pending items
5. `ls meetings/raw/` vs `ls meetings/summaries/` — any unprocessed transcripts?
6. `git log --oneline -10` — recent commits
7. `git status` — any uncommitted changes

## Report format

```
## Pipeline
<STATUS.md pipeline table>

## Recent progress (last 5 entries)
<top 5 PROGRESS.md entries>

## Open decisions
<list of pending DECISIONS.md items, or "none">

## Unprocessed transcripts
<count + filenames, or "none">

## Health
- Dispatches this invocation: N / 20
- Last agent: <name>
- Working tree: clean | <N changes>
- Last commit: <hash> <message>

## Next action
<what /continue would do next, without dispatching it>
```
