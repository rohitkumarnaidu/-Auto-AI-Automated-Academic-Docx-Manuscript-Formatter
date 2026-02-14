"""
Caption Matcher - Links figures to their captions.

This module detects caption blocks (e.g., "Figure 1: ...") and associates
them with the nearest Figure object.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from app.pipeline.base import PipelineStage

class CaptionMatcher(PipelineStage):
    """
    Links figures to their captions based on proximity and text patterns.
    
    Logic:
    1. Identify caption candidates using regex (BlockType is usually BODY).
    2. Identify figures (already extracted).
    3. Match each caption to the nearest figure, preferring the one immediately
       ABOVE the caption (standard academic style).
    4. Link them:
       - Figure gets `caption_text` and `caption_block_id`.
       - Block gets `BlockType.FIGURE_CAPTION` (if semantic update is allowed/safe).
    """
    
    def __init__(self, max_distance: int = 2):
        """
        Initialize the matcher.
        
        Args:
            max_distance: Max number of blocks between figure and caption to consider a match.
        """
        self.max_distance = max_distance
        # Regex for common caption patterns (case-insensitive)
        # Matches: "Figure 1.", "Fig. 2:", "Figure 3-a"
        self.caption_pattern = re.compile(
            r'^(?:Figure|Fig\.?)\s+\d+[a-zA-Z0-9\.]*', 
            re.IGNORECASE
        )

    def process(self, document: Document) -> Document:
        """
        Match specific figures to captions in the document.
        
        Args:
            document: Document with figures and classified blocks
            
        Returns:
            Document with linked figures
        """
        start_time = datetime.utcnow()
        
        blocks = document.blocks
        figures = document.figures
        
        if not figures:
            return document
            
        # 1. Detect Caption Candidates
        caption_candidates = self._find_caption_candidates(blocks)
        
        # 2. Match Figures to Captions
        matches = self._match_candidates(blocks, figures, caption_candidates)
        
        # 3. Apply Links
        match_count = 0
        vision_enhanced = 0
        
        for fig, cap_block in matches:
            # Update Figure
            fig.caption_text = cap_block.text.strip()
            fig.caption_block_id = cap_block.block_id
            
            # Update Block metadata
            cap_block.metadata["is_figure_caption"] = True
            cap_block.metadata["linked_figure_id"] = fig.figure_id
            match_count += 1
        
        # 4. (NEW) Vision Analysis Enhancement
        if self.enable_vision and self.vision_client:
            vision_enhanced = self._enhance_captions_with_vision(figures)
        
        # Update processing history
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        message = f"Linked {match_count} captions to figures"
        if vision_enhanced > 0:
            message += f", enhanced {vision_enhanced} with vision analysis"
        
        document.add_processing_stage(
            stage_name="figure_linking",
            status="success",
            message=message,
            duration_ms=duration_ms
        )
        
        document.updated_at = datetime.utcnow()
        
        return document

    def _find_caption_candidates(self, blocks: List[Block]) -> List[int]:
        """
        Find parser indices of blocks that look like captions.
        """
        candidates = []
        for block in blocks:
            # Captions are usually BODY or UNKNOWN (if missed), but rarely HEADINGS.
            # We skip headings to reduce false positives (e.g. "Figure 1 Analysis" as a section title).
            if block.is_heading():
                continue
                
            text = block.text.strip()
            if self.caption_pattern.match(text):
                candidates.append(block.index)
        return candidates

    def _match_candidates(self, 
                         blocks: List[Block], 
                         figures: List[Figure], 
                         candidate_indices: List[int]) -> List[Tuple[Figure, Block]]:
        """
        Match detected caption blocks to figures.
        """
        matches = []
        assigned_figures: Dict[str, bool] = {} # Keep track of matched figures
        
        # Create block_map for O(1) lookup by parser index
        block_map: Dict[int, Block] = {block.index: block for block in blocks}
        
        # Create a list index map to calculate "Logical Distance" (number of blocks between)
        # This makes the matcher resilient to arbitrary index steps (e.g. 100)
        list_index_map: Dict[int, int] = {block.index: i for i, block in enumerate(blocks)}
        
        # Sort candidates to handle document flow
        candidate_indices.sort()
        
        for cap_idx in candidate_indices:
            caption_block = block_map.get(cap_idx)
            if not caption_block or cap_idx not in list_index_map:
                continue
            
            best_figure = None
            min_distance = float('inf')
            
            cap_list_idx = list_index_map[cap_idx]
            
            for figure in figures:
                if figure.figure_id in assigned_figures:
                    continue
                    
                fig_block_idx = figure.metadata.get("block_index")
                if fig_block_idx is None or fig_block_idx not in list_index_map:
                    continue
                
                # Logical distance = caption_list_pos - figure_list_pos
                distance = cap_list_idx - list_index_map[fig_block_idx]
                
                # Check absolute distance against max_distance (threshold in blocks)
                if abs(distance) <= self.max_distance:
                    current_dist_abs = abs(distance)
                    
                    if current_dist_abs < min_distance:
                        min_distance = current_dist_abs
                        best_figure = figure
                    elif current_dist_abs == min_distance:
                        # Tie-breaker: Prefer figure ABOVE the caption (distance > 0)
                        if distance > 0:
                            best_figure = figure
                            
            if best_figure:
                matches.append((best_figure, caption_block))
                assigned_figures[best_figure.figure_id] = True
                
        return matches

# Convenience function
def link_figures(document: Document) -> Document:
    matcher = CaptionMatcher()
    return matcher.process(document)
