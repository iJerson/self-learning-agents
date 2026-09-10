#!/usr/bin/env python3
"""
Trajectory eval for the self-learning-agents team.

Checks mechanical invariants against a real agent_log.jsonl trace —
things with a definite right answer, so a script checks them instead of
an LLM judge. Anything genuinely subjective belongs in trajectory-judge
(see evals/README.md), not here.

Usage:
    python3 check_trajectory.py path/to/agent_log.jsonl

Exit code 0 = all invariants held for every task_id in the log.
Exit code 1 = at least one violation; details printed per line.
"""

import json
import sys
from collections import defaultdict

TERMINAL_STATUSES = {"done", "failed", "escalated"}


def load_events(path):
    events = []
    with open(path) as f:
        for lineno, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"line {lineno}: invalid JSON — {e}")
                continue
            ev["_line"] = lineno
            events.append(ev)
    return events


def check_closed_dispatches(events):
    """Every dispatch has a matching terminal result for the same
    task_id + worker pair (orchestrator.md's own stated rule)."""
    violations = []
    open_dispatches = {}  # (task_id, worker) -> line number

    for ev in events:
        task_id = ev.get("task_id")
        event = ev.get("event")
        if event == "dispatch" and ev.get("from") == "orchestrator":
            worker = ev.get("to")
            open_dispatches[(task_id, worker)] = ev["_line"]
        elif event == "result":
            worker = ev.get("from")
            key = (task_id, worker)
            if key in open_dispatches and ev.get("status") in TERMINAL_STATUSES:
                del open_dispatches[key]

    for (task_id, worker), line in open_dispatches.items():
        violations.append(
            f"line {line}: dispatch to '{worker}' for task '{task_id}' "
            f"has no matching terminal result — edge left open"
        )
    return violations


def check_gate_ordering(events):
    """reviewer is never dispatched for a task_id before a done result
    from tester on that same task_id (orchestrator.md step 3)."""
    violations = []
    tester_done_seen = defaultdict(bool)

    for ev in events:
        task_id = ev.get("task_id")
        if ev.get("event") == "result" and ev.get("from") == "tester" and ev.get("status") == "done":
            tester_done_seen[task_id] = True
        elif ev.get("event") == "dispatch" and ev.get("to") == "reviewer":
            if not tester_done_seen[task_id]:
                violations.append(
                    f"line {ev['_line']}: reviewer dispatched for task "
                    f"'{task_id}' before tester reported done"
                )
    return violations


def check_no_premature_done(events):
    """A reviewer 'done' result never appears without a preceding tester
    'done' result for the same task_id."""
    violations = []
    tester_done_seen = defaultdict(bool)

    for ev in events:
        task_id = ev.get("task_id")
        if ev.get("event") == "result" and ev.get("from") == "tester" and ev.get("status") == "done":
            tester_done_seen[task_id] = True
        elif ev.get("event") == "result" and ev.get("from") == "reviewer" and ev.get("status") == "done":
            if not tester_done_seen[task_id]:
                violations.append(
                    f"line {ev['_line']}: reviewer reported done for task "
                    f"'{task_id}' with no prior tester done result"
                )
    return violations


CHECKS = [
    ("closed_dispatches", check_closed_dispatches),
    ("gate_ordering", check_gate_ordering),
    ("no_premature_done", check_no_premature_done),
]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    events = load_events(sys.argv[1])
    if not events:
        print("No events loaded — nothing to check.")
        sys.exit(0)

    total_violations = 0
    for name, check in CHECKS:
        violations = check(events)
        if violations:
            print(f"[FAIL] {name} ({len(violations)} violation(s)):")
            for v in violations:
                print(f"    {v}")
        else:
            print(f"[PASS] {name}")
        total_violations += len(violations)

    print()
    if total_violations:
        print(f"{total_violations} trajectory violation(s) found.")
        sys.exit(1)
    else:
        print("All trajectory invariants held.")
        sys.exit(0)


if __name__ == "__main__":
    main()
