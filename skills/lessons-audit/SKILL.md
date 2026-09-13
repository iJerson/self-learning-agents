---
name: lessons-audit
description: Scan .claude/memory/lessons.md for entries that now qualify for promotion to a skill (recurred 3+ times, error-prone, or non-obvious/tool-specific), and hand each one to skill-factory. Use for /lessons-audit, periodic maintenance, or when the user asks to review accumulated lessons.
---

`lessons.md` exists so a lesson doesn't need to become a skill the moment
it's noticed — but its own template says entries that recur or turn error-prone
should be promoted "instead of leaving it here indefinitely." Nothing
proactively rereads the file to check, so qualifying entries can sit there
unpromoted. This skill is that reread.

1. Read `.claude/memory/lessons.md` in full.
2. For each entry, judge against skill-factory's bar: has it recurred 3+
   times (same gotcha across separate dated entries, or explicitly noted as
   repeating), caused a repeated error, or is it non-obvious/tool-specific
   project knowledge worth codifying? Skip anything genuinely one-off.
3. For every entry that qualifies, check it isn't already covered by an
   approved skill or an existing candidate first (`.claude/memory/skill-registry.yaml`,
   `.claude/skills/candidates/`) — if it is, skip it.
4. For each remaining qualifying entry, invoke `skill-factory` to draft a
   candidate under `.claude/skills/candidates/<name>/SKILL.md`, citing the
   lesson entry (date + title) as the recurrence evidence.
5. Report which entries were promoted to candidates, which were skipped as
   already covered, and which were left in `lessons.md` as still one-off.
   Never edit or delete entries in `lessons.md` yourself — that stays the
   source record even after a lesson is promoted.

Never draft a skill directly — always go through `skill-factory`, which
enforces the candidate-only write path and never promotes on its own.

Validation: run this on a `lessons.md` with a planted 3+-recurrence entry
and confirm a candidate is drafted for it; run it again on a `lessons.md`
with only one-off entries and confirm nothing is drafted.
