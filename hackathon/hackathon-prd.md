# PRD — RFP Response Swarm

**Base repo:** `rosscrooke/specialist-swarm` (Option 3 — Specialist Swarm)
**Owner:** CTO, Americas — Consulting & Engineering Services
**Status:** v0.2 — supersedes v0.1
**Scope:** Definition only. No implementation in this document.

---

## 1. What the base repo already gives us

The starter is a working coordinator-plus-specialists pattern on Claude Managed Agents (multi-agent), with custom Skills uploaded via the Skills API and the pre-built docx skill for output.

Already wired (Card A — Deal Desk):

| Component | Starter state |
|---|---|
| Coordinator ("Senior Partner — Deal Desk Lead") | Reads RFP, fans out, synthesises |
| 4 specialists | Pricing, Legal, Technical Fit, Competitive Intel |
| 3 custom skills | pricing-playbook, legal-checklist, competitive-intel |
| Trigger | Synthetic RFP (`synthetic-data/rfp-acme-corp.md`) |
| Output | Branded Word doc (`outputs/proposal-response.docx`) |
| Stretch hook | Critic sub-agent, firm-voice skill, memory across deals, synthetic MCP for past wins |

**This means we are not building a pipeline. We are re-specifying a roster and writing skills.** That reframes the entire effort. The engineering is done; the differentiation is entirely in (a) how we cut the specialist roster and (b) what proprietary content goes into the SKILL.md files.

---

## 2. The central design decision

The whiteboard architecture routes by **motion**: classify the RFP into Transformative/Build, Run/Managed Services, or Consulting, then dispatch to a matching SME.

The base repo routes by **function**: Pricing, Legal, Technical Fit, Competitive Intel — the same four specialists on every deal regardless of what the deal is.

These are different axes and both are correct. Services work needs both.

**Decision: two-tier roster.**

**Tier 1 — Motion specialists (conditional).** Activated by classification. Each owns the offering catalog, delivery model, and approach language for its motion.

- Build Specialist — transformation, modernization, custom engineering
- Run Specialist — managed services, operations, SLA construction
- Consulting Specialist — advisory, assessment, roadmap

**Tier 2 — Cross-cutting specialists (always on).** Run on every RFP regardless of motion.

- Commercial Specialist — pricing construct, rate card application, commercial model selection
- Risk & Compliance Specialist — regulatory obligations, contractual risk, security/data requirements

**Classification is a coordinator responsibility, not a fifth agent.** The coordinator reads the RFP, produces the requirements register, assigns motion per requirement, and then activates only the motion specialists it needs. Making classification its own sub-agent adds a serial hop before the fan-out and kills the parallelism that makes the demo land.

**Consequence for the roster file:** the starter creates a fixed set of specialists and saves their IDs. We create all five up front; the coordinator selects from the callable roster at runtime. No dynamic agent creation — that is out of scope for a 60-minute build.

---

## 3. Goals

| # | Goal | Success signal |
|---|---|---|
| G1 | Classify per requirement, not per document | A multi-tower test RFP produces a mixed-motion register, not a single label |
| G2 | Map requirements to the DXC offering catalog | ≥80% of requirements mapped to a named offering with a stated justification |
| G3 | Produce a consultative response, not a compliance matrix | Output contains a POV, a sequencing argument, and a "why us" |
| G4 | Encode proprietary content as Skills | Offering catalog, firm voice, and review rubric exist as SKILL.md files, reusable outside this hackathon |
| G5 | Visible parallelism | Events stream shows concurrent specialist threads; this is the demo |

### Non-goals

- Deal desk approval workflow, submission portal integration, contract redlining
- Dynamic agent creation at runtime
- Live client RFPs or real rate cards in the hackathon environment
- Any output that leaves the room

---

## 4. Agent contracts

Each specialist is defined by three things: what it receives, what skill it carries, and what it must return. The return contract matters more than the prompt — the coordinator cannot reconcile five parallel outputs without a fixed shape.

### Universal input

Every specialist receives the **Requirements Register** (or its motion-filtered slice): a list of records carrying requirement ID, verbatim source text, section reference, mandatory/optional flag, and assigned motion with confidence.

### Universal return shape

Every specialist returns, per requirement it touched:

- `requirement_id` — mandatory, carried through unchanged
- `finding` — the specialist's substantive content
- `confidence` — high / medium / low
- `assumptions` — explicit, list form
- `gaps` — where the specialist could not answer and why

**Traceability rule:** any content in the final document that cannot be traced to a requirement ID is a defect. This is the single constraint that separates a usable draft from an impressive-looking one, because it is what lets a pursuit lead verify the output in minutes instead of re-reading the RFP.

### Per-specialist definition

| Specialist | Skill carries | Returns |
|---|---|---|
| **Build** | Build offering catalog, reference architectures, accelerators, delivery models | Offering mapping, architecture skeleton, technical approach, effort drivers |
| **Run** | Managed services catalog, SLA library, transition method, run-cost drivers | Service model, SLA table, transition plan, steady-state assumptions |
| **Consulting** | Advisory method, workshop constructs, deliverable definitions | Method, engagement shape, deliverable set, outcome framing |
| **Commercial** | Rate card structure, commercial model definitions (fixed fee / retainer / outcome), past-win reference points | Pricing construct with named model, effort model, explicit assumption list |
| **Risk & Compliance** | Regulatory checklist, contractual risk positions, security/data obligations | Flagged requirements, recommended positions, escalation list |

**Commercial constraint — non-negotiable.** The Commercial Specialist selects and applies; it does not invent. It picks a rate card and a commercial model, and where effort cannot be derived from the register it returns a sized placeholder with the assumption stated in the open. A generated number that looks authoritative is worse than a blank, because a blank gets filled in and a number gets sent.

---

## 5. Skills specification

The skills are the deliverable that outlives the hackathon. Code in this repo is disposable; a well-written offering-catalog skill is an asset.

| Skill | Purpose | Notes |
|---|---|---|
| `offering-catalog-build` | Build/transform offerings, structured | One entry per offering: name, description, when it applies, differentiator, delivery model, disqualifiers |
| `offering-catalog-run` | Managed services offerings | Same structure; include SLA tiers |
| `offering-catalog-consulting` | Advisory offerings | Same structure; include deliverable definitions |
| `commercial-playbook` | Rate card structure, model selection logic, guardrails | Rates may be masked. Structure must be real |
| `risk-checklist` | Regulatory and contractual screening | Financial services and healthcare patterns are the highest-value cases |
| `firm-voice` | How DXC writes | Stretch in the base repo; treat as core here — voice is what makes the draft usable |
| `solution-review` | Weighted rubric, R/A/G scoring, gap enumeration | Powers the critic. Reuse the existing solution review rubric rather than authoring a new one |

**Disqualifiers matter as much as capabilities.** An offering entry that only says what we do produces a specialist that maps everything to something. Each entry needs an explicit "do not use this when" clause, or coverage metrics will look excellent while the mapping is wrong.

---

## 6. Quality gate — the critic

The base repo offers a critic sub-agent as a stretch goal. **Treat it as core scope, not stretch.** A swarm without a critic produces a confident draft nobody can evaluate.

The critic runs after synthesis and before document generation, carrying the `solution-review` skill:

- Weighted scoring across responsiveness, differentiation, technical credibility, commercial coherence, risk posture
- Red / Amber / Green per section
- Enumerated list of requirement IDs with no corresponding content
- Enumerated list of assumptions requiring human confirmation

**Any Red blocks generation without explicit human override.** The override is logged in the document as an open item.

---

## 7. Output

**Primary:** branded Word document. This matches the base repo's wiring and the pre-built docx skill, and most RFPs mandate prose format anyway.

**Secondary (stretch):** deck output via the DXC pptx skill.

Do not build both in the hackathon window. Teams that split output effort will finish neither.

---

## 8. Data requirements — the long pole

Staged before day one, or the hackathon produces architecture diagrams instead of working swarms:

| Asset | Purpose | Owner |
|---|---|---|
| 2–3 anonymized historical RFPs, one deliberately multi-tower | Trigger + ground truth | TBD |
| Human-produced responses to those RFPs | Baseline for classification accuracy and quality comparison | TBD |
| Structured offering catalog, per motion | Source content for the three catalog skills | TBD |
| Rate card structure (rates maskable) | Commercial playbook skill | TBD |
| 2 winning responses as voice exemplars | Firm-voice skill | TBD |

The starter's synthetic Acme RFP is adequate for a smoke test and inadequate for anything else. It is single-motion and clean; real RFPs are neither.

---

## 9. Acceptance criteria

1. Swarm runs end to end against a real (anonymized) multi-tower RFP.
2. Requirements register produced with per-requirement motion classification; ≥85% agreement with the human-labeled baseline.
3. Offering mapping covers ≥80% of requirements, each with a justification.
4. All five specialists return the contracted shape; every requirement ID reconciles.
5. Critic runs and produces R/A/G plus an explicit gap list.
6. Branded Word document generated, with traceability preserved.
7. Events stream shows genuine parallel specialist threads.
8. Full run under 30 minutes.

---

## 10. Evaluation rubric for teams

| Dimension | Weight |
|---|---|
| Per-requirement classification accuracy | 15% |
| Quality and honesty of offering mapping (including correct gap flags) | 20% |
| Consultative quality — POV, not compliance | 25% |
| Traceability and auditability | 15% |
| Skill quality and reusability beyond the hackathon | 15% |
| Demo execution (visible parallelism, narration) | 10% |

Note that skill quality is weighted at 15% and code is weighted at zero. That is deliberate and should be stated to teams at kickoff.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| **Multi-agent access not granted on workspace** | Confirm API key and research-preview access days before, not on the morning. This is the most likely cause of a failed hackathon |
| Classification collapses to one motion | Test explicitly against a multi-tower RFP; treat a single-label register as a failure |
| Fabricated pricing escapes the room | Retrieval-only commercial specialist; hard block on unpriced output; no live client data in environment |
| Specialist outputs cannot be reconciled | Fixed return contract with mandatory requirement_id; enforce at coordinator |
| Draft reads generic | Firm-voice skill promoted to core scope; consultative quality weighted highest in rubric |
| Teams spend the window on plumbing | Base repo is already wired — teams that rewrite the orchestration have misread the exercise |
| Thin catalog content | Catalog skills staged and reviewed before day one, not written during |

---

## 12. Open decisions

1. **Roster size.** Five specialists (3 motion + 2 cross-cutting) plus a critic is six agents. Confirm this is within the multi-agent limit and within the 60-minute window; the fallback is dropping Risk & Compliance to stretch.
2. **Does classification stay with the coordinator?** Recommended yes. Revisit only if classification quality proves to be the bottleneck.
3. **Are we running Card A only, or letting teams pick B and C?** Recommendation: all teams run the RFP scenario. A shared scenario makes outputs comparable and makes the rubric meaningful.
4. **Who owns catalog content quality?** The skills are firm IP. Someone senior needs to sign off on what goes into them before they are uploaded.
5. **What happens to gap-flagged requirements?** Partner sourcing, no-bid recommendation, or manual escalation — this determines whether the output is a draft or a decision.

---

## 13. Beyond the hackathon

- **Phase 1 (hackathon):** single RFP, single run, human reviews everything
- **Phase 2:** catalog skills as maintained assets with an owner; memory across deals; past-wins retrieval via MCP
- **Phase 3:** bid/no-bid scoring — evaluate fit before a response is ever drafted

Phase 3 is where the actual value is. The response draft saves days; the bid decision saves pursuits.