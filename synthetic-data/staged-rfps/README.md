# Staged RFPs — Data Staging §8

Real, public-record government procurement RFPs, sourced as substitutes for anonymized historical client RFPs (none were available — see gap note below). All three are already public documents, so no anonymization was needed or applied.

## 1. `inprs-cloud-migration-iam-rfp.pdf`
**Indiana Public Retirement System (INPRS) — RFP 23-04**, cloud migration disposition + IAM assessment.

- **Motion mix:** Consulting-heavy (application assessment, transformation roadmap) + Risk & Compliance-heavy (IAM, ZTNA/SASE, NIST 800-63-3, HIPAA/GDPR references). Build-adjacent only — RFP explicitly bars vendors from proposing their own technical solution; scope is an independent assessment, not implementation.
- **Term:** 3 years + 3 one-year renewal options (10-year cap).
- **Use for:** Consulting + Risk specialist testing; good example of a requirement that should NOT be classified as Build despite cloud/IAM keywords.

## 2. `port-tacoma-maximo-cloud-migration-support-rfp.pdf`
**Port of Tacoma — RFP #071658**, Maximo Azure Cloud Migration and Support.

- **Motion mix:** Best multi-tower example — Build (fixed-price one-time migration, $25K–$75K) + Run (ongoing managed services, $3K–$6K/month) + light Consulting (deployment architecture planning) + Risk (Attachment E — Vendor Cybersecurity Self-Assessment).
- **Commercial:** Literal rate-table structure across three pricing models (fixed price, T&M, monthly retainer) — usable as a structural reference for `commercial-playbook`.
- **Technical detail:** Attachment C has real environment specs (SQL Server 2016, 21GB DB, RTO 8hrs/RPO 12hrs, Azure AD auth) — good for Build specialist effort-driver testing.
- **Term:** 3-year personal services contract, not-to-exceed $200,000, one optional 1-year extension.
- **Use for:** Primary multi-tower classification test case; compact (19 pages) so easy to trace requirement-by-requirement.

## 3. `suny-it-managed-services-rfp.pdf`
**SUNY Research Foundation — IT Managed Services RFP**.

- **Motion mix:** Single-motion contrast case — pure Run. 8 functional towers (Application, Data Center, Service Desk, Networking, Workstation/Printer, Network OS, Voice/Video, IT Security), vendors may bid on any subset.
- **Commercial:** Fee structure required annually per service area, 5-year minimum term assumed. Attachment B (IS Summary Job Descriptions) gives experience-tier structure (Associate 1–3yr / Intermediate 3–7yr / Senior 7+yr) per role — usable as a rate-card structure reference alongside Port of Tacoma's.
- **Insurance:** $2M general liability / $5M professional liability — Risk & Compliance test case, lighter-weight than INPRS.
- **Use for:** Regression test that a clean single-motion RFP still produces a single-label register (should NOT trigger false multi-tower classification), per PRD's warning that "a single-label register [on a multi-tower RFP] is a failure" — the inverse check matters too.

## Known gap — not sourceable from the internet

Per PRD §8, two staging items remain unresolved and are **not solvable via internet sourcing** the way RFPs are, since they're meant to be internal, proprietary firm artifacts:

- **Human-produced responses to these RFPs** — needed as the baseline for AC #2 (≥85% classification agreement) and quality comparison. These 3 RFPs are real but nobody on this team responded to them, so there's no ground-truth response to grade against.
- **2 winning responses as voice exemplars** — needed to ground `skills/firm-voice/SKILL.md` in real firm phrasing.

**Resolved for demo purposes with synthetic stand-ins** (see `../baseline-labels/` and `../voice-exemplars/`):
1. `baseline-labels/port-tacoma-requirements-register-baseline.json` — a generated human-labeled requirements register for Port of Tacoma (30 requirements, real RFP text, motion + confidence per item) to make AC #2's classification-agreement check testable now.
2. `baseline-labels/port-tacoma-commercial-baseline-response.md` — a short synthetic "how a human would answer" excerpt for the Commercial section, for quality comparison.
3. `voice-exemplars/` — two synthetic winning-response excerpts in a delivery-anchored voice, to ground `firm-voice` for a demo.

All three are clearly marked synthetic in-file and must be swapped for real content before being trusted beyond a demo — see each folder's README for what a real replacement should look like.
