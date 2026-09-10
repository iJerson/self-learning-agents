---
name: async-subagent-file-handoff
description: Use when dispatching an async background subagent via the Agent tool (developer/tester/reviewer/skill-reviewer/trajectory-judge) and you need a specific structured report back (verdict, findings, pass/fail) rather than just file edits you'll inspect yourself — the task-notification's <result> field is unreliable for this.
---

# Async subagent file handoff

Use this when you are an orchestrator-role agent dispatching a background
subagent via the Agent tool (e.g. `developer`, `tester`, `reviewer`,
`skill-reviewer`, `trajectory-judge`) and you need a **specific structured
report back** — not just "go do this, I'll inspect the resulting
code/files myself."

## Why this exists

The async task-notification's `<result>` field is unreliable. It sometimes
contains a placeholder ("Ending turn.", "(no action)", "*(no output)*",
"Done.") instead of the subagent's actual final report — even when the
dispatch prompt explicitly instructs the subagent to end its turn with
specific text, and even when the subagent has no other tool that could have
captured the output instead. This happens even though the subagent did the
real work correctly; only the final-response delivery is lossy. If your
project keeps a lessons/memory log, it's worth recording the first incident
you hit this on there — the pattern recurs across unrelated tasks once a
project starts dispatching background subagents regularly.

You also cannot fall back to reading the subagent's raw `output_file`
transcript — that's explicitly disallowed (context-overflow risk) and is
unreliable anyway, since most of it is unrelated tool-call noise.

## When to use file-based handoff

Any time you (the orchestrator) need to consume a specific piece of
structured output from the subagent's turn — a verdict, a list of findings,
a pass/fail with reasons, a summary of what changed and why — rather than
just needing the subagent to have modified files you'll inspect yourself.

Skip it for dispatches where the deliverable IS the file(s) the subagent
edits (e.g. "implement this function") and you'll verify by reading/running
those files directly — no separate report is needed in that case.

## A read-only agent needs this too — don't assume only Write-capable agents hit it

This isn't only a concern for agents that already have a `Write` tool for
other reasons (like `developer`/`tester`). A strictly read-only reviewer-
style agent (e.g. `skill-reviewer`, `trajectory-judge`) hits the exact same
`<result>`-unreliability failure mode, and without any Write tool at all it
has **no fallback channel whatsoever** when that happens — the verdict is
simply lost. If you're defining a new read-only judge/reviewer-style agent
that reports a verdict rather than editing anything, give it a narrow,
explicitly-scoped `Write` exception for exactly this handoff (write only to
a report path the dispatch prompt gives it, nothing else, and don't invoke
`Write` at all if no path was given) — don't leave it with zero tools
capable of reliably returning its output.

## How to structure the dispatch prompt

1. **Put the Write instruction first, and make it mandatory.** State it as
   a required step to do immediately, not as the last item of a checklist.
   A long, multi-step verification prompt causes the subagent to spend its
   turn budget on the checklist and never reach the Write call.
2. **Keep the prompt short and narrowly scoped.** Give a small, fixed set
   of files/things to check rather than "review everything" or "verify all
   acceptance criteria." Narrow scope is what lets the subagent reach the
   Write step within its turn budget.
3. **Specify an exact file path** for the report, under the session
   scratchpad directory (or another path you control), e.g.:
   `<scratchpad>/reviewer-report-phase0.md`
   Don't rely on the subagent to invent a sensible path — name it exactly.
4. **Specify the exact required content/format** of that file (e.g. "a
   PASS/FAIL verdict on line 1, then a bulleted list of issues found, each
   with file:line"). Treat it like a return-value contract.
5. **Explicitly forbid redundant work.** If a prior agent (e.g. developer,
   tester) already produced artifacts the subagent could reuse (lint output,
   test results, a diff), say so and tell the subagent not to re-run that
   work — e.g. "do not re-run lint/typecheck, that's the tester's job; read
   its report at <path> instead." This is often what was eating the turn
   budget that should have gone to the Write step.
6. **After dispatch, `Read` the exact file path directly** once the
   notification indicates the subagent finished — do not parse or trust the
   notification's `<result>` field for the actual content, only as a
   signal that the subagent's turn ended.

## What NOT to do

- Don't rely on the notification's `<result>` field for anything beyond
  "did the subagent finish" — treat its text content as unreliable.
- Don't read the subagent's raw `output_file` transcript to recover the
  report — disallowed and noisy.
- Don't retry a failed dispatch with the same long, checklist-shaped prompt
  hoping it works the second time — shorten and re-scope it first.
- Don't skip specifying an exact path/format and hope the subagent picks a
  sane default — be explicit.
- Don't leave a read-only judge/reviewer-style agent with zero write
  capability and no fallback — see the section above.

## Validation

Two concrete tasks to run and record PASS/FAIL on:

1. **Positive case.** Dispatch a real background subagent with a short,
   narrowly-scoped prompt that puts the mandatory Write-to-exact-path
   instruction first, per "How to structure the dispatch prompt" above.
   After the notification signals completion, `Read` the exact report path.
   PASS = the file exists and contains the specified report content/format.
   FAIL = the file is missing or doesn't match the specified format.
2. **Negative control.** Dispatch a second background subagent using the
   OLD anti-pattern prompt shape this skill was written to fix: a long,
   multi-step verification checklist with the Write instruction buried at
   the end, no scope narrowing, and no "don't redo prior work" instruction.
   Target the same or a similar report path. This is expected to fail or
   produce unreliable output — that's the desired outcome, since it
   demonstrates the fix (not coincidence) is what makes case 1 work. PASS
   for this task = it reproduces the original failure (missing file,
   placeholder text, or wrong format); FAIL = it unexpectedly succeeds,
   which would undermine the skill's premise and should be reported back
   for review.

## Example prompt shape (paraphrased)

```
Write your full review report to <scratchpad>/<name>-report.md — do this
immediately after your check below, before any other exploration. This is
mandatory.

Check only these files: <file1>, <file2>. Do not re-run lint or typecheck —
the tester already ran those; see <tester-report-path> for that output.

Report format (write exactly this shape to the file):
Line 1: PASS or FAIL
Then: bullet list of issues, each as `path:line — description`. If none,
write "No issues found."
```

Then, once the notification signals completion, `Read` the report file
directly rather than trusting the notification's own result text.

## Scope note

Scratchpad paths are session-specific — don't hardcode a literal path from
one session into a prompt template. Always compute/insert the current
session's actual scratchpad path (or another orchestrator-controlled path)
at dispatch time.
