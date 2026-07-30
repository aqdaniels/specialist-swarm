"""
Smoke test: call each of the 5 live specialists with its motion-filtered
slice of the stub Requirements Register, and assert every reply contains
at least one valid return_findings tool call.

Not a permanent CI suite — one runnable check that the roster + skills
work end to end. Requires .specialist_ids.json (create_specialists.py)
and .environment_id (setup_environment.py) to already exist.

Usage:
    python test_specialists.py
"""

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic

from contracts import validate_finding

STUB_REGISTER_PATH = Path("synthetic-data/requirements-register-acme-stub.json")

# Tier 2 specialists see every requirement; Tier 1 see only their motion's slice.
TIER_2_KEYS = {"commercial", "risk_compliance"}


def load_requirements() -> list[dict]:
    data = json.loads(STUB_REGISTER_PATH.read_text())
    return data["requirements"]


def slice_for(specialist_key: str, requirements: list[dict]) -> list[dict]:
    if specialist_key in TIER_2_KEYS:
        return requirements
    return [r for r in requirements if r["motion"] == specialist_key]


def run_specialist(client: Anthropic, environment_id: str, specialist_id: str, specialist_key: str, requirements: list[dict]) -> tuple[bool, str]:
    requirement_ids = {r["requirement_id"] for r in requirements}
    register_text = json.dumps(requirements, indent=2)

    session = client.beta.sessions.create(
        agent=specialist_id,
        environment_id=environment_id,
        title=f"Dev B smoke test — {specialist_key}",
    )

    user_message = (
        "Here is your slice of the Requirements Register. Call return_findings "
        "once per requirement below.\n\n" + register_text
    )

    tool_calls = []
    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_message}]}],
        )
        for event in stream:
            if event.type == "agent.tool_use" and getattr(event, "name", None) == "return_findings":
                tool_calls.append(event.input)
            elif event.type == "session.status_idle":
                break

    if not tool_calls:
        return False, "no return_findings tool calls received"

    errors = []
    for call in tool_calls:
        call_errors = validate_finding(call)
        if call_errors:
            errors.append(f"  call {call.get('requirement_id', '?')}: {'; '.join(call_errors)}")
        elif call["requirement_id"] not in requirement_ids:
            errors.append(f"  call {call['requirement_id']}: not in this specialist's slice")

    if errors:
        return False, f"{len(tool_calls)} calls received, {len(errors)} invalid:\n" + "\n".join(errors)

    covered = {c["requirement_id"] for c in tool_calls}
    missing = requirement_ids - covered
    if missing:
        return False, f"{len(tool_calls)} valid calls, but missing requirement(s): {sorted(missing)}"

    return True, f"{len(tool_calls)} valid calls, all {len(requirement_ids)} requirement(s) covered"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".specialist_ids.json")
    environment_id_path = Path(".environment_id")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_specialists.py first.")
    if not environment_id_path.exists():
        raise SystemExit("Run setup_environment.py first.")

    specialist_ids = json.loads(specialist_ids_path.read_text())
    environment_id = environment_id_path.read_text().strip()
    requirements = load_requirements()

    client = Anthropic(default_headers={"anthropic-beta": "managed-agents-2026-04-01"})

    results = {}
    for key, specialist_id in specialist_ids.items():
        req_slice = slice_for(key, requirements)
        print(f"\n=== {key} ({len(req_slice)} requirement(s)) ===")
        ok, detail = run_specialist(client, environment_id, specialist_id, key, req_slice)
        results[key] = ok
        print(("PASS: " if ok else "FAIL: ") + detail)

    print("\n=== Summary ===")
    for key, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {key}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
