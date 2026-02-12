"""
Table Caption Matcher - Production Grade Stage 3 Component.
Links extracted Table objects to their corresponding caption blocks.
"""

import re
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from app.models import PipelineDocument as Document, Block, BlockType, Table
from app.pipeline.base import PipelineStage

class TableCaptionMatcher(PipelineStage):
    """
    Production-safe, deterministic, real-time table caption matcher.
    
    Logic:
    - Identifies potential caption blocks starting with "Table" (case-insensitive).
    - Matches tables to captions within a proximity window (-2 above, +1 below).
    - Guarantees O(n) performance and respects structural boundaries.
    """
    
    def __init__(self, search_window_above: int = 2, search_window_below: int = 1):
        """
        Initialize the matcher.
        
        Args:
            search_window_above: Max blocks above table to search.
            search_window_below: Max blocks below table to search.
        """
        self.search_window_above = search_window_above
        self.search_window_below = search_window_below
        
        # Regex for common table caption patterns (Production Grade)
        # Matches: "Table 1:", "TABLE 2. Results", "Table 3 – Performance", 
        # "Table 1.1:...", "Table I:...", "Table A:..."
        # Case-insensitive per requirements.
        self.caption_regex = re.compile(
            r'^\s*Table\s+([0-9]+(\.[0-9]+)*|[IVXLCDM]+|[A-Z])([\s\.\:–-].*)?$',
            re.IGNORECASE
        )

    def process(self, document: Document) -> Document:
        """
        Match captions to tables in the document.
        
        Args:
            document: Document with tables and blocks
            
        Returns:
            Document with linked tables
        """
        start_time = datetime.utcnow()
        
        blocks = document.blocks
        tables = document.tables
        
        if not tables or not blocks:
            return document
            
        # 1. Performance Optimization: O(n) mapping of block_index -> Block
        # We also filter out Headings and References as per requirements.
        # Find References start index to avoid matching inside references.
        ref_start_idx = self._find_references_start_index(blocks)
        
        block_map: Dict[int, Block] = {}
        for block in blocks:
            # Requirements: "Do NOT match: References, Headings"
            # We skip those during candidate mapping
            if block.is_heading() or block.block_type == BlockType.REFERENCES_HEADING:
                continue
            
            # Skip if inside References section
            if ref_start_idx is not None and block.index >= ref_start_idx:
                continue
                
            block_map[block.index] = block

        # FORENSIC FIX: Use logical position search instead of raw index arithmetic
        # With Step-100 sparse indices, raw arithmetic fails (e.g., caption at 1100, table at 1201)
        # Create list_index_map to convert parser indices to logical positions
        list_index_map: Dict[int, int] = {block.index: i for i, block in enumerate(blocks)}
        
        # Initialize matching state
        assigned_block_ids: Dict[str, bool] = {}
        match_count = 0
        
        # Map table indices to avoid crossing tables
        table_indices = sorted([t.block_index for t in tables])
        
        for table in tables:
            table_idx = table.block_index
            
            # Convert table index to logical position
            if table_idx not in list_index_map:
                # Table index not in blocks list (expected - tables are separate)
                # Find nearest block position for window calculation
                table_list_pos = None
                for i, block in enumerate(blocks):
                    if block.index >= table_idx:
                        table_list_pos = i
                        break
                if table_list_pos is None:
                    table_list_pos = len(blocks) - 1
            else:
                table_list_pos = list_index_map[table_idx]
            
            # Find bounds for this table (do not cross another table)
            prev_table_idx = -1
            next_table_idx = float('inf')
            curr_pos = table_indices.index(table_idx)
            if curr_pos > 0:
                prev_table_idx = table_indices[curr_pos - 1]
            if curr_pos < len(table_indices) - 1:
                next_table_idx = table_indices[curr_pos + 1]
            
            # Calculate search window in LOGICAL POSITIONS (not raw indices)
            lower_pos = max(0, table_list_pos - self.search_window_above)
            upper_pos = min(len(blocks) - 1, table_list_pos + self.search_window_below)
            
            best_caption = None
            min_dist = float('inf')
            
            # Scan candidates in logical position window
            for pos in range(lower_pos, upper_pos + 1):
                candidate = blocks[pos]
                
                # Skip if already assigned
                if candidate.block_id in assigned_block_ids:
                    continue
                
                # Skip headings and references (already filtered in block_map, but double-check)
                if candidate.is_heading() or candidate.block_type == BlockType.REFERENCES_HEADING:
                    continue
                
                # Skip if inside References section
                if ref_start_idx is not None and candidate.index >= ref_start_idx:
                    continue
                
                # Skip if candidate index is beyond table boundaries (cross-table protection)
                if candidate.index <= prev_table_idx or candidate.index >= next_table_idx:
                    continue
                
                text = candidate.text.strip()
                if self.caption_regex.match(text):
                    # Calculate logical distance (position-based, not index-based)
                    dist = abs(pos - table_list_pos)
                    
                    # Tie-breaker: Prefer Above (standard for tables) if equidistant
                    if dist < min_dist:
                        min_dist = dist
                        best_caption = candidate
                    elif dist == min_dist and pos < table_list_pos:
                        # Prefer Above
                        best_caption = candidate

            # 3. Apply Links
            if best_caption:
                table.caption_text = best_caption.text.strip()
                table.caption_block_id = best_caption.block_id
                
                # Rule: Update Block Metadata as requested in master prompt
                best_caption.block_type = BlockType.TABLE_CAPTION
                best_caption.metadata["linked_table_id"] = table.table_id
                best_caption.metadata["classification_method"] = "deterministic_table_caption_rule"
                
                assigned_block_ids[best_caption.block_id] = True
                match_count += 1
            else:
                # MARK MISSING as requested
                if not table.caption_text:
                    table.metadata["caption_status"] = "Missing"

        # 4. Final Processing History Update
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        document.add_processing_stage(
            stage_name="table_caption_matching",
            status="success",
            message=f"Linked {match_count} captions to tables",
            duration_ms=duration_ms
        )
        
        return document

    def _find_references_start_index(self, blocks: List[Block]) -> Optional[int]:
        """Utility to find start of References section based on BlockType or keywords."""
        for block in blocks:
            if block.block_type == BlockType.REFERENCES_HEADING:
                return block.index
            
            # Fallback keyword match if classifier hasn't run or missed it
            text = block.text.strip().lower()
            if text in ["references", "bibliography", "works cited"] and block.is_heading():
                return block.index
        return None

# Convenience function for orchestrator
def match_table_captions(document: Document) -> Document:
    matcher = TableCaptionMatcher()
    return matcher.process(document)
