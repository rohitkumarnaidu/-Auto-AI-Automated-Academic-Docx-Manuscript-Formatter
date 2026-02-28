# -*- coding: utf-8 -*-
"""
DocumentGenerator -- orchestrator for generate-from-scratch jobs.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.block import Block, BlockType
from app.models.pipeline_document import DocumentMetadata, PipelineDocument, TemplateInfo
from app.pipeline.export.exporter import Exporter
from app.pipeline.formatting.formatter import Formatter
from app.pipeline.generation.content_parser import ContentParser
from app.pipeline.generation.prompt_builder import PromptBuilder
from app.routers.stream import emit_event
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

GENERATED_DIR = Path(os.getenv("GENERATED_OUTPUT_DIR", "generated_outputs"))

_BLOCK_TYPE_MAP: dict[str, BlockType] = {
    "TITLE": BlockType.TITLE,
    "AUTHOR_INFO": BlockType.AUTHOR,
    "AUTHOR": BlockType.AUTHOR,
    "AFFILIATION": BlockType.AFFILIATION,
    "ABSTRACT": BlockType.ABSTRACT_BODY,
    "SUMMARY": BlockType.BODY,
    "KEYWORDS": BlockType.KEYWORDS_BODY,
    "HEADING_1": BlockType.HEADING_1,
    "HEADING_2": BlockType.HEADING_2,
    "HEADING_3": BlockType.HEADING_3,
    "BODY": BlockType.BODY,
    "BULLET": BlockType.LIST_ITEM,
    "BULLET_LIST": BlockType.LIST_ITEM,
    "REFERENCE_ENTRY": BlockType.REFERENCE_ENTRY,
    "FIGURE_CAPTION": BlockType.FIGURE_CAPTION,
    "TABLE_CAPTION": BlockType.TABLE_CAPTION,
}


class DocumentGenerator:
    """Orchestrates document generation from metadata."""

    def __init__(self) -> None:
        self._progress_store: dict[str, dict[str, Any]] = {}

    async def start_job(
        self,
        doc_type: str,
        template: str,
        metadata: dict,
        options: dict,
        user_id: str,
    ) -> str:
        job_id = str(uuid.uuid4())
        generated_filename = f"generated_{doc_type}_{job_id[:8]}.docx"
        formatting_options = {
            "generation": True,
            "doc_type": doc_type,
            "include_placeholder_content": bool(options.get("include_placeholder_content", True)),
            "word_count_target": int(options.get("word_count_target", 3000)),
            "export_formats": ["docx", "pdf"],
        }

        db_created = DocumentService.create_document(
            doc_id=job_id,
            user_id=str(user_id) if user_id else None,
            filename=generated_filename,
            template=template,
            formatting_options=formatting_options,
        )
        if db_created is None:
            logger.warning("Generation job %s created in memory only (DB unavailable).", job_id)

        self._progress_store[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "stage": "queued",
            "message": "Generation job queued.",
            "doc_type": doc_type,
            "template": template,
            "metadata": metadata,
            "options": options,
            "user_id": user_id,
            "outline": [],
            "output_path": None,
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._emit(job_id, phase="QUEUED", status="PENDING", message="Generation job queued.", progress=0, stage="queued")
        return job_id

    async def run_pipeline(self, job_id: str) -> None:
        state = self._progress_store.get(job_id)
        if not state:
            logger.error("run_pipeline: generation job '%s' not found", job_id)
            return

        doc_type = state["doc_type"]
        template = state["template"]
        metadata = state["metadata"]
        options = state["options"]

        try:
            self._update(job_id, "generating", 10, "Building LLM prompt...")
            prompt_builder = PromptBuilder()
            prompt = prompt_builder.build(doc_type, metadata, options)

            self._update(job_id, "generating", 30, "AI writing document content...")
            llm_response = await self._llm_generate(prompt, job_id)

            self._update(job_id, "structuring", 50, "Structuring AI output into blocks...")
            parser = ContentParser()
            raw_blocks = parser.parse(llm_response, doc_type)
            outline = self._extract_outline(raw_blocks)
            state["outline"] = outline

            DocumentService.upsert_document_result(
                job_id,
                structured_data={
                    "doc_type": doc_type,
                    "template": template,
                    "blocks": raw_blocks,
                    "outline": outline,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
                validation_results={},
            )

            self._update(job_id, "formatting", 75, f"Applying {template.upper()} template...")
            output_path = await self._format_and_export(
                raw_blocks=raw_blocks,
                template=template,
                job_id=job_id,
                metadata=metadata,
                doc_type=doc_type,
            )

            try:
                output_hash = self._compute_sha256(output_path)
                DocumentService.update_output_hash(job_id, output_hash)
            except Exception as exc:
                logger.warning("Failed to persist output hash for generation job %s: %s", job_id, exc)

            raw_text = "\n\n".join(
                block.get("content", "").strip()
                for block in raw_blocks
                if str(block.get("content", "")).strip()
            )
            DocumentService.mark_document_completed(job_id, str(output_path), raw_text=raw_text)
            self._update(job_id, "done", 100, "Document ready for download!", output_path=str(output_path))
            logger.info("Generation job %s completed: %s", job_id, output_path)
        except Exception as exc:
            logger.exception("Generation job %s failed: %s", job_id, exc)
            DocumentService.mark_document_failed(job_id, str(exc))
            self._update(job_id, "error", 0, str(exc), error=str(exc))

    def get_status(self, job_id: str) -> dict[str, Any]:
        state = self._progress_store.get(job_id)
        if state:
            return {
                "job_id": state["job_id"],
                "status": state["status"],
                "stage": state["stage"],
                "progress": state["progress"],
                "message": state["message"],
                "error": state.get("error"),
                "output_path": state.get("output_path"),
                "outline": list(state.get("outline") or []),
            }

        doc = DocumentService.get_document(job_id)
        if not doc:
            raise KeyError(f"generation job not found: '{job_id}'")

        db_status = str(doc.get("status") or "PENDING").upper()
        mapped_status = {
            "PENDING": "pending",
            "PROCESSING": "processing",
            "COMPLETED": "done",
            "COMPLETED_WITH_WARNINGS": "done",
            "FAILED": "failed",
            "CANCELLED": "failed",
        }.get(db_status, "processing")
        stage = str(doc.get("current_stage") or "QUEUED").lower()
        progress = int(doc.get("progress") or 0)
        message = doc.get("error_message") or f"{stage}..."
        error = doc.get("error_message") if mapped_status == "failed" else None
        output_path = doc.get("output_path")

        outline: list[str] = []
        result = DocumentService.get_document_result(job_id)
        if result and isinstance(result.get("structured_data"), dict):
            raw_outline = result["structured_data"].get("outline") or []
            if isinstance(raw_outline, list):
                outline = [str(item).strip() for item in raw_outline if str(item).strip()]

        return {
            "job_id": str(job_id),
            "status": mapped_status,
            "stage": stage,
            "progress": progress,
            "message": str(message),
            "error": error,
            "output_path": output_path,
            "outline": outline,
        }

    def get_download_path(self, job_id: str) -> Path | None:
        state = self._progress_store.get(job_id)
        if state and state.get("status") == "done":
            output = state.get("output_path")
            if output:
                return Path(output)

        doc = DocumentService.get_document(job_id)
        if not doc:
            return None
        status = str(doc.get("status") or "").upper()
        if status not in {"COMPLETED", "COMPLETED_WITH_WARNINGS"}:
            return None
        output_path = doc.get("output_path")
        return Path(output_path) if output_path else None

    def _update(
        self,
        job_id: str,
        stage: str,
        progress: int,
        message: str,
        output_path: str | None = None,
        error: str | None = None,
    ) -> None:
        state = self._progress_store.get(job_id, {})
        status = "failed" if stage == "error" else ("done" if progress >= 100 else ("pending" if stage == "queued" else "processing"))
        state.update(
            {
                "status": status,
                "stage": stage,
                "progress": int(max(0, min(100, progress))),
                "message": str(message),
            }
        )
        if output_path:
            state["output_path"] = output_path
        if error:
            state["error"] = error
        self._progress_store[job_id] = state

        doc_status = "FAILED" if status == "failed" else ("COMPLETED" if status == "done" else "PROCESSING")
        updates: dict[str, Any] = {
            "status": doc_status,
            "current_stage": stage.upper(),
            "progress": state["progress"],
        }
        if error:
            updates["error_message"] = error
        if output_path:
            updates["output_path"] = output_path
        DocumentService.update_document(job_id, updates)

        phase_status = "FAILED" if doc_status == "FAILED" else ("COMPLETED" if doc_status == "COMPLETED" else "PROCESSING")
        DocumentService.upsert_processing_status(
            job_id,
            phase=stage.upper(),
            status=phase_status,
            progress_percentage=state["progress"],
            message=message,
        )

        self._emit(
            job_id,
            phase=stage.upper(),
            status=phase_status,
            message=message,
            progress=state["progress"],
            stage=stage,
            output_path=state.get("output_path"),
            error=state.get("error"),
        )

    def _emit(self, job_id: str, **payload: Any) -> None:
        try:
            emit_event(job_id, "status_update", payload)
        except Exception as exc:
            logger.debug("SSE emission failed for generation job %s: %s", job_id, exc)

    async def _llm_generate(self, prompt: str, job_id: str) -> str:
        """
        Call the LLM via existing service fallbacks.
        """
        try:
            from app.services.llm_service import LLM_NVIDIA

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: LLM_NVIDIA.complete(prompt, max_tokens=4096, temperature=0.3),
            )
            if response and response.strip():
                logger.info("Generation job %s: NVIDIA Tier 1 LLM succeeded", job_id)
                return response
        except Exception as exc:
            logger.warning("Generation job %s: NVIDIA Tier 1 failed (%s), trying DeepSeek", job_id, exc)

        try:
            from app.services.llm_service import LLM_DEEPSEEK

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: LLM_DEEPSEEK.complete(prompt, max_tokens=4096, temperature=0.3),
            )
            if response and response.strip():
                logger.info("Generation job %s: DeepSeek Tier 2 LLM succeeded", job_id)
                return response
        except Exception as exc:
            logger.warning("Generation job %s: DeepSeek Tier 2 failed (%s), using rule fallback", job_id, exc)

        logger.warning("Generation job %s: all LLMs unavailable, using rule-based skeleton", job_id)
        state = self._progress_store.get(job_id, {})
        return self._rule_based_skeleton(str(state.get("doc_type", "academic_paper")), state.get("metadata") or {})

    @staticmethod
    def _rule_based_skeleton(doc_type: str, metadata: dict) -> str:
        import json

        title = metadata.get("title") or metadata.get("name") or "Document Title"
        blocks = [
            {"type": "TITLE", "content": title, "level": 0},
            {"type": "ABSTRACT", "content": metadata.get("abstract", "Abstract placeholder."), "level": 0},
            {"type": "HEADING_1", "content": "Introduction", "level": 1},
            {"type": "BODY", "content": "This section will be completed once AI services are available.", "level": 0},
            {"type": "HEADING_1", "content": "Conclusion", "level": 1},
            {"type": "BODY", "content": "Conclusion placeholder.", "level": 0},
        ]
        if doc_type == "resume":
            blocks = [
                {"type": "TITLE", "content": title, "level": 0},
                {"type": "HEADING_1", "content": "Professional Summary", "level": 1},
                {"type": "BODY", "content": metadata.get("summary", "Summary placeholder."), "level": 0},
                {"type": "HEADING_1", "content": "Experience", "level": 1},
                {"type": "BODY", "content": "Experience placeholder.", "level": 0},
            ]
        return json.dumps(blocks)

    async def _format_and_export(
        self,
        raw_blocks: list[dict[str, Any]],
        template: str,
        job_id: str,
        metadata: dict[str, Any],
        doc_type: str,
    ) -> Path:
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        output_path = (GENERATED_DIR / f"{job_id}.docx").resolve()

        pipeline_blocks: list[Block] = []
        for index, raw_block in enumerate(raw_blocks):
            text = str(raw_block.get("content", "")).strip()
            if not text:
                continue
            raw_type = str(raw_block.get("type", "BODY")).upper().strip()
            block_type = _BLOCK_TYPE_MAP.get(raw_type, BlockType.BODY)
            level = raw_block.get("level")
            try:
                level_value = int(level) if level is not None else None
            except Exception:
                level_value = None
            pipeline_blocks.append(
                Block(
                    block_id=f"{job_id}-{index}",
                    text=text,
                    block_type=block_type,
                    index=index,
                    level=level_value,
                    metadata=raw_block.get("metadata") or {},
                )
            )

        doc_metadata = DocumentMetadata(
            title=metadata.get("title") or metadata.get("name"),
            authors=[str(author) for author in metadata.get("authors", []) if str(author).strip()],
            abstract=metadata.get("abstract"),
            keywords=[str(keyword) for keyword in metadata.get("keywords", []) if str(keyword).strip()],
        )
        pipeline_doc = PipelineDocument(
            document_id=job_id,
            original_filename=f"generated_{job_id[:8]}.docx",
            blocks=pipeline_blocks,
            metadata=doc_metadata,
            template=TemplateInfo(template_name=template),
            formatting_options={
                "generation": True,
                "doc_type": doc_type,
                "export_formats": ["docx", "pdf"],
                "cover_page": False,
                "toc": False,
            },
            output_path=str(output_path),
        )

        formatter = Formatter()
        pipeline_doc = formatter.process(pipeline_doc)
        if not getattr(pipeline_doc, "generated_doc", None):
            raise RuntimeError("Formatting failed: no document artifact generated.")

        exporter = Exporter()
        pipeline_doc = exporter.process(pipeline_doc)
        if not output_path.exists():
            raise RuntimeError("Export failed: generated DOCX file not found.")

        return output_path

    @staticmethod
    def _extract_outline(raw_blocks: list[dict[str, Any]]) -> list[str]:
        outline: list[str] = []
        for block in raw_blocks:
            block_type = str(block.get("type", "")).upper()
            if block_type.startswith("HEADING") or block_type in {"TITLE", "ABSTRACT"}:
                content = str(block.get("content", "")).strip()
                if content:
                    outline.append(content)
        deduped: list[str] = []
        seen: set[str] = set()
        for item in outline:
            normalized = item.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(item)
        return deduped[:50]

    @staticmethod
    def _compute_sha256(filepath: Path) -> str:
        digest = hashlib.sha256()
        with open(filepath, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


_generator_singleton: DocumentGenerator | None = None


def get_generator() -> DocumentGenerator:
    global _generator_singleton
    if _generator_singleton is None:
        _generator_singleton = DocumentGenerator()
    return _generator_singleton
