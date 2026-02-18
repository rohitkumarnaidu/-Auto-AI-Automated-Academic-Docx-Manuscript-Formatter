"""
Formatter Module - Applies structure and styles to create a Word document.

All rendering helpers are wrapped in @safe_function so that a failure in
one block/figure/equation does not abort the entire document generation.
"""

import logging
import os
import yaml
from typing import Optional, Any
from docx import Document as WordDocument
from docx.shared import Inches, Pt
from io import BytesIO
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

logger = logging.getLogger(__name__)

from app.models import PipelineDocument as Document, BlockType, Figure
from app.pipeline.contracts.loader import ContractLoader
from app.pipeline.formatting.style_mapper import StyleMapper
from app.pipeline.formatting.numbering import NumberingEngine
from app.pipeline.formatting.reference_formatter import ReferenceFormatter
from app.pipeline.formatting.template_renderer import TemplateRenderer
from app.pipeline.tables.renderer import TableRenderer
from app.pipeline.safety.safe_execution import safe_function, safe_execution

class Formatter:
    """
    Formats the validated Document into a python-docx object based on a template.
    """
    
    def __init__(self, templates_dir: str = "app/templates", contracts_dir: str = "app/pipeline/contracts"):
        self.templates_dir = templates_dir
        self.contract_loader = ContractLoader(contracts_dir=contracts_dir)
        self.style_mapper = StyleMapper(self.contract_loader)
        self.numbering_engine = NumberingEngine(self.contract_loader)
        self.reference_formatter = ReferenceFormatter(self.contract_loader)
        self.template_renderer = TemplateRenderer(templates_dir=templates_dir)
        self.table_renderer = TableRenderer()
        
    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        template_name = (
            document.template.template_name
            if document.template and hasattr(document.template, "template_name")
            else "none"
        )
        # We store the resulting Word object in a transient field
        document.generated_doc = self.format(document, template_name)
        return document

    @safe_function(fallback_value=None, error_message="Formatter.format failed")
    def format(self, document: Document, template_name: str = "IEEE") -> Optional[Any]:
        """
        Apply formatting using contract-driven modular components.
        """
        if not template_name:
            template_name = "none" # No default template - use neutral formatting
            
        # 1. Apply rules to model before rendering
        document = self.numbering_engine.apply_numbering(document, template_name)
        self._prepare_references(document, template_name)

        # 2. Primary path: docxtpl/Jinja2 template rendering.
        # Keep legacy python-docx path as a fallback for robustness.
        try:
            return self.template_renderer.render(document, template_name)
        except Exception as exc:
            logger.warning(
                "docxtpl render failed for template '%s'. Falling back to legacy formatter. Error: %s",
                template_name, exc
            )
        
        # 2. Load Resources
        # Note: template.docx is still the base for styles
        is_none = template_name.lower() == "none"
        template_path = os.path.join(self.templates_dir, template_name.lower(), "template.docx")
        contract_path = os.path.join(self.templates_dir, template_name.lower(), "contract.yaml")
        
        if is_none:
            logger.info("No template specified (General Formatting). Using blank document.")
            word_doc = WordDocument()
        elif not os.path.exists(template_path):
            logger.warning("Template file not found at %s. Using blank.", template_path)
            word_doc = WordDocument()
        else:
            word_doc = WordDocument(template_path)
            
        contract = self._load_contract(contract_path)
        style_map = contract.get("styles", {})
        
        # 2. Add Content
        items_to_insert = []
        
        # Add Blocks
        for block in document.blocks:
            # SKIP figure captions - check both Enum and String to be safe
            b_type = str(block.block_type).upper()
            if "FIGURE_CAPTION" in b_type or "TABLE_CAPTION" in b_type:
                continue
            
            # Special handling for references: if it's a reference entry, we might want to re-format it
            if block.block_type == BlockType.REFERENCE_ENTRY:
                # Find matching reference object
                ref = next((r for r in document.references if r.block_id == block.block_id), None)
                if ref:
                    block.text = self.reference_formatter.format_reference(ref, template_name)
            
            items_to_insert.append({
                "type": "block",
                "index": block.index,
                "obj": block
            })
            
        # Add Figures (using index)
        # We need sequential numbering for captions: Figure 1, Figure 2, ...
        # The document.figures list is ordered by extraction.
        for i, fig in enumerate(document.figures):
            # i+1 is the sequential number
            
            # fig.metadata["block_index"] is where it was found in parser.
            b_idx = fig.metadata.get("block_index", -1)
            
            # We insert figure AFTER the block it was attached to
            # Use small offset to ensure it comes after the block
            # HARDENING FIX: Deterministic sub-offset for multiple figures same paragraph
            # If multiple figures share same block_index, add sub-offset based on position
            # Example: 3 figures at index 100 -> 100.1, 100.101, 100.102
            # Maintains base offset (+0.1) and avoids equation collision (+0.2)
            sub_offset = i * 0.001  # Position-based sub-offset
            items_to_insert.append({
                "type": "figure",
                "index": b_idx + 0.1 + sub_offset, 
                "obj": fig,
                "number": i + 1
            })

            
        # Add Equations
        for i, eqn in enumerate(document.equations):
            # FORENSIC FIX: Sort by block_index (position in text) not equation index (creation order)
            # Use small offset (+0.2) to place immediately after parent block
            sort_index = eqn.metadata.get("block_index", eqn.index)
            items_to_insert.append({
                "type": "equation",
                "index": sort_index + 0.2,
                "obj": eqn
            })
            
        # Add Tables
        for i, table in enumerate(document.tables):
             items_to_insert.append({
                "type": "table",
                "index": table.block_index, # Fixed: Tables have global block_index
                "obj": table,
                "number": i + 1  # Sequential number for caption (Table 1, Table 2, ...)
            })
            
        # Sort by index
        items_to_insert.sort(key=lambda x: x["index"])
        
        # 3. Render
        self._apply_initial_layout(word_doc, template_name)
        
        # --- NEW FORMATTING OPTIONS IMPLEMENTATION ---
        options = document.formatting_options or {}
        
        # A. Page Size
        self._apply_page_size(word_doc, options.get("page_size", "Letter"))
        
        # B. Cover Page
        if options.get("cover_page", True):
            self._add_cover_page(word_doc, document)
            
        # C. Table of Contents
        if options.get("toc", False):
            self._add_table_of_contents(word_doc)
            
        # D. Page Numbers
        if options.get("page_numbers", True):
             self._add_page_numbers(word_doc)

        # E. Borders
        if options.get("borders", False):
            self._add_page_borders(word_doc)

        current_columns = None
        
        for item in items_to_insert:
            if item["type"] == "block":
                block = item["obj"]
                
                # Layout logic: Check if we need a column change
                target_cols = self._get_target_columns(block, template_name)
                if current_columns is not None and target_cols != current_columns:
                    # Switch layout: Add new section
                    new_section = word_doc.add_section()
                    self._set_columns(new_section, target_cols)
                
                if current_columns is None:
                    # Initialize first section
                    self._set_columns(word_doc.sections[0], target_cols)
                    
                current_columns = target_cols
                self._render_block(word_doc, block, template_name)
                
            elif item["type"] == "figure":
                self._render_figure(word_doc, item["obj"], item["number"])
            elif item["type"] == "equation":
                self._render_equation(word_doc, item["obj"])
            elif item["type"] == "table":
                self.table_renderer.render(word_doc, item["obj"], item.get("number"))
                
        # 4. Render Footnotes (Supplemental)
        footnotes = [b for b in document.blocks if b.block_type == BlockType.FOOTNOTE]
        if footnotes:
            word_doc.add_section() # New page or section for footnotes? 
            # Usually footnotes are at bottom of page, but for simple formatter, append at end.
            p = word_doc.add_paragraph()
            p.add_run("FOOTNOTES").bold = True
            p.alignment = 1 # Center
            
            for fn in footnotes:
                fn_p = word_doc.add_paragraph(style="Normal")
                # Format: [ID] Text
                fn_id = fn.metadata.get("footnote_id", "")
                prefix = f"[{fn_id}] " if fn_id else "* "
                fn_p.add_run(prefix).italic = True
                fn_p.add_run(fn.text)
                
        return word_doc

    def _prepare_references(self, document: Document, template_name: str) -> None:
        """Populate missing reference.formatted_text values before rendering."""
        if not document.references:
            return

        for ref in document.references:
            if ref.formatted_text and ref.formatted_text.strip():
                continue
            try:
                ref.formatted_text = self.reference_formatter.format_reference(ref, template_name)
            except Exception:
                ref.formatted_text = ref.raw_text or ''

    @safe_function(fallback_value=None, error_message="Equation rendering failed")
    def _render_equation(self, doc, equation):
        """Render an equation block."""
        # Simple implementation: Use the text fallback
        # In more advanced versions, we'd insert the OMML directly
        p = doc.add_paragraph()
        if equation.number:
            # Format: [Equation Text] (Number)
            # Use tabs for alignment if needed
            p.text = f"{equation.text}\t\t{equation.number}"
        else:
            p.text = equation.text
            
        p.style = "Normal" # or custom Equation style
        p.paragraph_format.alignment = 1 # Center

    def _apply_initial_layout(self, doc, publisher: str):
        """Set margins and initial properties."""
        contract = self.contract_loader.load(publisher)
        layout = contract.get("layout", {})
        if not layout: return
        
        section = doc.sections[0]
        # Margins (inches)
        section.top_margin = Inches(layout.get("margins", {}).get("top", 1.0))
        section.bottom_margin = Inches(layout.get("margins", {}).get("bottom", 1.0))

    def _get_target_columns(self, block, publisher: str) -> int:
        """Determine required column count for a block."""
        contract = self.contract_loader.load(publisher)
        layout = contract.get("layout", {})
        default = layout.get("default_columns", 1)
        
        s_name = (block.section_name or "").lower()
        overrides = layout.get("section_overrides", {})
        
        # Check canonical matching or direct matching
        for key, val in overrides.items():
            if key in s_name:
                return val
        
        return default

    def _apply_page_size(self, doc, size_name: str):
        """Sets the page size for all sections."""
        from docx.shared import Inches, Mm
        
        size_map = {
            "Letter": (Inches(8.5), Inches(11)),
            "A4": (Mm(210), Mm(297)),
            "Legal": (Inches(8.5), Inches(14))
        }
        
        width, height = size_map.get(size_name, size_map["Letter"])
        
        for section in doc.sections:
            section.page_width = width
            section.page_height = height

    def _add_cover_page(self, doc, document_obj):
        """Adds a cover page with title and metadata."""
        # Insert a new paragraph at the very beginning
        # Note: We can't easily prepend in python-docx, so we rely on this being called 
        # BEFORE content addition if we want it first, OR we add a section break.
        # However, typically cover pages are separate sections at the start.
        # Since we call this early in `format()`, we can just add to the empty doc.
        
        p = doc.add_paragraph()
        p.alignment = 1 # Center
        
        # Title
        title = document_obj.metadata.title or document_obj.original_filename or "Untitled Document"
        run = p.add_run(title + "\n\n")
        run.bold = True
        run.font.size = Pt(24)
        
        # Authors
        authors = ", ".join(document_obj.metadata.authors) if document_obj.metadata.authors else "Unknown Author"
        run = p.add_run(authors + "\n")
        run.font.size = Pt(14)
        
        # Date
        from datetime import datetime
        run = p.add_run(datetime.now().strftime("%B %d, %Y"))
        run.font.size = Pt(12)
        
        doc.add_page_break()

    def _add_table_of_contents(self, doc):
        """Adds a TOC field code."""
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        p = doc.add_paragraph()
        run = p.add_run("Table of Contents")
        run.bold = True
        run.font.size = Pt(16)
        
        # XML for TOC field
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar)
        
        instr = OxmlElement('w:instrText')
        instr.set(qn('xml:space'), 'preserve')
        instr.text = 'TOC \\o "1-3" \\h \\z \\u'
        run._r.append(instr)
        
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        run._r.append(fldChar2)
        
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar3)
        
        doc.add_page_break()

    def _add_page_numbers(self, doc):
        """Adds simple page numbers to the footer."""
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        # Simplification: Add to first section's footer
        section = doc.sections[0]
        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = 1 # Center
        
        run = p.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar)
        
        instr = OxmlElement('w:instrText')
        instr.set(qn('xml:space'), 'preserve')
        instr.text = "PAGE"
        run._r.append(instr)
        
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar2)

    def _add_page_borders(self, doc):
        """Adds page borders via OXML."""
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        # Get the section properties
        sec_pr = doc.sections[0]._sectPr
        # Create pgBorders element
        pg_borders = OxmlElement('w:pgBorders')
        pg_borders.set(qn('w:offsetFrom'), 'page')
        
        for border_name in ('top', 'left', 'bottom', 'right'):
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4') # 1/8 point
            border.set(qn('w:space'), '24')
            border.set(qn('w:color'), 'auto')
            pg_borders.append(border)
            
        sec_pr.append(pg_borders)

    def _set_columns(self, section, count: int):
        """Helper to set column count on a python-docx section."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        # Access underlying XML
        sectPr = section._sectPr
        cols = sectPr.xpath('./w:cols')
        if not cols:
            cols = OxmlElement('w:cols')
            sectPr.append(cols)
        else:
            cols = cols[0]
            
        cols.set(qn('w:num'), str(count))
        # Ensure space between columns if > 1
        if count > 1:
            cols.set(qn('w:space'), '720') # 0.5 inch (720 twips)

    def _load_contract(self, path: str) -> dict:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning("Failed to load contract %s: %s", path, e)
            return {}


    @safe_function(fallback_value=None, error_message="Block rendering failed")
    def _render_block(self, doc, block, template_name):
        """Render a block with contract-driven spacing, formatting, and dynamic list detection."""
        # Skip rendering empty anchor blocks (preserve in pipeline)
        if block.text.strip() == "" and block.metadata.get("has_figure", False):
            return  # Block remains in pipeline for anchor stability
        
        if block.text.strip() == "" and block.metadata.get("has_equation", False):
            return  # Block remains in pipeline for anchor stability
        
        # DYNAMIC LIST DETECTION
        clean_text = block.text.strip()
        if not clean_text:
            return  # Skip empty blocks
        
        try:
            # Check if this is a list item
            if self._is_bullet_list_item(clean_text):
                # Render as bullet list
                p = doc.add_paragraph(self._clean_list_text(clean_text), style="List Bullet")
            elif self._is_numbered_list_item(clean_text):
                # Render as numbered list
                p = doc.add_paragraph(self._clean_list_text(clean_text), style="List Number")
            else:
                # Normal paragraph rendering
                word_style = self.style_mapper.get_style_name(block, template_name)
                p = doc.add_paragraph(clean_text, style=word_style)
            
            # Apply contract-driven spacing
            self._apply_spacing_from_contract(p, block, template_name)
            
        except Exception:
            # Fallback if style missing
            if clean_text:
                p = doc.add_paragraph(clean_text)
                self._apply_spacing_from_contract(p, block, template_name)
            else:
                return
        
        # PROACTIVE FIX: Render Hyperlinks extracted in Stage 1
        hyperlinks = block.metadata.get("hyperlinks", [])
        if hyperlinks:
            p.add_run(" (Links: ")
            for i, hl in enumerate(hyperlinks):
                label = hl.get("text", "Link")
                url = hl.get("url", "")
                p.add_run(f"[{label}]({url})").font.italic = True
                if i < len(hyperlinks) - 1:
                    p.add_run(", ")
            p.add_run(")")
        
        return p


    def _apply_spacing_from_contract(self, paragraph, block, template_name):
        """Apply spacing rules from contract to paragraph."""
        contract = self.contract_loader.load(template_name)
        layout = contract.get("layout", {})
        spacing_rules = layout.get("spacing", {})
        
        if not spacing_rules:
            return  # No spacing rules in contract
        
        # Determine block type and get appropriate spacing
        if hasattr(block, 'is_heading') and block.is_heading():
            spacing = spacing_rules.get("heading", {})
        elif str(block.block_type).upper() in ["FIGURE_CAPTION", "TABLE_CAPTION"]:
            # Use figure or table spacing for captions
            if "FIGURE" in str(block.block_type).upper():
                spacing = spacing_rules.get("figure", {})
            else:
                spacing = spacing_rules.get("table", {})
        elif "REFERENCES" in str(block.block_type).upper():
            # Special spacing for references section
            spacing = spacing_rules.get("references", spacing_rules.get("heading", {}))
        else:
            spacing = spacing_rules.get("paragraph", {})
        
        # Apply spacing if defined
        if spacing:
            before = spacing.get("before", 0)
            after = spacing.get("after", 0)
            paragraph.paragraph_format.space_before = Pt(before)
            paragraph.paragraph_format.space_after = Pt(after)

    @safe_function(fallback_value=None, error_message="Image sizing failed")
    def _calculate_image_size(self, figure: Figure):
        """
        Calculate optimal image size based on actual dimensions and page constraints.
        
        Strategy:
        1. Use figure.width/height if available (from Figure model)
        2. Constrain to page width (6.5 inches for standard letter with 1" margins)
        3. Maintain aspect ratio
        4. Set reasonable min/max bounds
        """
        # Page constraints (standard letter: 8.5" wide, 1" margins each side = 6.5" usable)
        MAX_WIDTH = Inches(6.5)
        MAX_HEIGHT = Inches(9.0)  # Standard letter: 11" tall, 1" margins = 9" usable
        MIN_WIDTH = Inches(2.0)   # Minimum for readability
        DEFAULT_WIDTH = Inches(5.0)  # Good default for most images
        
        # If figure has dimensions, use them
        if figure.width and figure.height:
            # Convert to inches (assuming pixels at 96 DPI)
            img_width_inches = Inches(figure.width / 96.0)
            img_height_inches = Inches(figure.height / 96.0)
            
            # Calculate aspect ratio
            aspect_ratio = figure.width / figure.height
            
            # Scale to fit within page width
            if img_width_inches > MAX_WIDTH:
                final_width = MAX_WIDTH
                final_height = Inches(MAX_WIDTH.inches / aspect_ratio)
            elif img_width_inches < MIN_WIDTH:
                # Small images: scale up to minimum width
                final_width = MIN_WIDTH
                final_height = Inches(MIN_WIDTH.inches / aspect_ratio)
            else:
                # Image fits naturally
                final_width = img_width_inches
                final_height = img_height_inches
            
            # Ensure height doesn't exceed page
            if final_height > MAX_HEIGHT:
                final_height = MAX_HEIGHT
                final_width = Inches(MAX_HEIGHT.inches * aspect_ratio)
            
            return final_width, final_height
        else:
            # No dimensions available: use smart default
            # Default to 5 inches wide (good for most academic figures)
            return DEFAULT_WIDTH, None  # Let python-docx maintain aspect ratio

    @safe_function(fallback_value=None, error_message="Figure rendering failed")
    def _render_figure(self, doc, figure: Figure, number: int):
        """Render a figure with dynamic sizing based on image dimensions."""
        # 1. Add image with dynamic sizing
        if figure.export_path and os.path.exists(figure.export_path):
            try:
                # Calculate optimal size based on image dimensions
                width, height = self._calculate_image_size(figure)
                # Add image and get the paragraph containing it
                paragraph = doc.add_paragraph()
                run = paragraph.add_run()
                run.add_picture(figure.export_path, width=width, height=height)
                paragraph.alignment = 1  # Center the image
            except Exception as e:
                logger.warning("Failed to render figure from export_path: %s", e)
                # Fallback: add placeholder text if image fails
                p = doc.add_paragraph(f"[Image: {figure.export_path}]")
                p.alignment = 1  # Center
        elif figure.image_data:
            # If we have image_data, use BytesIO (more reliable than temp files)
            try:
                from io import BytesIO
                image_stream = BytesIO(figure.image_data)
                # Calculate optimal size
                width, height = self._calculate_image_size(figure)
                # Add image to a paragraph and center it
                paragraph = doc.add_paragraph()
                run = paragraph.add_run()
                if height:
                    run.add_picture(image_stream, width=width, height=height)
                else:
                    run.add_picture(image_stream, width=width)
                paragraph.alignment = 1  # Center the image
                logger.info("Rendered figure %d from image_data (%d bytes)", number, len(figure.image_data))
            except Exception as e:
                logger.warning("Failed to render figure from image_data: %s", e)
                # Fallback: add placeholder
                p = doc.add_paragraph(f"[Figure {number} - Image rendering failed: {str(e)[:50]}]")
                p.alignment = 1  # Center
        else:
            # If no image data or path, add a placeholder
            p = doc.add_paragraph(f"[Figure {number} Placeholder - No image data]")
            p.alignment = 1  # Center the placeholder too
        
        # 2. Add caption with bold prefix (check if prefix already exists)
        if figure.caption_text:
            caption_p = doc.add_paragraph(style="Caption")
            # Check if caption already starts with "Figure N:" to avoid duplication
            caption_lower = figure.caption_text.lower().strip()
            if caption_lower.startswith(f"figure {number}:"):
                # Caption already has prefix, just add it as-is with bold prefix
                run = caption_p.add_run(f"Figure {number}: ")
                run.bold = True
                # Add the rest after the prefix
                rest_text = figure.caption_text[len(f"Figure {number}:"):].strip()
                caption_p.add_run(rest_text)
            else:
                # Caption doesn't have prefix, add it
                run = caption_p.add_run(f"Figure {number}: ")
                run.bold = True
                caption_p.add_run(figure.caption_text)
            caption_p.alignment = 1  # Center

    def _is_bullet_list_item(self, text: str) -> bool:
        """Dynamically detect if text is a bullet list item."""
        if not text:
            return False
        stripped = text.lstrip()
        # Check for common bullet markers
        return stripped.startswith(('\u2022', '-', '*', '\u00b7', '\u25e6', '\u25aa', '\u25ab'))
    
    def _is_numbered_list_item(self, text: str) -> bool:
        """Dynamically detect if text is a numbered list item."""
        if not text:
            return False
        import re
        # Match patterns like "1. ", "1) ", "a. ", "a) ", "i. ", "i) "
        return bool(re.match(r'^\s*([0-9]+|[a-z]|[ivxlcdm]+)[\.)\s]\s+', text, re.IGNORECASE))
    
    def _clean_list_text(self, text: str) -> str:
        """Remove list markers from text for proper Word list rendering."""
        import re
        # Remove bullet markers
        text = re.sub(r'^\s*[\u2022\-\*\u00b7\u25e6\u25aa\u25ab]\s+', '', text)
        # Remove numbered markers
        text = re.sub(r'^\s*([0-9]+|[a-z]|[ivxlcdm]+)[\.)\s]\s+', '', text, flags=re.IGNORECASE)
        return text

