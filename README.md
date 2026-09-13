# self-learning-agents

A Claude Code plugin bundling a full five-role build team (orchestrator,
planner, developer, tester, reviewer) plus a skill-proposal/review/promotion
pipeline that lets that team turn recurring or high-risk work into reusable,
reviewed skills instead of re-solving the same problem from scratch every
time. Extracted and generalized from the SAGIP PH project, which produced
one real skill end-to-end through this pipeline (3 revision rounds before
approval) using this exact agent team.

## What's in the plugin

- `agents/orchestrator.md` — drives a task end-to-end by delegating to
  planner/developer/tester/reviewer, gates progress on tester+reviewer
  sign-off, maintains `PROGRESS.md` and `agent_log.jsonl`, and is the sole
  agent allowed to promote an approved skill candidate.
- `playbooks/<agent-name>/` — one numbered-steps file per task shape, read
  by that agent before dispatching or implementing anything.
  `playbooks/orchestrator/` ships four: `investigation.md`, `bug-fix.md`,
  `feature.md`, `refactoring.md`. `playbooks/developer/` ships four more:
  `implementation.md` (default), `bug-fix.md` (reproduce first, trace to
  root cause — not just patch the symptom), `frontend-ui.md`,
  `skill-candidate-draft.md`. Each playbook states only what's different
  about its task shape; the shared mechanics (logging, hard gates, failure
  handling, skill promotion for orchestrator; safety rule, skills policy
  for developer) live once in the owning agent's own `.md` file. Add more
  files under an agent's directory as new task shapes recur, and add a
  sibling `playbooks/<other-agent>/` directory if another agent in this
  plugin needs its own set — rather than growing any agent's prompt itself.
- `agents/planner.md` — produces an implementation plan before code is
  written, for tasks non-trivial enough to need a design pass. Read-only.
- `agents/developer.md` — implements one phase/task's code at a time. Also
  drafts skill candidates when asked (renamed from `senior-engineer` in the
  original SAGIP PH project — generic role name for portability).
- `agents/tester.md` — writes/runs tests, proves acceptance criteria with
  real command output, not assertions. Also validates skill candidates.
- `agents/reviewer.md` — read-only review of a diff against the project's
  spec and any declared safety rules. Reports findings, never edits.
- `agents/skill-reviewer.md` — a separate, narrower read-only agent that
  returns APPROVED / REVISE / REJECT on a candidate skill. Never edits or
  promotes.
- `skills/skill-factory/` — meta-skill: searches for existing coverage,
  proposes, and drafts a candidate skill. Never promotes.
- `skills/setup/` and `skills/project-skills/` — see [Skills](#skills) below.
- `skills/async-subagent-file-handoff/` — the dispatch pattern every worker
  agent in this plugin needs: an async subagent's task-notification
  `<result>` field is unreliable, so a structured report (a verdict,
  findings, pass/fail) must be written to an exact file path and read back,
  never trusted from the notification text alone. Promoted here after
  recurring independently in more than one project using this plugin.
- `skills/async-dispatch-patience/` — the sibling half of the same
  reliability concern: what does and doesn't count as evidence that an
  async dispatch has stalled or failed, before you redispatch or escalate.
  A static transcript, a `SubagentStop` firing, or a missing file on first
  check are NOT reliable stall signals — only the real
  `<task-notification status="completed">` event is. Promoted here for the
  same reason as the skill above.
- `skills/lessons-audit/` — rereads `.claude/memory/lessons.md` for entries
  that now meet skill-factory's promotion bar (recurred 3+ times,
  error-prone, or non-obvious/tool-specific) and hands each one to
  `skill-factory` to draft as a candidate. `lessons.md` says qualifying
  entries should be promoted "instead of leaving it here indefinitely," but
  nothing reread the file to check until this skill existed.
- `hooks/hooks.json` — a `SubagentStop` hook that silently prompts a
  lead/coordinating agent to run the retrospective check after a task
  finishes (see `hooks/skill-retrospective.md` reference below).
- `agent-viz.html` — standalone, self-contained (no build step, no
  dependencies) real-time visualizer for `agent_log.jsonl`: hub-and-spoke
  Canvas view of the orchestrator dispatching to workers, with simultaneous
  pulsing for parallel dispatches. Copy it into a project root next to
  `agent_log.jsonl` and serve the directory (e.g. `python3 -m http.server`)
  to watch the orchestrator work live. Colors unknown agent names via a
  stable hash, so it works even if you rename/add agents beyond the five
  this plugin ships.

All five build-team agents are generic — they read a project's own spec
file, CLAUDE.md, and PROGRESS.md at runtime rather than hardcoding any
project's specific tech stack, schema, or domain rules. Point them at a new
project and they adapt to whatever spec/conventions they find there.

## Skills

Besides `skill-factory`, this plugin ships two more skills invoked the same
way, by name (`/setup`, `/project-skills`) — Claude Code plugins don't
support a separate `commands/` component type, so these are plain skills
under `skills/<name>/SKILL.md`, not a distinct "commands" mechanism.

- **`/setup`** — one-time per-project setup: stages `.claude/skill-proposals`,
  `.claude/skills/candidates`, and `.claude/memory`, copies the memory
  templates (skipping any that already exist), pastes `CLAUDE-SNIPPET.md`'s
  policy sections into your project's CLAUDE.md (skipping if already
  present), and asks whether to copy `agent-viz.html` (default no).
- **`/project-skills`** — proactively scans the codebase itself
  (build/test/deploy scripts, conventions, gotchas) for skill-worthy
  material and drafts candidates for review — unlike `skill-factory`, which
  only fires reactively on runtime recurrence noticed mid-task. Always
  confirms scope with the user before drafting, and drafts only under
  `.claude/skills/candidates/`, never top-level.

## What you set up per-project (not shipped by the plugin, since it's
## project-specific)

1. **Install the plugin:**
   ```
   /plugin marketplace add /path/to/self-learning-agents
   /plugin install self-learning-agents
   ```
   Or, once pushed to a git remote, replace the local path with the repo URL.

2. **Run `/setup`.** Does steps 2-4 below for you: creates the staging
   directories, copies the memory templates (skipping any that already
   exist), pastes `CLAUDE-SNIPPET.md`'s policy sections into your project's
   CLAUDE.md (skipping if already present), and asks whether to copy
   `agent-viz.html` (default no). To do it by hand instead:
   ```
   mkdir -p .claude/skill-proposals .claude/skills/candidates .claude/memory
   cp <plugin>/memory-templates/lessons.md .claude/memory/lessons.md
   cp <plugin>/memory-templates/skill-registry.yaml .claude/memory/skill-registry.yaml
   ```
   then paste the policy sections from `CLAUDE-SNIPPET.md` into your
   project's CLAUDE.md — written for this plugin's bundled agent names, edit
   if you're using a different team.

3. **Narrow the hook's matcher** (important — avoids noise; `/setup` only
   reminds you, it doesn't do this step). The bundled
   `hooks/hooks.json` matches every `SubagentStop` event and relies on the
   prompt telling non-lead agents to skip it. That works but is noisier than
   necessary. Once you know which agent is your project's lead/coordinator
   (the one authorized to invoke `skill-factory` and promote candidates),
   copy the hook into your own `.claude/settings.json` and set
   `"matcher"` to that agent's exact name — e.g. `"matcher": "orchestrator"`.
   This was a real lesson learned building the original system: matching
   every agent stop (not just the lead's) roughly quadrupled hook firings
   for no benefit, since only the lead agent can act on the retrospective.

4. **Optionally copy `agent-viz.html`** into your project root if you want
   the live visualizer — `/setup` asks this too (default no), since it's a
   standalone dev tool, not agent/skill/hook config.

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
