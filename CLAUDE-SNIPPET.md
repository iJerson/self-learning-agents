Paste this section into the consuming project's own CLAUDE.md (adjust the
agent names in brackets to match that project's real agent team).

---

## Continuous improvement

Before inventing a new workflow, search `.claude/skills/` (top-level
`<name>/SKILL.md` folders — approved skills) and `.claude/memory/lessons.md`.

When a reusable workflow is discovered:
1. Create a proposal in `.claude/skill-proposals/`.
2. Do not add it to `.claude/skills/<name>/` directly.
3. Include recurrence, evidence, scope, expected benefit, and risk.
4. The `skill-reviewer` agent must approve it.
5. Only approved skills may be moved into a top-level `.claude/skills/<name>/`
   folder and added to `.claude/memory/skill-registry.yaml`.

A skill is warranted only for repeated, error-prone, non-obvious, or
tool-specific work. Record one-off observations as a memory lesson instead.

Policy: any agent may propose; [YOUR IMPLEMENTING AGENT] may draft the
candidate under `.claude/skills/candidates/`; [YOUR VALIDATING AGENT]
validates its two validation tasks; `skill-reviewer` approves or rejects;
only [YOUR LEAD/COORDINATING AGENT] promotes an approved candidate to a live
top-level skill. This lets the team learn and create new skills without its
instructions, tools, or privileges drifting silently — no agent skips a step
in this chain, even under time pressure.
