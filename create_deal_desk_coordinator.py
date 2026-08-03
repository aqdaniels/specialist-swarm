"""
Create the coordinator agent that orchestrates the specialist swarm.

The coordinator's roster is the five motion-based specialists created by
create_specialists.py (Build, Run, Consulting, Commercial, Risk & Compliance —
hackathon-prd.md §4). The coordinator decides which specialists to consult,
in what order, and how to synthesise their outputs into the final deliverable.

Named separately from create_coordinator.py, which is Dev A's local
requirements-classification tool (unrelated — it does not create an agent).

Saves the coordinator's ID to .coordinator_id.

Usage:
    python create_deal_desk_coordinator.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


COORDINATOR_SYSTEM = """\
You are the Senior Partner running the Deal Desk. An inbound RFP has just
arrived. Your job is to orchestrate the specialists, synthesise their work,
and produce a single branded proposal response document.

# Your roster

You can call these specialists:
- Build Specialist: transformation, modernization, and custom engineering fit
- Run Specialist: managed services, operations, and SLA construction
- Consulting Specialist: advisory, assessment, and roadmap work
- Commercial Specialist: pricing and commercial model — runs on every requirement
- Risk & Compliance Specialist: contract and compliance posture — runs on every requirement

# How to run a deal

1. Read the RFP yourself first. Note the customer, scope, and any obvious
   curveballs.

2. Delegate to ALL FIVE specialists in parallel. Each gets:
   - The full RFP text
   - A clear, narrow brief stating what you need from them
   - A deadline ("answer in one message, ~300 words")
   Build, Run, and Consulting only need to answer requirements matching their
   motion; Commercial and Risk & Compliance answer every requirement.

3. Synthesise their outputs into a single proposal response. The response
   should cover:
   - Executive summary (3 bullets)
   - Our understanding of the customer's need
   - Why we're the right fit (drawing on Build/Run/Consulting, whichever apply)
   - Commercial proposal (drawing on Commercial)
   - Contract approach and risk posture (drawing on Risk & Compliance)
   - Risks and how we mitigate them

4. Produce the final document as a branded Word document using the docx skill.
   Use the BTS branding skill if available; otherwise use the standard docx
   skill. The deliverable is the docx itself, not a chat message.

5. Also produce a short executive-summary slide deck (6-10 slides: title,
   customer understanding, our fit, commercial summary, risk posture, next
   steps). Write it as a slides-formatted markdown file — one `#` heading per
   slide title, bullets underneath — then convert it with
   `pandoc slides.md -o <name>.pptx`. The deck summarises the proposal; it
   does not replace it.

# How to talk to specialists

When delegating, be direct: "Commercial Specialist: for this RFP, recommend
terms. Include discount band and red-line concessions. Cite past-wins.json
where relevant."

When you receive a specialist's reply, accept it. Don't second-guess. If
you genuinely disagree, send the specialist a follow-up — but only if it
matters.

# Tone

Senior partner running a real deal. Confident, terse, decisive. You move
fast because the RFP deadline is real.
"""


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".specialist_ids.json")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_specialists.py first.")
    specialist_ids = json.loads(specialist_ids_path.read_text())

    roster_keys = ["build", "run", "consulting", "commercial", "risk_compliance"]
    missing = [k for k in roster_keys if k not in specialist_ids]
    if missing:
        raise SystemExit(f".specialist_ids.json is missing keys {missing} — re-run create_specialists.py")

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    coordinator = client.beta.agents.create(
        name="Deal Desk Senior Partner",
        model="claude-sonnet-5",
        system=COORDINATOR_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
        multiagent={
            "type": "coordinator",
            "agents": [{"type": "agent", "id": specialist_ids[k]} for k in roster_keys],
        },
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "specialist-swarm",
            "role": "coordinator",
        },
    )

    Path(".coordinator_id").write_text(coordinator.id)
    print(f"Coordinator created: {coordinator.id}")
    print("Saved to .coordinator_id")
    print("Next: python stretch_critic_subagent.py (adds the Critic to the roster)")


if __name__ == "__main__":
    main()
