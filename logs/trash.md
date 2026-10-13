# Trash Log

Every file "removal" is recorded here. Format:

```
YYYY-MM-DD HH:MM  <original-path>  →  .trash/YYYY-MM-DD/<basename>   reason: <why>
```

Entries are appended by the `/trash` command, the `trash-file` skill, and
`compile_paper.sh` (LaTeX build artifacts).

---

## (no entries yet)
2026-04-11 22:08  TUTORIAL.md  →  .trash/2026-04-11/TUTORIAL.md.superseded   reason: superseded by docs/ split
2026-10-14 00:00  CLAUDE_part2_variant.md  →  .trash/2026-10-14/CLAUDE_part2_variant.md   reason: merged into CLAUDE.md Part 2
2026-10-14 00:00  docs/  →  .trash/2026-10-14/   reason: template tutorial; lives in upstream lab-research-template
2026-10-14 00:00  variants/  →  .trash/2026-10-14/   reason: only used by bootstrap.sh
2026-10-14 00:00  STATUS.md PROGRESS.md HEARTBEAT.md DECISIONS.md  →  .trash/2026-10-14/   reason: orchestrator state files; progress tracked in tasks/todo.md
2026-10-14 00:00  .claude/agents/ .claude/hooks/ .claude/skills/orchestrate/  →  .trash/2026-10-14/   reason: auto-agent orchestration not used
2026-10-14 00:00  .claude/commands/{continue,status,resume,checkpoint}.md  →  .trash/2026-10-14/   reason: auto-agent orchestration not used
