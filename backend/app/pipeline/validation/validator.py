"""
Document Validator - checks for structural and content validity.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import PipelineDocument as Document, BlockType, Figure
from app.pipeline.contracts.loader import ContractLoader
from app.pipeline.formatting.section_ordering import SectionOrderValidator
from app.pipeline.integrity.cross_ref import CrossReferenceEngine
from app.pipeline.validation.review_manager import ReviewManager
from app.pipeline.base import PipelineStage

class ValidationResult(BaseModel):
    """Result of a document validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentValidator(PipelineStage):
    """
    Validates document structure and content completeness.
    Driven by contract rules.
    """
    
    def __init__(self, contracts_dir: str = "app/pipeline/contracts"):
        self.contract_loader = ContractLoader(contracts_dir=contracts_dir)
        self.order_validator = SectionOrderValidator(self.contract_loader)
        self.integrity_engine = CrossReferenceEngine()
        
    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        self.validate(document)
        return document

    def validate(self, document: Document) -> ValidationResult:
        """
        Run all validation checks.
        """
        start_time = datetime.utcnow()
        
        errors = []
        warnings = []
        
        # 1. Section Completeness
        section_errors, section_warnings = self._check_sections(document)
        errors.extend(section_errors)
        warnings.extend(section_warnings)
        
        # 2. Figure Validation
        fig_errors, fig_warnings = self._check_figures(document)
        errors.extend(fig_errors)
        warnings.extend(fig_warnings)
        
        # 3. Reference Validation
        ref_errors, ref_warnings = self._check_references(document)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)

        # 4. Integrity / Cross-Reference Validation
        integrity_violations = self.integrity_engine.validate_integrity(document)
        for violation in integrity_violations:
            if "Dangling" in violation:
                errors.append(violation)
            else:
                warnings.append(violation)

        # 5. Table Validation
        table_errors, table_warnings = self._check_tables(document)
        errors.extend(table_errors)
        warnings.extend(table_warnings)
        
        # 6. Confidence-Based HITL Signs
        review_manager = ReviewManager()
        review_manager.evaluate(document)
        
        # 7. Final Verdict
        is_valid = len(errors) == 0
        
        # Update Document
        document.is_valid = is_valid
        document.validation_errors = errors
        document.validation_warnings = warnings
        
        # Log
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        document.add_processing_stage(
            stage_name="validation",
            status="success" if is_valid else "warning",
            message=f"Validation complete: {len(errors)} errors, {len(warnings)} warnings",
            duration_ms=duration_ms
        )
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=document.get_stats()
        )

    def _check_sections(self, document: Document) -> tuple:
        errors = []
        warnings = []
        
        publisher = document.template.template_name if document.template else "IEEE"
        
        # Use contract-driven order validator
        order_violations = self.order_validator.validate_order(document, publisher)
        for violation in order_violations:
            if "Missing required" in violation:
                errors.append(violation)
            else:
                warnings.append(violation)
        
        return errors, warnings

    def _check_figures(self, document: Document) -> tuple:
        errors = []
        warnings = []
        
        for fig in document.figures:
            if not fig.has_caption():
                warnings.append(f"Figure {fig.figure_id} missing caption")
        
        return errors, warnings

    def _check_references(self, document: Document) -> tuple:
        errors = []
        warnings = []
        
        if not document.references:
            # If References section exists but no references parsed -> Error
            # If References section missing -> Error/Warning handled above
            # If References section exists and references parsed -> check quality
            
            # Check if section exists
            sections = {s.lower() for s in document.get_section_names() if s}
            if "references" in sections:
                warnings.append("References section found but no reference entries parsed")
            return errors, warnings

        for ref in document.references:
            # Critical fields
            if not ref.year:
                warnings.append(f"Reference '{ref.citation_key}' missing publication year")
            if not ref.authors:
                errors.append(f"Reference '{ref.citation_key}' missing authors")
            if not ref.title:
                warnings.append(f"Reference '{ref.citation_key}' missing title")
                
        return errors, warnings

    def _check_tables(self, document: Document) -> tuple:
        warnings = []
        # Check Tables without captions
        if hasattr(document, 'tables'):
             for i, table in enumerate(document.tables):
                 if not table.caption_text:
                     warnings.append(f"Table {i+1} missing caption")
        return [], warnings

        for ref_num in referenced_numbers:
            if ref_num not in actual_numbers:
                warnings.append(f"Figure {ref_num} referenced in text but missing from document (found {len(actual_numbers)} figures)")
                
        return errors, warnings


# Convenience
def validate_document(document: Document) -> ValidationResult:
    validator = DocumentValidator()
    return validator.validate(document)
