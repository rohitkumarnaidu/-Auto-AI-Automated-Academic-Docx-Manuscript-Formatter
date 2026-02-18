"""
PDF Parser - Extract content from PDF files.

Uses PyMuPDF (fitz) to extract text, images, and basic structure from PDF documents.
Converts to internal Document model for processing through the pipeline.
"""

import logging
import os
from typing import List, Tuple

logger = logging.getLogger(__name__)
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from app.pipeline.parsing.base_parser import BaseParser
from app.models import (
    PipelineDocument as Document,
    DocumentMetadata,
    Block,
    BlockType,
    TextStyle,
    Figure,
    ImageFormat,
)
from app.utils.id_generator import generate_block_id, generate_figure_id


class PdfParser(BaseParser):
    """Parses PDF files into Document model instances."""
    
    def __init__(self):
        """Initialize the PDF parser."""
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for PDF parsing. Install with: pip install PyMuPDF"
            )
        self.block_counter = 0
        self.figure_counter = 0
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if this parser supports PDF format."""
        return file_extension.lower() == '.pdf'
    
    def parse(self, file_path: str, document_id: str) -> Document:
        """
        Parse a PDF file into a Document model.
        
        Args:
            file_path: Path to the .pdf file
            document_id: Unique identifier for this document
        
        Returns:
            Document instance with all extracted content
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Reset counters
        self.block_counter = 0
        self.figure_counter = 0
        
        # Open PDF document
        try:
            pdf_doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF file: {e}")
        
        # Convert document_id to string if needed
        if not isinstance(document_id, str):
            document_id = str(document_id)
        
        # Initialize document
        document = Document(
            document_id=document_id,
            original_filename=Path(file_path).name,
            source_path=file_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Extract metadata
        document.metadata = self._extract_metadata(pdf_doc)
        
        # Extract content
        blocks, figures = self._extract_content(pdf_doc)
        
        document.blocks = blocks
        document.figures = figures
        
        # Add processing history
        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=f"Parsed PDF: {len(blocks)} blocks, {len(figures)} figures from {len(pdf_doc)} pages"
        )
        
        pdf_doc.close()
        return document
    
    def _extract_metadata(self, pdf_doc) -> DocumentMetadata:
        """Extract metadata from PDF document."""
        metadata = DocumentMetadata()
        
        pdf_metadata = pdf_doc.metadata
        if pdf_metadata:
            if pdf_metadata.get('title'):
                metadata.title = pdf_metadata['title']
            if pdf_metadata.get('author'):
                metadata.authors = [pdf_metadata['author']]
            if pdf_metadata.get('subject'):
                metadata.abstract = pdf_metadata['subject']
            if pdf_metadata.get('keywords'):
                keywords_raw = pdf_metadata.get('keywords', '')
                metadata.keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
        
        return metadata

    def _calculate_font_stats(self, pdf_doc) -> float:
        """
        Calculate the most frequent font size (body text size) in the document.
        
        Returns:
            float: The body text font size (default 11.0 if detection fails)
        """
        font_sizes = {}
        
        # Scan a subset of pages (up to 5) to estimate font statistics
        # Scanning all pages might be too slow for large docs
        pages_to_scan = min(5, len(pdf_doc))
        
        for i in range(pages_to_scan):
            try:
                page = pdf_doc[i]
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                size = round(span.get("size", 0), 1)
                                if size > 0:
                                    font_sizes[size] = font_sizes.get(size, 0) + len(span.get("text", ""))
            except Exception:
                continue
                
        if not font_sizes:
            return 11.0
            
        # Return the font size with the most characters (weighted mode)
        body_size = max(font_sizes.items(), key=lambda x: x[1])[0]
        return body_size

    def _is_header_footer(self, block_bbox: list, page_rect: list) -> bool:
        """
        Check if a block is likely a header or footer based on position.
        """
        if not block_bbox or not page_rect:
            return False
            
        page_height = page_rect[3] - page_rect[1]
        if page_height <= 0: return False
        
        y0, y1 = block_bbox[1], block_bbox[3]
        
        # Thresholds: Top 7% or Bottom 7%
        top_threshold = page_rect[1] + (page_height * 0.07)
        bottom_threshold = page_rect[3] - (page_height * 0.07)
        
        # If block is strictly within top or bottom margins
        is_top = y1 <= top_threshold
        is_bottom = y0 >= bottom_threshold
        
        return is_top or is_bottom

    def _extract_content(self, pdf_doc) -> Tuple[List[Block], List[Figure]]:
        """Extract text blocks, tables, and images from PDF."""
        blocks = []
        figures = []
        
        # 0. Content Analysis (Dynamic Font Sizing)
        # ------------------------------------------------
        body_font_size = self._calculate_font_stats(pdf_doc)
        
        # Define adaptive thresholds
        h1_threshold = body_font_size * 1.6     # e.g., 11 * 1.6 = 17.6
        h2_threshold = body_font_size * 1.3     # e.g., 11 * 1.3 = 14.3
        h3_threshold = body_font_size * 1.1     # e.g., 11 * 1.1 = 12.1 (+ bold usually)
        
        logger.debug(
            "PDF Analysis: Body Size=%.1fpt, H1>%.1fpt, H2>%.1fpt",
            body_font_size, h1_threshold, h2_threshold,
        )
        
        for page_num, page in enumerate(pdf_doc):
            # 1. Extract Tables first (PyMuPDF find_tables)
            # ------------------------------------------------
            table_rects = []
            try:
                tables = page.find_tables()
                for table in tables:
                    # Get table bounding box to exclude raw text later
                    table_rects.append(table.bbox)
                    
                    # Extract table content as list of lists
                    header = table.header
                    rows = table.extract()
                    
                    # Convert to Markdown-like table text
                    table_lines = []
                    if header:
                        table_lines.append(" | ".join([str(h) if h else "" for h in header]))
                        table_lines.append(" | ".join(["---"] * len(header)))
                    
                    for row in rows:
                        # Clean cell content (remove newlines within cells)
                        cleaned_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        table_lines.append(" | ".join(cleaned_row))
                        
                    if table_lines:
                        block_id = generate_block_id(self.block_counter)
                        self.block_counter += 1
                        
                        block = Block(
                            block_id=block_id,
                            text="\n".join(table_lines),
                            index=self.block_counter * 100,
                            block_type=BlockType.UNKNOWN,
                            style=TextStyle(),
                            page_number=page_num + 1
                        )
                        block.metadata["is_table"] = True
                        blocks.append(block)
            except Exception as exc:
                logger.warning("PDF table extraction failed on page %d: %s", page_num + 1, exc)

            # 2. Extract Text (excluding tables)
            # ------------------------------------------------
            # Extract text with formatting details
            try:
                text_dict = page.get_text("dict")
            except Exception as exc:
                logger.warning("Failed to get text dict on page %d: %s", page_num + 1, exc)
                text_dict = {"blocks": []}
            
            # Process each block in the page
            for block in text_dict.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    # Check if block overlaps significantly with any table
                    block_bbox = block.get("bbox")
                    is_in_table = False
                    
                    if block_bbox:
                        # Check for header/footer
                        if self._is_header_footer(block_bbox, page.rect):
                            # Mark it but don't skip yet? Or skip?
                            # For now, mark it in metadata so LLM can decide, 
                            # BUT user wants "clean" text. 
                            # If I skip it, it's gone.
                            # If I mark it, I need to add it to block logic.
                            pass # Will add metadata later when creating block
                        
                        # specific logic: check if center of block is inside a table rect
                        b_x0, b_y0, b_x1, b_y1 = block_bbox
                        b_center_x = (b_x0 + b_x1) / 2
                        b_center_y = (b_y0 + b_y1) / 2
                        
                        for t_rect in table_rects:
                            # t_rect is (x0, y0, x1, y1)
                            if (t_rect[0] <= b_center_x <= t_rect[2] and 
                                t_rect[1] <= b_center_y <= t_rect[3]):
                                is_in_table = True
                                break
                    
                    if is_in_table:
                        continue  # Skip text that is part of a table

                    block_text_parts = []
                    avg_font_size = 0
                    font_sizes = []
                    is_bold = False
                    is_italic = False
                    
                    # Extract text and analyze styles from spans
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            span_text = span.get("text", "")
                            line_text += span_text
                            
                            # Track font size for heading detection
                            font_size = span.get("size", 0)
                            if font_size > 0:
                                font_sizes.append(font_size)
                            
                            # Check font flags for bold/italic
                            flags = span.get("flags", 0)
                            if flags & 16:  # Bold
                                is_bold = True
                            if flags & 2:   # Italic
                                is_italic = True
                        
                        if line_text.strip():
                            block_text_parts.append(line_text.strip())
                    
                    text = " ".join(block_text_parts).strip()
                    
                    if text:
                        block_id = generate_block_id(self.block_counter)
                        self.block_counter += 1
                        
                        # Calculate average font size
                        if font_sizes:
                            avg_font_size = sum(font_sizes) / len(font_sizes)
                        
                        # Create text style
                        style = TextStyle(
                            bold=is_bold,
                            italic=is_italic
                        )
                        
                        block = Block(
                            block_id=block_id,
                            text=text,
                            index=self.block_counter * 100,
                            block_type=BlockType.UNKNOWN,
                            style=style,
                            page_number=page_num + 1
                        )
                        
                        # Detect potential headings using ADAPTIVE thresholds
                        # Logic: 
                        # - H1: Significantly larger than body (e.g. > 1.6x)
                        # - H2: Moderately larger (e.g. > 1.3x)
                        # - H3: Slightly larger (> 1.1x) OR (Bold AND Same Size)
                        
                        if avg_font_size >= h3_threshold or (is_bold and avg_font_size >= body_font_size):
                            block.metadata["potential_heading"] = True
                            
                            if avg_font_size >= h1_threshold:
                                block.metadata["heading_level"] = 1
                            elif avg_font_size >= h2_threshold:
                                block.metadata["heading_level"] = 2
                            else:
                                block.metadata["heading_level"] = 3
                        
                        block.metadata["font_size"] = avg_font_size
                        block.metadata["relative_size"] = (
                            avg_font_size / body_font_size if body_font_size > 0 else 1.0
                        )
                        blocks.append(block)
            
            # 3. Extract Images
            # ------------------------------------------------
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = pdf_doc.extract_image(xref)
                    image_data = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Map extension to ImageFormat
                    format_map = {
                        'png': ImageFormat.PNG,
                        'jpg': ImageFormat.JPEG,
                        'jpeg': ImageFormat.JPEG,
                        'gif': ImageFormat.GIF,
                        'bmp': ImageFormat.BMP,
                    }
                    image_format = format_map.get(image_ext.lower(), ImageFormat.UNKNOWN)
                    
                    figure_id = generate_figure_id(self.figure_counter)
                    self.figure_counter += 1
                    
                    figure = Figure(
                        figure_id=figure_id,
                        index=self.figure_counter,
                        image_data=image_data,
                        image_format=image_format
                    )
                    figure.metadata["page_number"] = page_num + 1
                    figures.append(figure)
                except Exception as exc:
                    logger.warning("Failed to extract image on page %d (img %d): %s", page_num + 1, img_index, exc)
        
        return blocks, figures
