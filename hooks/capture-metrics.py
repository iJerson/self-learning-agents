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

Must never block or error out the subagent's turn: any failure here just
prints the standard silent continue and exits 0.
"""

import json
import re
import sys
from datetime import datetime, timezone

SILENT_CONTINUE = {"continue": True, "suppressOutput": True}


def emit_and_exit():
    print(json.dumps(SILENT_CONTINUE))
    sys.exit(0)


def parse_transcript(path):
    input_tokens = 0
    output_tokens = 0
    timestamps = []
    task_id = None

    with open(path) as f:
        for raw in f:
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

    return task_id, input_tokens, output_tokens, duration_ms


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        emit_and_exit()
        return

    transcript_path = payload.get("transcript_path")
    subagent_type = payload.get("subagent_type") or "unknown"

    if not transcript_path:
        emit_and_exit()
        return

    try:
        task_id, input_tokens, output_tokens, duration_ms = parse_transcript(transcript_path)
    except OSError:
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

    emit_and_exit()


if __name__ == "__main__":
    main()
