# self-learning-agents

A Claude Code plugin that lets an agent team propose, draft, validate, and
promote reusable skills from recurring or high-risk work instead of
re-solving the same problem from scratch every time. Extracted from the
SAGIP PH project after it produced one real skill end-to-end through this
pipeline (3 revision rounds before approval).

## What's in the plugin

- `skills/skill-factory/` — meta-skill: searches for existing coverage,
  proposes, and drafts a candidate skill. Never promotes.
- `agents/skill-reviewer.md` — read-only agent that returns
  APPROVED / REVISE / REJECT on a candidate. Never edits or promotes.
- `hooks/hooks.json` — a `SubagentStop` hook that silently prompts a
  lead/coordinating agent to run the retrospective check after a task
  finishes (see `hooks/skill-retrospective.md` reference below).

## What you set up per-project (not shipped by the plugin, since it's
## project-specific)

1. **Install the plugin:**
   ```
   /plugin marketplace add /Users/jersoncastro/Documents/Development/Personal/self-learning-agents
   /plugin install self-learning-agents
   ```
   Or, once pushed to a git remote, replace the local path with the repo URL.

2. **Create the staging directories** in your project:
   ```
   mkdir -p .claude/skill-proposals .claude/skills/candidates .claude/memory
   cp <plugin>/memory-templates/lessons.md .claude/memory/lessons.md
   cp <plugin>/memory-templates/skill-registry.yaml .claude/memory/skill-registry.yaml
   ```

3. **Paste the policy section** from `CLAUDE-SNIPPET.md` into your project's
   CLAUDE.md, filling in your own agent names where bracketed.

4. **Narrow the hook's matcher** (important — avoids noise). The bundled
   `hooks/hooks.json` matches every `SubagentStop` event and relies on the
   prompt telling non-lead agents to skip it. That works but is noisier than
   necessary. Once you know which agent is your project's lead/coordinator
   (the one authorized to invoke `skill-factory` and promote candidates),
   copy the hook into your own `.claude/settings.json` and set
   `"matcher"` to that agent's exact name — e.g. `"matcher": "orchestrator"`.
   This was a real lesson learned building the original system: matching
   every agent stop (not just the lead's) roughly quadrupled hook firings
   for no benefit, since only the lead agent can act on the retrospective.

5. **Promotion is manual by design.** No agent — including the ones in this
   plugin — moves a candidate to a top-level `.claude/skills/<name>/`
   automatically. Only your project's lead/coordinating agent (or a human)
   does that, after `skill-reviewer` returns APPROVED. This keeps skill
   authority from drifting silently into whichever agent happens to run.

## Design notes

- Claude Code only auto-discovers skills at the exact top-level path
  `.claude/skills/<name>/SKILL.md`. A candidate sitting in
  `.claude/skills/candidates/<name>/SKILL.md` is invisible to normal use —
  that's deliberate, it's how staging works without a separate `approved/`
  subfolder scoping skills as `/plugin:skill` commands.
- `skill-registry.yaml` and `lessons.md` are per-project memory, not part of
  the plugin payload — each project accumulates its own history starting
  from the empty templates in `memory-templates/`.
- The hook is intentionally a static `command`-type hook emitting fixed JSON
  (no LLM call inside the hook itself) — cheap, side-effect-free, and easy
  to reason about compared to a `prompt`/`agent`-type hook.
