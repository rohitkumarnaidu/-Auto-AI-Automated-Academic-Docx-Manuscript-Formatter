"""
Table Model - Represents a table with rows, columns, and data.

Tables are extracted by the tables/ pipeline stage.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TableCell(BaseModel):
    """Represents a single cell in a table."""
    
    row: int = Field(..., description="Row index (0-based)")
    col: int = Field(..., description="Column index (0-based)")
    text: str = Field(default="", description="Cell text content")
    
    # Spanning information
    rowspan: int = Field(default=1, description="Number of rows this cell spans")
    colspan: int = Field(default=1, description="Number of columns this cell spans")
    
    # Styling
    is_header: bool = Field(default=False, description="Whether this cell is a header")
    bold: bool = Field(default=False, description="Bold text")
    italic: bool = Field(default=False, description="Italic text")
    alignment: Optional[str] = Field(
        default=None,
        description="Text alignment (left, center, right)"
    )
    
    class Config:
        frozen = True


class Table(BaseModel):
    """
    Represents a table in the document.
    
    Tables are extracted with their structure and content.
    Captions may appear above or below the table.
    """
    
    # Unique identifier
    table_id: str = Field(..., description="Unique identifier (e.g., 'tbl_001')")
    
    # Sequential numbering (assigned by formatting stage)
    number: Optional[int] = Field(
        default=None,
        description="Sequential table number in document (e.g., 1 for 'Table 1')"
    )
    
    # Table structure
    num_rows: int = Field(..., description="Total number of rows")
    num_cols: int = Field(..., description="Total number of columns")
    
    # Table data
    cells: List[TableCell] = Field(
        default_factory=list,
        description="List of all table cells"
    )
    
    # Table data (Source of Truth)
    data: List[List[str]] = Field(
        default_factory=list,
        description="2D array representation of table (row-major order). data[row][col] = text"
    )
    
    # Backward compatibility
    rows: List[List[str]] = Field(
        default_factory=list,
        description="2D array representation of table (row-major order)"
    )
    
    # Header information
    has_header: bool = Field(
        default=False,
        description="Whether the table has a header row"
    )
    has_header_row: bool = Field(
        default=False,
        description="Whether first row is a header"
    )
    has_header_col: bool = Field(
        default=False,
        description="Whether first column is a header"
    )
    header_rows: int = Field(
        default=0,
        description="Number of header rows"
    )
    
    # Position in document
    page_number: Optional[int] = Field(
        default=None,
        description="Page where table appears"
    )
    index: int = Field(
        ...,
        description="Sequential position among all tables (0-based)"
    )
    block_index: int = Field(
        ...,
        description="Global block index in document order (shared with text blocks)"
    )
    
    # Caption information
    caption_text: Optional[str] = Field(
        default=None,
        description="Full caption text (e.g., 'Table 1: Experimental Results')"
    )
    caption_block_id: Optional[str] = Field(
        default=None,
        description="Block ID of the caption block"
    )
    caption_position: Optional[str] = Field(
        default=None,
        description="Caption position relative to table (above, below)"
    )
    
    # Parsed caption components
    label: Optional[str] = Field(
        default=None,
        description="Table label (e.g., 'Table 1', 'Table I')"
    )
    title: Optional[str] = Field(
        default=None,
        description="Descriptive title from caption"
    )
    
    # Cross-references
    referenced_by: List[str] = Field(
        default_factory=list,
        description="List of block IDs that reference this table"
    )
    
    # Section context
    section_name: Optional[str] = Field(
        default=None,
        description="Section where this table appears"
    )
    
    # Validation
    is_valid: bool = Field(
        default=True,
        description="Whether table passed validation"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Validation warnings (e.g., missing caption, inconsistent columns)"
    )
    
    # Formatting metadata
    placement: Optional[str] = Field(
        default=None,
        description="Placement preference (e.g., 'top', 'bottom', 'here')"
    )
    style: Optional[str] = Field(
        default=None,
        description="Table style (e.g., 'grid', 'simple', 'booktabs')"
    )
    
    # Extensibility
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True
    
    def has_caption(self) -> bool:
        """Check if table has an associated caption."""
        return self.caption_text is not None and len(self.caption_text.strip()) > 0
    
    def get_cell(self, row: int, col: int) -> Optional[TableCell]:
        """Get cell at specified row and column."""
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        return None
    
    def get_display_label(self) -> str:
        """Get display label for this table."""
        if self.label:
            return self.label
        if self.number:
            return f"Table {self.number}"
        return f"Table {self.table_id}"
    
    def get_row_data(self, row: int) -> List[str]:
        """Get all cell text for a specific row."""
        if row < len(self.rows):
            return self.rows[row]
        return []
