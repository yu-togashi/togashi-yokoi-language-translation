---
name: incorporate-meeting
description: Read raw meeting transcripts, summarize, and update DECISIONS/STATUS/feedback. Use when the user says "process meetings", "update from meeting", or invokes /meeting.
---

# Incorporate Meeting

Translate raw PI-student meeting transcripts into structured agent guidance.
See `.claude/commands/meeting.md` for the authoritative step-by-step — this
skill is the reusable capability that the command invokes.

## The pattern

Raw transcript (`meetings/raw/<date>_<slug>.md`)
  → summary (`meetings/summaries/<date>_<slug>.md`)
  → decisions appended to `DECISIONS.md`
  → feedback appended to `meetings/feedback.md` (canonical, versioned)
  → STATUS.md pipeline table re-ordered to reflect next actions
  → STOP for PI confirmation

## Why this workflow exists

- **Raw transcripts are the truth.** Otter/Zoom exports are noisy but they
  contain the PI's actual words. Never discard them.
- **Summaries are searchable.** Agents in future sessions read the summary,
  not the raw transcript.
- **Feedback is versioned.** `meetings/feedback.md` is committed to git so
  teammates pulling the repo see the same guidance. Machine-local auto-memory
  is insufficient — it is invisible across machines and users.
- **The PI stays in the loop.** After processing, the orchestrator STOPS so
  the PI can verify the reinterpretation is correct before agents rush off.

## Key technical points

- Handle multilingual transcripts (JA/EN mixed). Summary in English, quotes
  preserved in original language.
- Chunk transcripts >15k tokens into a two-pass extractive summary.
- Use content hashes (`meetings/summaries/.hashes`) to detect replay, not
  just filenames.
- Process ALL unprocessed transcripts in one pass, oldest first.
