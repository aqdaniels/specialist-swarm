"""
Run Deal Desk — Orchestrates the RFP response flow.
Main entry point: coordinates requirement classification, specialist dispatch, and response reconciliation.
"""

import json
import asyncio
from pathlib import Path
from dataclasses import asdict
from typing import Optional
from datetime import datetime

from create_coordinator import RFPCoordinator, SpecialistResponse


class DealDesk:
    """
    Main orchestration layer for RFP response generation.
    - Loads RFP and extracts requirements
    - Dispatches to specialists in parallel
    - Reconciles specialist responses
    - Prepares for output generation (docx, traceability)
    """

    def __init__(self, rfp_path: str):
        """Initialize deal desk with RFP file."""
        self.rfp_path = Path(rfp_path)
        self.coordinator = RFPCoordinator(str(self.rfp_path))
        self.dispatch_plan = None
        self.specialist_responses = []
        self.reconciled_responses = None

    def stage_1_classify_requirements(self) -> dict:
        """
        Stage 1: Classify all requirements and determine specialist dispatch.
        Output: dispatch plan ready to send to specialists.
        """
        print("\n=== STAGE 1: Classify Requirements ===")
        
        analyses = self.coordinator.classify_and_dispatch()
        self.dispatch_plan = self.coordinator.dispatch_plan()
        
        summary = self.coordinator.summary()
        print(f"✓ Classified {summary['total_requirements']} requirements")
        print(f"✓ Total specialist assignments: {summary['total_specialist_assignments']}")
        
        return self.dispatch_plan

    def stage_2_dispatch_to_specialists(self, mock_responses: Optional[list[dict]] = None) -> list[SpecialistResponse]:
        """
        Stage 2: Send classified requirements to specialists in parallel.
        
        In production:
        - Send each specialist their assigned requirements via Agent tool
        - Specialists implement domain skills and return SpecialistResponse objects
        - Collect all responses
        
        For testing:
        - Accept mock_responses (list of SpecialistResponse dicts)
        """
        print("\n=== STAGE 2: Dispatch to Specialists ===")
        
        if mock_responses:
            # Testing mode: use mock responses
            self.specialist_responses = mock_responses
            print(f"✓ Using {len(mock_responses)} mock specialist responses for testing")
            return self.specialist_responses
        
        # Production mode: spawn agents for each specialist
        # TODO: Implement real specialist dispatch using Agent tool
        # For now, return empty list
        print("⚠ Production specialist dispatch not yet implemented")
        print("   Dev B will implement specialist agents and domain skills")
        return []

    def stage_3_reconcile_responses(self) -> dict:
        """
        Stage 3: Merge specialist responses by requirement_id.
        Enforces the fixed return contract and ensures all responses are usable.
        """
        print("\n=== STAGE 3: Reconcile Specialist Responses ===")
        
        if not self.specialist_responses:
            print("⚠ No specialist responses to reconcile")
            return None
        
        # Convert to JSON for coordinator's reconcile method
        responses_json = json.dumps(self.specialist_responses)
        self.reconciled_responses = self.coordinator.reconcile_responses(responses_json)
        
        total = self.reconciled_responses["total_requirements_analyzed"]
        print(f"✓ Reconciled responses for {total} requirements")
        
        return self.reconciled_responses

    def stage_4_critique_and_score(self) -> dict:
        """
        Stage 4: Critique aggregated responses (R/A/G scoring).
        
        TODO: This is Dev C's critic sub-agent.
        - Score confidence across specialists
        - Identify gaps
        - Generate assumptions list
        - Flag Red items requiring human override
        """
        print("\n=== STAGE 4: Critique & Scoring (Dev C) ===")
        print("⚠ Critic sub-agent not yet implemented")
        print("   Dev C will implement critic with R/A/G scoring")
        return None

    def stage_5_generate_output(self) -> dict:
        """
        Stage 5: Generate docx response with traceability.
        
        TODO: This is Dev C's output generation.
        - docx generation from reconciled responses
        - Traceability check: all content must link to requirement_id
        - Apply firm-voice skill
        """
        print("\n=== STAGE 5: Generate Output (Dev C) ===")
        print("⚠ Output generation not yet implemented")
        print("   Dev C will implement docx generation + traceability")
        return None

    def run_full_pipeline(self, mock_responses: Optional[list[dict]] = None) -> dict:
        """
        Run the full RFP response pipeline.
        Returns final state: requirements, dispatch plan, reconciled responses, critique.
        """
        print(f"\n{'='*60}")
        print(f"RFP Response Pipeline — {self.rfp_path.name}")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"{'='*60}")
        
        # Stage 1: Classify
        dispatch_plan = self.stage_1_classify_requirements()
        
        # Stage 2: Dispatch
        responses = self.stage_2_dispatch_to_specialists(mock_responses=mock_responses)
        
        # Stage 3: Reconcile
        if responses:
            self.stage_3_reconcile_responses()
        
        # Stage 4: Critique (when Dev C is ready)
        critique = self.stage_4_critique_and_score()
        
        # Stage 5: Output (when Dev C is ready)
        output = self.stage_5_generate_output()
        
        print(f"\n{'='*60}")
        print(f"Pipeline complete")
        print(f"{'='*60}\n")
        
        return {
            "dispatch_plan": dispatch_plan,
            "specialist_responses": responses,
            "reconciled": self.reconciled_responses,
            "critique": critique,
            "output": output
        }

    def export_dispatch_plan(self, output_path: str = "deal-desk-dispatch.json") -> None:
        """Export dispatch plan to JSON for specialists."""
        if not self.dispatch_plan:
            self.stage_1_classify_requirements()
        
        self.coordinator.to_json("coordinator-dispatch.json")
        
        # Also export just the dispatch piece for easier consumption
        dispatch_data = {
            "timestamp": datetime.now().isoformat(),
            "rfp_file": str(self.rfp_path),
            "total_requirements": self.dispatch_plan["total_requirements"],
            "specialist_dispatch": self.dispatch_plan["specialist_dispatch"]
        }
        
        Path(output_path).write_text(json.dumps(dispatch_data, indent=2))
        print(f"✓ Exported dispatch plan to {output_path}")

    def export_reconciliation_template(self, output_path: str = "reconciliation-template.json") -> None:
        """Export a template for specialist responses (helps ensure contract compliance)."""
        template = {
            "specialist_type": "Build|Run|Consulting|Commercial|Risk",
            "responses": [
                {
                    "requirement_id": "REQ-NNN",
                    "finding": "Brief statement of what our offering covers",
                    "confidence": "High|Medium|Low",
                    "assumptions": ["assumption 1", "assumption 2"],
                    "gaps": ["gap 1", "gap 2"],
                    "references": ["source 1", "source 2"]
                }
            ]
        }
        
        Path(output_path).write_text(json.dumps(template, indent=2))
        print(f"✓ Exported response template to {output_path}")


def mock_specialist_responses() -> list[dict]:
    """
    Generate mock specialist responses for testing.
    This simulates what specialists will return via the fixed contract.
    """
    return [
        {
            "requirement_id": "REQ-001",
            "specialist_type": "Consulting",
            "finding": "Our consulting methodology covers enterprise transformation roadmapping with phased migration planning.",
            "confidence": "High",
            "assumptions": ["Customer has documented current-state inventory", "Decision gates align with quarterly cycles"],
            "gaps": ["Custom ML pipeline roadmap requires specialist input from data science team"],
            "references": ["Consulting playbook §2.1", "Acme Corp case study"]
        },
        {
            "requirement_id": "REQ-001",
            "specialist_type": "Commercial",
            "finding": "24-month engagement, quarterly steering alignment gates are standard in our SOW.",
            "confidence": "High",
            "assumptions": ["Fixed-price for roadmap development; T&M for ongoing refinement"],
            "gaps": [],
            "references": ["Commercial playbook: Engagement models"]
        },
        {
            "requirement_id": "REQ-001",
            "specialist_type": "Risk",
            "finding": "Roadmap must address compliance constraints per Gramm-Leach-Bliley Act.",
            "confidence": "Medium",
            "assumptions": ["Legal compliance review at architecture gate"],
            "gaps": ["Detailed GLBA-specific architecture constraints not provided in RFP"],
            "references": ["Risk checklist: Financial services compliance"]
        }
    ]


if __name__ == "__main__":
    rfp_path = Path(__file__).parent / "synthetic-data" / "rfp-fintech-digital-transformation.md"
    
    # Initialize deal desk
    desk = DealDesk(str(rfp_path))
    
    # Export dispatch plan for specialists
    desk.export_dispatch_plan()
    desk.export_reconciliation_template()
    
    # Run pipeline with mock responses for testing
    print("\n>>> Running pipeline with mock specialist responses for testing...\n")
    mock_responses = mock_specialist_responses()
    result = desk.run_full_pipeline(mock_responses=mock_responses)
    
    # Print reconciled sample
    if desk.reconciled_responses:
        print("Sample reconciled response (REQ-001):")
        print("-" * 80)
        for req_resp in desk.reconciled_responses["merged_by_requirement"][:1]:
            print(f"\nRequirement: {req_resp['requirement_id']} — {req_resp['requirement_title']}")
            print(f"Status: {req_resp['mandatory_optional']}")
            print(f"\nSpecialist inputs:")
            for spec_input in req_resp["specialist_inputs"]:
                print(f"  • {spec_input['specialist']} (confidence: {spec_input['confidence']})")
                print(f"    Finding: {spec_input['finding'][:100]}...")
                print(f"    Gaps: {', '.join(spec_input['gaps']) if spec_input['gaps'] else 'None'}")
