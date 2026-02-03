"""
Pipeline Orchestrator - Coordinates all processing stages.
"""

import os
from typing import Optional, Dict, Any
from app.models import Document
from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer as TextNormalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.nlp.analyzer import ContentAnalyzer
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.references.parser import ReferenceParser
from app.pipeline.validation.validator import validate_document
from app.pipeline.formatting.formatter import Formatter
from app.pipeline.export.exporter import Exporter
from app.pipeline.input_conversion.converter import InputConverter

class PipelineOrchestrator:
    """
    Runs the full document processing pipeline from input file to final output.
    """
    
    def __init__(self, templates_dir: str = "app/templates", temp_dir: Optional[str] = None):
        self.templates_dir = templates_dir
        self.temp_dir = temp_dir
        self.converter = InputConverter(temp_dir=temp_dir)
        self.analyzer = ContentAnalyzer()
        
    def run_pipeline(
        self, 
        input_path: str, 
        job_id: str, 
        template_name: Optional[str] = None,
        enable_ocr: bool = True,
        enable_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full pipeline.
        """
        response = {
            "status": "processing",
            "job_id": job_id,
            "validation": None,
            "output_path": None,
            "message": "",
            "ocr_used": False, # Todo: Track this
            "ai_enabled": enable_ai
        }
        
        try:
            # 1. Input Conversion
            # We assume InputConverter handles flags (we just updated it)
            # Todo: InputConverter should return metadata about method used? 
            # Currently returns only path.
            docx_path = self.converter.convert_to_docx(input_path, job_id, enable_ocr=enable_ocr)
            
            # 2. Parsing
            parser = DocxParser()
            doc = parser.parse(docx_path)
            doc.document_id = job_id
            doc.original_filename = os.path.basename(input_path)
            
            # 3. Processing Stages
            # Normalization
            normalizer = TextNormalizer()
            doc = normalizer.normalize(doc)
            
            # Structure
            detector = StructureDetector()
            doc = detector.detect_structure(doc)
            
            # AI / NLP Enrichment (Phase 2)
            if enable_ai:
                doc = self.analyzer.analyze(doc)
            
            # Classification
            classifier = ContentClassifier()
            doc = classifier.classify(doc)

            
            # Figures
            caption_matcher = CaptionMatcher()
            doc = caption_matcher.match_captions(doc)
            
            # References
            ref_parser = ReferenceParser()
            doc = ref_parser.parse_references(doc)
            
            # 4. Validation
            val_result = validate_document(doc)
            # Convert pydantic model to dict safely
            response["validation"] = val_result.model_dump() if hasattr(val_result, 'model_dump') else val_result.dict()
            
            if not val_result.is_valid:
                 response["message"] = "Document validation failed. See validation report."
                 # We still allow formatting attempts? Requirement: "Return... message if formatting skipped"
                 # Typically we might stop, but soft failures are better.
                 # User constraint Phase 2: "Run full pipeline... formatting (optional)"
                 # Let's proceed unless critical failure (exception).
            
            # 5. Formatting & Export
            formatter = Formatter(templates_dir=self.templates_dir)
            formatted_doc = formatter.format(doc, template_name)
            
            if formatted_doc:
                exporter = Exporter()
                # Determine output path
                # output/{job_id}/[filename]_formatted.docx
                out_dir = os.path.join("output", job_id)
                out_name = f"{os.path.splitext(doc.original_filename)[0]}_formatted.docx"
                out_path = os.path.abspath(os.path.join(out_dir, out_name))
                
                saved_path = exporter.export(formatted_doc, out_path)
                response["output_path"] = saved_path
                response["status"] = "success"
                response["message"] = "Processing complete."
            else:
                response["status"] = "success" # Still success if validation passed but formatting skipped
                response["message"] = "Processing complete. Formatting skipped (no template)."
                
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
            
        return response
