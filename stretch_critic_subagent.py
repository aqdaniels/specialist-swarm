"""
Create the Deal Desk Critic sub-agent and wire it into the coordinator.

Promoted from stretch to core (hackathon-prd.md §6): the Critic gates every
draft with a weighted rubric before a document is produced — responsiveness,
differentiation, technical credibility, commercial coherence, risk posture —
plus Red/Amber/Green per proposal section, an enumerated coverage-gap list,
and an enumerated open-assumptions list. The rubric itself lives in the
`solution-review` skill (attached by upload_skills.py), not here, so it
isn't hardcoded in two places.

This script creates the critic agent, updates the coordinator's roster to
include it, and appends the review procedure (including the hard-block-on-
Red rule) to the coordinator's system prompt.

Usage:
    python stretch_critic_subagent.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from contracts import CRITIC_REVIEW_TOOL

load_dotenv()


CRITIC_SYSTEM = """\
You are the Deal Desk Critic. You don't write proposals. You review them.

When the coordinator asks for your review, you'll receive:
- The draft proposal
- The RFP (for context)
- The Requirements Register the coordinator worked from

The solution-review skill is your rubric. Use it exactly as written — five
weighted dimensions scored 1-5, Red/Amber/Green per proposal section (worst
governing dimension, not an average), the gap-enumeration method, and the
open-assumption-enumeration method. Don't improvise a different scoring
scheme.

Call `return_review` once per review round with:
- `dimension_scores` — all five, 1-5
- `section_ratings` — Red/Amber/Green per section, with a terse reason each
- `missing_requirements` — exact requirement_ids the draft doesn't cover
- `open_assumptions` — material assumptions pulled from specialist findings
- `verdict` — SHIP_IT / REVISE / STOP

Be sceptical. Your value to the coordinator is that you push back. A senior
partner who never gets pushback gets sloppy. On REVISE, list issues tersely —
no more than 5; if there are more, the draft isn't ready and the verdict
should be STOP instead.

Any single Red section is a hard block on SHIP_IT. You may only return
SHIP_IT alongside a Red section if the coordinator's message to you states
an explicit human override — in that case set `override_reason` to what was
overridden and why. Never grant an override yourself.
"""


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    coordinator_id = Path(".coordinator_id").read_text().strip()
    specialist_ids = json.loads(Path(".specialist_ids.json").read_text())

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    # Create the critic
    critic = client.beta.agents.create(
        name="Deal Desk Critic",
        model="claude-opus-4-7",  # The critic needs to be sharp
        system=CRITIC_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}, CRITIC_REVIEW_TOOL],
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "specialist-swarm",
            "role": "critic",
        },
    )
    print(f"Critic created: {critic.id}")

    # Add critic to specialist IDs and persist
    specialist_ids["critic"] = critic.id
    Path(".specialist_ids.json").write_text(json.dumps(specialist_ids, indent=2))

    # Update coordinator's roster to include the critic
    coordinator = client.beta.agents.retrieve(coordinator_id)
    new_roster = list(coordinator.multiagent.agents) + [
        {"type": "agent", "id": critic.id}
    ]

    # Append critic guidance to the coordinator's system prompt
    new_system = coordinator.system + (
        "\n\n# Critic\n\n"
        "Before producing the final documents, send your draft, the RFP, and "
        "the Requirements Register to the Deal Desk Critic. The Critic "
        "replies via return_review with dimension scores, a Red/Amber/Green "
        "rating per section, missing requirement IDs, open assumptions, and "
        "a verdict of SHIP_IT, REVISE, or STOP.\n\n"
        "- If SHIP_IT with no Red sections: produce the final docx and pptx.\n"
        "- If REVISE: address every listed issue and every missing "
        "requirement, then re-submit. Repeat at most twice; if still not "
        "SHIP_IT after two rounds, treat it as STOP.\n"
        "- If STOP, or if SHIP_IT but any section is Red: do NOT produce the "
        "documents. Report the Red section(s) and reasons to the user and "
        "ask whether to override. Only proceed to document generation on an "
        "explicit override instruction from the user — and when you do, "
        "add an \"Open Items\" section to the final document listing exactly "
        "what was overridden and why, verbatim from the Critic's "
        "override_reason.\n"
    )

    client.beta.agents.update(
        coordinator_id,
        version=coordinator.version,
        system=new_system,
        multiagent={"type": "coordinator", "agents": new_roster},
    )

    print("Coordinator roster updated. Now includes critic.")
    print("Next: python upload_skills.py (attaches solution-review to the critic)")


if __name__ == "__main__":
    main()
