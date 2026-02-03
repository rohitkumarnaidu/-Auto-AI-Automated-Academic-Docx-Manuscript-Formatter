"""
Caption Matcher - Links figures to their captions.

This module detects caption blocks (e.g., "Figure 1: ...") and associates
them with the nearest Figure object.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from app.models import Document, Block, Figure, BlockType


class CaptionMatcher:
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

    def match_captions(self, document: Document) -> Document:
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
        for fig, cap_block in matches:
            # Update Figure
            fig.caption_text = cap_block.text.strip()
            fig.caption_block_id = cap_block.block_id
            
            # Update Block (Semantic refinement)
            # The prompt says "Do NOT change BlockType". 
            # Wait, "Do NOT change BlockType" is a Rule.
            # But the metadata responsibilities in previous task implied FIGURE_CAPTION exists.
            # And current task checklist says "Update BlockType to FIGURE_CAPTION (optional)".
            # Strict Rule: "Do NOT change BlockType".
            # I will Respect the Rule "Do NOT change BlockType" strictly unless I can justify it.
            # However, semantic correctness suggests it SHOULD be FIGURE_CAPTION.
            # The prompt says "Output: The same Document model with figures linked to captions".
            # Responsibilities: "Attach caption text and block ID to Figure objects".
            # Deliverables section doesn't explicit mention updating BlockType.
            # Rules: "Do NOT change BlockType".
            # OK, checking previous prompt... BlockType enum HAS `FIGURE_CAPTION`.
            # If I leave it as BODY, it's ambiguous.
            # But the Rule is explicit.
            # Maybe the user meant "Don't change types derived from Structure stage UNLESS it's a caption"?
            # Re-reading: "Do NOT change BlockType". This is a negative constraint.
            # I will ONLY update metadata on the Block, and update the Figure object.
            # I will NOT change the BlockType of the caption block itself to avoid violating the rule.
            # Wait, if I don't change BlockType, future stages won't know it's a caption easily.
            # But maybe the Figure object holding the link is enough.
            
            # Correction: Looking at "Responsibilities":
            # "Attach caption text and block ID to Figure objects"
            # It does NOT say "Update block type".
            # I will stick to the rules. I will NOT change BlockType.
            # I will add metadata to the block though.
            
            cap_block.metadata["is_figure_caption"] = True
            cap_block.metadata["linked_figure_id"] = fig.figure_id
            match_count += 1

        # Update processing history
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        document.add_processing_stage(
            stage_name="figure_linking",
            status="success",
            message=f"Linked {match_count} captions to figures",
            duration_ms=duration_ms
        )
        
        document.updated_at = datetime.utcnow()
        
        return document

    def _find_caption_candidates(self, blocks: List[Block]) -> List[int]:
        """
        Find indices of blocks that look like captions.
        """
        candidates = []
        for i, block in enumerate(blocks):
            # Captions are usually BODY or UNKNOWN (if missed), but rarely HEADINGS.
            # We skip headings to reduce false positives (e.g. "Figure 1 Analysis" as a section title).
            if block.is_heading():
                continue
                
            text = block.text.strip()
            if self.caption_pattern.match(text):
                candidates.append(i)
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
        
        # Sort candidates to handle document flow
        candidate_indices.sort()
        
        for cap_idx in candidate_indices:
            caption_block = blocks[cap_idx]
            
            # Find nearest figure
            # We look for figures that:
            # 1. Are close to this block (within max_distance)
            # 2. Ideally appear BEFORE the caption (typical for academic papers)
            # 3. Are not yet assigned
            
            best_figure = None
            min_distance = float('inf')
            
            for figure in figures:
                if figure.figure_id in assigned_figures:
                    continue
                    
                #Get figure location (requires parser to have set this metadata)
                fig_block_idx = figure.metadata.get("block_index")
                if fig_block_idx is None:
                    continue
                
                # Calculated distance (signed) -> negative means figure is above
                # distance = caption_index - figure_block_index
                distance = cap_idx - fig_block_idx
                
                # Check absolute distance
                if abs(distance) <= self.max_distance:
                    # Prefer figures ABOVE (positive distance)
                    # If distance is negative (figure is below caption), penalty?
                    # Some styles have caption above. But mostly below.
                    # We prefer matched proximity first.
                    
                    # Logic: We want the *closest* available figure.
                    # If multiple are equidistant? e.g. Fig A [-1] Caption [+1] Fig B
                    # Usually caption follows figure. distance > 0.
                    
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
    return matcher.match_captions(document)
