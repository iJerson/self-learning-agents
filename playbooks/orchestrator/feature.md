# Feature playbook

Use for new or changed behavior: a spec phase, a requested feature, anything
with acceptance criteria to build toward. This is the default playbook —
route here when no narrower one (Investigation, Bug fix, Refactoring) fits.

1. Read the task's requirements and acceptance criteria from the spec (if
   one exists) or from what the user asked for.
2. If the task is non-trivial enough to need a design pass (a new feature, a
   phase whose shape isn't already fully spelled out in the spec, a change
   touching multiple files/subsystems, a real tradeoff), delegate to
   `planner` first. Skip it for small, already-well-scoped tasks and go
   straight to step 3.
3. Delegate implementation to `developer` with a specific, scoped prompt
   (`TASK_ID: <id>` first line, then the task list, relevant spec sections,
   path to the spec file). Don't hand it the whole project at once.
4. Delegate to `tester` to write/run the task's required tests and report
   pass/fail with real output. Wait for tester's result before moving on —
   do not dispatch `reviewer` in parallel with `tester`.
5. Only once tester reports back clean (no failing tests, no unmet
   acceptance criteria), delegate to `reviewer` to check the diff against
   spec + any safety rules this project has declared non-negotiable. If
   tester found real issues, send those back to `developer` first (step 6)
   and re-run tester before ever reaching reviewer.
6. If reviewer or tester surfaces problems, send them back to `developer`
   with the specific findings and re-run steps 3-5 on just the fix. Do not
   move on with known failures or unresolved safety findings.
7. Only mark the phase/task `done` in `PROGRESS.md` when tester's
   acceptance-criteria evidence and reviewer's sign-off are both clean.
   Then proceed to the next phase/task.

Logging, hard gates, failure handling, and skill promotion follow the shared
rules in `agents/orchestrator.md` — this playbook only names the
feature-specific sequence.
