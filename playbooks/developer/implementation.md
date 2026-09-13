# Implementation playbook (default)

Use for a normal spec/schema/service task — new or changed backend behavior
with stated acceptance criteria. Route here when no narrower playbook
(Frontend UI, Bug fix, Skill candidate draft) fits.

1. Implement exactly one phase or task at a time, matching that task's
   stated acceptance criteria — don't jump ahead to later phases' code.
2. Follow the project's existing file layout and schema conventions. Don't
   introduce extra abstractions, packages, or files the spec/task doesn't
   call for.
3. Before writing code, run the task past the lazy-engineering ladder —
   stop at the first rung that actually holds, then write the minimum code
   that satisfies it:
   1. **Does this need to exist at all?** A speculative need the task
      didn't actually ask for — skip it, note the skip in your report.
   2. **Already in this codebase?** A helper/util/type/pattern from an
      earlier phase that does this or most of it — reuse it, don't
      reimplement. Grep for it before writing new code.
   3. **Stdlib/framework/ORM feature covers it?** (a DB constraint instead
      of app-level validation, a built-in query operator instead of
      hand-rolled filtering) — use it.
   4. **An already-installed dependency solves it?** Use it. Never add a
      new dependency for what a few lines already in `package.json` can do.
   5. **Only then:** the minimum new code that satisfies the task's actual
      acceptance criteria — no interface with one implementation, no config
      knob for a value that never changes, no abstraction layer for a
      single caller.
4. Write tests alongside code when the task calls for them.
5. Run the project's lint/analyze and relevant test commands yourself
   before reporting a task done; fix failures rather than reporting them as
   someone else's problem.
6. If a task requires real-world data you don't have (API keys, verified
   facts, production identifiers), stop and ask — never invent one.
7. Report back concisely: what changed (files), what you ran to verify it,
   and any deviation from the spec with reasoning.

The ladder never overrides a hard safety/correctness requirement — input
validation at trust boundaries, server-side authorization, error handling
that prevents data loss, and anything the spec explicitly asks for are never
the "unrequested" part to cut. It's about not inventing extra structure
beyond what the task and the project's non-negotiables actually require, not
about skipping rigor.
