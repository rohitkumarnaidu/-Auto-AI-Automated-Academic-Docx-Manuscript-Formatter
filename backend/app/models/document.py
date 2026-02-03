"""
Document Model - Top-level container for all document components.

This is the canonical data structure that flows through the entire pipeline.
Each pipeline stage takes a Document as input and returns an enriched Document.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from .block import Block
from .figure import Figure
from .table import Table
from .reference import Reference


class DocumentMetadata(BaseModel):
    """Document-level metadata."""
    
    # Core metadata
    title: Optional[str] = Field(
        default=None,
        description="Document title"
    )
    authors: List[str] = Field(
        default_factory=list,
        description="List of author names"
    )
    affiliations: List[str] = Field(
        default_factory=list,
        description="List of author affiliations"
    )
    abstract: Optional[str] = Field(
        default=None,
        description="Document abstract"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="List of keywords"
    )
    
    # Publication metadata
    publication_date: Optional[datetime] = Field(
        default=None,
        description="Publication date"
    )
    journal: Optional[str] = Field(
        default=None,
        description="Target journal/conference name"
    )
    doi: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier"
    )
    
    # Correspondence
    corresponding_author: Optional[str] = Field(
        default=None,
        description="Corresponding author name"
    )
    email: Optional[str] = Field(
        default=None,
        description="Corresponding author email"
    )
    
    # Extensibility
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata fields"
    )


class TemplateInfo(BaseModel):
    """Information about the target formatting template."""
    
    template_name: str = Field(
        ...,
        description="Template identifier (e.g., 'ieee', 'springer', 'apa')"
    )
    template_version: Optional[str] = Field(
        default=None,
        description="Template version"
    )
    template_path: Optional[str] = Field(
        default=None,
        description="Path to template.docx file"
    )
    contract_path: Optional[str] = Field(
        default=None,
        description="Path to contract.yaml file"
    )


class ProcessingHistory(BaseModel):
    """Track processing history through pipeline stages."""
    
    stage_name: str = Field(..., description="Pipeline stage name")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this stage was executed"
    )
    status: str = Field(..., description="Status (success, warning, error)")
    message: Optional[str] = Field(
        default=None,
        description="Status message or error details"
    )
    duration_ms: Optional[int] = Field(
        default=None,
        description="Processing duration in milliseconds"
    )


class Document(BaseModel):
    """
    Top-level document container.
    
    This is the central data structure that flows through the entire pipeline.
    Each stage enriches the document by:
    - Adding metadata to blocks
    - Extracting figures/tables
    - Parsing references
    - Applying formatting
    
    IMPORTANT: Pipeline stages must NEVER drop content.
    All blocks, figures, tables, and references must be preserved.
    """
    
    # Unique identifier
    document_id: str = Field(
        ...,
        description="Unique document identifier (e.g., job ID)"
    )
    
    # Original file information
    original_filename: Optional[str] = Field(
        default=None,
        description="Original uploaded filename"
    )
    source_path: Optional[str] = Field(
        default=None,
        description="Path to source .docx file"
    )
    
    # Document content (populated and enriched by pipeline stages)
    blocks: List[Block] = Field(
        default_factory=list,
        description="All text blocks in sequential order"
    )
    figures: List[Figure] = Field(
        default_factory=list,
        description="All figures extracted from document"
    )
    tables: List[Table] = Field(
        default_factory=list,
        description="All tables extracted from document"
    )
    references: List[Reference] = Field(
        default_factory=list,
        description="All bibliographic references"
    )
    
    # Document metadata (extracted by parser and structure_detection)
    metadata: DocumentMetadata = Field(
        default_factory=DocumentMetadata,
        description="Document-level metadata"
    )
    
    # Template and formatting
    template: Optional[TemplateInfo] = Field(
        default=None,
        description="Target template information"
    )
    
    # Processing tracking
    processing_history: List[ProcessingHistory] = Field(
        default_factory=list,
        description="History of pipeline stages applied"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this document object was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this document was last updated"
    )
    
    # Validation status
    is_valid: bool = Field(
        default=True,
        description="Overall document validation status"
    )
    validation_errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="List of validation warnings"
    )
    
    # Export information (populated by export stage)
    output_path: Optional[str] = Field(
        default=None,
        description="Path to formatted output .docx file"
    )
    
    # Extensibility
    custom_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom data for specific pipeline stages"
    )
    
    class Config:
        use_enum_values = True
    
    # --- Utility methods ---
    
    def get_block_by_id(self, block_id: str) -> Optional[Block]:
        """Get block by its ID."""
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        return None
    
    def get_figure_by_id(self, figure_id: str) -> Optional[Figure]:
        """Get figure by its ID."""
        for figure in self.figures:
            if figure.figure_id == figure_id:
                return figure
        return None
    
    def get_table_by_id(self, table_id: str) -> Optional[Table]:
        """Get table by its ID."""
        for table in self.tables:
            if table.table_id == table_id:
                return table
        return None
    
    def get_reference_by_id(self, reference_id: str) -> Optional[Reference]:
        """Get reference by its ID."""
        for reference in self.references:
            if reference.reference_id == reference_id:
                return reference
        return None
    
    def get_reference_by_citation_key(self, citation_key: str) -> Optional[Reference]:
        """Get reference by citation key."""
        for reference in self.references:
            if reference.citation_key == citation_key:
                return reference
        return None
    
    def get_blocks_by_type(self, block_type: str) -> List[Block]:
        """Get all blocks of a specific type."""
        return [b for b in self.blocks if b.block_type == block_type]
    
    def get_blocks_in_section(self, section_name: str) -> List[Block]:
        """Get all blocks in a specific section."""
        return [b for b in self.blocks if b.section_name == section_name]
    
    def add_processing_stage(
        self,
        stage_name: str,
        status: str = "success",
        message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Add a processing stage to the history.
        
        Args:
            stage_name: Name of the pipeline stage
            status: Status (success, warning, error)
            message: Optional status message
            duration_ms: Processing duration in milliseconds
        """
        history_entry = ProcessingHistory(
            stage_name=stage_name,
            status=status,
            message=message,
            duration_ms=duration_ms
        )
        self.processing_history.append(history_entry)
        self.updated_at = datetime.utcnow()
    
    def get_section_names(self) -> List[str]:
        """Get list of all unique section names in the document."""
        sections = set()
        for block in self.blocks:
            if block.section_name:
                sections.add(block.section_name)
        return sorted(list(sections))
    
    def count_words(self) -> int:
        """Count total words in all text blocks."""
        total_words = 0
        for block in self.blocks:
            total_words += len(block.text.split())
        return total_words
    
    def get_stats(self) -> Dict[str, int]:
        """Get document statistics."""
        return {
            "total_blocks": len(self.blocks),
            "total_figures": len(self.figures),
            "total_tables": len(self.tables),
            "total_references": len(self.references),
            "total_words": self.count_words(),
            "sections": len(self.get_section_names()),
        }
