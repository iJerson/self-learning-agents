# Investigation playbook

Use for a read-only question, not a change: "how does X work", "why was Y
built this way", "are we sure Z is true", "what would break if we changed X".

1. Skip `PROGRESS.md` and the `developer`/`tester` dispatch entirely — there
   is no code to write or test.
2. Answer it yourself with `Read`/`Grep`/`Glob`/`Bash`, or dispatch `planner`
   (read-only) if the question needs a broader design/tradeoff read than you
   want to do inline. Never dispatch `developer` for this — it writes code,
   which this isn't asking for.
3. If the answer changes what gets built next (the investigation reveals the
   plan is wrong, or surfaces a real tradeoff), say so and stop there — don't
   silently roll straight into implementation on the same turn. Let the user
   decide whether to proceed.
4. Still log it: one `dispatch`/`result` pair in `agent_log.jsonl` if you
   delegated to `planner`, `from`/`to: "ledger"` if you answered it yourself
   — same rules as any other logged step, just no phase/task in
   `PROGRESS.md` for a question that changed nothing.
5. If mid-investigation you find yourself proposing an actual code change,
   that's the signal to switch playbooks — treat it as a new task under
   **Feature** or **Bug fix**, not a continuation of the investigation.
