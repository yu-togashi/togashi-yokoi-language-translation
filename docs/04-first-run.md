# 04 — Your First `continue` Command, Step by Step

**Read time:** ~10 minutes. Assumes you have finished
[`03-setup.md`](03-setup.md) and your project has a filled-in `GOAL.md`
and `CLAUDE.md` Part 2.

This chapter walks through what happens when you type `continue` for the
very first time. By the end, one or more agents will have run, their
output will be on disk, and the pipeline state will have advanced.

---

## 1. Launch Claude Code

From inside your project directory:

```bash
cd ~/Documents/Claude/Projects/my_first_project
claude
```

You should see the Claude Code prompt. It looks like a shell prompt
but it speaks to Claude, not to bash. You can also type `!<command>`
at this prompt to run a shell command — useful if you need to check
`git status` without leaving the session.

---

## 2. Type `continue`

```
> continue
```

(Just `continue`, no slash. The slash version `/continue` is the same
thing, just explicit.)

This invokes the orchestrator, which runs the prompt in
`.claude/commands/continue.md`. Here is what Claude does, in order,
every single time you type `continue`.

---

## 3. The orchestrator loop, spelled out

### 3.1 Read state

Claude reads four files:

- `STATUS.md` — to find the next pending stage
- `GOAL.md` — to know what the project is trying to do
- `DECISIONS.md` — to check for blocking questions
- `meetings/feedback.md` — if it exists, to honor accumulated guidance

Plus it lists `meetings/raw/` to check for unprocessed transcripts.

### 3.2 Run guards

Before dispatching any agent, Claude checks:

| Guard | What it checks | What happens if it fires |
|---|---|---|
| **Pending decision** | Any `### D<NN>` block in `DECISIONS.md` without a Resolution | Stop, show the PI the open decisions |
| **Unprocessed transcript** | Any file in `meetings/raw/` without a matching summary in `meetings/summaries/` | Invoke `/meeting` first, then stop for PI confirmation |
| **Dispatch cap** | `HEARTBEAT.md` counter ≥ 20 | Stop, tell the PI to `/checkpoint` and start a fresh `continue` |

If any guard fires, Claude stops and prints what it saw. You fix the
issue and type `continue` again.

### 3.3 Pick the next agent

Claude scans the `STATUS.md` table for the first row marked `pending`
whose prerequisites are met. For a fresh theory-paper project, the
first row is usually **Foundation — survey** → the surveyor agent.

Claude announces what it's about to do, something like:

```
Next action: Foundation stage — dispatching the surveyor to produce a
literature review of Koopman-based causality detection, Granger
causality, CCM, Hankel-DMD realization theory, and Krylov causal
inference. Expected output: survey/*.md files and additions to
paper/references.bib.
```

### 3.4 Dispatch the agent

Claude invokes the Agent tool, passing the agent's spec plus a focused
prompt about the current task. The agent runs as a *subagent* — it
does not pollute your main conversation. You will see it print status
updates in the main conversation while it works.

**This can take a while.** A surveyor run with dozens of papers to
summarize can take 10–20 minutes. A theorist run verifying every
equation in a paper can take 20–40 minutes. **Do not interrupt** unless
you see the agent going clearly off course.

### 3.5 After the agent returns

The orchestrator does five things:

1. **Verify the output file exists.** If the agent said "done" but the
   expected output is not on disk, the orchestrator logs an entry in
   `DECISIONS.md` and stops. This is the "no unverified done" rule.
2. **Update `STATUS.md`.** The pipeline row flips from `in_progress`
   to `done`, with the output path filled in.
3. **Prepend to `PROGRESS.md`.** A one-paragraph summary of what the
   agent did, timestamped, newest at the top.
4. **Write a descriptive log.** A file at
   `logs/<descriptive_name>.md` — for example,
   `logs/literature_survey_koopman.md`. This is the detailed audit
   trail for the run.
5. **Auto-commit via the hook.** The `post-agent-commit.sh` hook fires
   as the subagent stops. It stages the agent's changes (excluding
   forbidden paths), runs a Python syntax check if any `.py` files
   changed, commits to `agent/auto/<date>`, and best-effort pushes. You
   will see it print one or two lines in the main conversation.

### 3.6 Loop

Back to step 3.1, unless a guard stops it. The orchestrator runs until:

- The pipeline is done.
- A guard fires (decision pending, transcript unprocessed, dispatch cap hit).
- An agent fails in a way the orchestrator cannot auto-resolve.
- You hit `Ctrl+C`.

---

## 4. What you should see in the terminal

Rough shape of a first run on a theory-paper project:

```
> continue

[orchestrator] Reading STATUS.md, GOAL.md, DECISIONS.md
[orchestrator] No pending decisions.
[orchestrator] No unprocessed transcripts.
[orchestrator] Dispatch counter: 0/20
[orchestrator] Next action: surveyor — literature review

[surveyor] Starting. Reading GOAL.md and documents/main.pdf.
[surveyor] Identified ~15 candidate topics.
[surveyor] Searching arxiv for "Koopman causality"
...
[surveyor] Wrote survey/sugihara_2012_ccm.md
[surveyor] Wrote survey/arbabi_2017_koopman.md
...
[surveyor] Appended 14 citations to paper/references.bib
[surveyor] Done.

[post-agent-commit] Staging 15 files. Python syntax: n/a.
[post-agent-commit] Committed auto(surveyor): subagent checkpoint 2026-04-11T14:22
[post-agent-commit] Pushed agent/auto/2026-04-11

[orchestrator] Verified: survey/ has 14 new files, references.bib updated.
[orchestrator] Updated STATUS.md: Foundation — survey → done.
[orchestrator] Prepended PROGRESS.md entry.
[orchestrator] Wrote logs/literature_survey_koopman_causality.md
[orchestrator] Dispatch counter: 1/20

[orchestrator] Next action: theorist — verify derivations in documents/main.pdf
[theorist] Starting. Reading GOAL.md and documents/main.pdf.
...
```

The exact output varies a lot depending on your project. The
**important thing** is that between each agent dispatch, you see the
orchestrator verify, update files, and announce the next step.

---

## 5. What to do while agents run

You have two good options and one bad one.

### Good: read what they write, as they write it

Open `PROGRESS.md` and `STATUS.md` in your editor. They update as
agents run. You can also open files under `survey/`, `theory/`, or
`code/src/` to peek at output as it lands.

### Good: read the detailed log after each agent

After an agent finishes, open `logs/<descriptive_name>.md`. It contains
the agent's own summary of what it did, often with more detail than the
`PROGRESS.md` paragraph.

### Bad: walk away and stop reading

You are supposed to notice if something goes wrong. Agents can
hallucinate citations, misread a derivation, or write tests that pass
but check the wrong thing. The template catches many failure modes
automatically, but not all.

**Rule of thumb:** after every 2–3 agent runs, skim
`PROGRESS.md` and open one of the output files. If something looks
wrong, interrupt and fix it.

---

## 6. How to interrupt

Press `Ctrl+C`. Claude Code will stop the current agent cleanly at the
next safe point (usually within a few seconds).

After an interrupt:

- Run `git status` to see what is half-written.
- If there are partial changes you want to keep: let the
  `post-agent-commit.sh` hook run by typing a trivial prompt and then
  stopping. Or commit manually.
- If there are partial changes you want to discard: use `/trash <path>`
  for individual files, or `git checkout -- <path>` for uncommitted
  edits. **Do not use `git reset --hard`** unless you are sure.

---

## 7. When the orchestrator stops "voluntarily"

The loop exits for one of these reasons. Each has a specific response.

| Why it stopped | What to do |
|---|---|
| `DECISIONS.md` has a pending item | Open `DECISIONS.md`, fill in **Resolution** on the blocking item(s), add your initials + date, save. Type `continue`. |
| Unprocessed transcript in `meetings/raw/` | Type `/meeting`. Read the generated summary. If it looks right, type `continue`. |
| Dispatch counter hit 20 | Type `/checkpoint` to merge, then `continue` fresh. |
| An agent failed verification | Read `DECISIONS.md` — the orchestrator logged what failed. Fix, type `continue`. |
| Pipeline finished | Congratulations. `/checkpoint` and celebrate. |

---

## 8. Reading your first `PROGRESS.md` entry

After the first agent finishes, open `PROGRESS.md`. The top entry
should look like:

```markdown
## 2026-04-11 — surveyor: literature review done

Surveyor produced 14 structured notes under `survey/` covering
Granger causality, CCM, Koopman/DMD, Hankel-DMD, realization theory
(Ho-Kalman, ERA), and Krylov-based causal inference. Also appended
14 citations to `paper/references.bib`. Full log at
`logs/literature_survey_koopman_causality.md`. No open decisions.
Next: theorist.
```

If that looks roughly right, the system is working as designed.

---

## 9. Your first commit from agent work

Check the git log:

```bash
git log --oneline --all -10
```

You should see something like:

```
* 2a3f4d1 auto(surveyor): subagent checkpoint 2026-04-11T14:22  (agent/auto/2026-04-11)
* 1b2c3d4 PI setup: fill GOAL.md and CLAUDE.md Part 2           (main)
* f5e6d7c Initial scaffold from lab-research-template            (main)
```

The `auto(surveyor)` commit is on a side branch (`agent/auto/2026-04-11`),
not on `main`. That is correct — `main` stays clean until you
`/checkpoint`.

---

## 10. End of your first session

You have seen one full orchestrator cycle. Recap:

- You typed `continue`.
- Claude read the state and picked the next agent (surveyor).
- The surveyor produced output under `survey/` and `paper/references.bib`.
- A hook auto-committed the changes to a side branch.
- The orchestrator updated `STATUS.md`, `PROGRESS.md`, and `logs/`.
- It then moved on to the next agent, and the next, until a guard
  stopped it or you interrupted.

**If you are ready to stop for the day**, type `/checkpoint`. That
merges all the agent side branches into `main`, runs tests, compiles
the paper (if any), pushes, and writes a checkpoint summary. Details
in [`05-daily-workflow.md`](05-daily-workflow.md).

---

## What to read next

- Day-to-day operations: [`05-daily-workflow.md`](05-daily-workflow.md)
- Deeper understanding of each agent: [`06-agents.md`](06-agents.md)
- When something breaks: [`07-troubleshooting.md`](07-troubleshooting.md)
