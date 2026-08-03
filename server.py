"""
Live demo server: pick an RFP in the browser, watch the agent swarm run in
real time (SSE), see the resulting deliverable.

Single process, single port — serves the dashboard UI, the classification
JSON, and streams the live Managed Agents session as Server-Sent Events.

Usage:
    python server.py
    open http://localhost:8000/
"""

import json
from pathlib import Path

import httpx
import mammoth
from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langfuse import get_client
from pypdf import PdfReader

load_dotenv()

app = FastAPI()

# id -> (path, short description). Descriptions are hand-written from the
# staged-rfps/README.md breakdown — real PDFs don't carry this metadata themselves.
RFP_CATALOG = {
    "acme-corp": (
        Path("synthetic-data/rfp-acme-corp.md"),
        "Synthetic - enterprise data platform RFP with aggressive commercial/legal terms (stress-test case).",
    ),
    "fintech-digital-transformation": (
        Path("synthetic-data/rfp-fintech-digital-transformation.md"),
        "Synthetic - 13 requirements spanning Build/Run/Consulting/Commercial/Risk motions.",
    ),
    "port-tacoma-maximo": (
        Path("synthetic-data/staged-rfps/port-tacoma-maximo-cloud-migration-support-rfp.pdf"),
        "Real - Port of Tacoma #071658. Best multi-tower example: Build + Run + Consulting + Risk.",
    ),
    "inprs-cloud-migration": (
        Path("synthetic-data/staged-rfps/inprs-cloud-migration-iam-rfp.pdf"),
        "Real - Indiana PRS RFP 23-04. Consulting + Risk heavy; bars vendors from proposing Build.",
    ),
    "suny-it-managed-services": (
        Path("synthetic-data/staged-rfps/suny-it-managed-services-rfp.pdf"),
        "Real - SUNY Research Foundation. Pure Run, single-motion contrast case.",
    ),
}
SUPPORTING_FILES = [
    Path("synthetic-data/past-wins.json"),
    Path("synthetic-data/product-overview.md"),
]
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
PPTX_TEMPLATE = Path("templates/bts-reference.pptx")
PPTX_TEMPLATE_MOUNT = "/mnt/session/inputs/bts-reference.pptx"


def read_rfp_text(rfp_path: Path) -> str:
    if rfp_path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(rfp_path)).pages)
    return rfp_path.read_text(encoding="utf-8")


def load_context(rfp_path: Path) -> str:
    blocks = [f"=====  DOCUMENT: {rfp_path.name}  =====\n{read_rfp_text(rfp_path)}"]
    for path in SUPPORTING_FILES:
        if path.exists():
            blocks.append(f"=====  DOCUMENT: {path.name}  =====\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(blocks)


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.get("/api/rfps")
def list_rfps():
    return [
        {
            "id": rfp_id,
            "label": path.name,
            "type": path.suffix.lstrip("."),
            "size_kb": round(path.stat().st_size / 1024, 1),
            "description": description,
        }
        for rfp_id, (path, description) in RFP_CATALOG.items()
        if path.exists()
    ]


@app.get("/api/run")
def run_swarm(rfp: str):
    entry = RFP_CATALOG.get(rfp)
    rfp_path = entry[0] if entry else None
    if not rfp_path or not rfp_path.exists():
        return StreamingResponse(iter([sse({"type": "error", "text": "unknown RFP"})]), media_type="text/event-stream")

    def event_gen():
        langfuse = get_client()
        span = langfuse.start_observation(name="deal-desk-run", as_type="span", input={"rfp": rfp})

        coordinator_id = Path(".coordinator_id").read_text().strip()
        environment_id = Path(".environment_id").read_text().strip()
        client = Anthropic(default_headers={"anthropic-beta": "managed-agents-2026-04-01"})

        session = client.beta.sessions.create(
            agent=coordinator_id,
            environment_id=environment_id,
            title=f"Deal Desk - {rfp_path.stem}",
        )
        yield sse({"type": "session_started", "session_id": session.id})

        pptx_instruction = "Convert it with `pandoc slides.md -o <name>.pptx`."
        if PPTX_TEMPLATE.exists():
            with PPTX_TEMPLATE.open("rb") as f:
                template_file = client.beta.files.upload(file=f, betas=["managed-agents-2026-04-01"])
            client.beta.sessions.resources.add(
                session.id,
                file_id=template_file.id,
                type="file",
                mount_path=PPTX_TEMPLATE_MOUNT,
                betas=["managed-agents-2026-04-01"],
            )
            pptx_instruction = (
                f"A branded reference deck is mounted at {PPTX_TEMPLATE_MOUNT} — "
                f"convert with `pandoc slides.md --reference-doc={PPTX_TEMPLATE_MOUNT} "
                "-o <name>.pptx` so the deck picks up BTS colors and fonts instead of "
                "pandoc's plain default theme."
            )

        user_message = (
            "An RFP has just landed. Please run the standard Deal Desk process:\n"
            "1. Read the RFP yourself.\n"
            "2. Delegate to all five specialists in parallel.\n"
            "3. Synthesise their replies into a draft.\n"
            "4. Send the draft to the Deal Desk Critic before finalising, and "
            "address any REVISE feedback (max 2 rounds).\n"
            "5. Produce the final proposal response as a branded Word document "
            "if you have access to a docx skill; otherwise output the response "
            "as a structured markdown document.\n"
            "6. Also produce a short executive-summary slide deck (6-10 slides) "
            "as a .pptx, converted via pandoc from a slides-formatted markdown "
            f"outline. {pptx_instruction} The deck summarises the proposal; it "
            "does not replace it.\n\n"
            f"{load_context(rfp_path)}"
        )

        client.beta.sessions.events.send(
            session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_message}]}],
        )

        # Long multi-agent runs can sit idle for minutes while specialists work;
        # the SSE connection can drop in that window even though the session
        # keeps running server-side. Reconnect on transport errors instead of
        # treating a dropped connection as job failure.
        terminated = False
        reconnect_attempts = 0
        while not terminated:
            try:
                with client.beta.sessions.events.stream(session.id) as stream:
                    for event in stream:
                        reconnect_attempts = 0
                        t = event.type
                        if t == "session.thread_created":
                            yield sse({"type": "thread_spawned", "agent": event.agent_name})
                        elif t == "session.thread_status_running":
                            yield sse({"type": "thread_running", "agent": getattr(event, "agent_name", "?")})
                        elif t == "agent.thread_message_received":
                            yield sse({"type": "reply", "agent": event.from_agent_name})
                        elif t == "agent.thread_message_sent":
                            yield sse({"type": "delegate", "agent": event.to_agent_name})
                        elif t == "agent.message":
                            for block in event.content:
                                if getattr(block, "type", None) == "text":
                                    yield sse({"type": "text", "text": block.text})
                        elif t == "agent.tool_use":
                            yield sse({"type": "tool_use", "name": getattr(event, "name", "?")})
                        elif t == "agent.custom_tool_use":
                            # return_findings (contracts.py) is a "custom" tool: the API
                            # does not execute it, it blocks the calling thread until the
                            # client answers with a user.custom_tool_result. Without this,
                            # every specialist that calls it stalls forever and the
                            # coordinator never gets its replies.
                            yield sse({"type": "tool_use", "name": event.name})
                            result_event = {
                                "type": "user.custom_tool_result",
                                "custom_tool_use_id": event.id,
                                "content": [{"type": "text", "text": "Recorded."}],
                            }
                            if event.session_thread_id:
                                result_event["session_thread_id"] = event.session_thread_id
                            client.beta.sessions.events.send(session.id, events=[result_event])
                        elif t == "session.status_terminated":
                            # Actual session close / fatal error. On a normal
                            # successful run this never fires — completion is
                            # signalled by session.status_idle + stop_reason
                            # end_turn below.
                            terminated = True
                            break
                        elif t == "session.status_idle":
                            stop_reason = getattr(event.stop_reason, "type", None)
                            if stop_reason == "end_turn":
                                # Whole multiagent tree is idle with nothing left
                                # to do — this is the real "job finished" signal.
                                # requires_action idles (e.g. an unanswered
                                # custom tool call) are handled above as they
                                # stream in and must NOT break the loop here.
                                terminated = True
                                break
                            elif stop_reason == "retries_exhausted":
                                span.update(level="ERROR", status_message="session retries exhausted")
                                span.end()
                                langfuse.flush()
                                yield sse({"type": "error", "text": "session retries exhausted"})
                                return
            except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ReadTimeout, httpx.ConnectError) as exc:
                reconnect_attempts += 1
                if reconnect_attempts > 10:
                    span.update(level="ERROR", status_message=f"lost connection: {exc}")
                    span.end()
                    langfuse.flush()
                    yield sse({"type": "error", "text": f"lost connection to session: {exc}"})
                    return
                yield sse({"type": "reconnecting", "attempt": reconnect_attempts})

        files = client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"])
        downloaded = []
        for f in files.data:
            out_path = OUTPUT_DIR / f.filename
            client.beta.files.download(f.id).write_to_file(str(out_path))
            downloaded.append(f.filename)
        span.update(output={"session_id": session.id, "files": downloaded})
        span.end()
        langfuse.flush()
        yield sse({"type": "done", "session_id": session.id, "files": downloaded})

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/view/{filename}")
def view_docx(filename: str):
    target = (OUTPUT_DIR / filename).resolve()
    if not target.is_relative_to(OUTPUT_DIR.resolve()) or target.suffix.lower() != ".docx" or not target.exists():
        return HTMLResponse("<p>Not found.</p>", status_code=404)

    with target.open("rb") as f:
        body = mammoth.convert_to_html(f).value

    return HTMLResponse(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{filename}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", sans-serif; max-width: 820px;
          margin: 40px auto; padding: 0 24px 60px; color: #1f2937; line-height: 1.6; }}
  h1, h2, h3 {{ color: #1e3a5f; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  td, th {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
</style></head>
<body>{body}</body></html>""")


@app.get("/coordinator-dispatch.json")
def coordinator_dispatch():
    return FileResponse("coordinator-dispatch.json")


@app.get("/reconciled-responses.json")
def reconciled_responses():
    return FileResponse("reconciled-responses.json")


@app.get("/")
def dashboard():
    return FileResponse("agent-charles-dashboard.html")


# ponytail: only outputs/ is served as static — never mount the repo root, it
# contains .env and agent-id files.
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
