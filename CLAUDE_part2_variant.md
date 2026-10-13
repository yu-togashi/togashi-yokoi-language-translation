# PART 2 — THEORY-PAPER VARIANT

Starting point for a theory + computation + paper project. Replace the
placeholder problem statement with your own, then hand-tune the pipeline
stages if needed. Keep this file short — agent rules live in
`.claude/agents/*.md`, LaTeX build lives in `compile_paper.sh` inline
comments, Python conventions live in `.claude/agents/coder.md` and
`pyproject.toml`.

## The problem

(One paragraph: research question, starting material in `documents/`, expected
final artifact. What paper are you reproducing or extending? What's the
scientific question? What's the deliverable?)

## Pipeline stages

```
FOUNDATION (parallel)
  ├─ surveyor: literature review of the field
  ├─ theorist: verify derivations from source paper, identify extensions
  └─ coder: implement core method + baselines
VALIDATION
  ├─ coder: simulation / test systems
  └─ analyst: reproduce reference examples from the source paper
BENCHMARKING
  ├─ analyst: systematic comparison vs baselines
  ├─ analyst: parameter sensitivity sweeps
  └─ surveyor: find open datasets for real-data validation
REAL DATA
  └─ analyst: apply method to open datasets
PAPER (parallel with REAL DATA)
  ├─ writer: draft intro, methods, results, discussion
  └─ surveyor: finalize bibliography
REVIEW-REVISE (iterative)
  └─ reviewer → writer/analyst/coder → compile → reviewer → ...
```

## Domain-specific conventions

(Project-specific naming, score conventions, baseline fairness rules, honesty
clauses — only things that do NOT belong in any general-purpose agent file.
Delete this heading if none apply.)
