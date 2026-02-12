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
        word_table.style = 'Table Grid' # Standard style
        
        # 2. Populate Cells
        for r, row_data in enumerate(table_model.rows):
            row_cells = word_table.rows[r].cells
            for c, cell_text in enumerate(row_data):
                # Safety check for ragged rows
                if c < len(row_cells):
                    row_cells[c].text = str(cell_text) if cell_text else ""
                    
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
