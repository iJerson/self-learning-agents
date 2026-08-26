---
name: skill-factory
description: Propose and draft a project skill when a recurring or high-risk workflow needs reusable guidance. Do not use for one-off tasks.
---

Create a skill proposal only when the workflow has recurred at least three
times, created repeated errors, or requires non-obvious project knowledge.

1. Search approved skills (`.claude/memory/skill-registry.yaml`, and the
   top-level `.claude/skills/<name>/` folders it lists) and memory
   (`.claude/memory/lessons.md`) for duplicates. If an existing approved
   skill or a recorded lesson already covers this, stop — extend that
   instead of proposing a new one.
2. Write a proposal under `.claude/skill-proposals/<name>.md` covering:
   recurrence (how many times, in what tasks), evidence (what went wrong
   or what was repeated), scope (what it does and does not cover),
   expected benefit, and risk.
3. Draft the skill only under `.claude/skills/candidates/<name>/SKILL.md`
   — never directly under a top-level `.claude/skills/<name>/`. Give it
   real `name` and `description` YAML frontmatter; the description must
   say both what it does and when Claude should load it.
4. Add two representative validation tasks to the candidate draft (what a
   human or another agent could run to confirm the skill actually works).
5. Never promote the candidate, install dependencies, change permissions,
   or create/modify hooks. Promotion is gated on `skill-reviewer`'s
   approval — see this project's CLAUDE.md "Continuous improvement"
   section (or the equivalent policy note) for the full chain. Promotion
   moves the skill from `.claude/skills/candidates/<name>/` to the
   top-level `.claude/skills/<name>/SKILL.md` (Claude Code only
   auto-discovers skills at that exact top-level path — a candidate
   sitting one level deeper is invisible to normal use by design, which
   is the whole point of the candidates/ staging area).

A skill is warranted only for repeated, error-prone, non-obvious, or
tool-specific work. Record one-off observations as a memory lesson in
`.claude/memory/lessons.md` instead of drafting a skill for them.
