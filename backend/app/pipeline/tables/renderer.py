"""
Table Renderer - Renders Table models into python-docx tables.
"""

from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.models import Table

class TableRenderer:
    """
    Renders Table objects into a Word document.
    """
    
    def __init__(self):
        pass
        
    def render(self, doc, table_model: Table, number: int = None):
        """
        Render a Table model into the document with caption.
        
        Args:
            doc: python-docx Document object
            table_model: Table model instance
            number: Sequential table number (1, 2, 3...) for caption
        """
        if not table_model.rows:
            return

        # 1. ADD CAPTION FIRST (if exists) - Academic standard: caption ABOVE table
        if table_model.caption_text:
            caption_p = doc.add_paragraph(style="Caption")
            # Use sequential number if provided, otherwise fall back to index+1
            table_num = number if number is not None else (table_model.index + 1)
            
            # Check if caption already starts with "Table N:" to avoid duplication
            caption_lower = table_model.caption_text.lower().strip()
            if caption_lower.startswith(f"table {table_num}:"):
                # Caption already has prefix, just add it as-is with bold prefix
                run = caption_p.add_run(f"Table {table_num}: ")
                run.bold = True
                # Add the rest after the prefix
                rest_text = table_model.caption_text[len(f"Table {table_num}:"):].strip()
                caption_p.add_run(rest_text)
            else:
                # Caption doesn't have prefix, add it
                run = caption_p.add_run(f"Table {table_num}: ")
                run.bold = True
                caption_p.add_run(table_model.caption_text)
            caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 2. CREATE TABLE
        rows = len(table_model.rows)
        cols = len(table_model.rows[0]) if rows > 0 else 0
        
        if cols == 0:
            return
            
        word_table = doc.add_table(rows=rows, cols=cols)
        
        # 3. APPLY STYLE SAFELY
        try:
            # Check if 'Table Grid' exists in the document styles
            if 'Table Grid' in doc.styles:
                word_table.style = 'Table Grid'
            else:
                # Fallback to a basic internal style or none
                pass
        except:
            pass
        
        # 4. POPULATE CELLS
        # We iterate over model cells to handle metadata and potentially nested content
        for cell_model in table_model.cells:
            r, c = cell_model.row, cell_model.col
            if r < len(word_table.rows) and c < len(word_table.rows[r].cells):
                word_cell = word_table.rows[r].cells[c]
                
                # Set text
                word_cell.text = cell_model.text if cell_model.text else ""
                
                # RECURSIVE RENDERING: Check for nested tables
                nested_tables = cell_model.metadata.get("nested_tables", [])
                for nested_tbl in nested_tables:
                    # python-docx cells support add_table in modern versions
                    try:
                        self.render(word_cell, nested_tbl)
                    except Exception as e:
                        # Fallback: maybe add as text if rendering fails
                        word_cell.add_paragraph(f"[Nested Table: {nested_tbl.table_id}]")
                        print(f"  [Warning] Nested table rendering failed: {e}")

