#!/usr/bin/env bash
# SubagentStop hook. After a subagent finishes, auto-stage + sanity-check +
# commit its changes to an agent/auto/<date> side branch. Never commits
# directly to main.
#
# This hook is best-effort. If CLAUDE_SUBAGENT_NAME is absent (known case:
# background-mode subagents may not set it), we still commit under a
# generic "subagent" label. The orchestrator's /continue loop also runs
# this script manually after every agent return as a defensive safety
# net in case the SubagentStop event itself does not fire.
#
# The script is idempotent: clean tree → no commit.
#
# Branch-switching strategy (v3):
#   Rather than "git checkout <target-branch>" with staged files (which
#   fails when the two branches diverge), we:
#     1. Stage changes on the current branch (main).
#     2. Create the commit object on the CURRENT branch.
#     3. Move (git branch -f) the agent/auto branch pointer to that commit.
#     4. Reset the current branch back to its original HEAD (soft reset,
#        so the working tree and index are left as-is — but the commit is
#        now recorded on the agent/auto branch, not on main).
#   This is purely a ref-manipulation trick — no checkout, no merge,
#   no stash. Works even when branches diverge significantly.
#
# Contract: exit 0 = allow subagent stop, exit 2 = block with reason on stderr.
set -u

root=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
[ -z "$root" ] && exit 0
cd "$root"

# ------------------------------------------------------------------
# Diagnostic log — helps us verify the hook actually fires.
# Append-only, gitignored (logs/hook_debug.log). Last 200 lines only.
# ------------------------------------------------------------------
mkdir -p logs 2>/dev/null || true
if [ -f logs/hook_debug.log ] && [ "$(wc -l < logs/hook_debug.log 2>/dev/null)" -gt 400 ]; then
  tail -200 logs/hook_debug.log > logs/hook_debug.log.tmp && \
    mv logs/hook_debug.log.tmp logs/hook_debug.log
fi
{
  echo "---"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) post-agent-commit fired"
  echo "  CLAUDE_SUBAGENT_NAME=${CLAUDE_SUBAGENT_NAME:-<unset>}"
  echo "  pwd=$(pwd)"
  echo "  status=$(git status --porcelain | wc -l | tr -d ' ') files changed"
} >> logs/hook_debug.log 2>/dev/null || true

agent="${CLAUDE_SUBAGENT_NAME:-subagent}"

# Nothing to do if the tree is clean
if [ -z "$(git status --porcelain)" ]; then
  echo "  result: clean tree, nothing to commit" >> logs/hook_debug.log 2>/dev/null || true
  exit 0
fi

# ------------------------------------------------------------------
# Refuse to stage forbidden paths
# ------------------------------------------------------------------
forbidden=$(git status --porcelain | awk '{print $NF}' | \
  grep -E '^(data/|meetings/raw/|\.env|.*secret.*|.*\.pem$|id_rsa)' || true)
if [ -n "$forbidden" ]; then
  echo "post-agent-commit refuses to stage forbidden paths:" >&2
  echo "$forbidden" >&2
  echo "Move these out of the working tree before continuing." >&2
  echo "  result: blocked on forbidden paths" >> logs/hook_debug.log 2>/dev/null || true
  exit 2
fi

# ------------------------------------------------------------------
# Stage everything except forbidden paths and framework artifacts.
# Use --ignore-errors so that gitignored files listed explicitly
# don't cause the whole add to abort.
# ------------------------------------------------------------------
git add --ignore-errors -A -- . \
  ':(exclude)data' \
  ':(exclude)meetings/raw' \
  ':(exclude).env' \
  ':(exclude)*.pem' \
  ':(exclude)id_rsa*' \
  ':(exclude)credentials*' \
  ':(exclude).claude/agent-memory' \
  ':(exclude)logs/hook_debug.log' \
  2>/dev/null || true

# ------------------------------------------------------------------
# Sanity check: Python syntax on staged .py files
# ------------------------------------------------------------------
py_changed=$(git diff --cached --name-only | grep -E '\.py$' || true)
if [ -n "$py_changed" ]; then
  err=$(poetry run python -m py_compile $py_changed 2>&1 || true)
  if [ -n "$err" ]; then
    echo "post-agent-commit aborted: Python syntax errors in staged files" >&2
    echo "$err" >&2
    git reset HEAD -- . >/dev/null
    echo "  result: blocked on Python syntax error" >> logs/hook_debug.log 2>/dev/null || true
    exit 2
  fi
fi

# If everything was excluded, nothing to commit
if [ -z "$(git diff --cached --name-only)" ]; then
  echo "  result: nothing left to commit after exclusions" >> logs/hook_debug.log 2>/dev/null || true
  exit 0
fi

# ------------------------------------------------------------------
# Commit to today's agent/auto branch WITHOUT switching branches or
# advancing the current branch.
#
# v4 technique (plumbing): use git write-tree + git commit-tree with an
# explicit parent = agent/auto tip (or HEAD if the branch doesn't exist
# yet). Then git update-ref to move the branch pointer. Then git reset
# to clear the index (worktree untouched).
#
# This fixes two earlier bugs:
#   v2 (-B): reset agent/auto to HEAD, destroying earlier commits.
#   v3 (git commit + reset --mixed): the commit's parent was always
#        the current HEAD (main), so on subsequent fires the new
#        commit was a child of main rather than of agent/auto's
#        actual tip, orphaning earlier commits.
#
# With commit-tree we control the parent explicitly, so commits chain
# correctly on agent/auto regardless of what main is pointing at.
# ------------------------------------------------------------------
branch="agent/auto/$(date +%F)"
current=$(git rev-parse --abbrev-ref HEAD)
msg="auto($agent): subagent checkpoint $(date +%Y-%m-%dT%H:%M)"

# Parent for the new commit: the existing tip of agent/auto/<date> if
# it exists (locally or on origin), else the current HEAD.
if git show-ref --verify --quiet "refs/heads/$branch"; then
  parent_sha=$(git rev-parse "refs/heads/$branch")
elif git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
  parent_sha=$(git rev-parse "refs/remotes/origin/$branch")
  # Also create a local ref tracking origin, so update-ref below is clean.
  git branch "$branch" "origin/$branch" >/dev/null 2>&1 || true
else
  parent_sha=$(git rev-parse HEAD)
fi

# Write the current index as a tree object.
tree_sha=$(git write-tree 2>/dev/null) || {
  echo "post-agent-commit: git write-tree failed" >&2
  echo "  result: write-tree failed" >> logs/hook_debug.log 2>/dev/null || true
  exit 2
}

# Create the commit object with the explicit parent.
new_sha=$(echo "$msg" | git commit-tree "$tree_sha" -p "$parent_sha" 2>/dev/null) || {
  echo "post-agent-commit: git commit-tree failed" >&2
  echo "  result: commit-tree failed" >> logs/hook_debug.log 2>/dev/null || true
  exit 2
}

# Move (or create) the branch ref to point at the new commit.
git update-ref "refs/heads/$branch" "$new_sha" "$parent_sha" 2>/dev/null || \
  git update-ref "refs/heads/$branch" "$new_sha" 2>/dev/null || {
    echo "post-agent-commit: git update-ref failed for $branch" >&2
    echo "  result: update-ref failed" >> logs/hook_debug.log 2>/dev/null || true
    exit 2
  }

# Clear the index so the files show as untracked/modified on the
# current branch again (worktree is left alone). This prevents the
# hook from trying to re-stage the same content on the next fire.
git reset HEAD -- . >/dev/null 2>&1 || true

# Push best-effort (pushes the agent/auto branch, not main)
git push -u origin "$branch" 2>/dev/null || echo "post-agent-commit: push deferred"

echo "  result: committed to $branch as auto($agent)" >> logs/hook_debug.log 2>/dev/null || true
exit 0
