import logging
import json
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

from models import Artifact, ArtifactPart, JsonRpcRequest, JsonRpcResponse, Task, TaskStatus
from services.orchestrator import CityLifeOrchestrator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("citylife-ai")

app = FastAPI(title="CityLife AI")
orchestrator = CityLifeOrchestrator()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/")
async def handle_rpc(request: JsonRpcRequest):
    if request.method != "message/send":
        raise HTTPException(status_code=404, detail=f"Method {request.method} not found")

    try:
        user_message = request.params.message
        session_id = request.params.session_id

        input_text = ""
        for part in user_message.parts:
            if part.kind == "text" and part.text:
                input_text += part.text

        logger.info("Received planning request (session=%s): %s", session_id, input_text[:120])

        plan_json = await orchestrator.plan_day(user_query=input_text)

        task = Task(
            id=str(uuid.uuid4()),
            status=TaskStatus(state="completed", timestamp=datetime.now().isoformat()),
            artifacts=[Artifact(parts=[ArtifactPart(text=json.dumps(plan_json, ensure_ascii=True))])],
            contextId=session_id if session_id else str(uuid.uuid4()),
        )

        return JsonRpcResponse(id=request.id, result=task)
    except Exception as exc:
        logger.error("Error while processing request", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
