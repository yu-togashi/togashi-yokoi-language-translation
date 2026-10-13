# Orchestrator Heartbeat — togashi-yokoi-language-translation

Health-check checklist. Updated by the orchestrator on each `/continue`
invocation and each agent dispatch.

## Current invocation

- **Started:** (orchestrator fills in)
- **Dispatches this invocation:** 0 / 30
- **Last agent dispatched:** —
- **Last checkpoint:** —

## Agent status

| Agent | Last run | Status | Notes |
|-------|----------|--------|-------|
| surveyor | — | idle | |
| theorist | — | idle | |
| coder | — | idle | |
| analyst | — | idle | |
| writer | — | idle | |
| reviewer | — | idle | |

## Health checks (every /continue)

- [ ] No stale agents (>30 min in `in_progress`)
- [ ] No unresolved DECISIONS.md items
- [ ] No unprocessed transcripts in `meetings/raw/`
- [ ] Dispatch counter < 30 (configurable per project in CLAUDE.md Part 2)
- [ ] `git status` shows no merge conflicts
- [ ] Tests pass (`poetry run pytest -q` if code exists)
- [ ] Disk usage in `.trash/` is not runaway

If ANY check fails, the orchestrator STOPS and reports to the PI.
