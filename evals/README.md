# Evals for the agent team

This project already has `tester` proving **outcome evals** — does the
code the team produced meet the task's acceptance criteria. What's missing
is **trajectory evals** — did the *team itself* behave correctly getting
there (gates respected, no skipped steps, no silent bypass of a hard rule).
Both matter: code can pass tests while the process that produced it
violated a hard gate (e.g. reviewer never actually ran, or a skill got
promoted without human go-ahead).

## Outcome evals
Already covered — `tester`'s pass/fail-with-real-output on acceptance
criteria, per phase, is the outcome eval. Nothing new needed here.

## Trajectory evals

`agent_log.jsonl` is the trace. `check_trajectory.py` checks a handful of
**mechanical invariants** — no LLM call needed, no judgment call — because
these have a definite right answer and a script is more reliable than a
model asked to eyeball a log:

- **Closed dispatches** — every `dispatch` has a matching terminal `result`
  for the same `task_id`+worker pair (orchestrator.md already states this
  rule in prose; the script actually verifies it against a real log).
- **Gate ordering** — `reviewer` is never dispatched for a `task_id` before
  a `done` result from `tester` on that same `task_id` (orchestrator.md
  step 3: "do not dispatch reviewer in parallel with tester").
- **No premature done** — a `reviewer` `done` result never appears without
  a preceding `tester` `done` result for the same `task_id`.

Run it against any real log:
```
python3 check_trajectory.py path/to/agent_log.jsonl
```
Exit code 0 = all invariants held. Non-zero = prints the specific
task_id/line that violated which invariant — this is your regression
signal, not a vague pass/fail.

## What the script *can't* check — that's what `trajectory-judge` is for

Some things aren't mechanically checkable from the log alone — e.g. "was
the escalation message actually useful context for the human, or just
'stuck, help'?" or "did developer's report plausibly justify the deviation
it flagged?" That's a judgment call, so it reuses the exact verdict pattern
`skill-reviewer` already established in this codebase (per the project's
own lazy-engineering ladder — extend an existing pattern before inventing a
new one) — see `agents/trajectory-judge.md`.

## Golden set: build it from real failures, not synthetic cases

Per the video's advice, don't hand-write hypothetical scenarios first.
Every time `agent_log.jsonl` shows a `status: "escalated"` or `"failed"`
that reached a human, that's a real failure — cut that slice of the log
(from the originating `dispatch` to the terminal event) into
`scenarios/<short-name>.yaml` as a fixture with the invariants it should
have held. `scenarios/skill-promotion-gate.yaml` is a worked example (a
synthetic one, since this plugin is new and hasn't accumulated real
failures yet) — replace it with real ones as the log grows.

## Regression testing after every prompt change

Since your "code" here is agent `.md` prompt files, a prompt edit is a
deploy. Add to `CLAUDE.md`: **whenever `agents/*.md` changes, orchestrator
re-runs the scenarios in `evals/scenarios/` against the edited prompt
before the change is considered done** — same as `tester` re-running the
suite after an app-code change. This is the piece most agent projects skip
entirely, and it's the cheapest one to add here since the harness already
exists.

## LLM-as-judge pitfalls (worth stating explicitly, since this project cares about rigor)
- Don't use a judge for anything `check_trajectory.py` can already check
  mechanically — a judge is less reliable than a script for a yes/no with
  a definite answer, reserve it for genuinely subjective calls.
- A judge's verdict is not self-certifying — same rule as `skill-reviewer`:
  it reports, a human or `orchestrator` still gates on it.
- Re-judge the *exact* transcript being evaluated each time; don't let a
  cached verdict from an earlier prompt version carry over after an
  `agents/*.md` edit, same principle as the "no carry-over approval" rule
  already in `orchestrator.md`'s skill-promotion section.
