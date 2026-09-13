# Refactoring playbook

Use for a behavior-preserving change to structure or shape: rename, extract,
inline, dedupe, move. Distinct from Feature — nothing observable should
change; the acceptance criteria is parity, not new behavior.

1. Confirm scope is actually behavior-preserving before dispatching. If the
   request also changes what the code does (not just how it's structured),
   it's a Feature or Bug fix task, not this one — route it there instead.
2. Capture a baseline before the change: which existing tests currently
   pass. Have `tester` run the current suite first if there's any doubt it's
   green, so a later failure is attributable to the refactor, not
   pre-existing rot.
3. Delegate the refactor to `developer` with the scope and the explicit
   constraint that observable behavior must not change (`TASK_ID: <id>`
   first line).
4. Delegate to `tester` to run the same suite from step 2 and confirm it's
   still green with no changed assertions (a test that had to change its
   expected value means behavior moved, not just structure — flag that back
   to `developer` rather than accepting it as "expected").
5. Delegate to `reviewer` to confirm the diff is structural only — no
   snuck-in behavior change, no widened/narrowed scope beyond what was
   asked.
6. If reviewer or tester finds a behavior change, send it back to
   `developer` and re-run steps 3-5 on just the fix.
7. Mark the task `done` in `PROGRESS.md` only once tester confirms parity
   and reviewer confirms the diff is structural-only.

Logging, hard gates, failure handling, and skill promotion follow the shared
rules in `agents/orchestrator.md` — this playbook only names the
refactoring-specific sequence.
