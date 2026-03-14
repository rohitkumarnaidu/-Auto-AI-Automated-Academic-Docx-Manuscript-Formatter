from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from sse_starlette.sse import EventSourceResponse

from app.config.settings import settings
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.synthesis.synthesizer import MultiDocSynthesizer
from app.realtime.events import make_event
from app.realtime.pubsub import RedisPubSub
from app.routers import generator as legacy_generator
from app.routers.documents import ACCEPTED_EXTENSIONS, _validate_magic_bytes
from app.schemas.generator_session import MessageRequest
from app.services.generator_session_service import GeneratorSessionService
from app.services.llm_service import generate_with_fallback, sanitize_for_llm
from app.services.session_vector_store import SessionVectorStore
from app.utils.dependencies import get_current_user

from ._helpers import run_enveloped

logger = logging.getLogger(__name__)

router = APIRouter()
_pubsub = RedisPubSub()

_session_service = GeneratorSessionService()
_vector_store = SessionVectorStore()
_orchestrator = PipelineOrchestrator()
_synthesizer = MultiDocSynthesizer(
    session_service=_session_service,
    vector_store=_vector_store,
    llm_service=None,
    pipeline_orchestrator=_orchestrator,
    pubsub=_pubsub,
)


def _parse_config(raw_config: str) -> Dict[str, Any]:
    if not raw_config:
        return {}
    try:
        return json.loads(raw_config)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid config JSON: {exc}")


@router.post("/sessions", status_code=202)
async def start_generation(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    session_type: str = Form("multi_doc"),
    template: str = Form(settings.DEFAULT_TEMPLATE),
    config: str = Form("{}"),
    user=Depends(get_current_user),
):
    if session_type != "multi_doc":
        raise HTTPException(status_code=422, detail="Only multi_doc sessions are supported here.")
    if not files or len(files) < 2 or len(files) > 6:
        raise HTTPException(status_code=422, detail="Upload between 2 and 6 files.")

    config_payload = _parse_config(config)
    user_id = user.id if hasattr(user, "id") else str(user)
    session_id = await _session_service.create_session(user_id, session_type, config_payload)

    upload_dir = Path("uploads") / "synthesis" / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_entries: List[Dict[str, Any]] = []
    for idx, file in enumerate(files):
        filename = file.filename or f"upload_{idx}"
        ext = Path(filename).suffix.lower()
        if ext not in ACCEPTED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'.")
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds {settings.MAX_FILE_SIZE // (1024 * 1024)}MB limit.",
            )
        await _validate_magic_bytes(file, content=content, file_ext=ext)

        safe_name = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_dir / safe_name
        file_path.write_bytes(content)
        file_entries.append(
            {
                "path": str(file_path),
                "filename": filename,
                "size": len(content),
            }
        )

    config_payload.update({"template": template, "uploaded_files": file_entries})
    await _session_service.update_session(session_id, config_json=config_payload)

    background_tasks.add_task(_synthesizer.run, session_id, [f["path"] for f in file_entries], template)
    return {"session_id": session_id, "status": "started"}


@router.get("/sessions/{sessionId}")
async def get_generation_status(
    request: Request,
    sessionId: str,
    user=Depends(get_current_user),
):
    session = await _session_service.get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    latest_doc = await _session_service.get_latest_document(sessionId)
    return {
        "id": session.get("id"),
        "status": session.get("status"),
        "session_type": session.get("session_type"),
        "config": session.get("config_json") or {},
        "outline": session.get("outline_json"),
        "docx_path": (latest_doc or {}).get("docx_path"),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
    }


@router.get("/sessions/{sessionId}/download")
async def download_generated(
    request: Request,
    sessionId: str,
    format: str = "docx",
    user=Depends(get_current_user),
):
    async def operation():
        return await legacy_generator.download_generated(
            job_id=sessionId,
            format=format,
            user=user,
        )

    return await run_enveloped(
        request,
        operation,
        code_map={
            400: "INVALID_EXPORT_FORMAT",
            403: "GENERATION_ACCESS_DENIED",
            404: "SESSION_NOT_FOUND",
            409: "SESSION_NOT_READY",
        },
        logger=logger,
        operation_name="generation session download",
    )


@router.get("/sessions/{sessionId}/events")
async def generation_events(
    request: Request,
    sessionId: str,
    user=Depends(get_current_user),
):
    async def event_generator():
        channel = f"session:{sessionId}"
        connected_event = make_event(
            "connected",
            session_id=sessionId,
            payload={"message": f"Connected to session {sessionId}"},
        )
        yield {"event": "connected", "data": json.dumps(connected_event)}
        async for event in _pubsub.subscribe(channel):
            if await request.is_disconnected():
                break
            event_type = event.get("event_type") or "message"
            yield {"event": event_type, "data": json.dumps(event)}

    return EventSourceResponse(event_generator())


@router.post("/sessions/{sessionId}/messages")
async def generation_messages(
    request: Request,
    sessionId: str,
    payload: MessageRequest,
    user=Depends(get_current_user),
):
    session = await _session_service.get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    question = (payload.content or "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="Message content cannot be empty.")

    await _session_service.add_message(sessionId, "user", question, token_count=0)
    sources = _vector_store.query(sessionId, question, top_k=5)

    context = "\n\n".join(
        f"[{s.get('source_doc')} - {s.get('section')}] {s.get('text')}" for s in sources
    )
    system = (
        "You are a scholarly assistant. Answer using the provided sources. "
        "Cite sources inline in parentheses."
    )
    user_prompt = f"Question: {question}\n\nSources:\n{sanitize_for_llm(context)}"
    result = await asyncio.to_thread(
        generate_with_fallback,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )
    answer = (result.get("text") or "").strip()

    await _session_service.add_message(sessionId, "assistant", answer, token_count=0)
    return {
        "role": "assistant",
        "content": answer,
        "sources": [
            {"source_doc": s.get("source_doc"), "section": s.get("section")}
            for s in sources
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/sessions/{sessionId}/outline/approve")
async def approve_outline(
    request: Request,
    sessionId: str,
    payload: Dict[str, Any],
    user=Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Outline approval not implemented.")
