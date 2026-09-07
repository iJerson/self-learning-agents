---
name: setup
description: One-time per-project setup for this plugin — stages directories, copies memory templates, pastes the CLAUDE.md policy, and optionally copies agent-viz.html. Use when the user runs /setup or asks to set up this plugin in a project.
---

Set up this plugin (self-learning-agents) in the current project. Plugin root: `${CLAUDE_PLUGIN_ROOT}`.

Do the following, in order:

1. Create staging directories if missing:
   `.claude/skill-proposals`, `.claude/skills/candidates`, `.claude/memory`.

2. Copy memory templates, but never overwrite an existing file:
   - `${CLAUDE_PLUGIN_ROOT}/memory-templates/lessons.md` → `.claude/memory/lessons.md`
   - `${CLAUDE_PLUGIN_ROOT}/memory-templates/skill-registry.yaml` → `.claude/memory/skill-registry.yaml`
   If either destination already exists, skip it and tell the user it was left untouched.

3. Paste the policy sections from `${CLAUDE_PLUGIN_ROOT}/CLAUDE-SNIPPET.md` into the project's own
   `CLAUDE.md` (create `CLAUDE.md` if it doesn't exist). If `CLAUDE.md` already contains an
   "Implementation work: use the orchestrator agent" or "Continuous improvement" section, skip
   pasting and tell the user it looks already set up instead of duplicating it.

4. Ask the user (via AskUserQuestion) whether to also copy `agent-viz.html` (the standalone
   agent_log.jsonl visualizer) into the project root. Default / recommended answer is **No** —
   it's an optional dev tool, not required for the plugin to work. Only copy
   `${CLAUDE_PLUGIN_ROOT}/agent-viz.html` → `./agent-viz.html` if the user picks Yes.

5. Remind the user, in one short paragraph, to narrow the `SubagentStop` hook matcher in their
   own `.claude/settings.json` (copied from `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json`) to their
   project's actual lead/coordinator agent name (e.g. `orchestrator`), instead of leaving it
   matching every agent stop.

Report back concisely what was created, what was skipped (and why), and whether agent-viz.html
was copied.
