# Baseline labels — SYNTHETIC, not real firm output

Everything in this folder is a generated stand-in for the data the user doesn't have (per PRD §8: human-produced responses and their motion classifications). It exists so AC #2 and the quality-comparison workflow are testable *now* instead of blocked. Replace with real content whenever it becomes available — same filenames/schema, so nothing downstream needs to change.

## `port-tacoma-requirements-register-baseline.json`

A human-labeled requirements register for the Port of Tacoma RFP (the multi-tower test case), built from real verbatim/paraphrased RFP text with a motion label + confidence per requirement — the exact shape the coordinator's own output should be diffed against for AC #2's ≥85% agreement check.

30 requirements, deliberately including several `confidence: medium` entries with an `overlap_notes` field — these are the ones where a reasonable classifier could pick either of two motions. Don't tune the coordinator to hit 100% agreement on those; the point of the medium-confidence entries is to check whether the coordinator's own confidence score honestly reflects the ambiguity, not to be gamed for a perfect score.

## `port-tacoma-commercial-baseline-response.md`

A synthetic "how a human proposal writer would have answered" excerpt, covering only the Commercial section (Compensation, D.3) of the same RFP. Short by design — a full synthetic response for all 30 requirements would be a lot of generated content standing in for something that's supposed to be real firm IP, and the Commercial section is the one place a wrong answer (a fabricated rate) is highest-risk, so it's the one worth having a comparison point for.

## Still worth doing before the hackathon, if time allows

Swap the medium-confidence Build/Consulting overlaps (REQ-007, REQ-011, REQ-012, REQ-028, REQ-029) for a real person's judgment call — those are exactly the disagreements that would come up in an actual sign-off conversation, and having synthetic labels instead of a real opinion is the biggest fidelity gap in this stand-in.
