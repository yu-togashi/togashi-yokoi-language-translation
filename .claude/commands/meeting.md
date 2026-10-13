---
description: Read all unprocessed meeting transcripts, summarize, and update the pipeline.
---

You are processing raw meeting transcripts into actionable agent guidance.

## 1. Find ALL unprocessed transcripts

- List `meetings/raw/` sorted oldest → newest
- A transcript is **unprocessed** if no file with the same basename exists in
  `meetings/summaries/`, AND the content hash in `meetings/summaries/.hashes`
  does not match the raw file's SHA-256
- Process every unprocessed transcript in order. Do not stop at the first one.

## 2. For each transcript — context-budget-aware summarization

- Estimate token count (`wc -w` × 1.3)
- If > ~15,000 tokens: do a **two-pass extractive summary first**:
  1. Read the transcript in chunks of ~8k tokens
  2. For each chunk, extract verbatim-ish bullet points of what was said
  3. Concatenate into a condensed extractive draft
  4. Run step 3 on the extractive draft
- If ≤ 15,000 tokens: read the raw directly and go to step 3

## 3. Load grounding context

- `GOAL.md` — why this project exists
- `STATUS.md` — current pipeline state
- `PROGRESS.md` — top 30 lines (recent history)
- `DECISIONS.md` — open questions
- `meetings/feedback.md` — accumulated prior feedback (canonical)

## 4. Language handling

- Raw transcripts may be Japanese, English, or mixed
- Produce the summary in **English** (matches global language rule)
- Preserve key original-language quotes in a **Verbatim quotes** subsection

## 5. Write the summary

Write to `meetings/summaries/<same-basename>.md` with these sections:

- **TL;DR** — 2-3 sentences
- **Key points discussed** — bulleted
- **Decisions made** — explicit choices with rationale
- **Open questions** — things the PI did NOT decide
- **Feedback for agents** — guidance to change how agents work. Quote the
  transcript line if possible.
- **Next actions** — concrete pipeline steps, each tagged with an agent name
  and a priority (HIGH/MED/LOW)
- **Reconsideration** — given current `STATUS.md`, what changes? Which stages
  should be repeated, skipped, or re-prioritized?
- **Verbatim quotes** (if multilingual) — key original-language quotes

Append the raw file's SHA-256 to `meetings/summaries/.hashes` so we do not
re-process it next time:
```
<filename>  <sha256>
```

## 6. Apply the summary to the project

- For each **Decision** → append to `DECISIONS.md`
- For each **Feedback bullet** → append to **`meetings/feedback.md`**
  (versioned, visible to teammates who pull the repo). Do NOT rely on
  machine-local auto-memory for lab-wide feedback.
- For each **Next action** → update the `STATUS.md` pipeline table (add rows
  or re-order priorities); append a `PROGRESS.md` entry pointing at the summary

## 7. STOP — do not dispatch further agents

After processing all unprocessed transcripts, show the PI:

- Paths of every new summary file
- A short diff of what changed in `STATUS.md`, `DECISIONS.md`, and
  `meetings/feedback.md`

Wait for PI confirmation before resuming the pipeline with `/continue`.
