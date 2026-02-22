"""
Pipeline Orchestrator - Coordinates all processing stages.
"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db.supabase_client import get_supabase_client
from app.models import (
    Block, 
    BlockType,
    TemplateInfo,
    PipelineDocument,
)
from app.pipeline.parsing.parser_factory import ParserFactory
from app.pipeline.normalization.normalizer import Normalizer as TextNormalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.nlp.analyzer import ContentAnalyzer
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.tables.caption_matcher import TableCaptionMatcher
from app.pipeline.references.parser import ReferenceParser
from app.pipeline.references.formatter_engine import ReferenceFormatterEngine
from app.pipeline.validation import DocumentValidator, validate_document
from app.pipeline.validation.ai_explainer import AIExplainer
from app.pipeline.formatting.formatter import Formatter
from app.pipeline.export.exporter import Exporter
from app.pipeline.input_conversion.converter import InputConverter
from app.pipeline.contracts.loader import ContractLoader
from app.pipeline.equations.standardizer import get_equation_standardizer

# Phase 2: AI Intelligence Stack
from app.pipeline.intelligence.rag_engine import get_rag_engine
from app.pipeline.intelligence.reasoning_engine import get_reasoning_engine
from app.pipeline.intelligence.semantic_parser import get_semantic_parser

# Week 2: GROBID and Docling Services
from app.pipeline.services import GROBIDClient, DoclingClient
# Safety Hardening
from app.pipeline.safety import safe_execution

import logging
import threading

logger = logging.getLogger(__name__)

# Concurrent job limiter — prevents OOM from unlimited parallel pipelines
_MAX_CONCURRENT_JOBS = 5
_pipeline_semaphore = threading.Semaphore(_MAX_CONCURRENT_JOBS)

class PipelineOrchestrator:
    """
    Runs the full document processing pipeline from input file to final output.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    
    def __init__(self, templates_dir: str = "app/templates", temp_dir: Optional[str] = None):
        self.templates_dir = templates_dir
        self.temp_dir = temp_dir or "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize pipeline stages
        self.converter = InputConverter()
        self.analyzer = ContentAnalyzer()
        contracts_base = os.path.dirname(templates_dir)
        self.contracts_dir = os.path.join(contracts_base, "pipeline", "contracts")
        self.contract_loader = ContractLoader(contracts_dir=self.contracts_dir)
        self.ref_normalizer = ReferenceFormatterEngine(self.contract_loader)
        
        # Week 2: Initialize GROBID and Docling clients
        self.grobid_client = GROBIDClient()
        self.docling_client = DoclingClient()
        
    def _check_stage_interface(self, stage_instance: Any, method_name: str, stage_name: str):
        """
        Verify that a pipeline stage implements the expected interface.
        Raises RuntimeError with a clear message if the method is missing.
        """
        if not hasattr(stage_instance, method_name):
            raise RuntimeError(
                f"Pipeline Stage Error: '{stage_name}' ({type(stage_instance).__name__}) "
                f"does not implement required method '{method_name}'."
            )
        
    def _update_status(self, document_id, phase, status, message=None, progress: Optional[int] = None):
        """Update processing status in Supabase DB."""
        document_id = str(document_id)
        sb = get_supabase_client()
        if not sb:
            print(f"⚠️ Supabase client unavailable for status update: {phase} -> {status}")
            return

        try:
            # 1. Update/Upsert ProcessingStatus
            # Match is safest for upsert logic
            data = {
                "document_id": document_id,
                "phase": phase,
                "status": status,
                "message": message,
                "progress_percentage": progress,
                "updated_at": "now()"
            }
            
            # Check if record exists
            existing = sb.table("processing_status").select("id").match({"document_id": document_id, "phase": phase}).execute()
            
            if existing.data:
                sb.table("processing_status").update(data).match({"document_id": document_id, "phase": phase}).execute()
            else:
                sb.table("processing_status").insert(data).execute()

            # 2. Update Parent Document
            doc_data = {
                "current_stage": phase,
                "updated_at": "now()"
            }
            
            if status == "COMPLETED":
                if phase == "PERSISTENCE":
                    doc_data["status"] = "COMPLETED"
                else:
                    doc_data["status"] = "RUNNING"
            elif status == "FAILED":
                doc_data["status"] = "FAILED"
                doc_data["error_message"] = message
            else:
                doc_data["status"] = status

            if progress is not None:
                doc_data["progress"] = progress
            
            sb.table("documents").update(doc_data).eq("id", document_id).execute()
        except Exception as e:
            print(f"❌ Supabase status update failed for job {document_id}: {e}")

    def _run_with_timeout(self, func, timeout_sec: int, *args, **kwargs):
        """Helper to run a synchronous pipeline stage with a strict timeout."""
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout_sec)
            except concurrent.futures.TimeoutError:
                logger.error("Pipeline stage timed out after %ds", timeout_sec)
                raise TimeoutError(f"Stage timed out after {timeout_sec}s")

    def run_pipeline(
        self, 
        input_path: str, 
        job_id: str, 
        template_name: Optional[str] = "IEEE",
        formatting_options: Dict[str, Any] = None  # New Parameter
    ) -> Dict[str, Any]:
        """
        Execute full pipeline sequentially in the background.
        """
        if not _pipeline_semaphore.acquire(blocking=False):
            logger.warning("Pipeline semaphore full. Job %s rejected (Too Many Requests)", job_id)
            self._update_status(job_id, "SYSTEM", "FAILED", "Too many concurrent jobs. Please try again later.")
            return {"status": "failed", "reason": "Server is busy"}

        try:
            return self._run_pipeline_internal(input_path, job_id, template_name, formatting_options)
        finally:
            _pipeline_semaphore.release()

    def _run_pipeline_internal(
        self, 
        input_path: str, 
        job_id: str, 
        template_name: Optional[str] = "IEEE",
        formatting_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Internal pipeline execution logic."""
        logger.debug("Orchestrator.run_pipeline started with template='%s', options=%s", template_name, formatting_options)
        
        if formatting_options is None:
            formatting_options = {}

        # 🛡️ SAFETY: Ensure job_id is string (not UUID object) for Supabase JSON serialization
        job_id = str(job_id)

        # NO long-lived 'db' session at the start.
        response = {
            "status": "processing",
            "job_id": job_id,
            "message": ""
        }
        
        try:
            document_rec = None
            output_path = None
            
            # PHASE 0: SAFETY NET
            with safe_execution(f"Pipeline Job {job_id}"):
                sb = get_supabase_client()
                
                # Phase 1: Upload & Job Creation
                self._update_status(job_id, "UPLOAD", "COMPLETED", "File uploaded and job created.", progress=5)
                
                # Phase 2: Text Extraction
                self._update_status(job_id, "EXTRACTION", "IN_PROGRESS", progress=10)
                
                # Check if we can parse the file directly without conversion
                factory = ParserFactory()
                file_ext = os.path.splitext(input_path)[1].lower()
                
                # Formats our parsers support directly (no conversion needed)
                parser_supported_formats = ['.pdf', '.txt', '.html', '.htm', '.md', '.markdown', '.tex', '.latex']
                
                if file_ext in parser_supported_formats:
                    # Parse original file directly (no Pandoc/LibreOffice needed!)
                    logger.info("Parsing %s directly with ParserFactory (no conversion)", file_ext)
                    parser = factory.get_parser(input_path)
                    doc_obj = parser.parse(input_path, job_id)
                    doc_obj.formatting_options = formatting_options  # Inject Options
                    docx_path = input_path  # Keep original path for reference
                else:
                    logger.info("Converting %s to DOCX first...", file_ext)
                    docx_path = self.converter.convert_to_docx(input_path, job_id)
                    
                    # Parse the converted DOCX
                    parser = factory.get_parser(docx_path)
                    doc_obj = parser.parse(docx_path, job_id)
                    doc_obj.formatting_options = formatting_options # Inject Options
                
                raw_text = "\n".join([b.text for b in doc_obj.blocks])

                # FEAT 40: Nougat OCR fallback for scanned PDFs
                if (not doc_obj.blocks or all(b.text.strip() == "" for b in doc_obj.blocks)) and file_ext == '.pdf':
                    try:
                        from app.pipeline.parsing.nougat_parser import NougatParser
                        logger.info("Empty extraction for PDF — trying Nougat OCR fallback for job %s", job_id)
                        nougat = NougatParser()
                        nougat_doc = nougat.parse(input_path, job_id)
                        if nougat_doc.blocks and any(b.text.strip() for b in nougat_doc.blocks):
                            doc_obj = nougat_doc
                            doc_obj.formatting_options = formatting_options
                            raw_text = "\n".join([b.text for b in doc_obj.blocks])
                            logger.info("Nougat OCR produced %d blocks for job %s", len(doc_obj.blocks), job_id)
                    except Exception as nougat_exc:
                        logger.warning("Nougat OCR fallback failed for job %s: %s", job_id, nougat_exc)

                if template_name:
                    doc_obj.template = TemplateInfo(template_name=template_name)
                
                if sb:
                    sb.table("documents").update({
                        "raw_text": raw_text,
                        "original_file_path": input_path
                    }).eq("id", job_id).execute()
                    
                    
                self._update_status(job_id, "EXTRACTION", "COMPLETED", "Text extracted successfully.", progress=20)
                
                # Phase 2.1: GROBID Metadata Extraction (Week 2)
                # Phase 2: Parallel Extraction (Grobid + Docling)
                
                # Only run AI extraction for PDF files directly
                if file_ext == '.pdf':
                    # BUG-005 FIX: Skip if results already exist (e.g., from Agent V2)
                    has_grobid = hasattr(doc_obj, 'metadata') and doc_obj.metadata and doc_obj.metadata.ai_hints.get('grobid_metadata')
                    has_docling = hasattr(doc_obj, 'metadata') and doc_obj.metadata and doc_obj.metadata.ai_hints.get('docling_layout')
                    
                    if has_grobid and has_docling:
                        logger.info("AI Extraction already completed (Agent V2). Skipping parallel pass.")
                    else:
                        self._update_status(job_id, "EXTRACTION", "IN_PROGRESS", "Extracting metadata and layout (Parallel)...", progress=22)
                        
                        with ThreadPoolExecutor(max_workers=2) as executor:
                            # Define wrapper functions for safe execution
                            def run_grobid():
                                if self.grobid_client.is_available():
                                    try:
                                        logger.info("Extracting metadata with GROBID...")
                                        return self.grobid_client.process_header_document(input_path)
                                    except Exception as e:
                                        logger.warning("GROBID extraction failed: %s", e)
                                return {}

                            def run_docling():
                                if self.docling_client.is_available():
                                    try:
                                        logger.info("Analyzing layout with Docling...")
                                        return self.docling_client.analyze_layout(input_path)
                                    except Exception as e:
                                        logger.warning("Docling analysis failed: %s", e)
                                return {} 

                            # Submit tasks
                            future_grobid = executor.submit(run_grobid)
                            future_docling = executor.submit(run_docling)
                            
                            # Get results (this blocks until both are done or timeout)
                            import concurrent.futures
                            try:
                                grobid_metadata = future_grobid.result(timeout=120)
                            except concurrent.futures.TimeoutError:
                                logger.warning("GROBID extraction timed out after 120s")
                                grobid_metadata = {}
                                
                            try:
                                layout_result = future_docling.result(timeout=120)
                            except concurrent.futures.TimeoutError:
                                logger.warning("Docling analysis timed out after 120s")
                                layout_result = {}

                            # Process Grobid Result
                            if grobid_metadata and isinstance(grobid_metadata, dict):
                                if not hasattr(doc_obj, 'metadata') or doc_obj.metadata is None:
                                    from app.models import DocumentMetadata
                                    doc_obj.metadata = DocumentMetadata()
                                doc_obj.metadata.ai_hints['grobid_metadata'] = grobid_metadata
                                logger.info("GROBID extracted: Title='%s', Authors=%d", grobid_metadata.get('title', 'N/A'), len(grobid_metadata.get('authors', [])))
                            else:
                                 logger.info("GROBID result unavailable (file_ext=%s)", file_ext)

                            # Process Docling Result
                            if layout_result and isinstance(layout_result, dict):
                                if not hasattr(doc_obj, 'metadata') or doc_obj.metadata is None:
                                    from app.models import DocumentMetadata
                                    doc_obj.metadata = DocumentMetadata()
                                doc_obj.metadata.ai_hints['docling_layout'] = layout_result
                                logger.info("Docling analyzed: %d elements found", len(layout_result.get('elements', [])))
                            else:
                                 logger.info("Docling result unavailable (file_ext=%s)", file_ext)

                # Phase 2.5: Equation Standardization
                self._update_status(job_id, "EXTRACTION", "IN_PROGRESS", "Standardizing equations...", progress=25)
                
                # CRITICAL: SemanticParser NLP predictions MUST run AFTER structure detection
                # and BEFORE classification to populate metadata["nlp_confidence"]
                semantic_parser = get_semantic_parser()
                try:
                    semantic_blocks = self._run_with_timeout(semantic_parser.analyze_blocks, 60, doc_obj.blocks)
                    
                    # Update block metadata with AI predictions
                    for i, b in enumerate(doc_obj.blocks):
                        if i < len(semantic_blocks):
                            b.metadata["semantic_intent"] = semantic_blocks[i]["predicted_section_type"]
                            b.metadata["nlp_confidence"] = semantic_blocks[i]["confidence_score"]
                except Exception as e:
                    print(f"AI ERROR (Layer 2 - NLP Analysis): {e}. Falling back to Phase-1 Heuristics.")
                
                self._update_status(job_id, "NLP_ANALYSIS", "IN_PROGRESS", "Classifying content...", progress=40)
                classifier = ContentClassifier()
                self._check_stage_interface(classifier, "process", "ContentClassifier")
                doc_obj = classifier.process(doc_obj)
                
                self._check_stage_interface(self.analyzer, "process", "ContentAnalyzer")
                doc_obj = self.analyzer.process(doc_obj)
                
                caption_matcher = CaptionMatcher(enable_vision=True)
                self._check_stage_interface(caption_matcher, "process", "CaptionMatcher")
                doc_obj = caption_matcher.process(doc_obj)
                
                table_caption_matcher = TableCaptionMatcher()
                self._check_stage_interface(table_caption_matcher, "process", "TableCaptionMatcher")
                doc_obj = table_caption_matcher.process(doc_obj)
                
                ref_parser = ReferenceParser()
                self._check_stage_interface(ref_parser, "process", "ReferenceParser")
                doc_obj = ref_parser.process(doc_obj)
                
                self._check_stage_interface(self.ref_normalizer, "process", "ReferenceFormatterEngine")
                doc_obj = self.ref_normalizer.process(doc_obj)
                
                self._update_status(job_id, "NLP_ANALYSIS", "COMPLETED", "Structural analysis complete.", progress=50)
                
                # Phase 4: AI Validation & Formatting
                self._update_status(job_id, "VALIDATION", "IN_PROGRESS", progress=60)
                
                # ------ CROSSREF VALIDATION (NEW) ------
                with safe_execution("CrossRef Citation Validation"):
                    try:
                        from app.services.crossref_client import get_crossref_client
                        crossref = get_crossref_client()
                        if hasattr(doc_obj, "references") and doc_obj.references:
                            print(f"🔬 Validating {len(doc_obj.references)} references against CrossRef...")
                            with ThreadPoolExecutor(max_workers=4) as cr_exec:
                                def validate_ref(ref):
                                    raw = getattr(ref, "raw_text", getattr(ref, "text", None))
                                    if raw:
                                        res = crossref.validate_citation(raw)
                                        if res:
                                            # Support both dict and Pydantic models blindly
                                            if not hasattr(ref, "metadata") or ref.metadata is None:
                                                ref.metadata = {}
                                            if isinstance(ref.metadata, dict):
                                                ref.metadata["crossref_validation"] = res
                                            elif hasattr(ref.metadata, "__setitem__"):
                                                ref.metadata["crossref_validation"] = res
                                            else:
                                                setattr(ref.metadata, "crossref_validation", res)
                                
                                list(cr_exec.map(validate_ref, doc_obj.references))
                    except Exception as e:
                        print(f"⚠️ CrossRef validation skipped (Non-Fatal): {e}")
                # ----------------------------------------
                
                self._update_status(job_id, "VALIDATION", "IN_PROGRESS", "Applying styles and templates...", progress=70)
                
                # Layer 1 & 3: RAG + DeepSeek Reasoning
                rag = get_rag_engine()
                reasoner = get_reasoning_engine()
                
                # Retrieve rules for critical sections
                rules_context = ""
                for sec in ["abstract", "references", "introduction", "methodology"]:
                    rule_matches = rag.query_rules(template_name, sec, top_k=2)
                    for r in rule_matches:
                        rules_context += f"\n- [{sec.upper()}]: {r['text']}"
                
                # This happens BEFORE Validation to guide deterministic decisions
                semantic_advice = {}
                with safe_execution("AI Reasoning Layer (Non-Critical)"):
                    # Phase 2: RAG Retrieval for Guidelines
                    rule_matches = []
                    if hasattr(rag, "query_rules"):
                        rule_matches = rag.query_rules(template_name, sec, top_k=2)
                    
                    # Context Compression + DeepSeek Reasoning (Layer 3)
                    rules_context = ""
                    for sec in ["Abstract", "Introduction", "References", "Figures"]:
                        if hasattr(rag, "query_guidelines"):
                            guidelines = rag.query_guidelines(template_name, sec, top_k=2)
                            if guidelines:
                                rules_context += f"\n- {sec}: {' '.join(guidelines)}"
                    
                    # DeepSeek Semantic Reasoning (Local Ollama)
                    # Input: Semantic blocks + RAG Context
                    context_blocks = [{"id": b.metadata.get("block_id", i), "text": b.text[:100], "type": b.metadata.get("semantic_intent")} 
                                     for i, b in enumerate(doc_obj.blocks[:15])]
                    
                    if hasattr(reasoner, "generate_instruction_set"):
                        semantic_advice = reasoner.generate_instruction_set(context_blocks, rules_context)
                    
                    # GUARDRAIL 1: Confidence Gating (0.85)
                    # Mark blocks for review if AI is unsure
                    for instruction in semantic_advice.get("instructions", []):
                        if instruction.get("confidence", 0) < 0.85:
                            instruction["review_required"] = True
                    
                    doc_obj.metadata.ai_hints["semantic_advice"] = semantic_advice

                from app.pipeline.validation.validator_v3 import DocumentValidator
                validator = DocumentValidator(contracts_dir=self.contracts_dir)
                self._check_stage_interface(validator, "process", "DocumentValidator")
                doc_obj = self._run_with_timeout(validator.process, 60, doc_obj)
                
                # GUARDRAIL 2: YAML Contract Override
                # Validation logic in validator.py already uses YAML contract as Truth.
                # We inject semantic_advice into validation_results for the UI.
                
                validation_results = {
                    "is_valid": doc_obj.is_valid,
                    "errors": doc_obj.validation_errors,
                    "warnings": doc_obj.validation_warnings,
                    "stats": doc_obj.get_stats(),
                    "ai_semantic_audit": semantic_advice # Integrated for Compare UI
                }
                
                formatter = Formatter(templates_dir=self.templates_dir, contracts_dir=self.contracts_dir)
                self._check_stage_interface(formatter, "process", "Formatter")
                doc_obj = self._run_with_timeout(formatter.process, 60, doc_obj)
                
                output_path = None
                if hasattr(doc_obj, 'generated_doc') and doc_obj.generated_doc:
                    exporter = Exporter()
                    out_dir = os.path.join("output", str(job_id))
                    os.makedirs(out_dir, exist_ok=True)
                    out_name = f"{os.path.splitext(os.path.basename(input_path))[0]}_formatted.docx"
                    output_path_rel = os.path.join(out_dir, out_name)
                    output_path = os.path.abspath(output_path_rel)
                    
                    doc_obj.output_path = output_path
                    self._check_stage_interface(exporter, "process", "Exporter")
                    doc_obj = exporter.process(doc_obj)
                else:
                    # RAISE EXPLICIT FAILURE
                    print(f"CRITICAL: Formatter failed to produce generated_doc for job {job_id}")
                    if sb:
                        sb.table("documents").update({
                            "status": "FAILED",
                            "error_message": "Formatting failed: No document artifact generated."
                        }).eq("id", job_id).execute()
                    raise Exception("Formatting stage failed to generate output artifact.")
                
                # Phase 5: Persistence (Benchmarked: 100%)
                self._update_status(job_id, "PERSISTENCE", "IN_PROGRESS", progress=90)

                explainer = AIExplainer()
                ai_explanations = explainer.explain_results(validation_results, template_name)
                validation_results["ai_explanations"] = ai_explanations
                
                # Fetch structured data (already generated above)
                structured_data = {
                    "sections": {},
                    "metadata": doc_obj.metadata.model_dump(mode='json'),
                    "references": [ref.model_dump(mode='json') for ref in doc_obj.references],
                    "history": [s.model_dump(mode='json') for s in doc_obj.processing_history]
                }
                for b in doc_obj.blocks:
                    if b.block_type:
                        bt_val = b.block_type.value if hasattr(b.block_type, 'value') else str(b.block_type)
                        if bt_val not in structured_data["sections"]:
                            structured_data["sections"][bt_val] = []
                        structured_data["sections"][bt_val].append(b.text)

                doc_result_data = {
                    "document_id": job_id,
                    "structured_data": structured_data,
                    "validation_results": validation_results,
                    "created_at": "now()"
                }
                if sb:
                    sb.table("document_results").insert(doc_result_data).execute()
                
                # ATOMIC COMPLETION CHECK
                # Only mark COMPLETED if output_path exists and is valid
                final_status = "FAILED"
                final_msg = "Persistence failed unknown error"
                
                if output_path and os.path.exists(output_path):
                    final_status = "COMPLETED"
                    final_msg = "All results persisted."
                    if sb:
                        sb.table("documents").update({
                            "status": "COMPLETED",
                            "output_path": output_path
                        }).eq("id", job_id).execute()
                else:
                    final_status = "FAILED"
                    final_msg = "Output generation failed."
                    if sb:
                        sb.table("documents").update({
                            "status": "FAILED",
                            "error_message": "Output file generation failed or path missing."
                        }).eq("id", job_id).execute()
                
                self._update_status(job_id, "PERSISTENCE", "COMPLETED", final_msg, progress=100)
                
                if final_status == "COMPLETED":
                    response["status"] = "success"
                    response["message"] = "Processing complete."
                else:
                    response["status"] = "error" 
                    response["message"] = f"Processing failed: {final_msg}"
            
        except asyncio.CancelledError:
            # Graceful shutdown: Log the interruption but do NOT re-raise.
            # This prevents noisy stack traces in Starlette/Uvicorn logs.
            print(f"Graceful Shutdown: Task {job_id} was cancelled by server reload/shutdown.")
            try:
                self._update_status(job_id, "SYSTEM", "FAILED", "Interrupted by server shutdown", progress=0)
                if sb:
                    sb.table("documents").update({
                        "status": "FAILED",
                        "error_message": "Interrupted by server shutdown"
                    }).eq("id", job_id).execute()
            except:
                pass # Already shutting down, avoid secondary errors
            return {"status": "cancelled", "message": "Interrupted by server shutdown"}
        except Exception as e:
            import traceback
            error_msg = str(e)
            logger.error("Pipeline Error: %s", error_msg)
            
            # Fallback: If we have an output path, we can downgrade to WARNING
            if output_path and os.path.exists(output_path):
                logger.warning("Pipeline Validation Error (Non-Fatal): %s", error_msg)
                self._update_status(job_id, "PERSISTENCE", "COMPLETED", "Completed with validation warnings.", progress=100)
                if sb:
                    sb.table("documents").update({
                        "status": "COMPLETED_WITH_WARNINGS",
                        "error_message": f"Validation Warning: {error_msg}",
                        "output_path": output_path
                    }).eq("id", job_id).execute()
                response["status"] = "success"
            else:
                self._update_status(job_id, "PERSISTENCE", "FAILED", error_msg, progress=0)
                if sb:
                    sb.table("documents").update({
                        "status": "FAILED",
                        "error_message": error_msg
                    }).eq("id", job_id).execute()
                response["status"] = "error"
                response["message"] = f"Pipeline failed: {error_msg}"
                
            logger.error("Pipeline Error Traceback: %s", traceback.format_exc())
            
        return response

    def run_edit_flow(
        self, 
        job_id: str, 
        edited_structured_data: Dict[str, Any],
        template_name: str = "IEEE"
    ) -> Dict[str, Any]:
        """
        Re-run only validation and formatting on edited data.
        Non-destructive pass that creates a new DocumentResult.
        """
        # 🛡️ SAFETY: Ensure job_id is string (not UUID object)
        job_id = str(job_id)

        try:
            sb = get_supabase_client()
            if not sb:
                raise Exception("Supabase client unavailable for edit flow.")

            # 1. Fetch original record
            doc_query = sb.table("documents").select("filename, output_path").eq("id", job_id).execute()
            if not doc_query.data:
                raise Exception("Original document not found")
            
            filename = doc_query.data[0]["filename"]
            source_output_path = doc_query.data[0]["output_path"]

            # 2. Reconstruct doc_obj from structured_data
            pipeline_doc = PipelineDocument(document_id=job_id)
            sections = edited_structured_data.get("sections", {})
            idx = 0
            for sec_name, texts in sections.items():
                for text in texts:
                    block = Block(
                        block_id=f"edit_{idx}",
                        index=idx,
                        text=text,
                        block_type=BlockType(sec_name) if sec_name in [e.value for e in BlockType] else BlockType.UNKNOWN
                    )
                    pipeline_doc.blocks.append(block)
                    idx += 1
            
            # 3. Re-run Validation
            self._update_status(job_id, "VALIDATION", "IN_PROGRESS", "Re-validating edits...", progress=30)
            
            from app.pipeline.validation import validate_document
            val_result = validate_document(pipeline_doc)
            validation_results = val_result.model_dump() if hasattr(val_result, 'model_dump') else val_result.dict() if hasattr(val_result, 'dict') else {}
            
            # 4. Re-run Formatting
            self._update_status(job_id, "VALIDATION", "IN_PROGRESS", "Applying styles to edited content...", progress=60)
            formatter = Formatter(templates_dir=self.templates_dir, contracts_dir=self.contracts_dir)
            formatted_doc = formatter.process(pipeline_doc)
            
            output_path = None
            if formatted_doc:
                exporter = Exporter()
                out_dir = os.path.join("output", f"{job_id}_edit")
                os.makedirs(out_dir, exist_ok=True)
                out_name = f"{os.path.splitext(filename)[0]}_edited.docx"
                output_path_rel = os.path.join(out_dir, out_name)
                output_path = os.path.abspath(output_path_rel)
                
                pipeline_doc.output_path = output_path
                exporter.process(pipeline_doc)
            
            # 5. Save current DocumentResult as a version BEFORE overwriting
            existing_result = sb.table("document_results").select("*").eq("document_id", job_id).execute()
            
            if existing_result.data:
                # Get latest version number
                versions = sb.table("document_versions").select("version_number").eq("document_id", job_id).order("version_number", desc=True).limit(1).execute()
                
                if versions.data:
                    try:
                        last_num = int(versions.data[0]["version_number"].replace('v', ''))
                        next_version_num = f"v{last_num + 1}"
                    except:
                        next_version_num = f"v_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                else:
                    next_version_num = "v1"
                
                version_record = {
                    "document_id": job_id,
                    "version_number": next_version_num,
                    "edited_structured_data": existing_result.data[0]["structured_data"],
                    "output_path": source_output_path,
                    "created_at": "now()"
                }
                sb.table("document_versions").insert(version_record).execute()
                
                sb.table("document_results").update({
                    "structured_data": edited_structured_data,
                    "validation_results": validation_results,
                    "updated_at": "now()"
                }).eq("document_id", job_id).execute()
            else:
                explainer = AIExplainer()
                ai_explanations = explainer.explain_results(validation_results, template_name)
                validation_results["ai_explanations"] = ai_explanations
                
                sb.table("document_results").insert({
                    "document_id": job_id,
                    "structured_data": edited_structured_data,
                    "validation_results": validation_results,
                    "created_at": "now()"
                }).execute()
            
            sb.table("documents").update({
                "output_path": output_path,
                "updated_at": "now()"
            }).eq("id", job_id).execute()
            
            self._update_status(job_id, "PERSISTENCE", "COMPLETED", "Edit re-formatted successfully.", progress=100)
            
            return {"status": "success", "output_path": output_path}
        except asyncio.CancelledError:
            print(f"Graceful Shutdown: Edit flow {job_id} was cancelled by server reload/shutdown.")
            try:
                self._update_status(job_id, "SYSTEM", "FAILED", "Edit interrupted by server shutdown", progress=0)
            except:
                pass
            return {"status": "cancelled", "message": "Edit interrupted by server shutdown"}
        except Exception as e:
            import traceback
            print(f"Edit flow error: {e}")
            self._update_status(job_id, "PERSISTENCE", "FAILED", f"Edit pass failed: {str(e)}", progress=0)
            return {"status": "error", "message": str(e)}
