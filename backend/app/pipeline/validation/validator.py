"""
Document Validator - checks for structural and content validity.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import Document, BlockType, Figure

class ValidationResult(BaseModel):
    """Result of a document validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentValidator:
    """
    Validates document structure and content completeness.
    
    Checks:
    - Required sections (Abstract, Introduction, References)
    - Figure caption completeness
    - Reference completeness (Authors, Year)
    - Structural flow
    """
    
    def __init__(self):
        self.required_sections = {"introduction", "references"}
        # Abstract might be named differently (Abstract, Summary), usually "abstract".
        
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

        # 4. Figure Reference Validation (Text Scan)
        fig_ref_errors, fig_ref_warnings = self._check_figure_references(document)
        errors.extend(fig_ref_errors) 
        warnings.extend(fig_ref_warnings)

        # 5. Table Validation
        table_errors, table_warnings = self._check_tables(document)
        errors.extend(table_errors)
        warnings.extend(table_warnings)

        # 6. Citation Integrity (Text Scan used against Parsed Refs)
        cit_errors, cit_warnings = self._check_citation_integrity(document)
        errors.extend(cit_errors)
        warnings.extend(cit_warnings)
        
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
        
        # Get flattened list of section names (case insensitive)
        sections = {s.lower() for s in document.get_section_names() if s}
        
        # Check Abstract (Special Check)
        # Abstract might be a BlockType.ABSTRACT_HEADING regardless of section name "Abstract"
        has_abstract = any(b.block_type == BlockType.ABSTRACT_HEADING for b in document.blocks)
        
        if not has_abstract:
            # Fallback: check section name
            if "abstract" not in sections:
                warnings.append("Missing Abstract section")
        
        # Check Introduction
        if "introduction" not in sections:
             # Look for "1. Introduction" etc.
             # But section names in model were cleaned? Hopefully.
             # If not found, warning.
             warnings.append("Missing Introduction section")
             
        # Check References
        if "references" not in sections and "bibliography" not in sections:
            errors.append("Missing References section")
             
        # Structural Order Validation
        # Abstract -> Intro
        # We need the indices.
        abstract_idx = -1
        intro_idx = -1
        refs_idx = -1
        
        for i, block in enumerate(document.blocks):
            s_name = (block.section_name or "").lower()
            if block.block_type == BlockType.ABSTRACT_HEADING or "abstract" in s_name:
                if abstract_idx == -1: abstract_idx = i
            elif "introduction" in s_name:
                if intro_idx == -1: intro_idx = i
            elif "references" in s_name or "bibliography" in s_name:
                if refs_idx == -1: refs_idx = i
        
        if abstract_idx != -1 and intro_idx != -1:
            if abstract_idx > intro_idx:
                warnings.append("Structural issue: Abstract appears after Introduction")
        
        if refs_idx != -1 and len(document.blocks) > 0:
            # Check if refs are "near" the end?
            # Or just after Intro?
            if intro_idx != -1 and refs_idx < intro_idx:
                warnings.append("Structural issue: References appear before Introduction")
            
            # Warn if significant content follows references (e.g. not just Appendix)
            # This is hard to detect without knowing if it's Appendix.
            pass
        
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

    def _check_citation_integrity(self, document: Document) -> tuple:
        """
        Check if citations in text (e.g. [1], [2]) match parsed references.
        """
        warnings = []
        
        # Gather all parsed citation keys (e.g. "[1]", "[2]")
        # ReferenceParser should have extracted these.
        if not document.references:
            return [], [] # No references parsed, handled elsewhere
            
        parsed_keys = set()
        for ref in document.references:
            if ref.citation_key:
                parsed_keys.add(ref.citation_key.strip())
        
        # Regex for [N] or [N, M]
        # Simple Case: [1]
        pattern = re.compile(r'\[(\d+)\]')
        
        referenced_keys = set()
        
        target_types = {BlockType.BODY, BlockType.ABSTRACT_BODY}
        for block in document.blocks:
            if block.block_type in target_types:
                clean_text = block.text
                matches = pattern.findall(clean_text)
                for num_str in matches:
                    key = f"[{num_str}]"
                    referenced_keys.add(key)
        
        # Check for citations not in references list
        for key in referenced_keys:
            if key not in parsed_keys:
                warnings.append(f"Citation {key} matches no entry in References list")
                
        return [], warnings

    def _check_figure_references(self, document: Document) -> tuple:
        """
        Check if figures referenced in text exist in the document.
        """
        errors = [] # Not used for this check, but return empty list for consistency
        warnings = []
        
        # Regex for "Figure X", "Fig. X"
        # Case insensitive
        pattern = re.compile(r'\b(Figure|Fig\.?)\s+(\d+)\b', re.IGNORECASE)
        
        referenced_numbers = set()
        
        # Scan Body and Abstract
        target_types = {BlockType.BODY, BlockType.ABSTRACT_BODY}
        
        for block in document.blocks:
            if block.block_type in target_types:
                matches = pattern.findall(block.text)
                for _, num_str in matches:
                    referenced_numbers.add(int(num_str))
                    
        # Get actual figure numbers
        # If figures don't have explicit numbers, assume 1..N order
        actual_numbers = set()
        if document.figures:
            # Check if figures generally have numbers assigned?
            # Pipeline didn't explicitly assign 'number' field to Figure, but we have index.
            # We assume order-based numbering 1..N matches the text references.
            for i in range(len(document.figures)):
                actual_numbers.add(i + 1)
        
        # Check for missing figures
        if not actual_numbers and not referenced_numbers:
            return errors, warnings
            
        if not actual_numbers and referenced_numbers:
            warnings.append("Text references figures, but no figures were detected in the document")
            return errors, warnings
            
        for ref_num in referenced_numbers:
            if ref_num not in actual_numbers:
                warnings.append(f"Figure {ref_num} referenced in text but missing from document (found {len(actual_numbers)} figures)")
                
        return errors, warnings


# Convenience
def validate_document(document: Document) -> ValidationResult:
    validator = DocumentValidator()
    return validator.validate(document)
