# Meetings

Raw transcripts go in `raw/`. Claude-generated summaries go in `summaries/`.
Accumulated guidance for agents lives in `feedback.md`.

## Filename convention

Use `YYYY-MM-DD_<slug>.<ext>` in both `raw/` and `summaries/` so the pair
is obvious. Example:

- `raw/2026-04-11_weekly_sync.md` — PI drops this in
- `summaries/2026-04-11_weekly_sync.md` — Claude writes this via `/meeting`

## Workflow

1. **After a meeting**, drop the raw transcript into `raw/`. Any format works —
   plain text, Otter export, Zoom transcript, your own typed notes. Japanese,
   English, or mixed is fine.
2. **Launch Claude**: `claude`
3. **Type** `/meeting`. Claude will:
   - Find every unprocessed transcript in `raw/`
   - Chunk large ones (>15k tokens) via a two-pass extractive summary
   - Write a structured summary to `summaries/<same-basename>.md`
   - Append decisions to `DECISIONS.md`
   - Append feedback bullets to `feedback.md`
   - Update the `STATUS.md` pipeline table with any new next actions
   - STOP and wait for you to review before dispatching agents
4. Review the summary and the diff. If it looks right, type `continue` to
   resume the pipeline with the new guidance.

## What gets tracked where

| File | Purpose | Who edits it |
|---|---|---|
| `raw/*.md` | Verbatim transcripts | PI drops in |
| `summaries/*.md` | Structured summaries | Claude writes via `/meeting` |
| `summaries/.hashes` | SHA-256 of processed raws | Claude maintains |
| `feedback.md` | Accumulated agent guidance | Claude appends after each `/meeting` |

## Why versioned feedback, not auto-memory

Machine-local auto-memory is invisible to teammates pulling the repo on a
different laptop. `feedback.md` is committed to git so every lab member
working on this project sees the same accumulated guidance.
