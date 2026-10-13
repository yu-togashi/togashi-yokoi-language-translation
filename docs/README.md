# Beginner's Guide to `lab-research-template`

A complete walkthrough for a lab member who has **never used Claude Code
or this template before**. If you follow this guide in order, you will go
from "empty laptop" to "first agent running and committed" in about an
hour, and you will understand *why* each step matters, not just *what* to
type.

> **Already know the basics?** Go to [`../README.md`](../README.md) — it is
> the reference sheet. These docs are the narrative.

---

## Recommended reading order

Read these in order on your first project. Each chapter is short (5–15
minutes) and builds on the previous one.

| # | File | What you learn | Read it when |
|---|------|----------------|--------------|
| 1 | [`01-overview.md`](01-overview.md) | The mental model. What this template is, how the orchestrator thinks, why it's organized the way it is. | Before touching anything. |
| 2 | [`02-anatomy.md`](02-anatomy.md) | **Full folder/file tour.** Every folder, every key file, what it is for, who edits it, and when. | After the overview, before setup. This is the longest chapter; take your time. |
| 3 | [`03-setup.md`](03-setup.md) | One-time machine setup (`pyenv`, `poetry`, dotfiles) and how to bootstrap a new project. | When you are ready to actually create a project. |
| 4 | [`04-first-run.md`](04-first-run.md) | The first `continue` command, step by step. What the orchestrator does, what you see, how to read the output. | Right after `03-setup.md`. |
| 5 | [`05-daily-workflow.md`](05-daily-workflow.md) | `/status`, `/meeting`, `/checkpoint`, resuming the next day, the review-revise loop. | After your first agent has finished. |
| 6 | [`06-agents.md`](06-agents.md) | The six specialized agents in depth — job, workflow, constraints, output location. | When an agent does something surprising, or before you edit an agent spec. |
| 7 | [`07-troubleshooting.md`](07-troubleshooting.md) | Common problems, safety mechanics (trash box, hooks, permissions), how to interrupt a runaway agent. | Bookmark it. Come back when something breaks. |
| 8 | [`examples/sekizawa_causality_dogfood.md`](examples/sekizawa_causality_dogfood.md) | **What you actually get.** A real end-to-end run of the template on a 6-page theory preprint, showing every deliverable at every stage — 24 papers surveyed, theory verified to 1.25e-16, 31 tests passing, publishable LaTeX paper, two peer-review cycles ending in Accept. | After any of the reference chapters above, or **first** if you want to decide whether the template is worth using before learning the mechanics. |

---

## If you only have 15 minutes

Read the **Deliverables table** in
[`examples/sekizawa_causality_dogfood.md`](examples/sekizawa_causality_dogfood.md)
to see what the template actually produced on a real run, then read
[`01-overview.md`](01-overview.md) for the mental model. That is the
absolute minimum to decide whether to use the template and form a
realistic expectation of the output. Come back for the mechanics
when you are ready to bootstrap.

## If you are a PI, not a student

You mostly care about:

- [`01-overview.md`](01-overview.md) — so you know what you are looking at
- [`02-anatomy.md`](02-anatomy.md) — so you know where to read state on
  GitHub without launching Claude Code
- [`05-daily-workflow.md`](05-daily-workflow.md) — the meeting transcript
  workflow is your main steering mechanism

You do not need `04-first-run.md` or `06-agents.md` unless you are
customizing an agent.

## If something broke and you just want the answer

Go to [`07-troubleshooting.md`](07-troubleshooting.md) and search (Ctrl-F)
for the error message or symptom.

---

## Conventions used in these docs

- **Commands you type** are in `code font`. If they start with `$ `, type
  what is after the `$`. If they start with `>` inside a Claude Code
  session, type that at the Claude prompt.
- **File paths** are always relative to the project root unless stated
  otherwise.
- **"The PI"** means whoever owns the research direction — usually your
  supervisor, sometimes yourself.
- **"Agent"** means one of the six specialized Claude subagents defined
  in `.claude/agents/`. **"Orchestrator"** is the role Claude plays when
  you type `continue` — it is not a separate program.
- Sidebars in **blockquotes** like this one are optional context. You can
  skip them on a first read.

---

## Where to get help

1. Search these docs with Ctrl-F first.
2. Read the reference sheet at [`../README.md`](../README.md).
3. Read the agent spec at `.claude/agents/<name>.md` if an agent is
   behaving oddly.
4. Ask a labmate who has used the template before.
5. Open an issue on the `lab-research-template` repo.
