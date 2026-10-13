# Pipeline Status — togashi-yokoi-language-translation

**Last updated:** (orchestrator auto-fills this)
**Current stage:** `init`
**Next agent:** none — waiting for PI to fill in GOAL.md and CLAUDE.md Part 2

## Pipeline state

| Stage | Agent | Status | Output | Notes |
|-------|-------|--------|--------|-------|
| 1. Foundation — survey | surveyor | pending | survey/ | Waiting for PI |
| 2. Foundation — theory | theorist | pending | theory/ | |
| 3. Foundation — code | coder | pending | code/src/ | |
| 4. Validation | analyst | pending | analysis/ | |
| 5. Benchmarking | analyst | pending | analysis/ | |
| 6. Real data | analyst | pending | analysis/real/ | |
| 7. Paper draft | writer | pending | paper/ | |
| 8. Review-revise loop | reviewer → writer | pending | review/, paper/versions/ | |

## Blockers

- PI has not filled in `GOAL.md` yet
- PI has not filled in `CLAUDE.md` Part 2 yet

## How to advance

Once `GOAL.md` and `CLAUDE.md` Part 2 are filled, type `continue` and the
orchestrator will pick the first pending stage from the table above.

(Live dispatch state lives in `HEARTBEAT.md` — do not duplicate it here.)
