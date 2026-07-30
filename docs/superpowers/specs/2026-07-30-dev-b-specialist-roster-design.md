# Dev B — Specialist Roster & Domain Skills

**Date:** 2026-07-30
**Scope owner:** Dev B (this stream)
**Source:** `hackathon/hackathon-prd.md` §2, §4, §5 + team scope split (Dev A / Dev B / Dev C)

## 1. What this replaces

The base repo's 4 function-based specialists (Pricing, Legal, Technical Fit, Competitive Intel) are
replaced with the PRD's 5-specialist motion-based roster: Build, Run, Consulting (Tier 1, motion-conditional),
Commercial, Risk & Compliance (Tier 2, always-on). Competitive Intel has no slot in the new design and is
dropped; Technical Fit's product-capability role is absorbed into the Build specialist's offering mapping.

## 2. Components

```
contracts.py                                (NEW, repo root, flat file)
create_specialists.py                       (REWRITE — same script shape, new roster)
skills/commercial-playbook/SKILL.md         (renamed from pricing-playbook/, rewritten)
skills/risk-checklist/SKILL.md              (renamed from legal-checklist/, extended)
skills/competitive-intel/SKILL.md           (left as-is, unused — flagged for Dev C's upload_skills.py cleanup)
skills/offering-catalog-build/SKILL.md      (NEW folder)
skills/offering-catalog-run/SKILL.md        (NEW folder)
skills/offering-catalog-consulting/SKILL.md (NEW folder)
synthetic-data/requirements-register-acme-stub.json  (NEW — our test fixture, disposable)
test_specialists.py                         (NEW, repo root, flat file)
```

No new top-level directories. `skills/` keeps its existing one-folder-per-skill pattern (goes from 3 → 5
populated + 1 orphaned). `contracts.py` and `test_specialists.py` sit at repo root alongside the existing
scripts, matching the current flat layout.

## 3. Roster (`create_specialists.py`)

All 5 specialists use `model: "claude-sonnet-5"` (uniform — matches existing pattern of specialists on one
tier, only coordinator/critic get the top model; that choice belongs to Dev A/Dev C's files, not touched here).

| key | name | skill | returns (per PRD §4 table) |
|---|---|---|---|
| `build` | Build Specialist | offering-catalog-build | offering mapping, architecture skeleton, technical approach, effort drivers |
| `run` | Run Specialist | offering-catalog-run | service model, SLA table, transition plan, steady-state assumptions |
| `consulting` | Consulting Specialist | offering-catalog-consulting | method, engagement shape, deliverable set, outcome framing |
| `commercial` | Commercial Specialist | commercial-playbook | pricing construct with named model, effort model, explicit assumption list |
| `risk_compliance` | Risk & Compliance Specialist | risk-checklist | flagged requirements, recommended positions, escalation list |

Each specialist's system prompt states: input is the Requirements Register (or motion-filtered slice) —
records with `requirement_id`, verbatim source text, section reference, mandatory/optional flag, assigned
motion + confidence (PRD §4 "Universal input"). Output is one `return_findings` tool call per requirement
touched.

**Commercial Specialist hard rule:** retrieval-only. Where effort can't be derived from the register, return
a sized placeholder in `finding` with the gap stated explicitly in `gaps` — never an invented number.

Script structure (create loop, `.specialist_ids.json` save, idempotency) is otherwise unchanged from today's
`create_specialists.py`.

## 4. Return contract (`contracts.py`)

```python
RETURN_FINDINGS_TOOL = {
    "name": "return_findings",
    "description": "Return findings for one requirement from the Requirements Register.",
    "input_schema": {
        "type": "object",
        "properties": {
            "requirement_id": {"type": "string"},
            "finding": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "assumptions": {"type": "array", "items": {"type": "string"}},
            "gaps": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["requirement_id", "finding", "confidence", "assumptions", "gaps"],
    },
}
```

Single source of truth for the requirement_id/finding/confidence/assumptions/gaps shape. Imported by
`create_specialists.py` to attach to every specialist's `tools` list. Dev A's coordinator/reconciliation
code should import the same constant once it exists, so the two streams can't drift out of sync on this
schema.

## 5. Skills content plan

All 5 skills stay in the existing fictional BTS-Synthetic universe (Enterprise Data Platform vendor) —
consistent with the 3 existing skills and the Acme RFP already in `synthetic-data/`. No real DXC catalog
or rate-card content goes in the repo (PRD non-goal: no live client data in the hackathon environment).

- **offering-catalog-build / -run / -consulting**: one entry per offering — name, description, when it
  applies, differentiator, delivery model, and an explicit disqualifier ("do not use this when..."). PRD §5:
  "an offering entry that only says what we do produces a specialist that maps everything to something."
- **commercial-playbook** (rewritten from pricing-playbook): rate card structure, commercial model selection
  logic (fixed fee / retainer / outcome-based, not SaaS discount bands), guardrails, past-win reference
  points. Encodes the retrieval-only/no-invented-numbers rule as a hard constraint in the skill itself, not
  just the specialist's system prompt.
- **risk-checklist** (extended from legal-checklist): keeps the existing item-by-item checklist structure
  (data residency, liability, IP, audit, termination, breach notification, subprocessors, governing law, SLA,
  insurance), adds financial-services and healthcare regulatory patterns (PRD: "highest-value cases").

## 6. Test fixture and smoke test

`synthetic-data/requirements-register-acme-stub.json` — ~12 hand-extracted records from
`synthetic-data/rfp-acme-corp.md`, matching the universal input shape (requirement_id, verbatim text,
section ref, mandatory flag, motion + confidence). This is a stand-in for Dev A's not-yet-built
`requirements_register.py` — disposable, superseded once that lands.

`test_specialists.py` — loads the stub register, calls each of the 5 live specialists with its
motion-filtered slice (Tier 2 specialists get the full register), asserts each reply contains at least one
valid `return_findings` tool call matching `contracts.py`'s schema. Prints pass/fail per specialist. Not a
permanent CI suite — one runnable check that the roster + skills work end to end, per this project's
"non-trivial logic leaves one runnable check" convention.

## 7. Out of scope / handoff notes

- `upload_skills.py`'s `SKILL_TO_SPECIALIST` map (Dev C's file) needs updating for the new specialist keys
  and skill folder names — not edited here, flagged for Dev C.
- `skills/competitive-intel/` is left in place but unreferenced by the new roster — Dev C's call whether to
  remove it during `upload_skills.py` cleanup.
- `create_coordinator.py` (Dev A's file) needs to reference the new specialist keys once this lands — not
  edited here.
- Roster-size limit (5 specialists + critic = 6 agents, PRD §12.1 open decision) is Dev A/coordinator's
  concern to confirm; this stream builds all 5 specialists unconditionally per PRD core scope.
