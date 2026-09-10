---
name: async-dispatch-patience
description: Use when you are an orchestrator-role agent deciding whether an async subagent dispatch (planner/developer/tester/reviewer/skill-reviewer/trajectory-judge via the Agent tool) has stalled, failed, or is still working — before you redispatch, escalate, or trust a result. Prevents declaring a dispatch dead on unreliable early signals, and limits the damage if a redundant retry happens anyway.
---

# Async dispatch patience

Use this when you are an orchestrator-role agent that dispatched a background
subagent via the `Agent` tool (`planner`, `developer`, `tester`, `reviewer`,
`skill-reviewer`, `trajectory-judge`) and are trying to decide: is it done,
still working, or genuinely stalled? Get this wrong and you either waste a
redundant dispatch, or — worse — race a good in-flight result with a bad one
and silently lose the good one.

## Why this exists

Across a single project's early build phases, the orchestrator wrongly
declared an async dispatch "stalled" or "failed" 5+ times, using signals that
felt like evidence but weren't. Every one of those 5 dispatches was actually
still working and later delivered a complete, correct result via its real
`<task-notification status="completed">` event. If your project keeps a
lessons/memory log, it's worth recording your first incident there — this
pattern recurs across unrelated tasks once a project starts dispatching
background subagents regularly.

The worst instance: during one dispatch, the orchestrator checked the
subagent's raw transcript file size 4 times over ~2 minutes, saw it static,
concluded it had stalled, and launched a narrower redundant retry. The
*original* dispatch then delivered a complete, correct result. The redundant
retry's write landed *after* it and overwrote the good file with a worse,
partial version. It was only caught because the good version had, by luck,
already been manually backed up the moment it was first noticed.

## What is NOT reliable evidence of a stall

None of these mean a dispatch has failed — each one caused a false "stalled"
conclusion in the recorded incidents:

- **A static-looking transcript file size** across 1-2 minutes of polling.
  The subagent can be mid-way through a long tool call (a big Bash command, a
  large file write) with no new transcript bytes to show for a while.
- **A `SubagentStop` hook firing.** This means the subagent's own turn
  *ended* — not that its async result or file-write has been fully delivered
  or flushed to disk yet.
- **An expected report file missing on first check.** The dispatch may
  still be finishing the write, or the notification may have fired slightly
  before the last write was fully reflected on disk.
- **`git diff`/`git status` showing large changes.** If the touched files
  were already modified by prior phases/dispatches, this conflates old and
  new changes against a stale baseline — it doesn't tell you what *this*
  dispatch did.

## What IS reliable

1. **The actual `<task-notification status="completed">` event.** This is
   the only real "this dispatch's turn is over" signal. Wait for it before
   concluding anything about success or failure.
2. **A bounded polling loop with a real timeout, if you must check before
   the notification arrives.** Use many minutes, not a fixed short sleep or
   a one-shot check — the one genuinely stalled dispatch recorded in this
   pattern's history took ~600s+ before the harness itself reported "no
   progress for 600s (stream watchdog did not recover)." A 1-2 minute
   window is not long enough to distinguish "still working" from "stalled."
3. **`find <repo-root> -newer <a-known-recent-file> -not -path
   '*/node_modules/*' -not -path '*/.git/*' -type f`** — pick a file you
   know was written recently and *before* the dispatch you're checking
   (e.g. the latest migration folder, or a file from a confirmed-done
   earlier step). This tells you, unambiguously, whether anything in the
   repo has changed since that point — reliable even when `git diff` would
   be misleading due to prior-phase modifications to the same files.

## If you redispatch anyway and the original then lands too

Sometimes a genuinely long silence justifies a retry. If the original
dispatch's result then also arrives:

- **Back up whichever complete result appears first**, before a second
  dispatch's write can race and overwrite it — copy the file to a
  differently-named path the moment you see it, don't assume it'll still be
  there when you check again.
- **Prefer the more complete/correct result over "whichever wrote last."**
  A later write is not automatically the better one — it may be the
  redundant retry's partial output landing after the real thing.

## What NOT to do

- Don't conclude a dispatch failed from a static transcript, a
  `SubagentStop` firing, or a missing file, checked only once, within a
  couple minutes of dispatch.
- Don't trust `git diff`/`git status` alone to verify a multi-file
  dispatch's output when the touched files have prior-phase history.
- Don't redispatch and then walk away — if you do retry, actively watch for
  both results landing and back up the first complete one you see.

## Validation

1. **Positive case (patience holds):** dispatch a subagent with a task that
   takes a realistic multi-minute turnaround (e.g. a multi-file research +
   write task, not a trivial one-liner). Check its transcript/expected file
   once at the ~1-minute mark (it should look incomplete/static) and confirm
   you do NOT redispatch or declare it failed at that point — wait for the
   actual `<task-notification status="completed">` event, then verify the
   expected file/output is present and correct. `tester` records: did the
   orchestrator avoid a premature redispatch, and did the real result land
   correctly once actually waited for?
2. **Negative control (the old bad heuristic still fails the way the
   incidents describe):** for a dispatch given a task with a real multi-file
   deliverable, check for the expected output file within the first ~30-60s
   using only a static filesystem check (no bounded polling loop, no wait
   for the notification). Confirm this produces a false "missing/incomplete"
   read at that early checkpoint, then confirm the file is in fact complete
   once the real `<task-notification status="completed">` arrives shortly
   after — demonstrating why the early one-shot check would have caused a
   wrong conclusion. `tester` records both checkpoints' actual state.
