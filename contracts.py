"""
Shared return contract for the Deal Desk specialist roster.

Every specialist calls `return_findings` once per requirement it touches.
This is the single source of truth for that shape — create_specialists.py
attaches it as a tool, test_specialists.py validates against it. Dev A's
coordinator/reconciliation code should import RETURN_FINDINGS_TOOL's
input_schema too, once it exists, so the two streams can't drift apart.
"""

RETURN_FINDINGS_TOOL = {
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
