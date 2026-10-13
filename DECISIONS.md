# Pending Decisions — togashi-yokoi-language-translation

Agents and the orchestrator add items here when they need PI input. The
orchestrator STOPS if any item is pending.

## Format

Each decision gets a unique ID, a timestamp, an impact assessment, and a
proposed action. The PI resolves by editing the **Resolution** field and
appending their initials and the date.

```
### D<NN> — <short title>            (EXAMPLE — not a real decision)
- **Raised by:** <agent-name>
- **Date:** YYYY-MM-DD
- **Impact:** low | medium | high
- **Context:** (one paragraph)
- **Options considered:**
  - A: ...
  - B: ...
- **Recommendation:** (agent's best guess, may be wrong)
- **Resolution:** (PI fills this in; until then, considered pending)
```

---

## Pending

*(none yet)*

## Resolved

*(none yet)*
