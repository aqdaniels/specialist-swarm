# Option 3 — Specialist Swarm

**Concept landed:** Skills, plugins & sub-agents
**Tech:** [Claude Managed Agents multi-agent](https://platform.claude.com/docs/en/managed-agents/multi-agent) + [custom Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) + the pre-built [docx skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart)
**Time:** 60 minutes
**Output:** A coordinator agent that fans work out to 5 motion-based specialist sub-agents plus a Critic gate, each with its own skills, that assemble a real branded Word document and exec-summary slide deck.

## The pitch

This is the architecture that wins the next $50M transformation deal: **coordinator + specialists + skills**. It maps directly to how every services firm structures real work. A senior partner orchestrates; specialists (legal, pricing, technical) own their lanes; the senior partner synthesises and delivers.

You're going to build exactly that, in 60 minutes, around a Deal Desk scenario. Drop an RFP in, get a branded response doc out, watch the parallelism happen in real time on the events stream.

## Setup (5 min)

You need a workspace API key on the Console (multi-agent is currently in research preview — your workspace may need to be granted access).

```bash
cd specialist-swarm
pip install -r requirements.txt
```

Create a `.env` file with:

```
ANTHROPIC_API_KEY=sk-ant-...
```

(Optional: `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` if you want tracing on each run — `server.py` emits a Langfuse span per session either way.)

## Provisioning (run once)

The roster is Build, Run, Consulting, Commercial, and Risk & Compliance specialists, a coordinator, and a Critic gate — each step below persists its IDs to a local `.{name}_id` / `.json` file so later steps (and re-runs) can find them.

1. `python setup_environment.py` — creates the cloud Environment the session runs in → `.environment_id`.
2. `python create_specialists.py` — creates the 5 motion-based specialists → `.specialist_ids.json`.
3. `python create_deal_desk_coordinator.py` — creates the coordinator, rostering the 5 specialists → `.coordinator_id`.
4. `python stretch_critic_subagent.py` — creates the Critic and adds it to the coordinator's roster.
5. `python upload_skills.py` — uploads the skills in `skills/` and attaches each to its matching agent. It's idempotent (safe to re-run), and it's the reason step 4 has to run first: `solution-review` maps to the Critic, which doesn't exist until then — if you ran this before step 4, just run it again afterward to pick that one up.
6. `python build_pptx_template.py` — builds the branded reference deck (`templates/bts-reference.pptx`) that exec-summary decks pick up their BTS colors/fonts from.

## Run the live demo

```bash
python server.py
```

Open http://localhost:8000, pick an RFP from the catalog, and watch the swarm run in real time over the events stream (SSE) — parallel specialist threads, the Critic gate, then document generation. Finished deliverables (branded docx + pptx) land in `outputs/`.

To pull files from a specific past session instead of the last live run: `python download_deliverable.py <session_id>`.

`run_deal_desk.py` is a separate, local-only dry run of the classification/reconciliation stages against mock specialist responses — useful for testing that layer without spending real agent calls, but it doesn't hit the Managed Agents API or produce a real deliverable.

## Stretch goals (20 min)

See [`stretch-goals.md`](./stretch-goals.md) for the original list and [`hackathon/dev-c-tasks.md`](./hackathon/dev-c-tasks.md) for where this build actually stands against it. The Critic sub-agent has already been promoted from stretch to core (it's wired in via `stretch_critic_subagent.py` and gates every draft with a weighted rubric — see `skills/solution-review/SKILL.md`). Firm-voice, memory across deals, and a synthetic past-wins MCP are still open.

## Two-minute demo

Two-monitor setup:
- **Monitor 1:** `http://localhost:8000` — the dashboard, running the events stream live. You'll see `session.thread_created` × 6 (5 specialists + Critic), parallel `running`, then replies flowing back and the Critic's gate before document generation. The visible parallelism IS the demo.
- **Monitor 2:** the generated docx/pptx in `outputs/` (or via the dashboard's `/view/<filename>` route). Real documents, branded, ready to send.

Narrate the events stream while it runs. The room will get it.

## What's in this folder

```
specialist-swarm/
├── README.md
├── hackathon/hackathon-prd.md          (the actual spec this build follows)
├── hackathon/dev-c-tasks.md            (critic/voice/output workstream status)
├── scenario-cards.md
├── stretch-goals.md
├── requirements.txt
├── setup_environment.py                (provisions the cloud Environment)
├── create_specialists.py               (creates the 5 motion-based specialists)
├── create_deal_desk_coordinator.py     (creates the coordinator + roster)
├── stretch_critic_subagent.py          (creates the Critic, wires it into the coordinator)
├── upload_skills.py                    (uploads skills/ via the Skills API, attaches to agents)
├── build_pptx_template.py              (builds templates/bts-reference.pptx)
├── server.py                           (live demo: dashboard + SSE event stream)
├── download_deliverable.py             (pull files from any past session by ID)
├── run_deal_desk.py                    (local-only dry run, no real agents)
├── contracts.py                        (shared tool schemas: return_findings, return_review)
├── requirements_register.py            (requirements classification, Dev A)
├── create_coordinator.py               (local classification helper used by run_deal_desk.py, Dev A — not an agent)
├── agent-charles-dashboard.html        (the dashboard UI server.py serves)
├── skills/                             (custom skills, one per specialist + the critic)
│   ├── offering-catalog-build/
│   ├── offering-catalog-run/
│   ├── offering-catalog-consulting/
│   ├── commercial-playbook/
│   ├── risk-checklist/
│   ├── solution-review/                (the critic's rubric)
│   └── competitive-intel/
├── templates/                          (bts-reference.pptx, built by build_pptx_template.py)
├── outputs/                            (generated deliverables land here — gitignored)
└── synthetic-data/
    ├── rfp-acme-corp.md, rfp-fintech-digital-transformation.md
    ├── staged-rfps/                    (3 real public-sector RFPs)
    ├── baseline-labels/                (synthetic human-labeled requirements baseline)
    ├── voice-exemplars/                (synthetic winning-response excerpts)
    ├── past-wins.json
    └── product-overview.md
```
