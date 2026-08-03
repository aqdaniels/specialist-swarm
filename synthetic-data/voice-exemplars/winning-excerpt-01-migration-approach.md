<!-- SYNTHETIC voice exemplar — illustrative only, not a real winning proposal. See README.md in this folder. -->

# Excerpt: Migration approach (delivery-anchored voice)

We don't propose a migration plan in the abstract — here's exactly how we'd move your Maximo 7.6.1.2 instance to Azure, week by week.

**Weeks 1–2 — Environment validation, not assumption.** Before we touch anything, we replicate your production database schema (the 21GB SQL Server instance, encrypted at rest) into a scratch Azure resource group and run a byte-for-byte comparison against your Attachment C specs. If your Akwire vScheduler tables don't migrate cleanly on the first pass, we find that out in week 1, not week 6.

**Weeks 3–5 — Parallel-run cutover, not a weekend gamble.** Your 8-hour RTO and 12-hour RPO aren't a target we hit on paper — they're a number we test against a simulated failover before go-live, twice. We stand up the production VMs (sized to your historical workload, not a generic template), cut over Azure AD authentication first as a lower-risk rehearsal, then migrate the database with the application layer already validated against it.

**Week 6 — Go-live, with a rollback path that's actually rehearsed.** We don't call it done because the migration ran. We call it done when your team has run a real transaction end-to-end in the new environment and confirmed it matches what came out of the old one.

This is the same sequence we run on every Maximo-to-Azure migration, because it's the sequence that keeps go-live boring — which is the only kind of go-live worth having.
