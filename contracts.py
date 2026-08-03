"""
Shared return contract for the Deal Desk specialist roster.

Every specialist calls `return_findings` once per requirement it touches.
This is the single source of truth for that shape — create_specialists.py
attaches it as a tool, test_specialists.py validates against it. Dev A's
coordinator/reconciliation code should import RETURN_FINDINGS_TOOL's
input_schema too, once it exists, so the two streams can't drift apart.
"""

RETURN_FINDINGS_TOOL = {
    "type": "custom",
    "name": "return_findings",
    "description": (
        "Return this specialist's findings for ONE requirement from the "
        "Requirements Register. Call once per requirement touched."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "requirement_id": {
                "type": "string",
                "description": "The requirement_id carried through unchanged from the register.",
            },
            "finding": {
                "type": "string",
                "description": "The specialist's substantive content for this requirement.",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
            "assumptions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Explicit assumptions made to produce this finding.",
            },
            "gaps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Where this specialist could not answer, and why.",
            },
        },
        "required": ["requirement_id", "finding", "confidence", "assumptions", "gaps"],
    },
}

REQUIRED_FINDING_FIELDS = ("requirement_id", "finding", "confidence", "assumptions", "gaps")


CRITIC_REVIEW_TOOL = {
    "type": "custom",
    "name": "return_review",
    "description": (
        "Return the Critic's structured review of the coordinator's draft proposal, "
        "per the solution-review skill's weighted rubric. Call once per review round "
        "(the coordinator may re-submit after REVISE, up to 2 rounds)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "dimension_scores": {
                "type": "object",
                "description": "1-5 score per solution-review rubric dimension (5 = strongest).",
                "properties": {
                    "responsiveness": {"type": "integer", "minimum": 1, "maximum": 5},
                    "differentiation": {"type": "integer", "minimum": 1, "maximum": 5},
                    "technical_credibility": {"type": "integer", "minimum": 1, "maximum": 5},
                    "commercial_coherence": {"type": "integer", "minimum": 1, "maximum": 5},
                    "risk_posture": {"type": "integer", "minimum": 1, "maximum": 5},
                },
                "required": [
                    "responsiveness",
                    "differentiation",
                    "technical_credibility",
                    "commercial_coherence",
                    "risk_posture",
                ],
            },
            "section_ratings": {
                "type": "array",
                "description": "Red/Amber/Green per proposal section, per the rubric's section-to-dimension mapping.",
                "items": {
                    "type": "object",
                    "properties": {
                        "section": {"type": "string"},
                        "rating": {"type": "string", "enum": ["Red", "Amber", "Green"]},
                        "notes": {"type": "string"},
                    },
                    "required": ["section", "rating", "notes"],
                },
            },
            "missing_requirements": {
                "type": "array",
                "items": {"type": "string"},
                "description": "requirement_ids from the Requirements Register with no corresponding content in the draft.",
            },
            "open_assumptions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Material assumptions (commercial, legal, delivery) surfaced in specialist findings that need human confirmation before this goes out.",
            },
            "verdict": {
                "type": "string",
                "enum": ["SHIP_IT", "REVISE", "STOP"],
            },
            "override_reason": {
                "type": "string",
                "description": (
                    "Required ONLY when verdict is SHIP_IT despite a Red section rating "
                    "(explicit human override was given). Leave empty otherwise."
                ),
            },
        },
        "required": [
            "dimension_scores",
            "section_ratings",
            "missing_requirements",
            "open_assumptions",
            "verdict",
        ],
    },
}

REQUIRED_REVIEW_FIELDS = (
    "dimension_scores",
    "section_ratings",
    "missing_requirements",
    "open_assumptions",
    "verdict",
)


def validate_review(call_input: dict) -> list[str]:
    """Return a list of validation error strings; empty list means valid."""
    errors = []
    for field in REQUIRED_REVIEW_FIELDS:
        if field not in call_input:
            errors.append(f"missing field: {field}")

    dims = call_input.get("dimension_scores")
    if isinstance(dims, dict):
        for dim in (
            "responsiveness",
            "differentiation",
            "technical_credibility",
            "commercial_coherence",
            "risk_posture",
        ):
            score = dims.get(dim)
            if not isinstance(score, int) or not (1 <= score <= 5):
                errors.append(f"dimension_scores.{dim} must be an integer 1-5, got {score!r}")
    elif "dimension_scores" in call_input:
        errors.append("dimension_scores must be an object")

    ratings = call_input.get("section_ratings")
    if isinstance(ratings, list):
        for entry in ratings:
            if not isinstance(entry, dict) or entry.get("rating") not in ("Red", "Amber", "Green"):
                errors.append(f"section_ratings entry must have rating Red/Amber/Green, got {entry!r}")
    elif "section_ratings" in call_input:
        errors.append("section_ratings must be a list")

    if call_input.get("verdict") not in ("SHIP_IT", "REVISE", "STOP"):
        errors.append(f"verdict must be SHIP_IT/REVISE/STOP, got {call_input.get('verdict')!r}")

    has_red = any(
        isinstance(e, dict) and e.get("rating") == "Red" for e in (ratings or []) if isinstance(ratings, list)
    )
    if has_red and call_input.get("verdict") == "SHIP_IT" and not call_input.get("override_reason", "").strip():
        errors.append("verdict is SHIP_IT with a Red section but override_reason is empty — hard block requires an explicit override reason")

    return errors


def validate_finding(call_input: dict) -> list[str]:
    """Return a list of validation error strings; empty list means valid."""
    errors = []
    for field in REQUIRED_FINDING_FIELDS:
        if field not in call_input:
            errors.append(f"missing field: {field}")

    if "requirement_id" in call_input and not isinstance(call_input["requirement_id"], str):
        errors.append("requirement_id must be a string")

    if "finding" in call_input and not (
        isinstance(call_input["finding"], str) and call_input["finding"].strip()
    ):
        errors.append("finding must be a non-empty string")

    if "confidence" in call_input and call_input["confidence"] not in ("high", "medium", "low"):
        errors.append(f"confidence must be high/medium/low, got {call_input['confidence']!r}")

    for field in ("assumptions", "gaps"):
        if field in call_input and not isinstance(call_input[field], list):
            errors.append(f"{field} must be a list")

    return errors
