---
name: project-skills
description: Proactively scans a codebase (build/test/deploy scripts, conventions, gotchas) for skill-worthy material and drafts candidate skills for review, complementing skill-factory's reactive recurrence-triggered path. Use when the user runs /project-skills or asks to bootstrap project skills from the existing codebase.
---

Bootstrap skill candidates from this project's own codebase — a one-time (or
periodic) proactive scan, distinct from `skill-factory`'s reactive path
(which only fires on runtime recurrence noticed mid-task). Here the evidence
IS the codebase: a convention baked into the repo is worth documenting even
if no agent has hit it three times yet.

## 1. Survey, don't assume

Read what's actually there before guessing: `CLAUDE.md`/`README.md`, package
manifests and lockfiles, CI config, build/test/lint/deploy scripts,
directory layout, existing top-level `.claude/skills/<name>/`,
`.claude/memory/skill-registry.yaml`, `.claude/memory/lessons.md`, and any
`.claude/skill-proposals/` already pending. Anything already covered there —
skip, don't re-propose.

Then read the actual source, not just config: open several real feature
implementations (a handful of components/modules/endpoints across different
parts of the codebase) and compare them. Two or three similar files told the
same story is how you find a house pattern — a single file never proves one.

## 2. Weight this toward "how we build here", not just "what breaks here"

The goal is skills a future agent uses to *write new code the way this
project already does it* — architecture and tech-stack conventions are the
priority, not just pitfalls to dodge. For each of this project's actual
stack pieces (framework, state management, styling, API/data layer, test
setup, etc.), ask: does this project use it in a specific, repeated way that
isn't just "read the library's own docs"? If yes, that's a candidate:
- the project's architecture/module boundaries (how a feature is laid out
  across files/layers, naming and folder conventions, where a new one of
  X goes)
- a tech-stack idiom specific to this codebase (the house pattern for state
  management, API calls, styling, forms, error handling, etc. — not the
  library's generic tutorial pattern)
- a build/test/lint/deploy sequence with unusual steps, ordering, or flags
- a custom script or internal tool with real usage rules (not just `--help`)
- domain or data-model rules that aren't enforced by the type system
  (invariants, forbidden states, compliance/security constraints)
- a recurring gotcha visible in comments, commit messages, or docs (e.g. "do
  not do X, it broke prod") — worth capturing, but don't let this category
  crowd out the architecture/pattern ones above; a shortlist that's all
  troubleshooting and no "how we build a new feature here" has under-surveyed
  the source code in step 1

Do NOT draft a skill for anything generic (standard framework usage, common
CLI commands, one-off scripts with no real rules) — that's noise, not a
skill.

## 3. Confirm scope before writing anything

Present the shortlist (name + one-line rationale each) via AskUserQuestion
(multiSelect) and let the user pick which candidates to actually draft.
Never draft unconfirmed candidates — this skill can surface many
candidates on a large repo and the user should control how many land as
files.

## 4. Draft each confirmed candidate

Create staging directories if missing: `.claude/skill-proposals/`,
`.claude/skills/candidates/`. For each confirmed candidate:

1. Write `.claude/skill-proposals/<name>.md` covering: scope (what it does
   and does not cover), evidence (the specific files/patterns/commits that
   justify it — cite paths, not vibes), expected benefit, and risk. Where
   `skill-factory` cites runtime recurrence, cite the codebase evidence
   instead and say plainly this came from a bootstrap scan, not observed
   recurrence.
2. Draft `.claude/skills/candidates/<name>/SKILL.md` — never directly under
   a top-level `.claude/skills/<name>/`. Real `name` and `description` YAML
   frontmatter; the description must say both what it does and when Claude
   should load it.
3. Add two representative validation tasks to the candidate draft (what a
   human or another agent could run to confirm the skill actually works).

## 5. Never promote

Same chain as everywhere else in this plugin: only `skill-reviewer`
approves, only the project's lead/coordinating agent promotes a candidate
to a top-level `.claude/skills/<name>/`. This skill only drafts — it does
not install dependencies, change permissions, touch hooks, or move anything
out of `candidates/`.

## 6. Report

List what was drafted (proposal + candidate paths) and what was skipped as
already-covered or not skill-worthy, then remind the user to run
`skill-reviewer` before anything gets promoted.
