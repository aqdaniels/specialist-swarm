"""
RFP Coordinator — Classifies requirements and orchestrates specialist dispatch.
"""

import json
from pathlib import Path
from typing import Literal
from dataclasses import dataclass, asdict
from requirements_register import RequirementsRegister, Requirement, MotionType


@dataclass
class SpecialistResponse:
    """Fixed return contract for all specialist responses."""
    requirement_id: str
    specialist_type: str  # which specialist answered (Build, Run, Consulting, Commercial, Risk)
    finding: str  # what the offering/capability says about this requirement
    confidence: Literal["High", "Medium", "Low"]  # strength of response (does offering really cover this?)
    assumptions: list[str]  # what we're assuming about the requirement or our offering
    gaps: list[str]  # what's not covered or needs work
    references: list[str]  # citations back to offering docs, skills, past wins


@dataclass
class RequirementAnalysis:
    """Coordinator's analysis of a single requirement."""
    requirement: Requirement
    tier_1_specialists: list[str]  # motion-specific specialists (triggered by motion type)
    tier_2_specialists: list[str]  # always-on: Commercial + Risk
    specialist_responses: list[SpecialistResponse] = None  # populated after dispatch


class RFPCoordinator:
    """
    Coordinates RFP response analysis.
    - Reads requirements
    - Classifies each by motion type
    - Determines which specialists to activate
    - Reconciles specialist responses
    """

    # Motion type → which specialist handles Tier 1
    MOTION_TO_TIER1 = {
        "Consulting": ["Consulting"],
        "Build": ["Build"],
        "Run": ["Run"],
        "Risk": ["Risk"],
        "Commercial": ["Commercial"]
    }

    # Always activated (Tier 2)
    TIER2_ALWAYS = ["Commercial", "Risk"]

    def __init__(self, rfp_path: str):
        """Initialize coordinator with RFP file."""
        self.register = RequirementsRegister(rfp_path)
        self.requirements = self.register.parse()
        self.analyses: list[RequirementAnalysis] = []

    def classify_and_dispatch(self) -> list[RequirementAnalysis]:
        """
        For each requirement:
        1. Determine motion type (already done in register)
        2. Decide Tier 1 specialists (by motion type)
        3. Include Tier 2 specialists (always: Commercial + Risk)
        4. Return dispatch plan for coordinator to send to run_deal_desk
        """
        self.analyses = []

        for req in self.requirements:
            # Tier 1: motion-specific specialist
            tier1 = self.MOTION_TO_TIER1.get(req.motion_type, [])

            # Tier 2: always-on
            tier2 = self.TIER2_ALWAYS

            # Deduplicate (if motion_type is already Commercial or Risk, don't double-add)
            all_specialists = list(set(tier1 + tier2))

            analysis = RequirementAnalysis(
                requirement=req,
                tier_1_specialists=tier1,
                tier_2_specialists=tier2,
                specialist_responses=[]
            )
            self.analyses.append(analysis)

        return self.analyses

    def dispatch_plan(self) -> dict:
        """
        Return dispatch plan for run_deal_desk.py to send to specialists.
        Maps requirement_id → list of (specialist_type, requirement_text)
        """
        if not self.analyses:
            self.classify_and_dispatch()

        # Group by specialist: which requirements should each specialist receive?
        dispatch_by_specialist = {
            specialist: [] for specialist in set(
                s for a in self.analyses for s in a.tier_1_specialists + a.tier_2_specialists
            )
        }

        for analysis in self.analyses:
            all_specialists = set(analysis.tier_1_specialists + analysis.tier_2_specialists)
            for specialist in all_specialists:
                dispatch_by_specialist[specialist].append({
                    "requirement_id": analysis.requirement.requirement_id,
                    "title": analysis.requirement.title,
                    "mandatory_optional": analysis.requirement.mandatory_optional,
                    "verbatim": analysis.requirement.verbatim_text
                })

        return {
            "total_requirements": len(self.requirements),
            "specialist_dispatch": dispatch_by_specialist,
            "dispatch_logic": {
                "Consulting": "REQ motion_type=Consulting (Tier 1) + Commercial + Risk (Tier 2)",
                "Build": "REQ motion_type=Build (Tier 1) + Commercial + Risk (Tier 2)",
                "Run": "REQ motion_type=Run (Tier 1) + Commercial + Risk (Tier 2)",
                "Risk": "REQ motion_type=Risk (Tier 1) + Commercial (Tier 2), Risk always answers itself",
                "Commercial": "REQ motion_type=Commercial (Tier 1) + Risk (Tier 2), Commercial always answers itself"
            }
        }

    def reconcile_responses(self, specialist_responses_json: str) -> dict:
        """
        After specialists return their responses, reconcile them.

        Input: JSON list of SpecialistResponse objects
        Output: Merged response by requirement_id with all specialist inputs
        """
        responses = json.loads(specialist_responses_json)

        # Group responses by requirement_id
        merged = {}
        for resp_data in responses:
            req_id = resp_data["requirement_id"]
            if req_id not in merged:
                # Find the requirement
                req = next((r for r in self.requirements if r.requirement_id == req_id), None)
                merged[req_id] = {
                    "requirement_id": req_id,
                    "requirement_title": req.title if req else "Unknown",
                    "requirement_text": req.verbatim_text if req else "Unknown",
                    "mandatory_optional": req.mandatory_optional if req else "Unknown",
                    "specialist_inputs": []
                }

            merged[req_id]["specialist_inputs"].append({
                "specialist": resp_data["specialist_type"],
                "finding": resp_data["finding"],
                "confidence": resp_data["confidence"],
                "assumptions": resp_data["assumptions"],
                "gaps": resp_data["gaps"],
                "references": resp_data["references"]
            })

        return {
            "total_requirements_analyzed": len(merged),
            "merged_by_requirement": list(merged.values())
        }

    def summary(self) -> dict:
        """Return summary of dispatch plan."""
        if not self.analyses:
            self.classify_and_dispatch()

        specialist_counts = {}
        for analysis in self.analyses:
            all_specs = set(analysis.tier_1_specialists + analysis.tier_2_specialists)
            for spec in all_specs:
                specialist_counts[spec] = specialist_counts.get(spec, 0) + 1

        return {
            "total_requirements": len(self.requirements),
            "requirements_by_motion_type": self.register.summary()["by_motion_type"],
            "specialist_workload": specialist_counts,
            "total_specialist_assignments": sum(specialist_counts.values())
        }

    def to_json(self, output_path: str) -> None:
        """Export dispatch plan to JSON."""
        dispatch = self.dispatch_plan()
        summary = self.summary()

        output = {
            "coordinator_summary": summary,
            "dispatch_plan": dispatch,
            "analyses": [
                {
                    "requirement_id": a.requirement.requirement_id,
                    "title": a.requirement.title,
                    "motion_type": a.requirement.motion_type,
                    "tier_1_specialists": a.tier_1_specialists,
                    "tier_2_specialists": a.tier_2_specialists,
                    "all_specialists": list(set(a.tier_1_specialists + a.tier_2_specialists))
                }
                for a in self.analyses
            ]
        }

        Path(output_path).write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    rfp_path = Path(__file__).parent / "synthetic-data" / "rfp-fintech-digital-transformation.md"

    coordinator = RFPCoordinator(str(rfp_path))
    analyses = coordinator.classify_and_dispatch()

    print(f"\n✓ Classified {len(analyses)} requirements\n")

    # Print summary
    summary = coordinator.summary()
    print("Specialist Workload:")
    for specialist, count in sorted(summary["specialist_workload"].items()):
        print(f"  {specialist}: {count} requirements")

    print(f"\nTotal specialist assignments: {summary['total_specialist_assignments']}")

    # Print dispatch plan
    dispatch = coordinator.dispatch_plan()
    print(f"\nDispatch Plan (by specialist):")
    for specialist, reqs in sorted(dispatch["specialist_dispatch"].items()):
        print(f"  {specialist}: {len(reqs)} requirements")
        for req in reqs[:2]:  # Show first 2
            print(f"    - {req['requirement_id']}: {req['title']}")
        if len(reqs) > 2:
            print(f"    ... and {len(reqs) - 2} more")

    # Export to JSON
    coordinator.to_json("coordinator-dispatch.json")
    print(f"\n✓ Exported dispatch plan to coordinator-dispatch.json")
