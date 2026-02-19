"""
Docling Layout Analysis Client.

This module provides a client for IBM Docling library to extract advanced
layout information from PDF documents, including bounding boxes, font sizes,
and structural elements like headers/footers.

Docling excels at:
- Preserving document layout and reading order
- Detecting bounding boxes for all document elements
- Identifying tables, figures, headings, and paragraphs
- Extracting font information and styles
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.pipeline.safety import safe_function

logger = logging.getLogger(__name__)

try:
    import os
    # Windows Symlink Fix: Disable warning and force copy
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling library not available. Install with: pip install docling")


class BoundingBox:
    """Represents a bounding box for a document element."""
    
    def __init__(self, x0: float, y0: float, x1: float, y1: float, page: int = 0):
        self.x0 = x0  # Left
        self.y0 = y0  # Top
        self.x1 = x1  # Right
        self.y1 = y1  # Bottom
        self.page = page
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def center_y(self) -> float:
        """Vertical center position."""
        return (self.y0 + self.y1) / 2
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "page": self.page,
            "width": self.width,
            "height": self.height,
        }


class LayoutElement:
    """Represents a layout element with bounding box and metadata."""
    
    def __init__(
        self,
        text: str,
        bbox: BoundingBox,
        element_type: str,
        font_size: Optional[float] = None,
        is_bold: bool = False,
        is_italic: bool = False,
        confidence: float = 1.0,
    ):
        self.text = text
        self.bbox = bbox
        self.element_type = element_type  # title, paragraph, heading, table, figure, etc.
        self.font_size = font_size
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "bbox": self.bbox.to_dict(),
            "type": self.element_type,
            "font_size": self.font_size,
            "is_bold": self.is_bold,
            "is_italic": self.is_italic,
            "confidence": self.confidence,
        }


class DoclingClient:
    """
    Client for IBM Docling library to perform advanced PDF layout analysis.
    
    Features:
    - Bounding box extraction for all elements
    - Font size and style detection
    - Header/footer identification
    - Table and figure detection
    - Reading order preservation
    """
    
    def __init__(self):
        """Initialize the Docling client."""
        if not DOCLING_AVAILABLE:
            logger.warning("Docling not available - layout analysis will be limited")
        
        self.converter = None
        if DOCLING_AVAILABLE:
            try:
                # Initialize DocumentConverter with defaults
                self.converter = DocumentConverter()
                logger.info("Docling client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Docling converter: {e}")
                self.converter = None
    
    def is_available(self) -> bool:
        """Check if Docling is available and initialized."""
        return DOCLING_AVAILABLE and self.converter is not None
    
    @safe_function(fallback_value={}, error_message="DoclingClient.analyze_layout")
    def analyze_layout(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze the layout of a PDF file using Docling.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            Dictionary containing layout information (elements, boxes, etc.)
        """
        if not DOCLING_AVAILABLE:
            logger.warning("Docling is not installed or failed to load.")
            return {}
            
        try:
            logger.info(f"Starting Docling layout analysis for: {file_path}")
            
            try:
                # 🚀 PERFORMANCE OPTIMIZATION: Check for Digital-Native PDF
                # If the PDF has a dense text layer, we DISABLE OCR to save ~95% processing time.
                do_ocr = True
                # try:
                #     import pypdf
                #     reader = pypdf.PdfReader(file_path)
                #     if len(reader.pages) > 0:
                #         page = reader.pages[0]
                #         text = page.extract_text()
                #         # Heuristic: If >50 chars of text found on first page, assume digital-native
                #         if text and len(text.strip()) > 50:
                #             logger.info(f"Digital-native PDF detected ({len(text)} chars on p1). Disabling OCR for speed.")
                #             do_ocr = False
                # except Exception as e:
                #     logger.warning(f"Failed to check text density: {e}. Defaulting to OCR=True")

                # Configure pipeline options
                # do_ocr=True/False based on density check
                # pipeline_options = PdfPipelineOptions(do_ocr=do_ocr)
                
                # If we MUST do OCR, prevent full page force to save some time
                # if do_ocr:
                #    pipeline_options.ocr_options.force_full_page_ocr = False
                
                # Use default options to prevent 'backend' attribute error in newer docling versions
                doc_converter = DocumentConverter()
                doc = doc_converter.convert(file_path).document
            
            except Exception as e:
                logger.error(f"Docling conversion failed: {e}")
                raise e

            # Extract layout data from the Docling document object
            elements = []
            
            # Iterate through all elements in the document
            # Note: Docling's object model might vary by version
            # We map main text items, headers, tables, etc.
            
            # Text items (Paragraphs, Headings, etc.)
            for item in doc.texts:
                 # Extract bounding box
                 bbox = None
                 if item.prov and item.prov[0].bbox:
                     b = item.prov[0].bbox
                     # Normalize: Docling uses bottom-up/top-down depending on backend?
                     # Usually top-left origin for PDF analysis in this context
                     bbox = {
                         "x0": b.l,
                         "y0": b.t, 
                         "x1": b.r,
                         "y1": b.b,
                         "page": item.prov[0].page_no
                     }
                 
                 elements.append({
                     "text": item.text,
                     "type": item.label, # e.g., 'text', 'title', 'section_header'
                     "bbox": bbox,
                     "level": getattr(item, 'level', 0) # Headings structure
                 })

            # Tables
            for table in doc.tables:
                if table.prov and table.prov[0].bbox:
                     b = table.prov[0].bbox
                     bbox = {
                         "x0": b.l,
                         "y0": b.t, 
                         "x1": b.r,
                         "y1": b.b,
                         "page": table.prov[0].page_no
                     }
                     elements.append({
                         "type": "table",
                         "bbox": bbox,
                         "rows": len(table.data.grid),
                         "cols": len(table.data.grid[0]) if table.data.grid else 0
                     })
            
            # Safe handling of num_pages which can be a method or property depending on version
            num_pages = 1
            if hasattr(doc, 'num_pages'):
                np = doc.num_pages
                if callable(np):
                    num_pages = np()
                else:
                    num_pages = np
            
            result = {
                "elements": elements,
                "pages": num_pages
            }
            
            logger.info(f"Docling analysis complete. Found {len(elements)} elements.")
            return result
            
        except Exception as e:
            logger.error(f"Docling analysis failed: {e}")
            # Raise to trigger safe_function wrapper instead? 
            # safe_function will catch it and return fallback_value ({}).
            raise e
    
    def _extract_elements(self, document) -> List[LayoutElement]:
        """Extract layout elements from Docling document."""
        elements = []
        
        try:
            # Iterate through document items
            for item in document.iterate_items():
                # Get bounding box
                bbox_data = item.bbox if hasattr(item, 'bbox') else None
                if not bbox_data:
                    continue
                
                bbox = BoundingBox(
                    x0=bbox_data.l,
                    y0=bbox_data.t,
                    x1=bbox_data.r,
                    y1=bbox_data.b,
                    page=bbox_data.page if hasattr(bbox_data, 'page') else 0,
                )
                
                # Get text content
                text = item.text if hasattr(item, 'text') else ""
                
                # Get element type (title, paragraph, heading, etc.)
                element_type = item.label if hasattr(item, 'label') else "paragraph"
                
                # Get font information (if available)
                font_size = None
                is_bold = False
                is_italic = False
                
                if hasattr(item, 'prov') and item.prov:
                    for prov in item.prov:
                        if hasattr(prov, 'font_size'):
                            font_size = prov.font_size
                        if hasattr(prov, 'font_weight') and prov.font_weight > 600:
                            is_bold = True
                        if hasattr(prov, 'font_style') and 'italic' in str(prov.font_style).lower():
                            is_italic = True
                
                # Create layout element
                element = LayoutElement(
                    text=text,
                    bbox=bbox,
                    element_type=element_type,
                    font_size=font_size,
                    is_bold=is_bold,
                    is_italic=is_italic,
                    confidence=0.9,  # Docling has high confidence
                )
                
                elements.append(element)
        
        except Exception as e:
            logger.error(f"Failed to extract elements: {e}")
        
        return elements
    
    def _detect_headers_footers(
        self, elements: List[LayoutElement]
    ) -> Tuple[List[LayoutElement], List[LayoutElement]]:
        """
        Detect headers and footers based on position.
        
        Headers: Top 10% of page
        Footers: Bottom 10% of page
        """
        headers = []
        footers = []
        
        if not elements:
            return headers, footers
        
        # Group elements by page
        pages: Dict[int, List[LayoutElement]] = {}
        for elem in elements:
            page = elem.bbox.page
            if page not in pages:
                pages[page] = []
            pages[page].append(elem)
        
        # For each page, identify headers/footers
        for page_num, page_elements in pages.items():
            if not page_elements:
                continue
            
            # Find page height (max y1)
            page_height = max(elem.bbox.y1 for elem in page_elements)
            
            # Header threshold: top 10%
            header_threshold = page_height * 0.1
            
            # Footer threshold: bottom 10%
            footer_threshold = page_height * 0.9
            
            for elem in page_elements:
                # Check if in header region
                if elem.bbox.y1 < header_threshold:
                    headers.append(elem)
                # Check if in footer region
                elif elem.bbox.y0 > footer_threshold:
                    footers.append(elem)
        
        return headers, footers
    
    def _extract_tables(self, document) -> List[Dict[str, Any]]:
        """Extract table information."""
        tables = []
        
        try:
            for item in document.iterate_items():
                if hasattr(item, 'label') and item.label == 'table':
                    table_data = {
                        "text": item.text if hasattr(item, 'text') else "",
                        "bbox": item.bbox.to_dict() if hasattr(item, 'bbox') else None,
                        "rows": getattr(item, 'num_rows', 0),
                        "cols": getattr(item, 'num_cols', 0),
                    }
                    tables.append(table_data)
        except Exception as e:
            logger.error(f"Failed to extract tables: {e}")
        
        return tables
    
    def _extract_figures(self, document) -> List[Dict[str, Any]]:
        """Extract figure information."""
        figures = []
        
        try:
            for item in document.iterate_items():
                if hasattr(item, 'label') and item.label in ['figure', 'picture']:
                    figure_data = {
                        "text": item.text if hasattr(item, 'text') else "",
                        "bbox": item.bbox.to_dict() if hasattr(item, 'bbox') else None,
                        "caption": getattr(item, 'caption', ""),
                    }
                    figures.append(figure_data)
        except Exception as e:
            logger.error(f"Failed to extract figures: {e}")
        
        return figures
    
    def _calculate_confidence(self, elements: List[LayoutElement]) -> float:
        """Calculate overall confidence score."""
        if not elements:
            return 0.0
        
        # Average confidence of all elements
        total_confidence = sum(elem.confidence for elem in elements)
        return total_confidence / len(elements)
    
    def _empty_layout(self) -> Dict[str, Any]:
        """Return empty layout structure."""
        return {
            "elements": [],
            "headers": [],
            "footers": [],
            "tables": [],
            "figures": [],
            "confidence": 0.0,
        }
    
    def find_title_with_logo_tolerance(
        self, elements: List[LayoutElement], logo_y_threshold: float = 150.0
    ) -> Optional[LayoutElement]:
        """
        Find title element, accounting for logos at the top.
        
        Args:
            elements: List of layout elements
            logo_y_threshold: Y position below which to start looking for title
            
        Returns:
            Title element or None
        """
        # Filter elements below logo threshold
        candidate_elements = [
            elem for elem in elements
            if elem.bbox.y0 > logo_y_threshold and elem.text.strip()
        ]
        
        if not candidate_elements:
            return None
        
        # Find element with largest font size
        title_element = max(
            candidate_elements,
            key=lambda e: (e.font_size or 0, -e.bbox.y0)  # Largest font, highest position
        )
        
        return title_element
