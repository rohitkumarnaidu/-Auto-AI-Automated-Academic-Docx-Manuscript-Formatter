"""
PDF Parser - Extract content from PDF files.

Uses PyMuPDF (fitz) to extract text, images, and basic structure from PDF documents.
Converts to internal Document model for processing through the pipeline.
"""

import os
from typing import List, Tuple
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
                metadata.keywords = [k.strip() for k in pdf_metadata['keywords'].split(',')]
        
        return metadata
    
    def _extract_content(self, pdf_doc) -> Tuple[List[Block], List[Figure]]:
        """Extract text blocks and images from PDF."""
        blocks = []
        figures = []
        
        for page_num, page in enumerate(pdf_doc):
            # Extract text blocks
            text_blocks = page.get_text("blocks")  # Returns (x0, y0, x1, y1, text, block_no, block_type)
            
            for block_data in text_blocks:
                if len(block_data) >= 5:
                    text = block_data[4].strip()
                    if text:
                        block_id = generate_block_id(self.block_counter)
                        self.block_counter += 1
                        
                        block = Block(
                            block_id=block_id,
                            text=text,
                            index=self.block_counter * 100,
                            block_type=BlockType.UNKNOWN,
                            style=TextStyle(),
                            page_number=page_num + 1
                        )
                        blocks.append(block)
            
            # Extract images
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
                except Exception as e:
                    print(f"Warning: Failed to extract image from PDF: {e}")
        
        return blocks, figures
