# Skill retrospective

This is the prompt the bundled `hooks.json` injects as `additionalContext`
after a `SubagentStop` event. It's documented here as a standalone
reference so a human (or an agent) can also run it manually — e.g. via a
fork, or as an explicit end-of-task step — without waiting on the hook.

## The check

After finishing a non-trivial task, ask:

> Did this task reveal a repeated workflow, a failure mode we hit before, or
> a project convention that isn't already written down? If yes, invoke
> `skill-factory` to draft a proposal. If it's a one-off, record it in
> `.claude/memory/lessons.md` instead. If neither, do nothing — most tasks
> should end here.

Concretely, look for:
- The same multi-step procedure done from scratch 3+ times (a real skill
  candidate, not a lesson).
- An error that would recur if the next person didn't happen to remember
  this specific fix (a lesson at minimum, a skill if it's genuinely
  non-obvious or tool-specific).
- A safety-relevant pattern that's currently only documented in one file's
  doc comment rather than as reusable guidance.

## Tuning the hook

The bundled hook matches every `SubagentStop` event and relies on its own
prompt text to tell non-lead agents to skip it. If you find it's noisy or
producing spurious "No action." trailing turns, narrow `hooks.json`'s
`matcher` to your project's actual lead/coordinating agent's name in your
own `.claude/settings.json` copy — see the main README's setup step 4.
