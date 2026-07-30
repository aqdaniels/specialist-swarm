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
