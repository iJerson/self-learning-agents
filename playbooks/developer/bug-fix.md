# Bug fix playbook

Use when the orchestrator hands you a reported defect (its own
`playbooks/orchestrator/bug-fix.md` step 2) rather than new/changed
behavior. Distinct from Implementation — the acceptance criteria is "the
reported symptom no longer reproduces without a regression," not new
behavior, and the fix must trace to a root cause, not just silence the
symptom.

1. Reproduce first. Confirm you can actually trigger the reported symptom
   from the reproduction steps you were given — from a failing test, a
   log, or manual steps. If you can't reproduce it, stop and report that
   back rather than guessing at a fix from the description alone.
2. Trace to the root cause before touching code. Ask why the bad state
   occurred, not just where it surfaced. Resist the easy fix that patches
   the symptom's surface — a nil-check, a swallowed exception, a guard that
   silences the crash without addressing why the value was ever nil/thrown.
3. Grep every caller of the code you're about to change. A guard added only
   on the path the report named, while a sibling caller hits the same root
   cause a different way, is not a real fix — fix it where all callers
   route through, per the same lazy-engineering ladder used for
   Implementation (rung 2: reuse/fix the shared thing, don't patch each
   call site).
4. Write or extend a regression test that fails before your fix and passes
   after — this is what proves root-cause, not surface-patch. Then run the
   project's full relevant test suite yourself, not just the new test, to
   confirm no other behavior moved.
5. Report back: the reproduction steps, the root cause (not just the
   symptom), what changed, the regression test added, and full suite
   output — not just "fixed it."

If a task requires real-world data you don't have to reproduce the bug (API
keys, verified facts, production identifiers), stop and ask — never invent
one.
