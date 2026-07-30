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
