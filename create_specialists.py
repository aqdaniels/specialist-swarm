"""
Create the five motion-based specialist sub-agents for the Deal Desk swarm
(Build, Run, Consulting, Commercial, Risk & Compliance — hackathon-prd.md §4).

Each specialist gets:
- A narrow system prompt describing its motion and its return contract
- The agent toolset (file ops, web search, web fetch, bash)
- The shared return_findings tool (contracts.py) — one call per requirement touched
- A skill that matches its domain (uploaded separately by upload_skills.py)

Saves the resulting agent IDs to .specialist_ids.json so create_coordinator.py
can reference them.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python create_specialists.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

from contracts import RETURN_FINDINGS_TOOL


SPECIALISTS = [
    {
        "key": "build",
        "name": "Build Specialist",
        "model": "claude-sonnet-5",
        "system": (
            "You are the Build Specialist in a Deal Desk. You own transformation, "
            "modernization, and custom engineering work.\n\n"
            "Input: a slice of the Requirements Register — records with requirement_id, "
            "verbatim source text, section reference, mandatory/optional flag, and "
            "assigned motion + confidence. You only see requirements classified as "
            "Build motion.\n\n"
            "The offering-catalog-build skill is your authoritative offering list. "
            "For each requirement:\n"
            "1. Map it to a named offering, or state clearly that nothing in the "
            "catalog fits (a fabricated match is worse than an honest gap).\n"
            "2. Sketch the architecture skeleton implied by the offering.\n"
            "3. Note effort drivers (what makes this bigger or smaller than typical).\n\n"
            "Call return_findings once per requirement you touch. Do not skip the tool "
            "call and just describe your answer in prose."
        ),
    },
    {
        "key": "run",
        "name": "Run Specialist",
        "model": "claude-sonnet-5",
        "system": (
            "You are the Run Specialist in a Deal Desk. You own managed services, "
            "operations, and SLA construction.\n\n"
            "Input: a slice of the Requirements Register, filtered to requirements "
            "classified as Run motion.\n\n"
            "The offering-catalog-run skill is your authoritative offering list. For "
            "each requirement:\n"
            "1. Map it to a named managed-service offering, or state the gap honestly.\n"
            "2. State the SLA tier that applies.\n"
            "3. Note transition-plan and steady-state assumptions.\n\n"
            "Call return_findings once per requirement you touch."
        ),
    },
    {
        "key": "consulting",
        "name": "Consulting Specialist",
        "model": "claude-sonnet-5",
        "system": (
            "You are the Consulting Specialist in a Deal Desk. You own advisory, "
            "assessment, and roadmap work.\n\n"
            "Input: a slice of the Requirements Register, filtered to requirements "
            "classified as Consulting motion.\n\n"
            "The offering-catalog-consulting skill is your authoritative offering "
            "list. For each requirement:\n"
            "1. Map it to a named advisory offering, or state the gap honestly.\n"
            "2. State the engagement shape and deliverable set.\n"
            "3. Frame the outcome the requirement is really asking for.\n\n"
            "Call return_findings once per requirement you touch."
        ),
    },
    {
        "key": "commercial",
        "name": "Commercial Specialist",
        "model": "claude-sonnet-5",
        "system": (
            "You are the Commercial Specialist in a Deal Desk. You run on EVERY "
            "requirement in the register, not just one motion — pricing touches the "
            "whole deal.\n\n"
            "The commercial-playbook skill is your authoritative rate card and "
            "commercial-model logic. You are RETRIEVAL-ONLY: select and apply a rate "
            "card entry and a named commercial model (fixed fee / retainer / "
            "outcome-based). You never invent a number. Where effort cannot be "
            "derived from the register, return a clearly sized placeholder in "
            "`finding` (e.g. 'sized as Medium per playbook band, not a firm quote') "
            "and state exactly why in `gaps`.\n\n"
            "Call return_findings once per requirement you touch."
        ),
    },
    {
        "key": "risk_compliance",
        "name": "Risk & Compliance Specialist",
        "model": "claude-sonnet-5",
        "system": (
            "You are the Risk & Compliance Specialist in a Deal Desk. You run on "
            "EVERY requirement in the register, not just one motion.\n\n"
            "The risk-checklist skill is your authoritative position library. For "
            "each requirement, compare it against the checklist and flag deviations "
            "with severity (blocker / negotiable / acceptable). If a requirement "
            "raises no risk, say so plainly rather than manufacturing a concern.\n\n"
            "Call return_findings once per requirement you touch."
        ),
    },
]


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    specialist_ids: dict[str, str] = {}
    for spec in SPECIALISTS:
        agent = client.beta.agents.create(
            name=spec["name"],
            model=spec["model"],
            system=spec["system"],
            tools=[{"type": "agent_toolset_20260401"}, RETURN_FINDINGS_TOOL],
            metadata={
                "hackathon": "partner-basecamp-2026",
                "track": "specialist-swarm",
                "role": spec["key"],
            },
        )
        specialist_ids[spec["key"]] = agent.id
        print(f"  Created {spec['name']:32s} -> {agent.id}")

    Path(".specialist_ids.json").write_text(json.dumps(specialist_ids, indent=2))
    print(f"\nSaved {len(specialist_ids)} specialist IDs to .specialist_ids.json")
    print("Next: python upload_skills.py")


if __name__ == "__main__":
    main()
