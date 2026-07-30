"""
Requirements Register Parser
Extracts and classifies requirements from RFP documents.
"""

import re
import json
from pathlib import Path
from typing import TypedDict, Literal
from dataclasses import dataclass, asdict


MotionType = Literal["Consulting", "Build", "Run", "Risk", "Commercial"]


@dataclass
class Requirement:
    """A single extracted requirement from the RFP."""
    requirement_id: str
    motion_type: MotionType
    mandatory_optional: Literal["MANDATORY", "CONDITIONAL", "OPTIONAL"]
    section: str
    title: str
    verbatim_text: str


class RequirementsRegister:
    """Parse and classify RFP requirements."""

    # Motion type classifiers - keyword patterns that indicate type
    MOTION_KEYWORDS = {
        "Consulting": [
            "assessment", "advise", "roadmap", "strategy", "evaluation",
            "matrix", "evaluation matrix", "poc", "consulting", "vendor selection",
            "build vs. buy", "feasibility", "gap analysis", "design"
        ],
        "Build": [
            "implement", "architecture", "design and implement", "build", "develop",
            "microservices", "platform", "engineering", "migration", "rehost",
            "hardening", "create", "construct", "establish systems"
        ],
        "Run": [
            "managed operations", "24x5", "24x7", "support", "monitor", "incident response",
            "operations center", "sre", "on-call", "backup", "disaster recovery",
            "patch management", "capacity planning", "maintenance"
        ],
        "Risk": [
            "compliance", "security", "audit", "liability", "indemnification",
            "insurance", "breach", "regulatory", "soc 2", "hipaa", "glba", "pci-dss",
            "penetration test", "controls", "data loss prevention", "dlp", "zero-trust"
        ],
        "Commercial": [
            "pricing", "commercial", "discount", "payment", "terms", "payment terms",
            "cost", "fee", "rate", "budget", "most favored nation", "data residency",
            "staffing", "continuity", "flexibility", "change control", "vendor lock-in"
        ]
    }

    def __init__(self, rfp_path: str):
        """Initialize with path to RFP markdown file."""
        self.rfp_path = Path(rfp_path)
        self.content = self.rfp_path.read_text(encoding="utf-8")
        self.requirements: list[Requirement] = []

    def parse(self) -> list[Requirement]:
        """
        Parse RFP and extract all requirements.
        Returns list of Requirement objects.
        """
        # Find all requirements by looking for **REQ-NNN: pattern
        req_pattern = r"\*\*REQ-(\d{3}): ([^\*]+)\*\*\s*\n(.*?)(?=\*\*REQ-\d{3}:|$)"
        matches = re.finditer(req_pattern, self.content, re.DOTALL)

        for match in matches:
            req_id = f"REQ-{match.group(1)}"
            title = match.group(2).strip()
            body = match.group(3).strip()

            # Determine mandatory/conditional/optional
            mandatory_optional = self._classify_mandatory(req_id, title, body)

            # Classify motion type
            motion_type = self._classify_motion(title, body)

            # Extract verbatim requirement text (clean markdown, keep substance)
            verbatim_text = self._extract_verbatim(title, body)

            # Determine section by looking at headings before this requirement
            section = self._get_section(req_id)

            req = Requirement(
                requirement_id=req_id,
                motion_type=motion_type,
                mandatory_optional=mandatory_optional,
                section=section,
                title=title,
                verbatim_text=verbatim_text
            )
            self.requirements.append(req)

        return self.requirements

    def _get_section(self, req_id: str) -> str:
        """Find the section heading that precedes this requirement."""
        req_pos = self.content.find(f"**{req_id}:")
        if req_pos == -1:
            return "Unknown"

        # Look backwards for the nearest heading
        content_before = self.content[:req_pos]
        headings = re.findall(r"^#+\s+(.+)$", content_before, re.MULTILINE)

        return headings[-1] if headings else "Unknown"

    def _classify_mandatory(self, req_id: str, title: str, body: str) -> Literal["MANDATORY", "CONDITIONAL", "OPTIONAL"]:
        """Determine if requirement is mandatory, conditional, or optional."""
        text = f"{title} {body}".lower()

        if "[mandatory]" in text:
            return "MANDATORY"
        elif "[conditional" in text:
            return "CONDITIONAL"
        else:
            return "OPTIONAL"

    def _classify_motion(self, title: str, body: str) -> MotionType:
        """Classify requirement by motion type using keyword matching."""
        text = f"{title} {body}".lower()

        # Count keyword matches per motion type
        scores = {motion: 0 for motion in self.MOTION_KEYWORDS}

        for motion, keywords in self.MOTION_KEYWORDS.items():
            for keyword in keywords:
                scores[motion] += text.count(keyword)

        # Return motion with highest score, default to Consulting
        best_motion = max(scores, key=scores.get)
        return "Consulting" if scores[best_motion] == 0 else best_motion

    def _extract_verbatim(self, title: str, body: str) -> str:
        """
        Extract clean, readable verbatim text of the requirement.
        Removes markdown formatting but preserves substance.
        """
        lines = [title]

        # Take first substantial paragraphs, skip sub-headers for now
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("**") and not stripped.startswith("|"):
                lines.append(stripped)
            # Stop after first few lines to keep it concise
            if len(lines) > 8:
                break

        return " ".join(lines)

    def to_json(self, output_path: str = None) -> str:
        """Serialize requirements to JSON."""
        data = {
            "rfp_file": str(self.rfp_path),
            "total_requirements": len(self.requirements),
            "requirements": [asdict(r) for r in self.requirements]
        }

        json_str = json.dumps(data, indent=2)

        if output_path:
            Path(output_path).write_text(json_str)

        return json_str

    def to_csv(self, output_path: str) -> None:
        """Export requirements to CSV for easy viewing."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["requirement_id", "motion_type", "mandatory_optional", "section", "title"]
            )
            writer.writeheader()

            for req in self.requirements:
                writer.writerow({
                    "requirement_id": req.requirement_id,
                    "motion_type": req.motion_type,
                    "mandatory_optional": req.mandatory_optional,
                    "section": req.section,
                    "title": req.title
                })

    def summary(self) -> dict:
        """Return summary statistics."""
        by_motion = {}
        by_mandatory = {}

        for req in self.requirements:
            by_motion[req.motion_type] = by_motion.get(req.motion_type, 0) + 1
            by_mandatory[req.mandatory_optional] = by_mandatory.get(req.mandatory_optional, 0) + 1

        return {
            "total": len(self.requirements),
            "by_motion_type": by_motion,
            "by_mandatory_optional": by_mandatory
        }


if __name__ == "__main__":
    # Example usage
    rfp_path = Path(__file__).parent / "synthetic-data" / "rfp-fintech-digital-transformation.md"

    register = RequirementsRegister(str(rfp_path))
    requirements = register.parse()

    print(f"\n✓ Parsed {len(requirements)} requirements from RFP\n")

    # Print summary
    summary = register.summary()
    print("Summary by Motion Type:")
    for motion, count in summary["by_motion_type"].items():
        print(f"  {motion}: {count}")

    print("\nSummary by Mandatory/Optional:")
    for status, count in summary["by_mandatory_optional"].items():
        print(f"  {status}: {count}")

    print("\nDetailed Requirements:")
    print("-" * 100)
    for req in requirements:
        print(f"\n{req.requirement_id} [{req.motion_type}] {req.mandatory_optional}")
        print(f"Section: {req.section}")
        print(f"Title: {req.title}")
        print(f"Text: {req.verbatim_text[:150]}...")

    # Export to JSON
    register.to_json("requirements-register.json")
    print(f"\n✓ Exported to requirements-register.json")

    # Export to CSV
    register.to_csv("requirements-register.csv")
    print(f"✓ Exported to requirements-register.csv")
