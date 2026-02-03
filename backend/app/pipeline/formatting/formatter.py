"""
Formatter Module - Applies structure and styles to create a Word document.
"""

import os
import yaml
from typing import Optional, Any
from docx import Document as WordDocument
from docx.shared import Inches
from io import BytesIO

from app.models import Document, BlockType, Figure

class Formatter:
    """
    Formats the validated Document into a python-docx object based on a template.
    """
    
    def __init__(self, templates_dir: str = "app/templates"):
        self.templates_dir = templates_dir
        
    def format(self, document: Document, template_name: str = None) -> Optional[Any]:
        """
        Apply formatting.
        
        Args:
            document: Processed Document model
            template_name: Name of template folder (e.g. 'ieee')
            
        Returns:
            docx.Document object if template provided, else None.
        """
        if not template_name:
            print("INFO: Template not selected. Formatting skipped.")
            return None
            
        # 1. Load Resources
        template_path = os.path.join(self.templates_dir, template_name, "template.docx")
        contract_path = os.path.join(self.templates_dir, template_name, "contract.yaml")
        
        if not os.path.exists(template_path):
            print(f"WARNING: Template file not found at {template_path}. Using blank.")
            word_doc = WordDocument()
        else:
            word_doc = WordDocument(template_path)
            
        contract = self._load_contract(contract_path)
        style_map = contract.get("styles", {})
        
        # 2. Add Content
        # We need to handle blocks and figures in order?
        # The Document model splits them. `blocks` contains text logic.
        # Figures are referenced.
        # Simple approach: Iterate blocks. If block links to figure, insert figure?
        # Current logic: Blocks flow. Figures are floating or inline.
        # If we want exact position, we need to know where figures were.
        # `parser.py` extracted figures and text separately.
        # We lost exact figure positions in the Block stream unless we kept a placeholder or block index.
        # We checked figure references in text.
        # Strategy: Append figures at the end (Appendix style) or closest approximation?
        # Better: If we have `block_index` in Figure metadata, we can insert it after that block.
        
        # Merge blocks and figures for insertion
        items_to_insert = []
        
        # Add Blocks
        for block in document.blocks:
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
            items_to_insert.append({
                "type": "figure",
                "index": b_idx + 0.1, 
                "obj": fig,
                "number": i + 1
            })
            
        # Sort by index
        items_to_insert.sort(key=lambda x: x["index"])
        
        # 3. Render
        for item in items_to_insert:
            if item["type"] == "block":
                self._render_block(word_doc, item["obj"], style_map)
            elif item["type"] == "figure":
                self._render_figure(word_doc, item["obj"], item["number"])
                
        return word_doc

    def _load_contract(self, path: str) -> dict:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load contract {path}: {e}")
            return {}

    def _render_block(self, doc, block, style_map):
        # Determine Style
        # Map BlockType -> Word Style
        b_type = block.block_type
        # Use simple string lookup from contract, default to "Normal"
        word_style = style_map.get(b_type, "Normal")
        
        # Heuristics for defaults if not in contract
        if word_style == "Normal":
            if b_type == BlockType.HEADING_1: word_style = "Heading 1"
            elif b_type == BlockType.HEADING_2: word_style = "Heading 2"
            elif b_type == BlockType.HEADING_3: word_style = "Heading 3"
            elif b_type == BlockType.HEADING_4: word_style = "Heading 4"
            elif b_type == BlockType.TITLE: word_style = "Title"
            
        try:
            doc.add_paragraph(block.text, style=word_style)
        except:
            # Fallback if style missing
            doc.add_paragraph(block.text)

    def _render_figure(self, doc, figure: Figure, number: int):
        # 1. Image
        if figure.image_data:
            try:
                image_stream = BytesIO(figure.image_data)
                # Apply layout constraints: Center, 4.0 inches often good default
                doc.add_picture(image_stream, width=Inches(4.0)) 
                
                # Center alignment
                last_p = doc.paragraphs[-1]
                last_p.alignment = 1 # 1 = CENTER
                
            except Exception as e:
                doc.add_paragraph(f"[Image Error: {e}]")
        else:
            doc.add_paragraph(f"[Figure {number} Placeholder]")
            
        # 2. Caption
        # Format: "Figure {number}: {caption_text}"
        if figure.caption_text:
            caption_str = f"Figure {number}: {figure.caption_text}"
            try:
                doc.add_paragraph(caption_str, style="Caption")
            except:
                 doc.add_paragraph(caption_str)

