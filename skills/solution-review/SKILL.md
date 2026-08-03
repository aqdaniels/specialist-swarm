---
name: solution-review
description: BTS-Synthetic weighted rubric for reviewing a draft proposal response before it ships — five scored dimensions, Red/Amber/Green per proposal section, and the method for enumerating coverage gaps and open assumptions. Use whenever critiquing, scoring, or gating a draft deal-desk proposal prior to document generation. Trigger on any request to review, score, or approve a proposal draft.
---

# Solution Review Rubric

SYNTHETIC STAND-IN — no existing firm solution-review rubric was found in this
repo to port in (PRD §5 asks teams to reuse one rather than author from
scratch). This rubric is authored from the PRD's five named dimensions and
gate structure only. Treat it the same as `voice-exemplars` and
`baseline-labels`: fine to demo with, **must be replaced with the firm's real
rubric before it's trusted for an actual deal.**

## The five dimensions

Score each 1-5 (5 = strongest) against the draft as a whole.

| Dimension | Weight | What you're scoring |
| --- | --- | --- |
| Responsiveness | 20% | Does the draft actually answer what the RFP asked, in the RFP's own terms? A brilliant answer to a question they didn't ask scores low here. |
| Differentiation | 25% | Does this read as ours, or could any vendor have submitted it? Highest weight — a generic draft is the single most common way a technically sound response loses (see firm-voice skill). |
| Technical credibility | 20% | Is the Build/Run/Consulting content specific enough to believe we've done this before — named offerings, real architecture/delivery detail, not marketing language? |
| Commercial coherence | 20% | Does the commercial construct match the technical scope (right model for the motion mix, no fixed-fee promise against an admittedly undefined scope)? Flag any number that isn't traceable to the commercial-playbook or a past-win citation. |
| Risk posture | 15% | Are contractual/regulatory deviations from our standard positions surfaced and reasoned, not silently accepted or silently ignored? |

**Weighted score** = Σ(dimension score × weight), on the 1-5 scale.
- **Green**: weighted score ≥ 4.0
- **Amber**: 3.0 – 3.99
- **Red**: < 3.0

Score the whole draft this way once per review round — this is the basis for
`dimension_scores` in `return_review` (see `contracts.py`).

## Red/Amber/Green per section

The coordinator's draft has six sections (`create_deal_desk_coordinator.py`).
Rate each section independently using **the worst of the dimensions that
apply to it** — not an average. One badly wrong number in an otherwise solid
commercial section still makes that section Red; averaging would hide it.

| Section | Governing dimension(s) | Red means |
| --- | --- | --- |
| Executive summary | Responsiveness, Differentiation | Doesn't name the customer's actual problem, or reads as boilerplate that could open any proposal |
| Customer understanding | Responsiveness | Misstates or hand-waves the scope actually described in the RFP |
| Why we're the right fit | Differentiation, Technical credibility | No named offering, no concrete architecture/delivery detail, or a catalog mapping that's clearly wrong |
| Commercial proposal | Commercial coherence | A specific dollar figure with no traceable source, a commercial model mismatched to motion mix, or a disqualifier from commercial-playbook triggered and ignored |
| Contract approach & risk posture | Risk posture | A blocker-severity deviation (per risk-checklist) accepted without flagging it |
| Risks and mitigations | Risk posture | A known risk (from any specialist's `gaps`) omitted entirely |

## Gap enumeration method

1. Take the full `requirement_id` set from the Requirements Register the
   coordinator was given.
2. Take the full `requirement_id` set actually referenced in the draft
   (explicitly, or traceable to a specialist finding folded into a section).
3. Anything in (1) not covered by (2) goes in `missing_requirements` verbatim
   by ID — don't paraphrase or summarize, the coordinator needs the exact IDs
   to go fix.

## Open-assumption enumeration method

Specialists already flag assumptions per-requirement in their `return_findings`
calls (`assumptions` field, `contracts.py`). Don't re-derive these — pull
them forward into `open_assumptions`, but filter for materiality: an
assumption changes the deal's commercial or legal exposure if wrong. Keep:
payment-term assumptions, SLA-tier assumptions, sizing-band assumptions,
regulatory-scope assumptions. Drop: purely editorial or formatting
assumptions — those aren't the human's decision to confirm.

## Hard block

Any single Red section blocks document generation regardless of the overall
weighted score or verdict — a strong average can't buy back one section that
would actively lose the deal. The coordinator (not this skill) owns what
happens next: request explicit human override, or hold at REVISE/STOP. See
the Critic section of the coordinator's system prompt for that procedure.
