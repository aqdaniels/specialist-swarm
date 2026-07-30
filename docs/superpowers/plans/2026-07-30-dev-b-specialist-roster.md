# Dev B Specialist Roster & Domain Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 4 function-based specialists with the PRD's 5 motion-based specialists (Build, Run, Consulting, Commercial, Risk & Compliance), give each a domain skill, and prove the whole roster works end to end against a hand-built Requirements Register stub.

**Architecture:** `contracts.py` holds the one shared JSON tool-schema (`return_findings`) that every specialist calls once per requirement it touches. `create_specialists.py` creates the 5 agents on `claude-sonnet-5`, each with that tool attached and a domain skill. `test_specialists.py` starts a live session per specialist against a stub Requirements Register and asserts the tool call matches the schema.

**Tech Stack:** Python, `anthropic` SDK (`beta.agents`, `beta.skills`, `beta.sessions`), Managed Agents beta (`anthropic-beta: managed-agents-2026-04-01`).

## Global Constraints

- Model for all 5 specialists: `claude-sonnet-5` (exact string, per user instruction).
- No new top-level directories. `skills/` keeps one-folder-per-skill; `contracts.py` and `test_specialists.py` are flat root files, matching existing layout.
- Reuse `pricing-playbook/` → `commercial-playbook/` and `legal-checklist/` → `risk-checklist/` by renaming in place; `competitive-intel/` is left untouched and unreferenced.
- All skill content stays in the fictional BTS-Synthetic universe — no real DXC catalog/rate-card content.
- Commercial Specialist: retrieval-only, never an invented number — unresolved effort is a stated placeholder + gap, not a bare figure.
- Every offering-catalog entry needs an explicit disqualifier ("do not use this when...").
- `return_findings` schema (fixed): `requirement_id` (string), `finding` (string), `confidence` (enum high/medium/low), `assumptions` (string array), `gaps` (string array) — all required.

---

### Task 1: Shared return contract

**Files:**
- Create: `contracts.py`

**Interfaces:**
- Produces: `RETURN_FINDINGS_TOOL` (dict, Anthropic custom-tool definition) — imported by `create_specialists.py` (Task 2) and `test_specialists.py` (Task 6).
- Produces: `REQUIRED_FINDING_FIELDS = ("requirement_id", "finding", "confidence", "assumptions", "gaps")` (tuple) and `validate_finding(call_input: dict) -> list[str]` (returns list of error strings, empty = valid) — used by `test_specialists.py` (Task 6).

- [ ] **Step 1: Write `contracts.py`**

```python
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
```

- [ ] **Step 2: Sanity-check the module loads**

Run: `python -c "import contracts; print(contracts.validate_finding({}))"`
Expected: prints a list of 5 "missing field" strings (one per required field), no traceback.

- [ ] **Step 3: Commit**

```bash
git add contracts.py
git commit -m "feat: add shared return_findings contract for specialist roster"
```

---

### Task 2: Rewrite `create_specialists.py` with the 5-specialist roster

**Files:**
- Modify: `create_specialists.py` (full rewrite of the `SPECIALISTS` list and the `tools=` argument in `main()`)

**Interfaces:**
- Consumes: `contracts.RETURN_FINDINGS_TOOL` (Task 1).
- Produces: `.specialist_ids.json` with keys `build`, `run`, `consulting`, `commercial`, `risk_compliance` — consumed by Task 6 (`test_specialists.py`) and (later, out of scope) Dev A's `create_coordinator.py`.

- [ ] **Step 1: Replace the `SPECIALISTS` list and tools wiring**

Replace the existing `SPECIALISTS` list (the 4 function-based entries) and the `tools=[{"type": "agent_toolset_20260401"}]` line inside `main()`'s loop with:

```python
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
```

Then in `main()`, change the agent-creation call's `tools=` argument from:

```python
tools=[{"type": "agent_toolset_20260401"}],
```

to:

```python
tools=[{"type": "agent_toolset_20260401"}, RETURN_FINDINGS_TOOL],
```

Leave everything else in the file (`metadata`, the save-to-`.specialist_ids.json` loop, `main()` guard clauses) unchanged.

- [ ] **Step 2: Run it against the live API**

Run: `python create_specialists.py`
Expected: 5 lines of `  Created <Name> -> agent_...`, then `Saved 5 specialist IDs to .specialist_ids.json`.

- [ ] **Step 3: Verify the saved IDs**

Run: `python -c "import json; d=json.load(open('.specialist_ids.json')); print(sorted(d.keys()))"`
Expected: `['build', 'commercial', 'consulting', 'risk_compliance', 'run']`

- [ ] **Step 4: Commit**

```bash
git add create_specialists.py .specialist_ids.json
git commit -m "feat: replace 4 function specialists with 5 motion-based specialists"
```

---

### Task 3: Rename and rewrite `commercial-playbook` skill

**Files:**
- Rename: `skills/pricing-playbook/` → `skills/commercial-playbook/`
- Modify: `skills/commercial-playbook/SKILL.md` (full content rewrite)

**Interfaces:**
- Produces: skill `display_title` "Commercial Playbook" — consumed by Task 7 (`upload_skills.py` map update is Dev C's, out of scope, but the folder name and frontmatter `name` must be `commercial-playbook` for that future wiring to work).

- [ ] **Step 1: Rename the directory**

Run: `git mv skills/pricing-playbook skills/commercial-playbook` (falls back to plain `mv` if git mv errors on this checkout)

- [ ] **Step 2: Rewrite `skills/commercial-playbook/SKILL.md`**

```markdown
---
name: commercial-playbook
description: BTS-Synthetic commercial playbook for services engagements — rate card structure, commercial model selection (fixed fee / retainer / outcome-based), and past-win reference points. Use whenever recommending a commercial construct for an inbound RFP requirement. Trigger on any request to price, size effort, pick a commercial model, or recommend deal structure. Retrieval-only: select and apply, never invent a number.
---

# Commercial Playbook

## Rate card structure (Enterprise Data Platform engagements)

| Band | Typical annual engagement value | Delivery effort shape |
| --- | --- | --- |
| Small | < $250K | Single-workstream, 1 delivery pod |
| Medium | $250K – $750K | 2-3 workstreams, phased delivery |
| Large | $750K – $2M | Multi-workstream, dedicated program structure |
| Strategic | > $2M | Multi-year, executive sponsorship required |

Bands are sizing bands, not quotes. Use them to size a placeholder, not to fabricate a number.

## Commercial models

- **Fixed fee** — scope is well-defined, requirements register shows low ambiguity (few "gaps" flagged by other specialists). Preferred for single-motion, single-workstream deals.
- **Retainer** — ongoing Run-motion work with steady-state assumptions (SLA tiers, transition plans already defined). Preferred when the register shows recurring managed-service requirements rather than one-off delivery.
- **Outcome-based** — customer explicitly ties payment to a measurable business outcome (e.g., cost reduction, uptime target). Only recommend this when the RFP itself proposes outcome-based terms; do not propose it unprompted — it concentrates risk on us.

## Selection logic

1. If the register is dominated by Build-motion requirements with clear scope: **fixed fee**.
2. If the register is dominated by Run-motion requirements: **retainer**.
3. If the RFP explicitly asks for outcome-based terms: **outcome-based**, flagged for VP Sales sign-off (outcome deals always need executive review).
4. Mixed-motion registers: propose fixed fee for the Build/Consulting slice and retainer for the Run slice as two line items, rather than forcing one model across a mixed deal.

## Retrieval-only rule — do not invent numbers

You select a band and a model. You do not calculate a dollar figure from scratch.

- If the register gives you enough to size a band (scope, scale, duration signals), state the band and the model, and mark `confidence` accordingly.
- If it doesn't, return a clearly labeled placeholder: `"sized as <Band> per commercial-playbook, not a firm quote"` in `finding`, and state exactly what's missing (e.g. "no user count given, cannot size support tier") in `gaps`.
- Never return a specific dollar amount unless it's a list-price or past-win figure you are citing directly from source data.

## Payment terms guardrails

- **Default:** Annual upfront, Net 30.
- **Acceptable concessions:** Quarterly billing (no price change), Net 60 for large/strategic accounts with strong credit.
- **Do not accept:** Net 90+, monthly billing on annual commitments, payment tied to milestones without a written cure period.

## Disqualifiers — when NOT to recommend a model

- **Do not recommend fixed fee** when the register has 3+ "gap" flags from other specialists on the same requirement cluster — undefined scope under fixed fee is how engagements lose money.
- **Do not recommend outcome-based** unless the RFP itself proposes it — proposing it unprompted signals desperation and invites scope disputes.
- **Do not recommend retainer** for a one-time migration or build-only deal — retainers imply an ongoing relationship that doesn't exist yet.

## Reading the room

If the RFP demands a discount/reduction language typical of SaaS deals (e.g., "% off list") rather than services commercial language, flag this to the coordinator — it may mean the customer is evaluating us against a product vendor, not a services firm, and the response should lead with outcome and delivery model, not a percentage.
```

- [ ] **Step 3: Verify frontmatter parses**

Run: `python -c "import pathlib,re; t=pathlib.Path('skills/commercial-playbook/SKILL.md').read_text(); assert t.startswith('---'); print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add skills/commercial-playbook skills/pricing-playbook
git commit -m "feat: rename pricing-playbook to commercial-playbook, rewrite for services commercial models"
```

---

### Task 4: Rename and extend `risk-checklist` skill

**Files:**
- Rename: `skills/legal-checklist/` → `skills/risk-checklist/`
- Modify: `skills/risk-checklist/SKILL.md` (keep existing 10-item structure, add items 11-12)

**Interfaces:**
- Produces: skill `display_title` "Risk Checklist" — folder/frontmatter `name` must be `risk-checklist`.

- [ ] **Step 1: Rename the directory**

Run: `git mv skills/legal-checklist skills/risk-checklist`

- [ ] **Step 2: Update frontmatter and append two new checklist items**

Change the frontmatter block at the top of `skills/risk-checklist/SKILL.md` from:

```markdown
---
name: legal-checklist
description: BTS-Synthetic legal review checklist for inbound RFPs and contracts. Use whenever reviewing an RFP for contractual risk — covers data residency, liability, IP, audit, termination, and our standard counter-positions. Trigger on any request to legal-review, flag, redline, or assess contractual terms in an RFP or customer document.
---
```

to:

```markdown
---
name: risk-checklist
description: BTS-Synthetic regulatory and contractual risk checklist for inbound RFPs. Covers data residency, liability, IP, audit, termination, and sector-specific regulatory patterns (financial services, healthcare). Use whenever screening an RFP for contractual or regulatory risk. Trigger on any request to risk-review, flag, redline, or assess contractual/regulatory terms in an RFP or customer document.
---
```

Then, immediately before the existing `## How to flag` section, insert two new items (renumbering `## How to flag` is not needed — items are additive, existing 1-10 stay as-is):

```markdown
## 11. Financial services patterns

**Our standard:** We are not a bank or broker-dealer; we do not accept obligations that require us to hold a financial services license (e.g., acting as a fiduciary over customer funds, custody of financial instruments).

**Common deviations:**
- RFP requires SOC 1 Type II (not just SOC 2) because customer is itself regulated → negotiable, check with compliance before committing to a timeline
- RFP requires PCI-DSS scope because payment card data flows through the platform → blocker unless PCI-DSS certification already exists for the deployment target; do not promise a certification timeline without compliance sign-off
- RFP requires model risk management documentation (SR 11-7 style) for any ML/predictive component → negotiable, we can provide model documentation but not a formal model risk attestation

## 12. Healthcare patterns

**Our standard:** We are HIPAA-eligible (BAA available) but not a covered entity. We do not accept obligations beyond what a Business Associate Agreement covers.

**Common deviations:**
- RFP requires a signed BAA → acceptable, standard offering
- RFP requires FDA-regulated software validation (e.g., treating the platform as part of a medical device data pipeline) → blocker, our platform is not validated as a medical device component
- RFP requires HITRUST certification specifically (not just HIPAA-aligned controls) → negotiable, check current certification status before committing
```

- [ ] **Step 3: Verify frontmatter `name` matches folder**

Run: `python -c "import pathlib; t=pathlib.Path('skills/risk-checklist/SKILL.md').read_text(); assert 'name: risk-checklist' in t; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add skills/risk-checklist skills/legal-checklist
git commit -m "feat: rename legal-checklist to risk-checklist, add financial-services and healthcare patterns"
```

---

### Task 5: Author the 3 offering-catalog skills

**Files:**
- Create: `skills/offering-catalog-build/SKILL.md`
- Create: `skills/offering-catalog-run/SKILL.md`
- Create: `skills/offering-catalog-consulting/SKILL.md`

**Interfaces:**
- Produces: skill `display_title`s "Offering Catalog Build" / "Offering Catalog Run" / "Offering Catalog Consulting" — folder/frontmatter `name`s must match exactly for Task 7 (Dev C's `upload_skills.py`, out of scope here) to attach them later.

- [ ] **Step 1: Write `skills/offering-catalog-build/SKILL.md`**

```markdown
---
name: offering-catalog-build
description: BTS-Synthetic Build/Transform offering catalog for the Enterprise Data Platform — reference architectures, accelerators, and delivery models for custom engineering and modernization work. Use whenever mapping an RFP requirement to a build/transformation offering. Trigger on any request to assess build fit, propose an architecture, or scope a modernization engagement.
---

# Offering Catalog — Build

## Offerings

### Lakehouse Modernization Accelerator
- **Description:** Migrate a legacy warehouse (Teradata, on-prem Hadoop) onto the BTS-Synthetic lakehouse, using pre-built schema-translation and CDC pipelines.
- **When it applies:** Customer has a named legacy system being decommissioned, with a defined cutover deadline.
- **Differentiator:** Pre-built connectors for Teradata and Hadoop cut typical migration time by ~40% versus a from-scratch build.
- **Delivery model:** Fixed-fee, phased by source system. Typical phase: assess (2wk) → pilot migration (4wk) → cutover (2wk) per source.
- **Disqualifier:** Do not use this when the customer has no legacy system to decommission — this is a migration accelerator, not a greenfield build offering.

### Real-Time Ingest Build-Out
- **Description:** Custom-engineered streaming ingest pipeline for high-volume IoT/event data, built on the platform's native Kafka/Kinesis consumers.
- **When it applies:** RFP specifies a named events/second target and a device/source count.
- **Differentiator:** Tuned for sustained throughput up to 250K events/second on single-region deployments.
- **Delivery model:** Fixed-fee per pipeline, sized by peak events/second and source device count.
- **Disqualifier:** Do not use this when the RFP demands sub-100ms streaming query latency — the platform's streaming layer is not best-in-class there (see offering-catalog-run's SLA add-on for the closest fit, and flag as partial fit regardless).

### ML Pipeline Build-Out (Predictive Maintenance pattern)
- **Description:** Feature store + model registry + serving pipeline build-out for a named ML use case, using the platform's native model-serving.
- **When it applies:** RFP names a specific ML use case (e.g., predictive maintenance) with a defined data source, even if not yet in production.
- **Differentiator:** Bring-your-own-model support (HuggingFace, Anthropic, OpenAI) avoids vendor lock-in on the model layer itself.
- **Delivery model:** Fixed-fee for pipeline build-out; model training/tuning is scoped separately and is NOT included by default.
- **Disqualifier:** Do not use this when the RFP's ML requirement is aspirational with no named use case or data source — that's a Consulting-motion roadmap engagement (see offering-catalog-consulting), not a build engagement.

### Governance & Residency Build-Out
- **Description:** Configure per-table data residency pinning, row/column-level security, and PII detection/masking for multi-region deployments.
- **When it applies:** RFP has an explicit data residency requirement (e.g., "EU data stays in EU") combined with multi-region deployment.
- **Differentiator:** Per-table residency enforcement (not just per-database) — finer-grained than most lakehouse competitors offer.
- **Delivery model:** Fixed-fee, typically bundled into the Lakehouse Modernization Accelerator rather than sold standalone.
- **Disqualifier:** Do not use this standalone when there's no multi-region requirement — single-region deployments don't need residency pinning configuration.

## Effort drivers (for sizing, not pricing)

- Number of source systems to migrate (each adds a phase)
- Peak events/second and source device count (drives ingest pipeline complexity)
- Number of regions requiring residency pinning
- Whether an ML use case has a defined data source already, or needs discovery first

## How to format your output

For each requirement: name the offering (or state no offering fits), cite the specific RFP signal that triggered the match, note the architecture skeleton implied, and list effort drivers. If a requirement partially fits (e.g., sub-100ms latency demand), say so explicitly rather than rounding up to a full match.
```

- [ ] **Step 2: Write `skills/offering-catalog-run/SKILL.md`**

```markdown
---
name: offering-catalog-run
description: BTS-Synthetic Run/Managed Services offering catalog for the Enterprise Data Platform — SLA tiers, transition method, and steady-state operating models. Use whenever mapping an RFP requirement to a managed-service offering. Trigger on any request to assess run/operate fit, propose an SLA, or scope a managed-services transition.
---

# Offering Catalog — Run

## Offerings

### Standard Managed Operations
- **Description:** 24/5 monitoring, incident response, and platform administration for a live deployment.
- **When it applies:** Customer wants us to operate the platform post-go-live, no bespoke uptime commitment beyond the standard tier.
- **Differentiator:** Dedicated CSM included at Enterprise tier; not an outsourced ticket queue.
- **Delivery model:** Retainer, priced per environment (prod / non-prod) under management.
- **SLA tier:** 99.95% monthly uptime, service credits up to 30% of monthly fees as sole remedy.
- **Disqualifier:** Do not use this when the RFP demands 99.99%+ uptime — that requires the High-Availability Add-On below, not the standard tier.

### High-Availability Add-On
- **Description:** Bespoke multi-region active-active architecture and 24/7 (not 24/5) operations for uptime-critical deployments.
- **When it applies:** RFP explicitly demands 99.99% or higher monthly uptime.
- **Differentiator:** Only offering in the catalog that can credibly support 99.99%+; standard tier cannot.
- **Delivery model:** Retainer premium on top of Standard Managed Operations, typically $80K-$120K/year per the platform's published add-on pricing.
- **SLA tier:** 99.99%, requires multi-region active-active architecture as a prerequisite (may require a Build-motion engagement first if not already in place).
- **Disqualifier:** Do not propose this reflexively for every "high availability" mention — only when a specific numeric SLA target at or above 99.99% is stated. Vague "high availability" language without a number should get the Standard tier plus a clarifying question, not an automatic premium sell.

### Legacy Decommission Transition Service
- **Description:** Managed cutover and parallel-run support while a legacy system (e.g., Teradata) is being retired, including rollback planning.
- **When it applies:** RFP names a legacy system being decommissioned on a multi-year timeline (not an immediate hard cutover).
- **Differentiator:** Parallel-run period reduces cutover risk versus a hard cutover.
- **Delivery model:** Time-boxed retainer for the duration of the parallel-run period, then rolls into Standard Managed Operations.
- **Disqualifier:** Do not use this when there's no legacy system being retired — this is a transition service, not a standing offering.

## SLA tiers reference

| Tier | Uptime | Remedy | Prerequisite |
| --- | --- | --- | --- |
| Standard | 99.95% monthly | Credits up to 30% of monthly fees | None |
| High-Availability Add-On | 99.99% monthly | Credits up to 30% of monthly fees | Multi-region active-active architecture |

## Steady-state assumptions (state these explicitly when sizing)

- Number of environments under management (prod/non-prod count)
- Whether multi-region active-active is already in place or needs to be built first (drives whether Build-motion work is a prerequisite)
- Expected incident volume based on ingest scale (higher event volume → higher operational load)

## Disqualifiers — general

- Do not propose any Run offering for a requirement with no operational/SLA component at all (e.g., a pure IP-ownership contractual term) — that belongs to Risk & Compliance, not Run.

## How to format your output

For each requirement: name the service model and SLA tier, cite the RFP signal, state the transition plan if a legacy system is involved, and list steady-state assumptions explicitly.
```

- [ ] **Step 3: Write `skills/offering-catalog-consulting/SKILL.md`**

```markdown
---
name: offering-catalog-consulting
description: BTS-Synthetic Consulting/Advisory offering catalog for the Enterprise Data Platform — advisory method, workshop constructs, and deliverable definitions. Use whenever mapping an RFP requirement to an advisory offering. Trigger on any request to assess advisory fit, propose a roadmap engagement, or scope an assessment.
---

# Offering Catalog — Consulting

## Offerings

### Data Platform Readiness Assessment
- **Description:** 4-6 week assessment of current-state data architecture, producing a target-state roadmap and migration sequencing recommendation.
- **When it applies:** RFP asks for a roadmap, strategy, or "assessment" before committing to a build, OR the RFP's scope is broad enough that sequencing itself is an open question (e.g., multiple legacy systems with no stated order).
- **Differentiator:** Deliverable includes a sequencing argument, not just a capability gap list — tells the customer what to do first and why.
- **Delivery model:** Fixed-fee, workshop-based (typically 3-4 structured workshops with stakeholders).
- **Deliverables:** Current-state architecture map, target-state architecture, sequencing roadmap, executive readout deck.
- **Disqualifier:** Do not propose this when the RFP already has a fully defined scope and timeline — that's a Build-motion engagement; re-assessing a decision the customer has already made reads as stalling.

### Predictive Maintenance Use-Case Discovery
- **Description:** Structured discovery workshops to define a specific ML use case (data sources, target outcome, success metric) before any pipeline is built.
- **When it applies:** RFP mentions ML/predictive maintenance as "planned, not active" with no named data source or success metric yet.
- **Differentiator:** Produces a use-case definition specific enough to hand directly to a Build-motion ML Pipeline Build-Out — avoids the common failure mode of building a pipeline before the use case is well-defined.
- **Delivery model:** Fixed-fee, typically 2-3 weeks.
- **Deliverables:** Use-case definition document, data source inventory, success metric definition.
- **Disqualifier:** Do not propose this when the RFP already names a specific data source and success metric — go straight to the Build-motion ML Pipeline Build-Out instead.

### Governance Operating Model Advisory
- **Description:** Advisory engagement to define roles, processes, and policy for data governance (access control, PII handling, audit) ahead of a technical build.
- **When it applies:** RFP has extensive governance/compliance language but no technical architecture detail — the customer is asking "how should we govern this," not "build this."
- **Differentiator:** Produces an operating model (who approves what, how exceptions are handled) rather than just a technical control configuration.
- **Delivery model:** Fixed-fee, workshop-based.
- **Deliverables:** Governance operating model document, RACI for data access decisions, policy templates.
- **Disqualifier:** Do not propose this for a requirement that's really asking for a technical control (e.g., "enable row-level security") — that's a Build-motion configuration task, not an advisory engagement.

## Outcome framing (use this to write the "outcome framing" field)

For every mapped requirement, state the outcome framing as: what decision or capability the customer will have at the end that they don't have now. Not "we'll run workshops" — "you'll have a sequenced roadmap you can take to your board."

## Disqualifiers — general

- Do not propose a Consulting offering when the RFP's own requirement already specifies a concrete deliverable and timeline with no open strategic question — that's Build or Run, not Consulting. Consulting exists for open questions, not execution.

## How to format your output

For each requirement: name the offering, cite the RFP signal, state the engagement shape (duration, workshop count) and deliverable set, and frame the outcome in the terms above.
```

- [ ] **Step 4: Verify all three frontmatters parse**

Run: `python -c "
import pathlib
for name in ['build', 'run', 'consulting']:
    t = pathlib.Path(f'skills/offering-catalog-{name}/SKILL.md').read_text()
    assert t.startswith('---') and f'name: offering-catalog-{name}' in t
print('ok')
"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add skills/offering-catalog-build skills/offering-catalog-run skills/offering-catalog-consulting
git commit -m "feat: author offering-catalog-build/run/consulting skills"
```

---

### Task 6: Stub Requirements Register + live smoke test

**Files:**
- Create: `synthetic-data/requirements-register-acme-stub.json`
- Create: `test_specialists.py`

**Interfaces:**
- Consumes: `contracts.RETURN_FINDINGS_TOOL`, `contracts.validate_finding` (Task 1); `.specialist_ids.json` (Task 2); `.environment_id` (pre-existing, from `setup_environment.py`).
- Produces: pass/fail printout per specialist; no other file consumes this.

- [ ] **Step 1: Write `synthetic-data/requirements-register-acme-stub.json`**

```json
{
  "requirements": [
    {
      "requirement_id": "R1",
      "text": "The platform must support real-time ingest from ~40,000 IoT devices in the field, peak 80,000 events/second.",
      "section": "2.1 Workloads / 2.2 Scale",
      "mandatory": true,
      "motion": "build",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R2",
      "text": "Native Power BI integration is non-negotiable — 600 users today.",
      "section": "2.3 Capabilities",
      "mandatory": true,
      "motion": "build",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R3",
      "text": "Data residency: EU customer data must remain in EU, multi-region deployment primary EU secondary US East.",
      "section": "2.3 Capabilities",
      "mandatory": true,
      "motion": "build",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R4",
      "text": "Machine learning pipelines for predictive maintenance (planned, not active).",
      "section": "2.1 Workloads",
      "mandatory": false,
      "motion": "consulting",
      "motion_confidence": "medium"
    },
    {
      "requirement_id": "R5",
      "text": "We are seeking a 3-year initial term with a 2-year renewal option, pricing for the full 5-year horizon fixed at signature with no escalators.",
      "section": "3.1 Term",
      "mandatory": true,
      "motion": "run",
      "motion_confidence": "medium"
    },
    {
      "requirement_id": "R6",
      "text": "Vendor must commit to 99.99% monthly uptime. SLA failures of any duration entitle Acme to terminate immediately with full refund of fees paid in the affected month.",
      "section": "4.3 Service Levels",
      "mandatory": true,
      "motion": "run",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R7",
      "text": "Acme reserves the right to audit vendor's controls, facilities, and personnel without prior notice, up to four times per calendar year, at vendor's cost.",
      "section": "4.2 Audit",
      "mandatory": true,
      "motion": "risk_compliance",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R8",
      "text": "Vendor liability for any data breach is uncapped; vendor must indemnify Acme for all costs including regulatory fines and reputational damages.",
      "section": "4.1 Liability",
      "mandatory": true,
      "motion": "risk_compliance",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R9",
      "text": "All work product, including custom development, configurations, and integrations, shall vest in Acme Corp upon creation.",
      "section": "4.4 IP",
      "mandatory": true,
      "motion": "risk_compliance",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R10",
      "text": "Vendor shall obtain Acme's prior written consent, withholdable at Acme's sole discretion, before engaging any subprocessor.",
      "section": "4.5 Subprocessors",
      "mandatory": true,
      "motion": "risk_compliance",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R11",
      "text": "The successful vendor must offer no less than 35% off published list pricing. Annual fees billed in advance, due Net 90.",
      "section": "3.2 Payment / 3.3 Discount",
      "mandatory": true,
      "motion": "commercial",
      "motion_confidence": "high"
    },
    {
      "requirement_id": "R12",
      "text": "Vendor must warrant that pricing offered to Acme is no less favourable than pricing offered to any comparable customer for the duration of the contract (Most Favoured Nation).",
      "section": "3.4 Most Favoured Nation",
      "mandatory": true,
      "motion": "commercial",
      "motion_confidence": "high"
    }
  ]
}
```

- [ ] **Step 2: Write `test_specialists.py`**

```python
"""
Smoke test: call each of the 5 live specialists with its motion-filtered
slice of the stub Requirements Register, and assert every reply contains
at least one valid return_findings tool call.

Not a permanent CI suite — one runnable check that the roster + skills
work end to end. Requires .specialist_ids.json (create_specialists.py)
and .environment_id (setup_environment.py) to already exist.

Usage:
    python test_specialists.py
"""

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic

from contracts import validate_finding

STUB_REGISTER_PATH = Path("synthetic-data/requirements-register-acme-stub.json")

# Tier 2 specialists see every requirement; Tier 1 see only their motion's slice.
TIER_2_KEYS = {"commercial", "risk_compliance"}


def load_requirements() -> list[dict]:
    data = json.loads(STUB_REGISTER_PATH.read_text())
    return data["requirements"]


def slice_for(specialist_key: str, requirements: list[dict]) -> list[dict]:
    if specialist_key in TIER_2_KEYS:
        return requirements
    return [r for r in requirements if r["motion"] == specialist_key]


def run_specialist(client: Anthropic, environment_id: str, specialist_id: str, specialist_key: str, requirements: list[dict]) -> tuple[bool, str]:
    requirement_ids = {r["requirement_id"] for r in requirements}
    register_text = json.dumps(requirements, indent=2)

    session = client.beta.sessions.create(
        agent=specialist_id,
        environment_id=environment_id,
        title=f"Dev B smoke test — {specialist_key}",
    )

    user_message = (
        "Here is your slice of the Requirements Register. Call return_findings "
        "once per requirement below.\n\n" + register_text
    )

    tool_calls = []
    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_message}]}],
        )
        for event in stream:
            if event.type == "agent.tool_use" and getattr(event, "name", None) == "return_findings":
                tool_calls.append(event.input)
            elif event.type == "session.status_idle":
                break

    if not tool_calls:
        return False, "no return_findings tool calls received"

    errors = []
    for call in tool_calls:
        call_errors = validate_finding(call)
        if call_errors:
            errors.append(f"  call {call.get('requirement_id', '?')}: {'; '.join(call_errors)}")
        elif call["requirement_id"] not in requirement_ids:
            errors.append(f"  call {call['requirement_id']}: not in this specialist's slice")

    if errors:
        return False, f"{len(tool_calls)} calls received, {len(errors)} invalid:\n" + "\n".join(errors)

    covered = {c["requirement_id"] for c in tool_calls}
    missing = requirement_ids - covered
    if missing:
        return False, f"{len(tool_calls)} valid calls, but missing requirement(s): {sorted(missing)}"

    return True, f"{len(tool_calls)} valid calls, all {len(requirement_ids)} requirement(s) covered"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".specialist_ids.json")
    environment_id_path = Path(".environment_id")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_specialists.py first.")
    if not environment_id_path.exists():
        raise SystemExit("Run setup_environment.py first.")

    specialist_ids = json.loads(specialist_ids_path.read_text())
    environment_id = environment_id_path.read_text().strip()
    requirements = load_requirements()

    client = Anthropic(default_headers={"anthropic-beta": "managed-agents-2026-04-01"})

    results = {}
    for key, specialist_id in specialist_ids.items():
        req_slice = slice_for(key, requirements)
        print(f"\n=== {key} ({len(req_slice)} requirement(s)) ===")
        ok, detail = run_specialist(client, environment_id, specialist_id, key, req_slice)
        results[key] = ok
        print(("PASS: " if ok else "FAIL: ") + detail)

    print("\n=== Summary ===")
    for key, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {key}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the smoke test against the live API**

Run: `python test_specialists.py`
Expected: `PASS` for all 5 specialists in the summary. If any specialist FAILs, read the printed detail (missing tool calls, schema errors, or missing requirement coverage), fix that specialist's system prompt in `create_specialists.py` or the skill content, re-run `python create_specialists.py` (idempotent — reuses existing agents by ID, only affects the ones with prompt changes if the script is extended to update; if not, delete the affected key from `.specialist_ids.json` and re-run to recreate that one specialist), then re-run `python test_specialists.py` until all 5 PASS.

- [ ] **Step 4: Commit**

```bash
git add synthetic-data/requirements-register-acme-stub.json test_specialists.py
git commit -m "test: add Acme requirements register stub and live specialist smoke test"
```

---

## Self-Review Notes

- **Spec coverage:** Task 1 covers spec §4 (contracts.py); Task 2 covers §3 (roster); Tasks 3-5 cover §5 (all 5 skills + disqualifiers + retrieval-only rule); Task 6 covers §6 (stub + smoke test). Handoff notes (§7) are explicitly out of scope for this plan, not silently dropped.
- **Type consistency:** `return_findings` field names (`requirement_id`, `finding`, `confidence`, `assumptions`, `gaps`) are identical across `contracts.py`, all 5 system prompts, the stub register's `requirement_id` field, and `test_specialists.py`'s validation.
- **No placeholders:** every task has literal file content, not descriptions of content.
