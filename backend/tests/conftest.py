"""
conftest.py — shared pytest fixtures for ScholarForm AI backend tests.
"""
from __future__ import annotations

import pytest

from app.models import (
    Block,
    BlockType,
    DocumentMetadata,
    PipelineDocument,
    Reference,
    ReferenceType,
)


# ── Document fixtures ──────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_doc() -> PipelineDocument:
    """Bare-minimum PipelineDocument with title + one body block."""
    doc = PipelineDocument(
        document_id="test-doc-001",
        metadata=DocumentMetadata(
            title="Test Manuscript",
            authors=["Jane Doe"],
            abstract="A short abstract.",
        ),
    )
    doc.blocks = [
        Block(block_id="b1", index=1, block_type=BlockType.TITLE,  text="Test Manuscript"),
        Block(block_id="b2", index=2, block_type=BlockType.HEADING_1, text="Introduction"),
        Block(block_id="b3", index=3, block_type=BlockType.BODY,   text="Body content here."),
    ]
    return doc


@pytest.fixture()
def full_doc(minimal_doc: PipelineDocument) -> PipelineDocument:
    """PipelineDocument with metadata, blocks, and a reference."""
    minimal_doc.metadata.keywords = ["formatting", "test"]
    minimal_doc.metadata.affiliations = ["Test University"]
    ref = Reference(
        reference_id="ref_1",
        citation_key="ref1",
        raw_text="[1] J. Doe, Testing, 2024.",
        reference_type=ReferenceType.JOURNAL_ARTICLE,
        authors=["Doe, J."],
        title="Testing",
        year=2024,
        index=0,
        formatted_text="[1] J. Doe, 'Testing,' 2024.",
    )
    minimal_doc.references = [ref]
    minimal_doc.blocks.append(
        Block(block_id="b4", index=4, block_type=BlockType.REFERENCE_ENTRY, text="[1] J. Doe, Testing, 2024.")
    )
    return minimal_doc
