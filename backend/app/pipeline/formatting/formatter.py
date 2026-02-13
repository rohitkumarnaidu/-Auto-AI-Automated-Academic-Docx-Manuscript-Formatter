"""
Formatter Module - Applies structure and styles to create a Word document.
"""

import os
import yaml
from typing import Optional, Any
from docx import Document as WordDocument
from docx.shared import Inches, Pt
from io import BytesIO

from app.models import PipelineDocument as Document, BlockType, Figure
from app.pipeline.contracts.loader import ContractLoader
from app.pipeline.formatting.style_mapper import StyleMapper
from app.pipeline.formatting.numbering import NumberingEngine
from app.pipeline.formatting.reference_formatter import ReferenceFormatter
from app.pipeline.tables.renderer import TableRenderer

class Formatter:
    """
    Formats the validated Document into a python-docx object based on a template.
    """
    
    def __init__(self, templates_dir: str = "app/templates", contracts_dir: str = "app/pipeline/contracts"):
        self.templates_dir = templates_dir
        self.contract_loader = ContractLoader(contracts_dir=contracts_dir)
        self.style_mapper = StyleMapper(self.contract_loader)
        self.numbering_engine = NumberingEngine(self.contract_loader)
        self.numbering_engine = NumberingEngine(self.contract_loader)
        self.reference_formatter = ReferenceFormatter(self.contract_loader)
        self.table_renderer = TableRenderer()
        
    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        template_name = document.template.template_name if document.template else "none"
        # We store the resulting Word object in a transient field
        document.generated_doc = self.format(document, template_name)
        return document

    def format(self, document: Document, template_name: str = "IEEE") -> Optional[Any]:
        """
        Apply formatting using contract-driven modular components.
        """
        if not template_name:
            template_name = "none" # No default template - use neutral formatting
            
        # 1. Apply rules to model before rendering
        document = self.numbering_engine.apply_numbering(document, template_name)
        
        # 2. Load Resources
        # Note: template.docx is still the base for styles
        is_none = template_name.lower() == "none"
        template_path = os.path.join(self.templates_dir, template_name.lower(), "template.docx")
        contract_path = os.path.join(self.templates_dir, template_name.lower(), "contract.yaml")
        
        if is_none:
            print(f"INFO: No template specified (General Formatting). Using blank document.")
            word_doc = WordDocument()
        elif not os.path.exists(template_path):
            print(f"WARNING: Template file not found at {template_path}. Using blank.")
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
            # Example: 3 figures at index 100 → 100.1, 100.101, 100.102
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
            print(f"Warning: Failed to load contract {path}: {e}")
            return {}


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
            
        except:
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

    def _render_figure(self, doc, figure: Figure, number: int):
        """Render a figure with dynamic sizing based on image dimensions."""
        # 1. Add image with dynamic sizing
        if figure.export_path and os.path.exists(figure.export_path):
            try:
                # Calculate optimal size based on image dimensions
                width, height = self._calculate_image_size(figure)
                doc.add_picture(figure.export_path, width=width, height=height)
            except Exception as e:
                print(f"⚠️  Failed to render figure from export_path: {e}")
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
                if height:
                    doc.add_picture(image_stream, width=width, height=height)
                else:
                    doc.add_picture(image_stream, width=width)
                print(f"✅ Rendered figure {number} from image_data ({len(figure.image_data)} bytes)")
            except Exception as e:
                print(f"⚠️  Failed to render figure from image_data: {e}")
                # Fallback: add placeholder
                p = doc.add_paragraph(f"[Figure {number} - Image rendering failed: {str(e)[:50]}]")
                p.alignment = 1  # Center
        else:
            # If no image data or path, add a placeholder
            p = doc.add_paragraph(f"[Figure {number} Placeholder - No image data]")
            p.alignment = 1  # Center the placeholder too
        
        # 2. Add caption with bold prefix
        if figure.caption_text:
            caption_p = doc.add_paragraph(style="Caption")
            # Bold prefix: "Figure N: "
            run = caption_p.add_run(f"Figure {number}: ")
            run.bold = True
            # Regular caption text
            caption_p.add_run(figure.caption_text)
            caption_p.alignment = 1  # Center

    def _is_bullet_list_item(self, text: str) -> bool:
        """Dynamically detect if text is a bullet list item."""
        if not text:
            return False
        stripped = text.lstrip()
        # Check for common bullet markers
        return stripped.startswith(('•', '-', '*', '·', '◦', '▪', '▫'))
    
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
        text = re.sub(r'^\s*[•\-\*·◦▪▫]\s+', '', text)
        # Remove numbered markers
        text = re.sub(r'^\s*([0-9]+|[a-z]|[ivxlcdm]+)[\.)\s]\s+', '', text, flags=re.IGNORECASE)
        return text

