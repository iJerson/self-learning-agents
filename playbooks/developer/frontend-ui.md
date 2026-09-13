# Frontend UI playbook

Use when the task involves writing or restyling actual UI (a screen, a
component, CSS/styling) — skip entirely for backend/schema/service work,
which routes to Implementation instead.

Invoke the `frontend-design` skill first, via the `Skill` tool, before
falling back to your own judgment — check the available-skills listing and
prefer it fresh each time over the condensed notes below, since the skill
can be updated independently of this file. Only fall back to this file's
guidance if the skill isn't installed/available in this session.

Condensed fallback:

- Ground every choice in the actual subject matter and brand/design system
  already in this codebase (existing tokens, components, palette) — extend
  what's there (per the Implementation ladder) rather than inventing a
  fresh one per task. Only when a genuine search finds neither an existing
  design system nor brief-supplied direction should you make an aesthetic
  call yourself — and even then, prefer whatever direction the human
  already picked (a chosen mockup, a stated preference) over your own
  default.
- Avoid these tells of generic/templated AI output — don't default to them
  unless the brief/existing design system specifically calls for one: a
  warm cream background with a high-contrast serif and a terracotta
  accent; a near-black background with one acid-green/vermilion accent;
  identical rounded cards with the same soft grey shadow on everything
  regardless of hierarchy; tracked-out ALL-CAPS eyebrow labels above every
  heading; a "→" appended to every link/button; numbered markers (01/02/03)
  on content that isn't actually a sequence.
- Typography carries personality — one or two type families (clearly
  distinct if two), a real type scale, deliberate weights — not whatever
  default your framework reaches for. Line length under ~80 characters for
  body text.
- Spend boldness in one place per screen; keep the rest quiet and
  disciplined. Motion only for one deliberate moment or a direct response
  to a user action, never scattered hover/entrance effects on every element
  as a default.
- Written UI copy is design content, not filler: active voice, plain
  user-facing language (what the user understands, not internal
  system/implementation names), consistent action-name-to-confirmation
  ("Publish" produces "Published," not a generic toast), no
  vague/apologetic error copy.
- Build to the quality floor without being asked: responsive down to
  mobile, visible keyboard focus, reduced-motion respected, real color
  contrast.
