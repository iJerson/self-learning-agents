# Skill candidate draft playbook

Use when the orchestrator hands you a skill proposal rather than app-code
work.

1. Draft the skill under `.claude/skills/candidates/<name>/SKILL.md` only —
   never directly under a top-level `.claude/skills/<name>/`, and never
   touch `.claude/settings.json`, install a dependency, or change a
   permission while doing this.
2. Give it real `name`/`description` frontmatter — what it does, and when
   Claude should load it.
3. Include two validation tasks `tester` can actually run against the
   draft.
4. See this project's CLAUDE.md "Continuous improvement" section and
   `skill-factory`'s own `SKILL.md` for the full constraints — you're
   filling the same drafting role skill-factory fills, just invoked by the
   orchestrator instead of run directly.
5. **Verify the path before reporting done.** After writing,
   `ls .claude/skills/candidates/<name>/SKILL.md` (or equivalent) to
   confirm it landed exactly there — not `.claude/skills/<name>/` (that's
   the live, auto-discovered path; writing there accidentally auto-activates
   an unreviewed skill) and not `skills/<name>/` (that's this plugin's own
   top-level, not a project candidate). If the check shows the wrong path,
   move it yourself before reporting — don't hand a misplaced candidate to
   `tester`/`skill-reviewer` and let them catch it downstream.
