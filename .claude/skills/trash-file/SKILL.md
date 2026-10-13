---
name: trash-file
description: Safe file removal. Moves files to .trash/YYYY-MM-DD/ instead of calling rm. Use whenever an agent needs to remove or "delete" a file.
---

# Trash File

Agents never call `rm`. When you need to remove a file, use this skill.

## Steps

1. Create today's trash subfolder if missing:
   ```bash
   mkdir -p ".trash/$(date +%F)"
   ```
2. Move the file:
   ```bash
   mv "<path>" ".trash/$(date +%F)/$(basename <path>)"
   ```
3. Append an entry to `logs/trash.md`:
   ```
   $(date +"%Y-%m-%d %H:%M")  <path>  →  .trash/$(date +%F)/$(basename <path>)   reason: <short reason>
   ```
4. Report what was moved in your PROGRESS.md entry.

## Edge cases

- **Target is a directory** → move the whole directory (mv handles this)
- **Target does not exist** → report that and do nothing; do not fail loudly
- **Collision** (file with same basename already in today's trash folder) →
  append a short timestamp to disambiguate: `foo.txt.1403` etc.
- **Target is in `.git/`, `.claude/`, or `documents/`** → STOP and flag in
  `DECISIONS.md`; these paths are load-bearing and should not be trashed
  without explicit PI approval

## Why not rm

- The global PreToolUse hook blocks all `rm` and `rmdir` calls
- The lab safety rule requires a staging folder before any permanent deletion
- `.trash/` is gitignored so mistakes do not pollute git history
- The PI sweeps `.trash/` manually outside Claude when they trust the contents
