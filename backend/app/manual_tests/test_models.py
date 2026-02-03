"""
Manual test script to validate model definitions.

Run this script to verify that all models can be instantiated
and work as expected.

Usage:
    cd automated-manuscript-formatter/backend
    python -m app.manual_tests.test_models
"""

import sys
from datetime import datetime

# Import all models
from app.models import (
    Block, BlockType, TextStyle, ListType,
    Figure, FigureType, ImageFormat,
    Table, TableCell,
    Reference, ReferenceType, CitationStyle,
    Document, DocumentMetadata, TemplateInfo, ProcessingHistory
)


def test_block_model():
    """Test Block model creation and validation."""
    print("\n=== Testing Block Model ===")
    
    # Create a simple block
    block = Block(
        block_id="blk_001",
        text="This is a test paragraph.",
        index=0,
        block_type=BlockType.PARAGRAPH
    )
    
    print(f"✓ Created block: {block.block_id}")
    print(f"  Type: {block.block_type}")
    print(f"  Text: {block.text[:50]}...")
    print(f"  Is content: {block.is_content()}")
    
    # Create a heading block
    heading = Block(
        block_id="blk_002",
        text="Introduction",
        index=1,
        block_type=BlockType.HEADING_1,
        style=TextStyle(bold=True, font_size=16.0),
        level=1
    )
    
    print(f"✓ Created heading: {heading.block_id}")
    print(f"  Is heading: {heading.is_heading()}")
    print(f"  Style: bold={heading.style.bold}, size={heading.style.font_size}")
    
    return [block, heading]


def test_figure_model():
    """Test Figure model creation."""
    print("\n=== Testing Figure Model ===")
    
    figure = Figure(
        figure_id="fig_001",
        number=1,
        index=0,
        caption_text="Figure 1: System Architecture",
        label="Figure 1",
        title="System Architecture",
        image_format=ImageFormat.PNG
    )
    
    print(f"✓ Created figure: {figure.figure_id}")
    print(f"  Display label: {figure.get_display_label()}")
    print(f"  Has caption: {figure.has_caption()}")
    print(f"  Caption: {figure.caption_text}")
    
    return [figure]


def test_table_model():
    """Test Table model creation."""
    print("\n=== Testing Table Model ===")
    
    # Create table cells
    cells = [
        TableCell(row=0, col=0, text="Header 1", is_header=True),
        TableCell(row=0, col=1, text="Header 2", is_header=True),
        TableCell(row=1, col=0, text="Data 1"),
        TableCell(row=1, col=1, text="Data 2"),
    ]
    
    table = Table(
        table_id="tbl_001",
        number=1,
        index=0,
        num_rows=2,
        num_cols=2,
        cells=cells,
        rows=[["Header 1", "Header 2"], ["Data 1", "Data 2"]],
        has_header_row=True,
        caption_text="Table 1: Experimental Results"
    )
    
    print(f"✓ Created table: {table.table_id}")
    print(f"  Display label: {table.get_display_label()}")
    print(f"  Dimensions: {table.num_rows}x{table.num_cols}")
    print(f"  Has header: {table.has_header_row}")
    print(f"  First row: {table.get_row_data(0)}")
    
    return [table]


def test_reference_model():
    """Test Reference model creation."""
    print("\n=== Testing Reference Model ===")
    
    reference = Reference(
        reference_id="ref_001",
        number=1,
        citation_key="Smith2020",
        raw_text="Smith, J. (2020). Machine Learning Fundamentals. IEEE Press.",
        index=0,
        reference_type=ReferenceType.BOOK,
        authors=["Smith, J."],
        title="Machine Learning Fundamentals",
        publisher="IEEE Press",
        year=2020
    )
    
    print(f"✓ Created reference: {reference.reference_id}")
    print(f"  Citation key: {reference.get_short_citation()}")
    print(f"  Primary author: {reference.get_primary_author()}")
    print(f"  Author list: {reference.get_author_list()}")
    print(f"  Type: {reference.reference_type}")
    
    return [reference]


def test_document_model():
    """Test Document model with all components."""
    print("\n=== Testing Document Model ===")
    
    # Create components
    blocks = test_block_model()
    figures = test_figure_model()
    tables = test_table_model()
    references = test_reference_model()
    
    # Create document metadata
    metadata = DocumentMetadata(
        title="Test Academic Paper",
        authors=["John Doe", "Jane Smith"],
        affiliations=["University A", "University B"],
        abstract="This is a test abstract.",
        keywords=["machine learning", "natural language processing"]
    )
    
    # Create template info
    template = TemplateInfo(
        template_name="ieee",
        template_version="2023"
    )
    
    # Create document
    document = Document(
        document_id="doc_001",
        original_filename="test_paper.docx",
        blocks=blocks,
        figures=figures,
        tables=tables,
        references=references,
        metadata=metadata,
        template=template
    )
    
    print(f"\n✓ Created document: {document.document_id}")
    print(f"  Title: {document.metadata.title}")
    print(f"  Authors: {', '.join(document.metadata.authors)}")
    print(f"  Template: {document.template.template_name}")
    
    # Test utility methods
    print(f"\n  Statistics:")
    stats = document.get_stats()
    for key, value in stats.items():
        print(f"    {key}: {value}")
    
    # Test lookup methods
    block = document.get_block_by_id("blk_001")
    print(f"\n  Lookup block 'blk_001': {block.text if block else 'Not found'}")
    
    figure = document.get_figure_by_id("fig_001")
    print(f"  Lookup figure 'fig_001': {figure.caption_text if figure else 'Not found'}")
    
    # Test adding processing history
    document.add_processing_stage(
        stage_name="parsing",
        status="success",
        message="Parsed 2 blocks",
        duration_ms=150
    )
    
    print(f"\n  Processing history: {len(document.processing_history)} stages")
    for entry in document.processing_history:
        print(f"    - {entry.stage_name}: {entry.status}")
    
    return document


def test_json_serialization():
    """Test that all models can be serialized to JSON."""
    print("\n=== Testing JSON Serialization ===")
    
    # Create a simple document
    block = Block(
        block_id="blk_test",
        text="Test",
        index=0
    )
    
    doc = Document(
        document_id="doc_test",
        blocks=[block]
    )
    
    # Serialize to JSON
    json_data = doc.model_dump_json(indent=2)
    print(f"✓ JSON serialization successful")
    print(f"  JSON length: {len(json_data)} characters")
    
    # Deserialize from JSON
    doc_restored = Document.model_validate_json(json_data)
    print(f"✓ JSON deserialization successful")
    print(f"  Restored document ID: {doc_restored.document_id}")
    print(f"  Restored blocks: {len(doc_restored.blocks)}")
    
    return True


def main():
    """Run all model tests."""
    print("=" * 60)
    print("DOCUMENT MODELS VALIDATION TEST")
    print("=" * 60)
    
    try:
        # Test individual models
        test_block_model()
        test_figure_model()
        test_table_model()
        test_reference_model()
        
        # Test complete document
        document = test_document_model()
        
        # Test serialization
        test_json_serialization()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nAll models are correctly defined and functional.")
        print("Models are ready for use in the pipeline.")
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ TESTS FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
