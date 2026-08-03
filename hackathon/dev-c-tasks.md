# Dev C Task List — Critic, Voice, Output, Data Staging

Scope per `hackathon-prd.md`. Owns: `stretch_critic_subagent.py` → core critic, `skills/firm-voice/`, `skills/solution-review/`, `upload_skills.py`, `download_deliverable.py`, `synthetic-data/`.

## 0. Data staging (do first — the long pole, §8)

Blocks Dev A/B's real testing, so start here, stub-test against synthetic Acme RFP in the meantime.

- [x] Source 2-3 anonymized historical RFPs; at least one deliberately multi-tower (mixed Build/Run/Consulting in one document) — 3 real public-sector RFPs staged in `synthetic-data/staged-rfps/` (INPRS: Consulting+Risk; Port of Tacoma: Build+Run+Consulting+Risk, the multi-tower case; SUNY: pure Run, single-motion contrast). See `synthetic-data/staged-rfps/README.md` for full breakdown. Already public record, no anonymization needed.
- [x] ~~BLOCKED~~ **Unblocked with synthetic stand-in.** Human-produced responses to those RFPs. No real baseline was available, so generated a synthetic human-labeled requirements register (`synthetic-data/baseline-labels/port-tacoma-requirements-register-baseline.json`, 30 requirements, real RFP text + motion label + confidence, ambiguous cases flagged) plus a short synthetic Commercial-section response excerpt for quality comparison. Good enough to demo AC #2 and the critic's quality check now — **must be swapped for real content before this is trusted for anything beyond a demo.**
- [x] Source rate card structure, rates maskable — hand off structure to Dev B for `commercial-playbook`. Two real structural references now staged: Port of Tacoma's 3-model rate table (fixed/T&M/retainer) and SUNY's Attachment B experience-tier structure (Associate/Intermediate/Senior).
- [x] ~~BLOCKED~~ **Unblocked with synthetic stand-in.** 2 synthetic "winning response" excerpts written in a delivery-anchored voice (`synthetic-data/voice-exemplars/`) — illustrative only, marked as such. Enough to ground `firm-voice` for a demo; **not real firm voice, do not present as authoritative.**
- [ ] Get sign-off from someone senior on catalog/voice content before it's uploaded (§12.4) — **applies doubly now**: sign-off needs to cover both the real catalog content AND a decision on whether the synthetic voice/baseline stand-ins are acceptable to demo with or need replacing first.

## 1. Critic sub-agent (promoted from stretch to core, §6)

Rework `stretch_critic_subagent.py` — current version is a simple SHIP IT / REVISE / STOP reviewer. Needs to become the PRD's weighted-rubric gate.

- [x] Replace verdict format with weighted scoring across: responsiveness, differentiation, technical credibility, commercial coherence, risk posture — `contracts.py`'s `CRITIC_REVIEW_TOOL`/`return_review`, scored via `skills/solution-review/SKILL.md`
- [x] Produce Red/Amber/Green per section, not a single verdict — `section_ratings` in `return_review`, worst-governing-dimension method
- [x] Enumerate requirement IDs with no corresponding content in the draft — `missing_requirements`
- [x] Enumerate assumptions requiring human confirmation — `open_assumptions`
- [x] Hard block: any Red prevents doc generation unless explicit human override; override gets logged in the final document as an open item — enforced in `contracts.validate_review` (schema-level) and the coordinator's appended Critic procedure (`stretch_critic_subagent.py`)
- [x] Wire critic into coordinator roster + system prompt (existing pattern in the script already does this — keep it, just swap the review contract)
- [x] Critic carries the `solution-review` skill (below) — don't hardcode the rubric in the system prompt twice — `upload_skills.py` maps `solution-review` → `critic`

## 2. `skills/solution-review/SKILL.md` (§5)

- [x] Reuse the existing solution review rubric — do not author a new one from scratch (confirm with team/firm whether one already exists to port in) — **no existing rubric found in-repo**; authored from PRD §5/§6's five named dimensions and gate structure, marked as a synthetic stand-in same as baseline-labels/voice-exemplars. Still needs the sign-off pass from item 0's last checkbox.
- [x] Structure: weighted dimensions (match §10's rubric weights where they overlap), R/A/G thresholds per dimension, gap-enumeration method
- [x] Follow the `SKILL.md` frontmatter pattern from `skills/pricing-playbook/SKILL.md` (`name` + trigger-oriented `description`) — matched against `skills/commercial-playbook/SKILL.md` (repo's actual current name for that skill)

## 3. `skills/firm-voice/SKILL.md` (§5, treat as core not stretch)

- [ ] Pick one voice flavor per `stretch-goals.md` S1 (transformation-led / risk-anchored / delivery-anchored) or define the firm's actual one
- [ ] Ground it in the 2 winning-response exemplars staged in step 0
- [ ] Include concrete do/don't phrasing examples, not just an adjective list — this is what makes drafts read as "ours" instead of generic
- [ ] Attach to the coordinator (voice applies at synthesis, not per-specialist)

## 4. Output + traceability (§7, §4)

- [x] ~~Confirm docx-only output for the hackathon window~~ **Reversed by explicit decision 2026-07-30**: pptx is now in scope alongside docx, despite §7's warning that splitting output effort finishes neither. Coordinator now also produces a 6-10 slide exec-summary deck via pandoc (markdown → pptx), same mechanism as the docx fallback. Watch for output-effort splitting risk the PRD warned about.
- [ ] Add a traceability check before/at doc generation: every claim in the final document must resolve to a `requirement_id` from the Requirements Register; flag anything that doesn't as a defect
- [ ] Verify `download_deliverable.py` still works unchanged against the new coordinator/session shape once Dev A's orchestration changes land

## 5. Skill upload plumbing

- [x] Update `SKILL_TO_SPECIALIST` mapping in `upload_skills.py` for the new roster: `solution-review` → critic done (also fixed a real ordering bug this exposed: the critic doesn't exist yet on a first `upload_skills.py` pass since it's created by `stretch_critic_subagent.py` afterward — added a skip-and-retry-later guard instead of crashing). `firm-voice` → coordinator still open, blocked on item 3.
- [ ] Confirm idempotent re-upload behavior still holds with the new skill set (existing dedupe-by-title logic should just work — verify, don't rewrite)

## Acceptance criteria this workstream is responsible for (§9)

- AC #5 — critic runs, produces R/A/G plus explicit gap list
- AC #6 — branded Word doc generated, traceability preserved
- AC #2 (shared with Dev A) — needs the human-labeled baseline from step 0 to even be checkable

## Dependencies / handoffs

- → Dev B: rate card structure (step 0) feeds `commercial-playbook`
- → Dev A: Requirements Register schema is what the traceability check validates against — confirm field names match before wiring
- ← Dev A: coordinator must call critic *after* synthesis, *before* docx generation, and must support the re-submit-on-REVISE loop (max 2 iterations, per current script's existing pattern)
