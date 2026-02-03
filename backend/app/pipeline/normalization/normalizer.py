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

from app.models import Document, Block, Table, DocumentMetadata
from app.utils.text_utils import (
    normalize_block_text,
    normalize_table_cell_text,
    clean_metadata_field,
)


class Normalizer:
    """
    Normalizes text content in a Document model.
    
    This stage cleans text without interpreting semantic meaning.
    Structure detection and classification happen in later stages.
    """
    
    def __init__(self):
        """Initialize the normalizer."""
        pass
    
    def normalize(self, document: Document) -> Document:
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
        Normalize text in all blocks.
        
        IMPORTANT: This preserves:
        - Block IDs
        - Block positions (index)
        - Block types (UNKNOWN)
        - Block order
        - All metadata
        
        Args:
            blocks: List of blocks from parsing
        
        Returns:
            List of blocks with normalized text
        """
        normalized_blocks = []
        
        for block in blocks:
            # Normalize the text content
            # Allow empty blocks (they might indicate structure)
            normalized_text = normalize_block_text(block.text, is_empty_ok=True)
            
            # Create a new block with normalized text
            # Using model_copy to preserve all other fields
            normalized_block = block.model_copy(update={"text": normalized_text})
            
            normalized_blocks.append(normalized_block)
        
        return normalized_blocks
    
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
    return normalizer.normalize(document)
