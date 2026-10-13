# Example — End-to-End Paper Reproduction

This chapter shows **what you get** when you apply `lab-research-template`
to a real theory-paper reproduction task, so you can form a realistic
expectation before bootstrapping your own project.

The example is a real run on the April-2026 preprint *"A Tractable and
Practical Method for Causality Detection from Partially Observed
Dynamics"* by Sekizawa & Oizumi. All artifacts are real and visible at
[`oizumi-lab/template_test_sekizawa_causality`](https://github.com/oizumi-lab/template_test_sekizawa_causality).

---

## One-sentence summary

Starting from a 6-page preprint, the template produced a
peer-reviewed, publishable LaTeX manuscript (accepted on the second
review cycle) in **less than 2 hours of PI wall-clock time**, plus
agent compute.

---

## What the PI did

Four things, in order. That's the entire human workload.

1. **Bootstrap** (~30 min). Cloned the template, ran
   `./bootstrap.sh my_project --variant theory-paper`, filled in
   `GOAL.md` (research question + deliverables) and `CLAUDE.md` Part 2
   (problem statement + pipeline + domain conventions), dropped the
   source PDF into `documents/`, created a private GitHub repo.
2. **First `/continue`** (~5 min of PI time). Launched `claude`, typed
   `continue`, walked away. The Foundation stage (surveyor + theorist
   + coder in parallel) ran for ~20 minutes.
3. **Resolve the first round of decisions** (~15 min). Read the
   12 entries the agents had raised in `DECISIONS.md`, picked
   resolutions based on each agent's own recommendations, typed
   `continue` again.
4. **Final review** (~30 min) after the pipeline finished: read the
   accepted paper draft, checked the review files, ran `/checkpoint`.

**Total PI wall-clock: under 2 hours** spread over a day. Everything
else — literature review, theory verification, coding, validation,
benchmarks, real-data application, paper writing, peer review — was
agent compute.

---

## What the agents produced

| Stage | Agent | Concrete deliverable |
|---|---|---|
| 1. Literature review | surveyor | 24 paper notes, positioning note, open-datasets note, 35 BibTeX entries in `paper/references.bib` |
| 2. Theory verification | theorist (opus) | 7 derivation files (~1,800 lines), 40-row verdict table. Linear case verified numerically to 1.25e-16; 10 hidden assumptions documented; a formal ρ(m) convergence bound for the Koopman extension |
| 3. Code | coder | 3 Python modules (Hankel regression + Granger causality + CCM), **37 pytest tests**, fully deterministic |
| 4. Validation | analyst | Reproduced both paper examples within 10% of the target values (9.9% / 7.6% / 5.4% / 3.9% errors) |
| 5. Systematic benchmarks | analyst | 6 experiments on 5+ synthetic systems. **Hankel TPR = 1.00 on 4 of 5 systems**; beats CCM on linear (CCM=0.00) and GC on confounder suppression (GC=0.86). Sensitivity sweeps over delay depth, trajectory length, and observation noise. SVHT-vs-Moore-Penrose comparison with honest mechanism analysis |
| 6. Real-data proof-of-principle | analyst | Synthetic ENSO-like surrogate. **Hankel 93% vs Granger 77% vs CCM 70%** correct-direction rate across a coupling sweep |
| 7. Paper draft | writer (opus) | ~1,600-line LaTeX manuscript, 5 sections + abstract, 35 BibTeX entries, 8 figures, 3 tables, 1 new proposition, **every numerical claim traceable to a CSV under `analysis/`** |
| 8. Peer review | reviewer (opus) → writer → reviewer → writer → reviewer | Three review cycles: v01 = Major revision (7 must-fix items), v02 = Accept, v03 = Accept with cosmetic polish |
| 9. Decisions | all agents | 17 design/convention/limitations decisions raised by agents, resolved by PI or orchestrator, fully documented in `DECISIONS.md` |

Full narrative is in the project's `PROGRESS.md` and the
stage-specific logs under `logs/`. Every file above exists on disk
and was produced by the template; none was hand-written.

---

## Headline numbers

| Item | Value |
|---|---|
| PI wall-clock time | < 2 hours |
| Agent wall-clock time | ~10 hours total |
| Pytest tests passing | **37 / 37**, deterministic |
| Paper versions compiled | v01 (766 KB) → v02 (784 KB, Accept) → v03 (818 KB, Accept + polish) |
| Reviewer cycles | 3 (Major → Accept → Accept) |
| Reproduction errors vs paper targets | 9.9% / 7.6% / 5.4% / 3.9% |
| Hankel TPR on 4 of 5 benchmark systems | **1.00** |
| CCM TPR on linear systems (known failure) | 0.00 |
| ρ(m) convergence rate on Lorenz 63 | α ≈ 1.34 (polynomial) |
| Linear-case theorem verified to | 1.25e-16 (machine precision) |

---

## Five things to take away

1. **The template works end-to-end.** This is the full pipeline, not
   a toy — literature, theory, code, validation, benchmarks,
   real-data, paper, and peer review all run against a real preprint.
2. **Reproducibility is free.** Every seed is pinned; every experiment
   is a committed script; every agent run is logged; every number in
   the paper traces to a CSV under `analysis/`.
3. **Honesty is enforced.** The template's honesty clause is in
   `CLAUDE.md` Part 2: "if the method does not beat a baseline, report
   it". Agents actually follow it — reviewers caught claims that would
   otherwise have over-sold the result, and the accepted paper is
   substantially more defensible than a first draft would have been.
4. **The PI stays in the loop but rarely blocks progress.** The
   template pauses only when agents raise a real scientific question
   in `DECISIONS.md`. Once resolved, the pipeline runs to completion
   on its own.
5. **Scope, not scale, is the bottleneck.** A 6-page preprint took
   ~10 hours of agent compute and <2 hours of PI time. A 21-page
   preprint (see the `template_test_predinfo_decomposition` example)
   took the same <2 hours of PI time and similar agent compute.

---

## How to replicate

From an empty laptop:

```bash
# 1. Clone the template (once per laptop)
git clone git@github.com:oizumi-lab/lab-research-template.git \
  ~/Documents/Claude/Projects/lab-research-template
cd ~/Documents/Claude/Projects/lab-research-template

# 2. Bootstrap a new project
./bootstrap.sh my_project --variant theory-paper
cd ../my_project

# 3. Fill in GOAL.md and CLAUDE.md Part 2, drop your source PDF
#    into documents/. Commit and push to a private GitHub repo.

# 4. Launch Claude Code and run the pipeline
claude
> continue
```

Walk away for ~20 minutes. When the orchestrator pauses, read
`DECISIONS.md`, resolve the pending items, and type `continue` again.
Repeat until the reviewer returns `Accept`.

Expect:
- **~10 agent dispatches** for a small theory-paper project (Foundation
  ×3 parallel, Validation, Benchmarking, Real-data, Paper, Review×2,
  Revision×1)
- **~10 hours of wall-clock time** for agents
- **under 2 hours of PI time** spread over a day

The full commit history for this example is at
[`oizumi-lab/template_test_sekizawa_causality`](https://github.com/oizumi-lab/template_test_sekizawa_causality).

---

## Where to read more

- **Mental model** — [`../01-overview.md`](../01-overview.md)
- **Every folder and file, explained** — [`../02-anatomy.md`](../02-anatomy.md)
- **Bootstrap and daily workflow** — [`../03-setup.md`](../03-setup.md),
  [`../05-daily-workflow.md`](../05-daily-workflow.md)
- **What each agent does** — [`../06-agents.md`](../06-agents.md)
- **Slash commands** — [`../05-daily-workflow.md`](../05-daily-workflow.md) §11
- **When something breaks** — [`../07-troubleshooting.md`](../07-troubleshooting.md)
- **A second worked example** (21-page preprint, different domain) —
  `template_test_predinfo_decomposition/docs/examples/predinfo_decomp_tutorial.md`
