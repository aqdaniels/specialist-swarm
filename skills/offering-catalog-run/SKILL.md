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
