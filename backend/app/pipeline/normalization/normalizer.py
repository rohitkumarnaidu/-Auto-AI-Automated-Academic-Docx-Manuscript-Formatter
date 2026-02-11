"""
Normalization Stage - Clean and normalize text content.

This is the second stage of the pipeline. It takes a parsed Document
and normalizes all text content without changing meaning or structure.

Input: Document from parsing stage (with UNKNOWN block types)
Output: Document with normalized text (still UNKNOWN block types)

Normalization includes:
- Unicode character normalization (quotes, dashes, spaces)
- Whitespace normalization (trim, collapse)
- Metadata field cleaning
- Table cell text trimming

IMPORTANT:
- Do NOT detect structure
- Do NOT classify blocks
- Do NOT re-order blocks
- Do NOT drop content
- Preserve all block IDs and positions
- Preserve UNKNOWN block types
- Be conservative (when unsure, do nothing)
"""

from typing import List
from datetime import datetime

from app.models import PipelineDocument as Document, Block, Table, DocumentMetadata
from app.utils.text_utils import (
    normalize_block_text,
    normalize_table_cell_text,
    clean_metadata_field,
)


from app.pipeline.base import PipelineStage

class Normalizer(PipelineStage):
    """
    Normalizes text content in a Document model.
    
    This stage cleans text without interpreting semantic meaning.
    Structure detection and classification happen in later stages.
    """
    
    def __init__(self):
        """Initialize the normalizer."""
        pass
    
    def process(self, document: Document) -> Document:
        """
        Normalize all text content in the document.
        
        This modifies block text, table cells, and metadata in place
        while preserving all IDs, positions, and block types.
        
        Args:
            document: Document from parsing stage
        
        Returns:
            Document with normalized text content
        """
        start_time = datetime.utcnow()
        
        # Normalize metadata
        document.metadata = self._normalize_metadata(document.metadata)
        
        # Normalize blocks
        document.blocks = self._normalize_blocks(document.blocks)
        
        # Normalize tables
        document.tables = self._normalize_tables(document.tables)
        
        # Note: Figures don't have text to normalize (only captions, which come later)
        
        # Update processing history
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        document.add_processing_stage(
            stage_name="normalization",
            status="success",
            message=f"Normalized {len(document.blocks)} blocks, {len(document.tables)} tables, metadata",
            duration_ms=duration_ms
        )
        
        document.updated_at = datetime.utcnow()
        
        return document
    
    def _normalize_metadata(self, metadata: DocumentMetadata) -> DocumentMetadata:
        """
        Normalize document metadata fields.
        
        Args:
            metadata: Original metadata
        
        Returns:
            Normalized metadata
        """
        # Clean title
        if metadata.title:
            metadata.title = clean_metadata_field(metadata.title)
        
        # Clean authors
        if metadata.authors:
            metadata.authors = [
                clean_metadata_field(author)
                for author in metadata.authors
                if clean_metadata_field(author)  # Remove empty authors
            ]
        
        # Clean affiliations
        if metadata.affiliations:
            metadata.affiliations = [
                clean_metadata_field(affiliation)
                for affiliation in metadata.affiliations
                if clean_metadata_field(affiliation)
            ]
        
        # Clean abstract
        if metadata.abstract:
            # Abstract can have newlines, so use block text normalization
            metadata.abstract = normalize_block_text(metadata.abstract)
        
        # Clean keywords
        if metadata.keywords:
            metadata.keywords = [
                clean_metadata_field(keyword)
                for keyword in metadata.keywords
                if clean_metadata_field(keyword)
            ]
        
        # Clean journal/publisher names
        if metadata.journal:
            metadata.journal = clean_metadata_field(metadata.journal)
        
        # Clean author names
        if metadata.corresponding_author:
            metadata.corresponding_author = clean_metadata_field(metadata.corresponding_author)
        
        if metadata.email:
            metadata.email = clean_metadata_field(metadata.email)
        
        return metadata
    
    def _normalize_blocks(self, blocks: List[Block]) -> List[Block]:
        """
        Normalize text in all blocks with strict sequential logic.
        
        STRICT ORDER OF OPERATIONS (Journal Editor Mode):
        1. CLEAN text (whitespace/unicode)
        2. REPAIR corruptions (e.g. "2ethodology" -> "2 Methodology")
        3. SPLIT merged blocks (Heading merged with body text)
        4. FILTER empty blocks (Post-split)
        """
        import re
        normalized_blocks = []
        
        # Comprehensive Keyword List for Academic Sections
        keywords = [
            "Abstract", "Introduction", "Methods", "Methodology", "Materials and Methods",
            "Results", "Findings", "Discussion", "Conclusion", "Conclusions", 
            "References", "Bibliography", "Works Cited", "Background", 
            "Literature Review", "Summary", "Keywords", "Acknowledgment", "Acknowledgements",
            "Appendix", "Appendices"
        ]
        kw_regex = "(?:" + "|".join(keywords) + ")"
        
        for block in blocks:
            # 1. CLEAN
            text = normalize_block_text(block.text, is_empty_ok=True)
            
            # 2. REPAIR (Crucial to run before splitting)
            text = self._repair_common_corruptions(text)
            
            # 3. SPLIT MERGED BLOCKS
            was_split = False
            
            # Pattern A: ABSTRACT SPLIT (ABSOLUTE PRIORITY)
            # Matches "AbstractThe system..." or "Abstract: This paper..."
            abstract_match = re.match(r'^Abstract[:\.\—\-]?\s*(.+)$', text, flags=re.IGNORECASE)
            if abstract_match:
                body_text = abstract_match.group(1).strip()
                if body_text:
                    # Split into "Abstract" (Heading) and "rest of text" (Body)
                    normalized_blocks.append(block.model_copy(update={
                        "text": "Abstract",
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "abstract_split"}
                    }))
                    normalized_blocks.append(block.model_copy(update={
                        "block_id": f"{block.block_id}_body",
                        "text": body_text,
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "abstract_split"}
                    }))
                    was_split = True
            
            if was_split:
                continue

            # Pattern B: Numbered Headings + Body
            # Match "1 IntroductionScientific..." or "1 Introduction: Scientific..."
            # The [A-Z] guard ensures we are splitting at a potential sentence boundary.
            numbered_merged_match = re.match(rf'^(\d+(?:\.\d+)*\.?\s*(?:{kw_regex}|[A-Z][a-z]+))[:\.\—\-]?\s*([A-Z].+)$', text)
            if numbered_merged_match:
                heading_part = numbered_merged_match.group(1).strip()
                body_part = numbered_merged_match.group(2).strip()
                
                if len(body_part) > 20 or re.search(r'[\.\?\!]\s', body_part):
                    normalized_blocks.append(block.model_copy(update={
                        "text": heading_part,
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "numbered_split"}
                    }))
                    normalized_blocks.append(block.model_copy(update={
                        "block_id": f"{block.block_id}_body",
                        "text": body_part,
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "numbered_split"}
                    }))
                    was_split = True

            if was_split:
                continue

            # Pattern C: Keyword + Body (Non-numbered)
            keyword_merged_match = re.match(rf'^({kw_regex})([A-Z][a-z].*)$', text)
            if keyword_merged_match:
                heading_part = keyword_merged_match.group(1).strip()
                body_part = keyword_merged_match.group(2).strip()
                
                if len(body_part) > 30 or re.search(r'[\.\?\!]\s', body_part):
                    normalized_blocks.append(block.model_copy(update={
                        "text": heading_part,
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "keyword_split"}
                    }))
                    normalized_blocks.append(block.model_copy(update={
                        "block_id": f"{block.block_id}_body",
                        "text": body_part,
                        "metadata": {**block.metadata, "split_from_original": True, "split_reason": "keyword_split"}
                    }))
                    was_split = True

            if not was_split:
                # 4. FILTER EMPTY (Finally append if not empty)
                if text.strip():
                    normalized_blocks.append(block.model_copy(update={"text": text}))
        
        # SAFE EXTENSION: Duplicate Consecutive Block Filter
        # Remove identical consecutive blocks (text, style, metadata)
        final_blocks = []
        for i, b in enumerate(normalized_blocks):
            if i == 0:
                final_blocks.append(b)
                continue
            
            prev = final_blocks[-1]
            if (b.text.strip() == prev.text.strip() and 
                b.style == prev.style and 
                b.metadata == prev.metadata):
                
                if b.text.strip():
                    prev.metadata["has_consecutive_duplicate"] = True
                    prev.warnings.append(f"Standardization: Consecutive duplicate suppressed ({b.block_id})")
                    continue
            
            final_blocks.append(b)
            
        return final_blocks

    def _repair_common_corruptions(self, text: str) -> str:
        """
        Repair specific known text corruptions from parsing artifacts.
        
        STRICTLY fix: "2ethodology" -> "2 Methodology"
        """
        import re
        if not text:
            return text
            
        # Patterns for common academic headings starting with a number
        # Fixing the lowercase first letter corruption
        repairs = [
            (r'^(\d+)\s*ntroduction', r'\1 Introduction'),
            (r'^(\d+)\s*ethodology', r'\1 Methodology'),
            (r'^(\d+)\s*esults', r'\1 Results'),
            (r'^(\d+)\s*iscussion', r'\1 Discussion'),
            (r'^(\d+)\s*onclusion', r'\1 Conclusion'),
            (r'^(\d+)\s*eferences', r'\1 References'),
            (r'^(\d+)\s*bstract', r'\1 Abstract'),
        ]
        
        for pattern, replacement in repairs:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        return text
    
    def _normalize_tables(self, tables: List[Table]) -> List[Table]:
        """
        Normalize text in all tables.
        
        This normalizes:
        - Cell text
        - Caption text (if present)
        - Both cells list and rows array
        
        Args:
            tables: List of tables from parsing
        
        Returns:
            List of tables with normalized cell text
        """
        normalized_tables = []
        
        for table in tables:
            # Normalize caption if present
            caption_text = table.caption_text
            if caption_text:
                caption_text = normalize_block_text(caption_text)
            
            # Normalize cells
            normalized_cells = []
            for cell in table.cells:
                normalized_cell_text = normalize_table_cell_text(cell.text)
                # Use model_copy to preserve all cell properties
                normalized_cell = cell.model_copy(update={"text": normalized_cell_text})
                normalized_cells.append(normalized_cell)
            
            # Normalize 2D rows array
            normalized_rows = []
            for row in table.rows:
                normalized_row = [normalize_table_cell_text(cell_text) for cell_text in row]
                normalized_rows.append(normalized_row)
            
            # Create normalized table
            # Preserve all properties except the ones we're updating
            normalized_table = table.model_copy(update={
                "caption_text": caption_text,
                "cells": normalized_cells,
                "rows": normalized_rows,
            })
            
            normalized_tables.append(normalized_table)
        
        return normalized_tables


# Convenience function
def normalize_document(document: Document) -> Document:
    """
    Normalize a parsed document.
    
    This is a convenience wrapper around Normalizer.
    
    Args:
        document: Document from parsing stage
    
    Returns:
        Document with normalized text
    
    Example:
        >>> from app.pipeline.parsing import parse_docx
        >>> from app.pipeline.normalization import normalize_document
        >>> 
        >>> doc = parse_docx("manuscript.docx", "job_123")
        >>> doc = normalize_document(doc)
        >>> print("Normalized!")
    """
    normalizer = Normalizer()
    return normalizer.process(document)
