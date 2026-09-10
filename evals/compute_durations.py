#!/usr/bin/env python3
"""
Derive dispatch->result durations from agent_log.jsonl.

No schema change — pairs each "dispatch" (from: orchestrator) with its
matching "result" (from: worker, to: orchestrator) by (task_id, worker) and
prints the elapsed time between their "ts" fields. Malformed or unmatched
lines are skipped, never fatal.

Usage:
    python3 compute_durations.py path/to/agent_log.jsonl
"""

import json
import sys
from datetime import datetime


def parse_ts(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None


def load_events(path):
    events = []
    with open(path) as f:
        for lineno, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ev["_line"] = lineno
            events.append(ev)
    return events


def compute_durations(events):
    """Returns a list of (task_id, worker, duration_ms, dispatch_line, result_line)."""
    open_dispatches = {}  # (task_id, worker) -> (ts, line)
    results = []

    for ev in events:
        task_id = ev.get("task_id")
        event = ev.get("event")
        ts = parse_ts(ev.get("ts"))

        if event == "dispatch" and ev.get("from") == "orchestrator" and ts:
            worker = ev.get("to")
            open_dispatches[(task_id, worker)] = (ts, ev["_line"])
        elif event == "result" and ts:
            worker = ev.get("from")
            key = (task_id, worker)
            if key in open_dispatches:
                dispatch_ts, dispatch_line = open_dispatches.pop(key)
                duration_ms = int((ts - dispatch_ts).total_seconds() * 1000)
                results.append((task_id, worker, duration_ms, dispatch_line, ev["_line"]))

    return results


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    try:
        events = load_events(sys.argv[1])
    except OSError as e:
        print(f"could not read {sys.argv[1]}: {e}")
        sys.exit(1)

    for task_id, worker, duration_ms, dispatch_line, result_line in compute_durations(events):
        print(f"{task_id}\t{worker}\t{duration_ms}ms\t(dispatch line {dispatch_line} -> result line {result_line})")


if __name__ == "__main__":
    main()
