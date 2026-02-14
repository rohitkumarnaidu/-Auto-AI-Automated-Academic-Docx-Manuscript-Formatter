"""
Pipeline Orchestrator - Coordinates all processing stages.
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from app.db.session import SessionLocal
from app.models import (
    Document, 
    DocumentResult, 
    ProcessingStatus, 
    PipelineDocument, 
    Block, 
    BlockType,
    DocumentVersion,
    TemplateInfo
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
from app.pipeline.validation.validator import validate_document
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

class PipelineOrchestrator:
    """
    Runs the full document processing pipeline from input file to final output.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    
    def __init__(self, templates_dir: str = "app/templates", temp_dir: Optional[str] = None):
        self.templates_dir = templates_dir
        self.temp_dir = temp_dir
        self.converter = InputConverter(temp_dir=temp_dir)
        self.analyzer = ContentAnalyzer()
        contracts_base = os.path.dirname(templates_dir)
        self.contracts_dir = os.path.join(contracts_base, "pipeline", "contracts")
        self.contract_loader = ContractLoader(contracts_dir=self.contracts_dir)
        self.ref_normalizer = ReferenceFormatterEngine(self.contract_loader)
        
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
        
    def _update_status(self, db, document_id, phase, status, message=None, progress: Optional[int] = None):
        """Update processing status in the database."""
        status_rec = db.query(ProcessingStatus).filter_by(document_id=document_id, phase=phase).first()
        if not status_rec:
            status_rec = ProcessingStatus(document_id=document_id, phase=phase)
            db.add(status_rec)
        
        status_rec.status = status
        status_rec.message = message
        if progress is not None:
            status_rec.progress_percentage = progress
            
        # Update Parent Document (Single Source of Truth)
        doc_rec = db.query(Document).filter_by(id=document_id).first()
        if doc_rec:
            # Only propagate COMPLETED to parent status if it's the final PERSISTENCE phase
            if status == "COMPLETED":
                if phase == "PERSISTENCE":
                    doc_rec.status = "COMPLETED"
                # Otherwise, keep it as RUNNING if not already failed
                elif doc_rec.status != "FAILED":
                    doc_rec.status = "RUNNING"
            elif status == "FAILED":
                doc_rec.status = "FAILED"
                doc_rec.error_message = message
            else:
                doc_rec.status = status
                
            if progress is not None:
                doc_rec.progress = progress
            if phase:
                doc_rec.current_stage = phase
        
        db.commit()

    def run_pipeline(
        self, 
        input_path: str, 
        job_id: str, 
        template_name: Optional[str] = "IEEE",
        enable_ocr: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full pipeline sequentially in the background.
        """
        # DEBUG LOG
        print(f"DEBUG: Orchestrator.run_pipeline started with template_name='{template_name}'")

        # NO long-lived 'db' session at the start.
        response = {
            "status": "processing",
            "job_id": job_id,
            "message": ""
        }
        
        try:
            document_rec = None
            output_path = None
            
            # Phase 1: Upload & Job Creation
            with SessionLocal() as db:
                self._update_status(db, job_id, "UPLOAD", "COMPLETED", "File uploaded and job created.", progress=5)
            
            # Phase 2: Text Extraction (Benchmarked: 20%)
            with SessionLocal() as db:
                self._update_status(db, job_id, "EXTRACTION", "IN_PROGRESS", progress=10)
            
            # Check if we can parse the file directly without conversion
            factory = ParserFactory()
            file_ext = os.path.splitext(input_path)[1].lower()
            
            # Formats our parsers support directly (no conversion needed)
            parser_supported_formats = ['.pdf', '.txt', '.html', '.htm', '.md', '.markdown', '.tex', '.latex']
            
            if file_ext in parser_supported_formats:
                # Parse original file directly (no Pandoc/LibreOffice needed!)
                print(f"✅ Parsing {file_ext} directly with ParserFactory (no conversion)")
                parser = factory.get_parser(input_path)
                doc_obj = parser.parse(input_path, job_id)
                docx_path = input_path  # Keep original path for reference
            else:
                # For .docx or other formats, use converter then parser
                docx_path = self.converter.convert_to_docx(input_path, job_id, enable_ocr=enable_ocr)
                parser = factory.get_parser(docx_path)
                doc_obj = parser.parse(docx_path, job_id)
            
            raw_text = "\n".join([b.text for b in doc_obj.blocks])

            # CRITICAL FIX: Set Template Info for Formatter
            if template_name:
                doc_obj.template = TemplateInfo(template_name=template_name)
            
            with SessionLocal() as db:
                document_rec = db.query(Document).filter_by(id=job_id).first()
                if document_rec:
                    document_rec.raw_text = raw_text
                    document_rec.original_file_path = input_path
                    db.commit()
                self._update_status(db, job_id, "EXTRACTION", "COMPLETED", "Text extracted successfully.", progress=20)
            
            # Phase 2.5: Equation Standardization
            with SessionLocal() as db:
                self._update_status(db, job_id, "EXTRACTION", "IN_PROGRESS", "Standardizing equations...", progress=25)
            
            standardizer = get_equation_standardizer()
            doc_obj = standardizer.process(doc_obj)
            
            # Phase 3: NLP Structural Analysis (Benchmarked: 50%)
            with SessionLocal() as db:
                self._update_status(db, job_id, "NLP_ANALYSIS", "IN_PROGRESS", progress=30)
            
            normalizer = TextNormalizer()
            self._check_stage_interface(normalizer, "process", "TextNormalizer")
            doc_obj = normalizer.process(doc_obj)
            
            # Layer 2: NLP Foundation (Semantic Parser)
            # PHASE 2: AI Intelligence Stack (SciBERT Semantic Analysis)
            # NOTE: This runs BEFORE structure detection to provide semantic hints
            semantic_parser = get_semantic_parser()
            semantic_blocks = []
            try:
                # Use getattr for maximum safety against interface drift
                if hasattr(semantic_parser, "detect_boundaries"):
                    doc_obj.blocks = semantic_parser.detect_boundaries(doc_obj.blocks)
                
                if hasattr(semantic_parser, "reconcile_fragmented_headings"):
                    doc_obj.blocks = semantic_parser.reconcile_fragmented_headings(doc_obj.blocks)
            except Exception as e:
                print(f"AI ERROR (Layer 2 - Preprocessing): {e}. Continuing with structure detection.")

            # Back to deterministic processing
            detector = StructureDetector(contracts_dir=self.contracts_dir)
            self._check_stage_interface(detector, "process", "StructureDetector")
            doc_obj = detector.process(doc_obj)
            
            # CRITICAL: SemanticParser NLP predictions MUST run AFTER structure detection
            # and BEFORE classification to populate metadata["nlp_confidence"]
            try:
                semantic_blocks = semantic_parser.analyze_blocks(doc_obj.blocks)
                
                # Update block metadata with AI predictions
                for i, b in enumerate(doc_obj.blocks):
                    if i < len(semantic_blocks):
                        b.metadata["semantic_intent"] = semantic_blocks[i]["predicted_section_type"]
                        b.metadata["nlp_confidence"] = semantic_blocks[i]["confidence_score"]
            except Exception as e:
                print(f"AI ERROR (Layer 2 - NLP Analysis): {e}. Falling back to Phase-1 Heuristics.")
            
            with SessionLocal() as db:
                self._update_status(db, job_id, "NLP_ANALYSIS", "IN_PROGRESS", "Classifying content...", progress=40)
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
            
            with SessionLocal() as db:
                self._update_status(db, job_id, "NLP_ANALYSIS", "COMPLETED", "Structural analysis complete.", progress=50)
            
            # Phase 4: AI Validation & Formatting (Benchmarked: 80%)
            with SessionLocal() as db:
                self._update_status(db, job_id, "VALIDATION", "IN_PROGRESS", progress=60)
                self._update_status(db, job_id, "VALIDATION", "IN_PROGRESS", "Applying styles and templates...", progress=70)
            
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
            try:
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
            except Exception as e:
                print(f"AI ERROR (Layer 1/3): {e}. Proceeding with deterministic defaults.")

            from app.pipeline.validation.validator import DocumentValidator
            validator = DocumentValidator(contracts_dir=self.contracts_dir)
            self._check_stage_interface(validator, "process", "DocumentValidator")
            doc_obj = validator.process(doc_obj)
            
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
            doc_obj = formatter.process(doc_obj)
            
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
                with SessionLocal() as db:
                    document_rec_err = db.query(Document).filter_by(id=job_id).first()
                    if document_rec_err:
                        document_rec_err.status = "FAILED"
                        document_rec_err.error_message = "Formatting failed: No document artifact generated."
                        db.commit()
                raise Exception("Formatting stage failed to generate output artifact.")
            
            # Phase 5: Persistence (Benchmarked: 100%)
            with SessionLocal() as db:
                self._update_status(db, job_id, "PERSISTENCE", "IN_PROGRESS", progress=90)
                
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

                doc_result = DocumentResult(
                    document_id=job_id,
                    structured_data=structured_data,
                    validation_results=validation_results
                )
                db.add(doc_result)
                db.commit()
            
            # ATOMIC COMPLETION CHECK
            # Only mark COMPLETED if output_path exists and is valid
            final_status = "FAILED"
            final_msg = "Persistence failed unknown error"
            
            if output_path and os.path.exists(output_path):
                final_status = "COMPLETED"
                final_msg = "All results persisted."
                with SessionLocal() as db:
                    document_rec_final = db.query(Document).filter_by(id=job_id).first()
                    if document_rec_final:
                        document_rec_final.status = "COMPLETED"
                        document_rec_final.output_path = output_path
                        db.commit()
            else:
                final_status = "FAILED"
                final_msg = "Output generation failed."
                with SessionLocal() as db:
                    document_rec_fail = db.query(Document).filter_by(id=job_id).first()
                    if document_rec_fail:
                        document_rec_fail.status = "FAILED"
                        document_rec_fail.error_message = "Output file generation failed or path missing."
                        db.commit()
            
            with SessionLocal() as db:
                self._update_status(db, job_id, "PERSISTENCE", "COMPLETED", final_msg, progress=100)
            
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
                with SessionLocal() as cleanup_db:
                    self._update_status(cleanup_db, job_id, "SYSTEM", "FAILED", "Interrupted by server shutdown", progress=0)
                    cleanup_doc = cleanup_db.query(Document).filter_by(id=job_id).first()
                    if cleanup_doc:
                        cleanup_doc.status = "FAILED"
                        cleanup_doc.error_message = "Interrupted by server shutdown"
                        cleanup_db.commit()
            except:
                pass # Already shutting down, avoid secondary errors
            return {"status": "cancelled", "message": "Interrupted by server shutdown"}
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Pipeline Error: {error_msg}")
            
            with SessionLocal() as db:
                # Fallback: If we have an output path, we can downgrade to WARNING
                if output_path and os.path.exists(output_path):
                     print(f"Pipeline Validation Error (Non-Fatal): {error_msg}")
                     self._update_status(db, job_id, "PERSISTENCE", "COMPLETED", "Completed with validation warnings.", progress=100)
                     document_rec_fail = db.query(Document).filter_by(id=job_id).first()
                     if document_rec_fail:
                         document_rec_fail.status = "COMPLETED_WITH_WARNINGS"
                         document_rec_fail.error_message = f"Validation Warning: {error_msg}"
                         document_rec_fail.output_path = output_path
                         db.commit()
                     response["status"] = "success"
                else:
                    self._update_status(db, job_id, "PERSISTENCE", "FAILED", error_msg, progress=0)
                    document_rec_fail = db.query(Document).filter_by(id=job_id).first()
                    if document_rec_fail:
                        document_rec_fail.status = "FAILED"
                        document_rec_fail.error_message = error_msg
                        db.commit()
                    response["status"] = "error"
                    response["message"] = f"Pipeline failed: {error_msg}"
                
            print(f"Pipeline Error Traceback: {traceback.format_exc()}")
            
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
        try:
            # 1. Fetch original record in atomic session
            with SessionLocal() as db:
                doc_rec = db.query(Document).filter_by(id=job_id).first()
                if not doc_rec:
                    raise Exception("Original document not found")
                filename = doc_rec.filename
                source_output_path = doc_rec.output_path

            # 2. Reconstruct doc_obj from structured_data
            # We create a PipelineDocument from the edited sections
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
            with SessionLocal() as db:
                doc_rec = db.query(Document).filter_by(id=job_id).first()
                if not doc_rec:
                    raise Exception("Original document not found")
                self._update_status(db, job_id, "VALIDATION", "IN_PROGRESS", "Re-validating edits...", progress=30)
            val_result = validate_document(pipeline_doc)
            validation_results = val_result.model_dump() if hasattr(val_result, 'model_dump') else val_result.dict() if hasattr(val_result, 'dict') else {}
            
            # 4. Re-run Formatting
            with SessionLocal() as db:
                self._update_status(db, job_id, "VALIDATION", "IN_PROGRESS", "Applying styles to edited content...", progress=60)
            formatter = Formatter(templates_dir=self.templates_dir)
            formatted_doc = formatter.format(pipeline_doc, template_name)
            
            output_path = None
            if formatted_doc:
                exporter = Exporter()
                out_dir = os.path.join("output", f"{job_id}_edit")
                os.makedirs(out_dir, exist_ok=True)
                out_name = f"{os.path.splitext(filename)[0]}_edited.docx"
                output_path_rel = os.path.join(out_dir, out_name)
                output_path = os.path.abspath(output_path_rel)
                exporter.export(formatted_doc, output_path)
            
            # 5. Save current DocumentResult as a version BEFORE overwriting
            with SessionLocal() as db:
                existing_result = db.query(DocumentResult).filter_by(document_id=job_id).first()
                doc_rec = db.query(Document).filter_by(id=job_id).first()
                
                if existing_result:
                    # Get latest version number to increment
                    latest_version = db.query(DocumentVersion).filter_by(
                        document_id=job_id
                    ).order_by(DocumentVersion.version_number.desc()).first()
                    
                    if latest_version:
                        try:
                            last_num = int(latest_version.version_number.replace('v', ''))
                            next_version_num = f"v{last_num + 1}"
                        except:
                            next_version_num = f"v_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                    else:
                        next_version_num = "v1"
                    
                    version_record = DocumentVersion(
                        document_id=job_id,
                        version_number=next_version_num,
                        edited_structured_data=existing_result.structured_data,
                        output_path=source_output_path
                    )
                    db.add(version_record)
                    
                    existing_result.structured_data = edited_structured_data
                    existing_result.validation_results = validation_results
                    db.add(existing_result)
                else:
                    explainer = AIExplainer()
                    ai_explanations = explainer.explain_results(validation_results, template_name)
                    validation_results["ai_explanations"] = ai_explanations
                    
                    new_result = DocumentResult(
                        document_id=job_id,
                        structured_data=edited_structured_data,
                        validation_results=validation_results
                    )
                    db.add(new_result)
                
                if doc_rec:
                    doc_rec.output_path = output_path
                    db.add(doc_rec)
                
                db.commit()
                self._update_status(db, job_id, "PERSISTENCE", "COMPLETED", "Edit re-formatted successfully.", progress=100)
            
            return {"status": "success", "output_path": output_path}
        except asyncio.CancelledError:
            # Graceful shutdown for edit flow
            print(f"Graceful Shutdown: Edit flow {job_id} was cancelled by server reload/shutdown.")
            try:
                with SessionLocal() as cleanup_db:
                    self._update_status(cleanup_db, job_id, "SYSTEM", "FAILED", "Edit interrupted by server shutdown", progress=0)
                    cleanup_db.commit()
            except:
                pass
            return {"status": "cancelled", "message": "Edit interrupted by server shutdown"}
        except Exception as e:
            import traceback
            print(f"Edit flow error: {e}")
            with SessionLocal() as db:
                self._update_status(db, job_id, "PERSISTENCE", "FAILED", f"Edit pass failed: {str(e)}", progress=0)
            return {"status": "error", "message": str(e)}
