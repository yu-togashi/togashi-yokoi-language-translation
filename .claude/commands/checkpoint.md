---
description: Merge agent side branches into main, compile paper, push, and write a summary.
---

You are running a formal checkpoint. Agent side branches (`agent/auto/*`)
are merged into `main`, the paper is re-compiled, everything is pushed, and
a one-page summary is written for the PI.

## Steps

1. **Verify clean state.** `git status` must be clean on `main`. If there are
   uncommitted changes, STOP and ask the PI how to proceed.

2. **Merge agent branches.** List `agent/auto/*` branches:
   ```
   git branch --list 'agent/auto/*'
   ```
   For each, squash-merge into `main`:
   ```
   git checkout main
   git merge --squash agent/auto/<date>
   git commit -m "checkpoint: merge agent/auto/<date>"
   ```
   (If there are conflicts, STOP and ask the PI — do NOT use `reset --hard`.)

3. **Run tests.** `poetry run pytest -q`. If tests fail, STOP and flag in
   `DECISIONS.md` — do NOT push broken code.

4. **Compile the paper** (if applicable). `./compile_paper.sh`. Save the
   resulting PDF to `paper/versions/main_v<NN>_$(date +%F).pdf`.

5. **Push to main.** `git push origin main`.

6. **Write a checkpoint summary** to `logs/checkpoint_$(date +%F).md` with:
   - What was merged (list of agent branches)
   - Test status
   - Paper version produced (if any)
   - Any open DECISIONS.md items
   - What the next stage is

7. **Reset the dispatch counter** in `HEARTBEAT.md` to 0.

8. Tell the PI the checkpoint is complete and show them the summary path.
