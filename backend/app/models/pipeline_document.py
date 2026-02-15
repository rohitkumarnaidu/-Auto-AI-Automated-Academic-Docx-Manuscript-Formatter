from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.block import Block
from app.models.figure import Figure
from app.models.table import Table
from app.models.reference import Reference
from app.models.equation import Equation
from app.models.review import ReviewStatus, ReviewMetadata



class DocumentMetadata(BaseModel):
    """Metadata extracted from the document or provided by the user."""
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    affiliations: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    corresponding_author: Optional[str] = None
    email: Optional[str] = None
    ai_hints: Dict[str, Any] = Field(default_factory=dict)

class TemplateInfo(BaseModel):
    """Information about the scientific template used for formatting."""
    template_name: str
    template_version: Optional[str] = "1.0"

class ProcessingStage(BaseModel):
    """Record of a single processing stage in the pipeline."""
    stage_name: str
    status: str
    message: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PipelineDocument(BaseModel):
    """
    Internal document model used throughout the pipeline.
    This is NOT the database model. It holds the full structured content.
    """
    document_id: str
    original_filename: Optional[str] = None
    source_path: Optional[str] = None
    
    # Content components
    blocks: List[Block] = Field(default_factory=list)
    figures: List[Figure] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    equations: List[Equation] = Field(default_factory=list)
    
    # Metadata
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    template: Optional[TemplateInfo] = None
    
    # Formatting Options
    formatting_options: Dict[str, Any] = Field(default_factory=dict)
    
    # Validation results
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    
    # HITL Signals
    review: Optional[ReviewMetadata] = Field(default=None)
    
    # Runtime/Persistence fields
    output_path: Optional[str] = None
    generated_doc: Optional[Any] = Field(None, exclude=True) # Transient field for Word object
    
    # Execution history
    processing_history: List[ProcessingStage] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_processing_stage(self, stage_name: str, status: str, message: Optional[str] = None, duration_ms: Optional[int] = None):
        """Helper to add a stage to history."""
        stage = ProcessingStage(
            stage_name=stage_name,
            status=status,
            message=message,
            duration_ms=duration_ms
        )
        self.processing_history.append(stage)
        self.updated_at = datetime.utcnow()

    def get_block_by_id(self, block_id: str) -> Optional[Block]:
        """Find a block by its ID."""
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        return None

    def get_figure_by_id(self, figure_id: str) -> Optional[Figure]:
        """Find a figure by its ID."""
        for figure in self.figures:
            if figure.figure_id == figure_id:
                return figure
        return None

    def get_equation_by_id(self, equation_id: str) -> Optional[Equation]:
        """Find an equation by its ID."""
        for eqn in self.equations:
            if eqn.equation_id == equation_id:
                return eqn
        return None

    def get_blocks_by_type(self, block_type: str) -> List[Block]:
        """Find blocks by their semantic type."""
        return [b for b in self.blocks if b.block_type == block_type]

    def get_blocks_in_section(self, section_name: str) -> List[Block]:
        """Find blocks belonging to a specific section."""
        return [b for b in self.blocks if b.section_name and section_name.lower() in b.section_name.lower()]

    def get_section_names(self) -> List[str]:
        """Get unique section names present in the document."""
        return list(set(b.section_name for b in self.blocks if b.section_name))

    def get_stats(self) -> Dict[str, int]:
        """Get counts of components."""
        return {
            "blocks": len(self.blocks),
            "figures": len(self.figures),
            "tables": len(self.tables),
            "references": len(self.references),
            "equations": len(self.equations),
            "stages": len(self.processing_history)
        }
