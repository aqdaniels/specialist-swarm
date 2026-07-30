"""
Offline logic check for the Dev B specialist pipeline — no live API calls.

Proves the deterministic pieces are wired correctly: the return_findings
schema validator, and each specialist's slice of the stub Requirements
Register. Does NOT prove the specialists behave correctly when actually
called — that requires test_specialists.py against a live API key.

Usage:
    python test_pipeline_logic.py
"""

from contracts import validate_finding
from test_specialists import load_requirements, slice_for, TIER_2_KEYS


def check(label: str, condition: bool) -> bool:
    print(f"  {'PASS' if condition else 'FAIL'}  {label}")
    return condition


def main() -> None:
    results = []

    valid_call = {
        "requirement_id": "R1",
        "finding": "Maps to X offering.",
        "confidence": "high",
        "assumptions": ["assumed Y"],
        "gaps": [],
    }
    results.append(check("valid call passes", validate_finding(valid_call) == []))

    missing_field = dict(valid_call)
    del missing_field["gaps"]
    results.append(check(
        "missing field caught",
        "missing field: gaps" in validate_finding(missing_field),
    ))

    bad_confidence = dict(valid_call, confidence="super-high")
    results.append(check(
        "bad confidence enum caught",
        any("confidence" in e for e in validate_finding(bad_confidence)),
    ))

    bad_assumptions_type = dict(valid_call, assumptions="not a list")
    results.append(check(
        "bad assumptions type caught",
        any("assumptions" in e for e in validate_finding(bad_assumptions_type)),
    ))

    empty_finding = dict(valid_call, finding="   ")
    results.append(check(
        "empty finding caught",
        any("finding" in e for e in validate_finding(empty_finding)),
    ))

    requirements = load_requirements()
    results.append(check("stub register has 12 requirements", len(requirements) == 12))

    for key in ("build", "run", "consulting"):
        req_slice = slice_for(key, requirements)
        results.append(check(
            f"{key} slice only contains {key}-motion requirements",
            bool(req_slice) and all(r["motion"] == key for r in req_slice),
        ))

    for key in TIER_2_KEYS:
        req_slice = slice_for(key, requirements)
        results.append(check(
            f"{key} (tier 2) sees full register",
            len(req_slice) == len(requirements),
        ))

    print()
    if all(results):
        print(f"All {len(results)} logic checks PASS.")
    else:
        print(f"{results.count(False)} of {len(results)} logic checks FAILED.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
