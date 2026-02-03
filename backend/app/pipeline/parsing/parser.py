"""
DOCX Parser - Extract raw content from DOCX documents.

This is the first stage of the pipeline. It reads a DOCX file and extracts:
- Paragraphs with text and style information
- Tables with cell structure
- Images/figures with binary data

Output: Document model with all raw content preserved in original order.

IMPORTANT:
- All blocks are marked as BlockType.UNKNOWN (classification happens later)
- No normalization, structure detection, or formatting
- Never drop content silently
- Preserve exact order from source document
"""

import io
import os
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from docx import Document as DocxDocument
from docx.document import Document as DocxDocumentType
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.shape import InlineShape

from app.models import (
    Document,
    DocumentMetadata,
    Block,
    BlockType,
    TextStyle,
    Figure,
    ImageFormat,
    Table,
    TableCell,
)
from app.utils.id_generator import generate_block_id, generate_figure_id, generate_table_id


class DocxParser:
    """
    Parses DOCX files into Document model instances.
    
    This parser extracts raw content without interpreting semantic meaning.
    Structure detection and classification happen in later pipeline stages.
    """
    
    def __init__(self):
        """Initialize the parser."""
        self.block_counter = 0
        self.figure_counter = 0
        self.table_counter = 0
        self.current_page = None  # DOCX doesn't provide reliable page numbers
    
    def parse(self, docx_path: str, document_id: str) -> Document:
        """
        Parse a DOCX file into a Document model.
        
        Args:
            docx_path: Path to the .docx file
            document_id: Unique identifier for this document (e.g., job ID)
        
        Returns:
            Document instance with all extracted content
        
        Raises:
            FileNotFoundError: If DOCX file doesn't exist
            ValueError: If file is not a valid DOCX
        """
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        # Reset counters for this parse
        self.block_counter = 0
        self.figure_counter = 0
        self.table_counter = 0
        
        # Open DOCX document
        try:
            docx = DocxDocument(docx_path)
        except Exception as e:
            raise ValueError(f"Failed to open DOCX file: {e}")
        
        # Initialize document
        document = Document(
            document_id=document_id,
            original_filename=Path(docx_path).name,
            source_path=docx_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Extract core properties
        document.metadata = self._extract_core_properties(docx)
        
        # Extract document content in order
        # DOCX structure: paragraphs and tables are interspersed
        blocks, figures, tables = self._extract_body_content(docx)
        
        document.blocks = blocks
        document.figures = figures
        document.tables = tables
        
        # Add processing history
        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=f"Parsed {len(blocks)} blocks, {len(figures)} figures, {len(tables)} tables"
        )
        
        return document
    
    def _extract_core_properties(self, docx: DocxDocumentType) -> DocumentMetadata:
        """
        Extract document metadata from DOCX core properties.
        
        Args:
            docx: python-docx Document object
        
        Returns:
            DocumentMetadata instance
        """
        core_props = docx.core_properties
        
        metadata = DocumentMetadata()
        
        # Extract available metadata
        if core_props.title:
            metadata.title = core_props.title
        
        if core_props.author:
            # Author may be a single string or semicolon-separated
            authors = [a.strip() for a in core_props.author.split(';')]
            metadata.authors = authors
        
        if core_props.subject:
            metadata.abstract = core_props.subject
        
        if core_props.keywords:
            # Keywords are usually comma or semicolon separated
            keywords = [k.strip() for k in core_props.keywords.replace(';', ',').split(',')]
            metadata.keywords = [k for k in keywords if k]
        
        if core_props.created:
            metadata.publication_date = core_props.created
        
        return metadata
    
    def _extract_body_content(
        self, docx: DocxDocumentType
    ) -> Tuple[List[Block], List[Figure], List[Table]]:
        """
        Extract all content from document body in original order.
        
        DOCX documents contain a mix of paragraphs and tables.
        We need to preserve their original sequential order.
        
        Args:
            docx: python-docx Document object
        
        Returns:
            Tuple of (blocks, figures, tables)
        """
        blocks: List[Block] = []
        figures: List[Figure] = []
        tables: List[Table] = []
        
        # Iterate through body elements in order
        # This preserves the exact sequence of content
        for element in docx.element.body:
            if isinstance(element, CT_P):
                # Paragraph element
                paragraph = DocxParagraph(element, docx)
                
                # Extract text block
                block = self._extract_paragraph(paragraph)
                if block:  # Only add if not None (skip certain empties)
                    blocks.append(block)
                
                # Check for inline images
                inline_figures = self._extract_inline_images(paragraph)
                
                # Attach block index to figures for proximity matching
                if block:
                    for figure in inline_figures:
                        figure.metadata["block_index"] = block.index
                
                figures.extend(inline_figures)
            
            elif isinstance(element, CT_Tbl):
                # Table element
                table = DocxTable(element, docx)
                extracted_table = self._extract_table(table)
                tables.append(extracted_table)
        
        return blocks, figures, tables
    
    def _extract_paragraph(self, paragraph: DocxParagraph) -> Optional[Block]:
        """
        Extract a paragraph as a Block.
        
        Args:
            paragraph: python-docx Paragraph object
        
        Returns:
            Block instance or None if paragraph should be skipped
        """
        # Get text content
        text = paragraph.text
        
        # Edge case: completely empty paragraphs
        # We preserve them as they might indicate spacing/structure
        # but mark them with empty text
        
        # Extract style information
        style = self._extract_paragraph_style(paragraph)
        
        # Generate unique ID
        block_id = generate_block_id(self.block_counter)
        self.block_counter += 1
        
        # Create block
        # Note: block_type is UNKNOWN - classification happens later
        block = Block(
            block_id=block_id,
            text=text,
            index=self.block_counter - 1,
            block_type=BlockType.UNKNOWN,
            style=style,
            page_number=None,  # DOCX doesn't provide direct page numbers
        )
        
        # Store paragraph style name in metadata for later structure detection
        if paragraph.style and paragraph.style.name:
            block.metadata["style_name"] = paragraph.style.name
        
        # Store alignment
        if paragraph.alignment is not None:
            block.metadata["alignment"] = str(paragraph.alignment)
        
        return block
    
    def _extract_paragraph_style(self, paragraph: DocxParagraph) -> TextStyle:
        """
        Extract text style from paragraph.
        
        For paragraphs with mixed formatting (runs), we extract the style
        of the first non-empty run as a representative sample.
        
        Args:
            paragraph: python-docx Paragraph object
        
        Returns:
            TextStyle instance
        """
        # Default style
        bold = False
        italic = False
        underline = False
        font_name = None
        font_size = None
        
        # Check runs for formatting
        # Edge case: paragraph may have multiple runs with different styles
        # We take the first run with actual content as representative
        for run in paragraph.runs:
            if run.text.strip():  # First non-empty run
                if run.bold is not None:
                    bold = run.bold
                if run.italic is not None:
                    italic = run.italic
                if run.underline is not None:
                    underline = True
                if run.font.name:
                    font_name = run.font.name
                if run.font.size:
                    font_size = run.font.size.pt  # Convert to points
                break
        
        # Alternative: check paragraph-level formatting if no runs
        if not paragraph.runs and paragraph.style:
            try:
                if paragraph.style.font.bold:
                    bold = True
                if paragraph.style.font.italic:
                    italic = True
                if paragraph.style.font.name:
                    font_name = paragraph.style.font.name
                if paragraph.style.font.size:
                    font_size = paragraph.style.font.size.pt
            except AttributeError:
                pass  # Style doesn't have font properties
        
        return TextStyle(
            bold=bold,
            italic=italic,
            underline=underline,
            font_name=font_name,
            font_size=font_size
        )
    
    def _extract_inline_images(self, paragraph: DocxParagraph) -> List[Figure]:
        """
        Extract inline images from a paragraph.
        
        Images in DOCX can be embedded inline within paragraphs.
        
        Args:
            paragraph: python-docx Paragraph object
        
        Returns:
            List of Figure instances
        """
        figures = []
        
        for run in paragraph.runs:
            # Check for inline shapes (images)
            if hasattr(run, '_element'):
                for drawing in run._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'):
                    # Found an image
                    try:
                        # Get image part
                        inline_shapes = run._element.findall(
                            './/{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'
                        )
                        
                        for inline in inline_shapes:
                            figure = self._extract_image_from_inline(inline, run._part)
                            if figure:
                                figures.append(figure)
                    except Exception as e:
                        # If image extraction fails, log but continue
                        # Don't let image errors stop paragraph processing
                        print(f"Warning: Failed to extract inline image: {e}")
        
        return figures
    
    def _extract_image_from_inline(self, inline_element, part) -> Optional[Figure]:
        """
        Extract image data from inline shape element.
        
        Args:
            inline_element: XML element for inline shape
            part: Document part containing image relationships
        
        Returns:
            Figure instance or None if extraction fails
        """
        try:
            # Find the image reference
            blip = inline_element.find(
                './/{http://schemas.openxmlformats.org/drawingml/2006/main}blip'
            )
            
            if blip is None:
                return None
            
            # Get relationship ID
            embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            
            if not embed_id:
                return None
            
            # Get image part from relationship
            image_part = part.related_parts[embed_id]
            image_data = image_part.blob
            
            # Determine image format from content type
            content_type = image_part.content_type
            image_format = self._get_image_format(content_type)
            
            # Get dimensions if available
            extent = inline_element.find(
                './/{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent'
            )
            width = None
            height = None
            if extent is not None:
                # EMUs (English Metric Units) - convert to pixels (approx)
                cx = extent.get('cx')
                cy = extent.get('cy')
                if cx:
                    width = int(cx) / 9525  # EMU to pixels (approx)
                if cy:
                    height = int(cy) / 9525
            
            # Create figure
            figure_id = generate_figure_id(self.figure_counter)
            self.figure_counter += 1
            
            figure = Figure(
                figure_id=figure_id,
                index=self.figure_counter - 1,
                image_data=image_data,
                image_format=image_format,
                width=width,
                height=height
            )
            
            return figure
        
        except Exception as e:
            print(f"Warning: Failed to extract image: {e}")
            return None
    
    def _get_image_format(self, content_type: str) -> ImageFormat:
        """
        Map MIME content type to ImageFormat enum.
        
        Args:
            content_type: MIME type (e.g., 'image/png')
        
        Returns:
            ImageFormat enum value
        """
        format_map = {
            'image/png': ImageFormat.PNG,
            'image/jpeg': ImageFormat.JPEG,
            'image/jpg': ImageFormat.JPG,
            'image/gif': ImageFormat.GIF,
            'image/bmp': ImageFormat.BMP,
            'image/tiff': ImageFormat.TIFF,
            'image/svg+xml': ImageFormat.SVG,
            'image/x-emf': ImageFormat.EMF,
            'image/x-wmf': ImageFormat.WMF,
        }
        
        return format_map.get(content_type, ImageFormat.UNKNOWN)
    
    def _extract_table(self, table: DocxTable) -> Table:
        """
        Extract a table with full cell structure.
        
        Args:
            table: python-docx Table object
        
        Returns:
            Table instance
        """
        # Generate unique ID
        table_id = generate_table_id(self.table_counter)
        self.table_counter += 1
        
        # Get table dimensions
        num_rows = len(table.rows)
        num_cols = len(table.columns) if table.columns else 0
        
        # Extract cells
        cells: List[TableCell] = []
        rows_data: List[List[str]] = []
        
        for row_idx, row in enumerate(table.rows):
            row_data = []
            for col_idx, cell in enumerate(row.cells):
                # Get cell text
                cell_text = cell.text.strip()
                
                # Create TableCell
                table_cell = TableCell(
                    row=row_idx,
                    col=col_idx,
                    text=cell_text,
                    # Note: python-docx doesn't easily expose rowspan/colspan
                    # These would need more complex XML parsing if needed
                    rowspan=1,
                    colspan=1,
                    # Check if this looks like a header (first row, bold text)
                    is_header=(row_idx == 0),
                    bold=self._is_cell_bold(cell)
                )
                
                cells.append(table_cell)
                row_data.append(cell_text)
            
            rows_data.append(row_data)
        
        # Create Table model
        extracted_table = Table(
            table_id=table_id,
            index=self.table_counter - 1,
            num_rows=num_rows,
            num_cols=num_cols,
            cells=cells,
            rows=rows_data,
            has_header_row=(num_rows > 0),  # Assume first row is header if table exists
            header_rows=1 if num_rows > 0 else 0
        )
        
        return extracted_table
    
    def _is_cell_bold(self, cell) -> bool:
        """
        Check if cell text is predominantly bold.
        
        Args:
            cell: python-docx Cell object
        
        Returns:
            True if cell appears to be bold
        """
        # Check paragraphs in cell
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                if run.bold:
                    return True
        return False


# Convenience function
def parse_docx(docx_path: str, document_id: str) -> Document:
    """
    Parse a DOCX file into a Document model.
    
    This is a convenience wrapper around DocxParser.
    
    Args:
        docx_path: Path to the .docx file
        document_id: Unique identifier for this document
    
    Returns:
        Document instance with extracted content
    
    Example:
        >>> doc = parse_docx("manuscript.docx", "job_123")
        >>> print(f"Extracted {len(doc.blocks)} blocks")
    """
    parser = DocxParser()
    return parser.parse(docx_path, document_id)
