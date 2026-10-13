---
description: Safely "remove" a file by moving it to .trash/ (no rm ever).
---

Usage: `/trash <path>` (or `/trash <path1> <path2> ...`)

You are safely removing files by moving them to `.trash/YYYY-MM-DD/` instead
of calling `rm`. This is the ONLY way agents are allowed to remove files in
lab projects.

## For each path the PI gives you

1. Verify the file exists: `ls <path>`
2. Ensure today's trash subfolder exists: `mkdir -p ".trash/$(date +%F)"`
3. Move the file: `mv <path> .trash/$(date +%F)/$(basename <path>)`
4. Append one line to `logs/trash.md`:
   ```
   YYYY-MM-DD HH:MM  <original-path>  →  .trash/YYYY-MM-DD/<basename>   reason: <why>
   ```
5. Tell the PI what was moved and where.

## Never
- Call `rm` or `rmdir`
- Empty `.trash/` yourself — that is the PI's job
- Trash files in `.git/`, `.claude/`, or `documents/` without explicit approval
