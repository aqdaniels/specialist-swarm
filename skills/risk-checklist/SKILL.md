---
name: risk-checklist
description: BTS-Synthetic regulatory and contractual risk checklist for inbound RFPs. Covers data residency, liability, IP, audit, termination, and sector-specific regulatory patterns (financial services, healthcare). Use whenever screening an RFP for contractual or regulatory risk. Trigger on any request to risk-review, flag, redline, or assess contractual/regulatory terms in an RFP or customer document.
---

# Risk Checklist

For each item below, compare the RFP language against our standard position. Flag deviations with severity (blocker / negotiable / acceptable).

## 1. Data residency

**Our standard:** EU customer data stays in EU. US data stays in US. We do NOT process data in jurisdictions without recognised data protection law.

**Common deviations:**
- RFP demands single-region processing only → blocker if outside our supported regions, otherwise negotiable
- RFP allows multi-region processing → acceptable but flag for review

## 2. Liability cap

**Our standard:** Aggregate liability capped at 12 months of fees. Higher caps require insurance check.

**Common deviations:**
- Uncapped liability for data breach → BLOCKER (insurance won't cover)
- Cap above 24 months → negotiable with sign-off
- Carve-outs for gross negligence and IP infringement → acceptable (we do this too)

## 3. Intellectual property

**Our standard:** We retain all IP in our service. Customer data is the customer's. Anything customer-specific (e.g., a custom report) that we build is licensed to the customer, not assigned.

**Common deviations:**
- RFP demands assignment of all work product → blocker (we lose IP in everything customer-specific)
- RFP demands joint ownership of derivative works → negotiable but discouraged
- RFP claims ownership of our underlying service → BLOCKER

## 4. Audit rights

**Our standard:** Customer may audit our controls once per year, with 30 days' notice. Audit confidentiality required. Customer pays for audits beyond the first per year.

**Common deviations:**
- More than 2 audits per year → negotiable
- "Without notice" audit right → blocker
- Right to audit our subprocessors directly → blocker (we audit them, customer audits us)

## 5. Termination

**Our standard:** Either party may terminate for convenience on 90 days' notice. Termination for material breach with 30-day cure period.

**Common deviations:**
- Customer's right to terminate <30 days for any reason → negotiable, push for 60+ days
- No termination for convenience (only for cause) → BLOCKER on initial term
- Refund pro-rated for early termination → acceptable
- Penalty fees on customer termination → never accept

## 6. Data breach notification

**Our standard:** Notify customer within 72 hours of confirming a breach affecting their data.

**Common deviations:**
- 24 hours → acceptable (we can do this)
- "Immediately" → negotiable, push for "without undue delay"
- More than 72 hours → never propose, but acceptable in their drafts

## 7. Subprocessors

**Our standard:** Maintain a public subprocessor list. Notify customer 30 days before adding a new subprocessor. Customer may object; we'll either substitute or allow termination.

**Common deviations:**
- Customer right to pre-approve every new subprocessor → blocker (too operationally heavy)
- Customer right to be notified only after the fact → blocker (audit failure)

## 8. Governing law and venue

**Our standard:** Delaware (for US customers) or England & Wales (for EU/UK). Disputes in the named courts, no arbitration.

**Common deviations:**
- Governing law in customer's home jurisdiction → negotiable for very large deals
- Mandatory arbitration → negotiable, depends on jurisdiction
- Governing law in a jurisdiction with weak commercial law → blocker

## 9. Service levels

**Our standard:** 99.95% monthly uptime for Enterprise. Service credits up to 30% of monthly fees as sole remedy.

**Common deviations:**
- 99.99% SLA demanded → negotiable but we likely can't honour reliably
- Right to terminate after one SLA miss → blocker
- Credits beyond 30% → blocker

## 10. Insurance

**Our standard:** $5M cyber liability, $5M E&O, $10M general liability. We provide certificates on request.

**Common deviations:**
- Higher coverage demanded → check with insurance broker; usually achievable for fee
- Customer named as additional insured → acceptable
- Customer demands proof of insurance for subprocessors → blocker

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

## How to flag

Use this format in your output:

```
ITEM 2 — LIABILITY CAP
RFP says: "Vendor liability uncapped for data breach"
Severity: BLOCKER
Why: Our cyber policy caps at 24mo fees. Uncapped liability voids coverage.
Counter: "Liability capped at 24 months of fees paid, with mutual carve-outs for IP infringement and gross negligence."
```
