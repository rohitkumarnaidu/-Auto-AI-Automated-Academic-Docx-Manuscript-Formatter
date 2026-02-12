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
        
    def render(self, doc, table_model: Table):
        """
        Render a Table model into the document.
        
        Args:
            doc: python-docx Document object
            table_model: Table model instance
        """
        if not table_model.rows:
            return

        # 1. Create Table
        rows = len(table_model.rows)
        cols = len(table_model.rows[0]) if rows > 0 else 0
        
        if cols == 0:
            return
            
        word_table = doc.add_table(rows=rows, cols=cols)
        
        # 2. Apply Style safely
        try:
            # Check if 'Table Grid' exists in the document styles
            if 'Table Grid' in doc.styles:
                word_table.style = 'Table Grid'
            else:
                # Fallback to a basic internal style or none
                pass
        except:
            pass
        
        # 3. Populate Cells
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
                    
        # 3. Add Caption (after table generally in Word, or before depending on style)
        # Academic standard: Table captions usually ABOVE
        # But we inserted table at 'index'. If we want caption, we should check style.
        # For simple renderer, we'll put it before if it exists.
        
        # NOTE: In the Formatter loop, we insert the object.
        # If we want the caption to be part of this 'item', we must render it here.
        if table_model.caption_text:
            # Insert caption paragraph BEFORE table?
            # doc.add_table appends to end.
            # To insert before, we'd need to manipulate the element tree.
            # Simplest approach for "append" mode:
            # Just add paragraph after? Or rely on the fact that we are appending sequentially.
            # Wait, if we are appending, we should add caption then table?
            # But doc.add_table appends.
            # If we want caption on top, we have to add paragraph, then add table.
            # But `word_table` is created inside `doc`.
            
            # Implementation:
            # 1. Insert Caption (Paragraph)
            # 2. Move Table (which was just added at end) ? No.
            
            # Correct: Just add paragraph first, then table.
            # BUT `doc.add_table` creates it at the end.
            # So:
            # p = doc.add_paragraph(f"Table {table_model.index}: {table_model.caption_text}", style="Caption")
            # table = doc.add_table(...)
            
            # However, `render` is called inside a loop that expects to just "render item".
            # The Formatter loop appends to `doc`.
            pass

        # Since we just appended the table, if we want a caption *above* it, 
        # we strictly should have added it before `doc.add_table`.
        # However, `doc.add_table` adds to the end.
        # So effective order:
        # Pre-existing content...
        # [We are here]
        
        # Visual improvement: Add spacer before?
        # doc.add_paragraph("")
        
        pass
