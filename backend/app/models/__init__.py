"""
Models package - Canonical data structures for the document pipeline.

All models are Pydantic-based for validation and serialization.
Each pipeline stage takes a Document as input and returns an enriched Document.
"""

from .block import Block, BlockType, ListType, TextStyle
from .figure import Figure, FigureType, ImageFormat
from .table import Table, TableCell
from .reference import Reference, ReferenceType, CitationStyle
from .document import (
    Document,
    DocumentMetadata,
    TemplateInfo,
    ProcessingHistory,
)

__all__ = [
    # Block models
    "Block",
    "BlockType",
    "ListType",
    "TextStyle",
    # Figure models
    "Figure",
    "FigureType",
    "ImageFormat",
    # Table models
    "Table",
    "TableCell",
    # Reference models
    "Reference",
    "ReferenceType",
    "CitationStyle",
    # Document models
    "Document",
    "DocumentMetadata",
    "TemplateInfo",
    "ProcessingHistory",
]
