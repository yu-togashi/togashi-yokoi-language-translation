# 07 — Troubleshooting and Safety Mechanics

**Read time:** ~10 minutes. Bookmark this chapter. Come back when
something breaks.

This chapter covers: (1) the safety rails already in place, so you
know *why* things are allowed or blocked; (2) a symptom → fix table
for the most common problems; and (3) a short recipe library for
recovering from specific disasters.

---

## 1. The safety rails

Three layers protect you. Understanding them makes troubleshooting
faster.

### 1.1 Global safety (lives in `~/.claude/`)

Installed by `lab-claude-dotfiles`. These apply to **every project on
your laptop**, not just this one. They block:

- Any `rm` or `rmdir` — hard block. Use `/trash` instead.
- `sudo`, `git push --force`, `git reset --hard`, `git clean -fdx`.
- Writes to `.env`, credentials, SSH keys.
- Outgoing network except: `arxiv.org`, `github.com`,
  `scholar.google.com`, `raw.githubusercontent.com`,
  `docs.anthropic.com`.

If one of these global rules blocks a legitimate operation, the fix
is usually **not** to remove the rule. Instead, find the right way
around it (e.g., use `/trash` instead of `rm`, use one of the
allow-listed hosts, etc.).

### 1.2 Project-local permissions (`.claude/settings.json`)

This file auto-allows common dev tools specific to a lab project:

- `poetry run`, `poetry install`, `python`, `pytest`
- `./compile_paper.sh`, `pdflatex`, `bibtex`, `latexmk`
- `git add`, `git commit`, `git push origin main`, `git pull`,
  `git fetch`, `git checkout`, `git branch`, `git merge`
- `mkdir -p`, `touch`, `cp`, `mv * .trash/*`

If an agent stops to ask permission for a command you use all the
time, add it to the `permissions.allow` list, commit, and continue.

**Do not** remove the `hooks` section from `settings.json` — that is
what wires up `post-agent-commit.sh` and `stop-progress-check.sh`.
Without those, auto-commit and progress tracking break.

### 1.3 Project hooks (`.claude/hooks/*.sh`)

Two shell scripts enforce project hygiene.

**`post-agent-commit.sh`** fires after a writer-class subagent
(`coder`, `analyst`, `writer`) finishes. It:

1. Stages the agent's changes (excluding forbidden paths: `data/`,
   `meetings/raw/`, `.env`, `*.pem`, `id_rsa*`, `credentials*`).
2. Runs `python -m py_compile` on any staged `.py` files; aborts if
   there is a syntax error.
3. Commits to `agent/auto/<date>` (creating the branch if needed,
   never directly to `main`).
4. Pushes best-effort; if push fails (offline, etc.), keeps going.
5. Returns the working tree to the previous branch.

**`stop-progress-check.sh`** fires when Claude Code tries to end a
session. It:

1. Refuses to stop if `PROGRESS.md` has not been updated in the last
   15 minutes.
2. Does a soft sanity check on `DECISIONS.md` formatting.

If you see "PROGRESS.md has not been updated in the last 15 minutes",
that is this hook. Append a one-paragraph summary (newest first) and
retry. See [`02-anatomy.md`](02-anatomy.md) section 2.4.

### 1.4 The trash box (`.trash/`)

**No `rm`, ever.** Files that need to be removed are *moved* to
`.trash/YYYY-MM-DD/` via the `/trash` command or the `trash-file`
skill, and the move is logged in `logs/trash.md`. The PI is the only
one who ever permanently deletes from `.trash/`.

This exists because a single wrong `rm` can erase weeks of agent
work. The trash box gives you a recovery window.

---

## 2. Symptom → fix table

Search (Ctrl-F) for your symptom.

| Symptom | Cause | Fix |
|---|---|---|
| `/continue` stops immediately, says "pending decision" | An agent raised a decision that blocks progress | Open `DECISIONS.md`, fill in **Resolution** on the pending item(s), save, `continue` |
| `/continue` stops, says "unprocessed transcript" | Raw transcript in `meetings/raw/` with no matching summary | Type `/meeting`, review the generated summary, then `continue` |
| `/continue` stops, says "dispatch cap reached" | You ran 20 agents in one invocation | `/checkpoint` to consolidate, then fresh `continue` |
| Agent asks for permission on a common command | Command not in `.claude/settings.json` allow list | Add it to `permissions.allow`, commit, retry |
| Agent tries to `rm` something, gets blocked | Global rule (always) | Use `/trash <path>` instead |
| `post-agent-commit: refuses to stage forbidden paths` | Agent wrote a file under `data/`, `meetings/raw/`, `.env`, etc. | Move the file out, or rename it, then retry |
| `post-agent-commit: Python syntax errors in staged files` | Agent wrote invalid Python | The agent should retry; if it does not, read the staged `.py` file, fix the syntax error, re-commit manually |
| `stop-progress-check: PROGRESS.md has not been updated in the last 15 minutes` | Session about to end but no progress entry | Append a one-paragraph summary to `PROGRESS.md` (newest first) and retry |
| `/checkpoint` says "working tree dirty" on `main` | Uncommitted changes on `main` | `git status` to see what; commit if intentional, `/trash` if not |
| `/checkpoint` says "tests fail" | `poetry run pytest -q` found a failing test | Read the failure, dispatch the coder to fix (`continue`), or fix manually; then re-checkpoint |
| `compile_paper.sh` fails pass 1 | LaTeX syntax error in `main.tex` or a section file | Read `paper/main.log` (last 60 lines printed on failure). Common causes: unescaped `%`, `&`, `_`, `#`, missing `}`, missing `\begin`/`\end` pair |
| `compile_paper.sh` warns "undefined references" | A `\cite{key}` uses a key not in `references.bib`, or a `\ref{label}` uses a label that does not exist | Either add the citation to `references.bib` or fix the typo in the key |
| Figure in paper is missing | `\includegraphics{../analysis/figures/FILE.pdf}` path wrong | Path is relative to `paper/`. It should be `../analysis/figures/FILE.pdf`, not `analysis/figures/FILE.pdf` |
| Agent wrote to `paper/` when it should not have | Agent spec violation | Revert that agent's changes (`git checkout agent/auto/<date> -- paper/` is NOT the way — use `git reset <file>` on the agent branch), then edit the agent spec in `.claude/agents/` to tighten the rule |
| The writer rebuilt a figure instead of asking the analyst | Agent spec violation | Same fix: revert and tighten the spec |
| Agent stuck in a loop re-running itself | Usually a verification mismatch — agent says done but output not found | Check `STATUS.md`; the orchestrator should have logged the mismatch in `DECISIONS.md`. Resolve |
| `HEARTBEAT.md` counter growing without finishing anything | Same as above, or a bad `STATUS.md` table | `Ctrl+C`. Read `STATUS.md` for the stage row. Fix by hand, `continue` |
| An agent produced a hallucinated citation | Surveyor cannot find a real paper it "remembers" | Delete the fake entry from `references.bib`, flag it in `DECISIONS.md`, re-run the surveyor with a `meetings/feedback.md` note to be stricter |
| You want to interrupt a runaway agent right now | — | `Ctrl+C`. Claude stops at the next safe point. Then `git status` to see what is half-written |
| You want to "undo" a whole day of agent work | You realize the pipeline went off the rails | **Do not** `git reset --hard`. Instead: create a new branch at the last known-good commit on `main`, `git checkout <that branch>`, proceed. The bad agent work stays on its `agent/auto/<date>` branch as a record |
| Push fails | Remote not configured, or permissions | `git remote -v`; confirm you can `git push` a trivial commit by hand; check lab org access |
| `/meeting` does nothing on a transcript you just dropped | Filename wrong, or already in `.hashes` | Check `meetings/summaries/.hashes` — if the raw file's SHA is already there, Claude thinks it was processed. Rename the raw file (or remove the hash line) and retry |

---

## 3. Recovery recipes

### 3.1 "An agent made a mess on its branch"

Say `coder` wrote a bunch of files, committed to
`agent/auto/2026-04-15`, and you realize the work was wrong. You have
not checkpointed yet, so `main` is unaffected.

```bash
# View what the agent did
git log agent/auto/2026-04-15 --oneline

# Option A: just abandon the branch, do not merge it in /checkpoint
#   Next /checkpoint will see the branch, merge it, and you WILL get
#   the bad work on main. To prevent that, delete the branch locally:
# (Note: deleting a branch does not delete commits — they live until gc'd.)
git branch -D agent/auto/2026-04-15     # safe — no file deletion, just moves HEAD reference

# Option B: keep the branch as a record, but exclude from /checkpoint
#   Rename it so /checkpoint does not pick it up:
git branch -m agent/auto/2026-04-15 agent/rejected/2026-04-15_coder_bad_hankel
```

Option B is preferred for a research repo — the rejected work is
evidence when you ask yourself later "why did we not take that approach".

### 3.2 "The writer corrupted `main.tex`"

The writer introduced a LaTeX error that `compile_paper.sh` cannot
resolve. It is still on an `agent/auto/<date>` branch. Recovery:

```bash
# See what the writer changed
git diff main agent/auto/2026-04-15 -- paper/

# Revert just the writer's changes to paper/main.tex, keep everything else
git checkout main -- paper/main.tex   # this is SAFE — no reset --hard

# Or revert the whole paper/ folder to its state on main
git checkout main -- paper/

# Then run compile to confirm it's building again
./compile_paper.sh
```

Follow up with a `meetings/feedback.md` note to the writer about the
specific LaTeX construct that broke, so the next writer run does not
repeat the mistake.

### 3.3 "I deleted something I didn't mean to"

If it went through `/trash`, it is recoverable:

```bash
# Find it
ls .trash/*/                       # browse by date

# Restore it
mv .trash/2026-04-15/important_file.md original/path/important_file.md

# Log the restore to logs/trash.md for audit
echo "$(date +'%Y-%m-%d %H:%M')  RESTORED .trash/2026-04-15/important_file.md → original/path/important_file.md   reason: deleted in error" >> logs/trash.md
```

If it went through `rm` (despite the global block) or `git reset
--hard`, the global safety rules should have stopped you. If they did
not, that is a lab-dotfiles bug — report it.

### 3.4 "Poetry says it cannot find Python 3.11"

```bash
# Check pyenv sees it
pyenv versions

# Install if missing
pyenv install 3.11.0

# Make sure .python-version is in place
cat .python-version    # should print 3.11.0

# Re-run poetry install
poetry install
```

If `poetry install` still complains, the virtualenv may be pointing
at the wrong Python:

```bash
# Nuke the stale venv (it is gitignored, safe to lose)
/trash .venv                       # inside Claude Code
# OR
mv .venv .trash/$(date +%F)/venv   # from the shell
poetry install
```

### 3.5 "Agent finished but its work is uncommitted on main"

**Symptom.** A subagent (coder, analyst, writer, etc.) returned cleanly.
`git branch` does **not** show `agent/auto/<date>`. `git status` shows the
agent's files as untracked or modified on `main`.

**Cause.** The `post-agent-commit.sh` hook did not fire. Known case:
background-mode subagents (`run_in_background=true`) may not emit a
`SubagentStop` event, or Claude Code may not set `CLAUDE_SUBAGENT_NAME`
in the hook environment.

**How to diagnose.**
```bash
tail -40 logs/hook_debug.log           # gitignored; every hook invocation logs here
```
If `logs/hook_debug.log` has no entry matching the time the agent
finished, the hook never fired. If it has an entry but ends in
`result: blocked on …`, the hook fired but refused the commit for a
stated reason (forbidden paths, syntax errors, etc.).

**How to recover.**
1. The orchestrator's `/continue` command now runs the hook *manually*
   after every agent return, as a defensive safety net. If the automatic
   hook failed but the defensive run succeeded, you will see the commit
   land on `agent/auto/<date>` a moment later.
2. If both failed, run the hook yourself:
   ```bash
   ./.claude/hooks/post-agent-commit.sh
   ```
   It is idempotent — a clean tree produces no commit.
3. Still nothing? Inspect `git status`, stage the files manually
   (excluding forbidden paths like `.env`, `data/`, `meetings/raw/`),
   and commit to `agent/auto/$(date +%F)` by hand.
4. Report the incident upstream on the `lab-research-template` issue
   tracker with the contents of `logs/hook_debug.log`.

### 3.6 Parallel-agent race on shared state files

**Symptom.** After dispatching multiple agents in parallel (e.g., the
Foundation stage's surveyor + theorist + coder), `/checkpoint` or a
manual merge of `agent/auto/<date>` branches into `main` produces
merge conflicts on `STATUS.md`, `HEARTBEAT.md`, `PROGRESS.md`, and
`DECISIONS.md`. Sometimes also on `survey/*.md` or `theory/*.md`.

**Cause.** When multiple agents run in parallel, they all write to the
same worktree on `main` (Claude Code does not yet support per-agent
`git worktree` isolation). Each agent `Edit`s shared state files
independently, and the `post-agent-commit.sh` hook snapshots the
entire worktree at every `SubagentStop` — so each agent's commit
contains a slightly different version of `STATUS.md` etc. When the
side branches are merged, git sees add/add conflicts on those files.

A related symptom: if Agent A finishes and its hook fires while Agent
B is still mid-write, Agent A's commit will include Agent B's partial
files. Harmless content-wise but confusing when reading history.

**How to recover.**
1. The merge conflicts are almost always trivially resolvable:
   - For `survey/*.md`, `theory/*.md`: take `--theirs` (the later,
     completed version of each file).
   - For `STATUS.md`, `HEARTBEAT.md`, `PROGRESS.md`: manually merge so
     the final state reflects every agent's updates (e.g., all three
     rows marked `done`, all three agents `idle`).
   - For `DECISIONS.md`: a straightforward append-only merge (each
     agent's new decision block survives).
2. After resolving, `git commit` the merge commit and push.

**How to avoid it in the first place.**
- **Serialize agents when possible.** If a stage doesn't *have* to be
  parallel, dispatch sequentially. The dispatch cap is 30 per
  `/continue`, so even a 6-stage pipeline with 2-3 agents per stage
  fits comfortably.
- **Accept the conflict.** For truly independent parallel work
  (Foundation = literature + theory + code), the conflicts are
  trivial and the time savings usually outweigh the merge cost.

**Future fix (not yet implemented).** Per-agent `git worktree`
isolation: each parallel subagent gets its own checkout, writes there,
and the orchestrator merges at the end. This would eliminate the race
entirely. It adds complexity and has not been prioritized.

### 3.7 Agent spec edit not taking effect — Claude Code session registry is cached at start

**Symptom.** You edit `.claude/agents/<name>.md` mid-session (e.g. add
`Bash` to the writer's tools list), dispatch that agent, and the new
tool or behavior does not appear. The agent seems to be running on
the pre-edit spec.

**Cause.** When Claude Code starts a session, it reads every
`.claude/agents/*.md` file **once** and registers the resulting
agent types with their tools list. The running session does NOT
re-read those files on each dispatch. Edits to the spec files
therefore do not affect the current session's agent registry — they
only take effect when a new `claude` session starts.

This bit us during the Wave 1.4 #1 rollout, documented as `D17` in
the `template_test_sekizawa_causality` dogfood run: the writer spec
was updated to include `Bash`, but the running session's writer
subagent still had the old tool list. The change is valid; it just
requires a session restart to take effect.

**How to recover.**

1. **Quit and relaunch Claude Code** (`Ctrl-D` or `/exit`, then
   `claude` again). The new session will re-read the agent specs
   and pick up your changes.
2. **Or, use the orchestrator's defensive-compile step** for the
   writer specifically: if the writer's new Bash capability is what
   you need, `/continue` already runs `./compile_paper.sh` yourself
   after a writer dispatch (see `.claude/commands/continue.md` step
   7f). The defensive compile is the safety net that makes the
   writer Bash feature session-restart-tolerant.

**How to verify a spec change took effect after restart.** Dispatch
the agent with a trivial "echo your tool list" prompt, or check the
Agent tool's own registry (printed somewhere in the system prompt,
or via `/agents` if your version of Claude Code supports it).

**Workaround for rapid iteration.** If you are iterating on an agent
spec during a single session, either (a) use the orchestrator-side
workflow (direct Edit/Bash/etc. from the main thread), or (b) plan
for one Claude Code session per spec revision.

### 3.8 "I cannot remember what state the project is in"

Always the same answer:

```
> /status
```

If `/status` itself looks wrong, read `STATUS.md`, `PROGRESS.md` (top
5 entries), and `logs/checkpoint_<latest>.md` in that order. That is
the full state reconstructed from source.

---

## 4. Things you should never do (recap)

From [`05-daily-workflow.md`](05-daily-workflow.md), repeated here
because they are the most common ways to break things:

- **Never `rm`.** Use `/trash`.
- **Never `git reset --hard`** or `git push --force`. They are
  globally blocked for a reason.
- **Never edit `CLAUDE.md` Part 1.** Only Part 2.
- **Never push directly to `main` while agents are running.** Use
  `/checkpoint`.
- **Never commit `.env`, credentials, or large datasets.**
- **Never run `pip install`.** Always `poetry add` or `poetry
  install`.

---

## 5. When the docs are wrong

These docs are human-written and out of date the moment something in
the template changes. If you find a discrepancy between what you read
here and what actually happens:

1. Trust the code / the spec file over the docs.
2. Open an issue (or a PR) against `lab-research-template` with the
   specific claim that is wrong and what actually happens.

Good candidates to check first:

- `README.md` — the reference sheet
- `CLAUDE.md` Part 1 — the orchestrator rules
- `.claude/agents/<name>.md` — agent specs
- `.claude/commands/<name>.md` — slash command prompts
- `.claude/hooks/*.sh` — hook scripts
- `bootstrap.sh` — project creation

---

## Where to go when the tutorial is not enough

- Read the one-line reference sheet at
  [`../README.md`](../README.md).
- Read the agent spec file for any agent you have questions about.
- Read `.claude/commands/continue.md` for the exact orchestrator
  prompt.
- Ask a labmate.
- Open an issue on `lab-research-template`.

Good luck, and remember: `STATUS.md` first, `PROGRESS.md` second, and
only then ask for help.
