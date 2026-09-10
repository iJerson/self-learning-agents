#!/usr/bin/env python3
"""
SubagentStop hook: auto-capture token/duration metrics per dispatch.

Standalone from — and never touches — the skill-retrospective printf entry
in hooks.json. Reads the hook's JSON payload from stdin (transcript_path,
subagent_type), sums token usage and elapsed time from the transcript, and
appends one "metrics" line to agent_log.jsonl. Correlates to a task_id by
finding a literal "TASK_ID: <id>" line in the transcript (see
orchestrator.md's dispatch convention) — falls back to task_id: null rather
than dropping the data point.

INCREMENTAL, not cumulative: a resumed/forked agent (via SendMessage, or one
left idle and re-triggered) shares one transcript_path across many separate
SubagentStop events, and that file keeps growing across the agent's whole
lifetime — which in a long-running session can span real days. Re-summing
the whole file from line 1 on every single stop produced two real bugs in
practice: (1) a near-duplicate "metrics" line every ~30s while that agent
was active, since nothing about the already-seen portion changes, and (2) a
nonsensical multi-day "duration_ms" (first-line to last-line of the whole
transcript, not this stop's actual span). Fixed by keeping a small
per-transcript high-water mark (line count + cumulative totals) in a state
file, and reporting only the delta since the last capture — skipping the
write entirely when there is nothing new to report.

Must never block or error out the subagent's turn: any failure here just
prints the standard silent continue and exits 0.
"""

import json
import re
import sys
from datetime import datetime, timezone

SILENT_CONTINUE = {"continue": True, "suppressOutput": True}
STATE_PATH = ".claude/.capture-metrics-state.json"


def emit_and_exit():
    print(json.dumps(SILENT_CONTINUE))
    sys.exit(0)


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state):
    try:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f)
    except OSError:
        pass


def parse_new_lines(path, already_processed):
    """Read only the lines beyond `already_processed` (the high-water mark
    from the last capture of this same transcript) — never re-reads or
    re-sums lines already accounted for."""
    input_tokens = 0
    output_tokens = 0
    timestamps = []
    task_id = None
    total_lines = 0

    with open(path) as f:
        for lineno, raw in enumerate(f, 1):
            total_lines = lineno
            if lineno <= already_processed:
                continue

            raw = raw.strip()
            if not raw:
                continue

            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue

            ts = entry.get("timestamp")
            if ts:
                timestamps.append(ts)

            message = entry.get("message") or {}
            usage = message.get("usage") or {}
            input_tokens += usage.get("input_tokens") or 0
            output_tokens += usage.get("output_tokens") or 0

            if task_id is None:
                content = message.get("content")
                texts = []
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    texts.extend(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict)
                    )
                for text in texts:
                    m = re.search(r"TASK_ID:\s*(\S+)", text)
                    if m:
                        task_id = m.group(1)
                        break

    duration_ms = None
    if len(timestamps) >= 2:
        try:
            start = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            end = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            duration_ms = int((end - start).total_seconds() * 1000)
        except ValueError:
            duration_ms = None

    return total_lines, task_id, input_tokens, output_tokens, duration_ms


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        emit_and_exit()
        return

    transcript_path = payload.get("transcript_path")
    subagent_type = payload.get("subagent_type")

    # No subagent_type means this SubagentStop-shaped event isn't actually a
    # subagent completion we can attribute — in practice this fires on the
    # coordinating session's own transcript (which keeps legitimately
    # growing every turn, so the incremental dedup above can't suppress it
    # the way it does true duplicate re-fires). A metrics line with no idea
    # which agent it's for is worse than no line at all — skip silently
    # rather than logging it as "unknown".
    if not transcript_path or not subagent_type:
        emit_and_exit()
        return

    state = load_state()
    prior = state.get(transcript_path, {})
    already_processed = prior.get("lines_processed", 0)
    prior_task_id = prior.get("task_id")

    try:
        total_lines, task_id, input_tokens, output_tokens, duration_ms = parse_new_lines(
            transcript_path, already_processed
        )
    except OSError:
        emit_and_exit()
        return

    task_id = task_id or prior_task_id

    # Nothing new since the last capture of this exact transcript — this is
    # the duplicate-firing case (a resumed/idle agent re-triggering the hook
    # with no new transcript content). Update the high-water mark (in case
    # total_lines moved without any usable content) but write nothing.
    if total_lines <= already_processed or (input_tokens == 0 and output_tokens == 0):
        state[transcript_path] = {"lines_processed": total_lines, "task_id": task_id}
        save_state(state)
        emit_and_exit()
        return

    line = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task_id": task_id,
        "from": subagent_type,
        "to": "orchestrator",
        "event": "metrics",
        "status": "n/a",
        "tokens": {"input": input_tokens, "output": output_tokens},
        "duration_ms": duration_ms,
        "note": "auto-captured by SubagentStop hook",
    }

    try:
        with open("agent_log.jsonl", "a") as f:
            f.write(json.dumps(line) + "\n")
    except OSError:
        pass

    state[transcript_path] = {"lines_processed": total_lines, "task_id": task_id}
    save_state(state)

    emit_and_exit()


if __name__ == "__main__":
    main()
