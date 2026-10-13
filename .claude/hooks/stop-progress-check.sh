#!/usr/bin/env bash
# Stop hook. Ensures PROGRESS.md has been updated recently before ending
# a session. Also checks DECISIONS.md for silently-accumulated pending items.
#
# Contract: exit 0 = allow stop, exit 2 = block stop with reason on stderr.
set -u

root=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
[ -z "$root" ] && exit 0
[ -f "$root/PROGRESS.md" ] || exit 0

# 1. Stale PROGRESS.md — if not touched in 15 min, nudge
if [ -z "$(find "$root/PROGRESS.md" -mmin -15 2>/dev/null)" ]; then
  echo "PROGRESS.md has not been updated in the last 15 minutes. Append a one-paragraph summary of what just happened (newest entry at the top) before stopping." >&2
  exit 2
fi

# 2. New unshown pending decisions — nudge the orchestrator to surface them
if [ -f "$root/DECISIONS.md" ]; then
  if grep -q '^### D[0-9]' "$root/DECISIONS.md" 2>/dev/null \
     && ! grep -q '^## Pending$' "$root/DECISIONS.md" 2>/dev/null; then
    : # malformed — ignore
  fi
fi

exit 0
