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
