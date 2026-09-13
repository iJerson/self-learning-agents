# Bug fix playbook

Use for a reported defect: something that used to work, or should work, and
doesn't. Distinct from Feature — the acceptance criteria is "the reported
symptom no longer reproduces," not new behavior.

1. Reproduce first. Before dispatching anyone, confirm you (or `developer`,
   as its first sub-step) can actually trigger the reported symptom — from
   the user's report, existing tests, or logs. If it can't be reproduced,
   say so and ask for more detail rather than guessing at a fix.
2. Delegate root-causing + fix to `developer`, with the reproduction steps
   and the exact symptom in the prompt (`TASK_ID: <id>` first line). Tell it
   explicitly not to patch the symptom's surface (a nil-check, a swallowed
   exception) without tracing to why the bad state occurred in the first
   place.
3. Delegate to `tester` to (a) confirm the original reproduction steps no
   longer trigger the bug, and (b) run the existing test suite to confirm
   no regression. Both need real output — a fix with no regression-test run
   is not proven.
4. Once tester reports clean, delegate to `reviewer` to check the fix
   against spec/safety rules and confirm it addresses the root cause, not
   just the reported instance.
5. If reviewer or tester surfaces problems, send them back to `developer`
   with the specific findings and re-run steps 2-4 on just the fix.
6. Mark the task `done` in `PROGRESS.md` only once tester's reproduction
   evidence and reviewer's sign-off are both clean.

Logging, hard gates, failure handling, and skill promotion follow the shared
rules in `agents/orchestrator.md` — this playbook only names the
bug-fix-specific sequence.
