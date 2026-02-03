"""
Structure Detector - Main orchestrator for structure detection.

This module coordinates heading detection, level inference, and section identification.
It enriches blocks with structure metadata without changing block types (remain UNKNOWN).

Input: Normalized Document
Output: Document with structure hints attached to blocks
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from statistics import mean, median

from app.models import Document, Block
from .heading_rules import analyze_heading_candidate
from .position_rules import analyze_position, boost_heading_confidence_by_position


class StructureDetector:
    """
    Detects document structure through rule-based heuristics.
    
    This stage identifies:
    - Heading candidates
    - Heading levels (1-4)
    - Section boundaries
    - Parent-child relationships
    
    IMPORTANT: Does NOT assign semantic block types (they remain UNKNOWN).
    Only attaches metadata for later classification stage.
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.avg_font_size: Optional[float] = None
        self.detected_headings: List[Dict[str, Any]] = []
    
    def detect(self, document: Document) -> Document:
        """
        Detect structure in a normalized document.
        
        This enriches blocks with structure metadata:
        - level: heading level (1-4)
        - is_heading_candidate: bool
        - section_name: inferred section name
        - parent_id: parent heading block ID
        
        Args:
            document: Normalized document
        
        Returns:
            Document with structure metadata attached to blocks
        """
        start_time = datetime.utcnow()
        
        # Step 1: Calculate average font size for comparison
        self.avg_font_size = self._calculate_avg_font_size(document.blocks)
        
        # Step 2: Detect heading candidates
        heading_candidates = self._detect_heading_candidates(document.blocks)
        
        # Step 3: Assign section names based on headings
        self._assign_section_names(document.blocks, heading_candidates)
        
        # Step 4: Build parent-child relationships
        self._build_hierarchy(document.blocks, heading_candidates)
        
        # Update processing history
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        num_headings = len(heading_candidates)
        num_sections = len(set(b.section_name for b in document.blocks if b.section_name))
        
        document.add_processing_stage(
            stage_name="structure_detection",
            status="success",
            message=f"Detected {num_headings} headings, {num_sections} sections",
            duration_ms=duration_ms
        )
        
        document.updated_at = datetime.utcnow()
        
        # Store detected headings for debugging
        self.detected_headings = heading_candidates
        
        return document
    
    def _calculate_avg_font_size(self, blocks: List[Block]) -> Optional[float]:
        """
        Calculate average font size in document.
        
        This is used to detect font size outliers (potential headings).
        
        Args:
            blocks: All blocks in document
        
        Returns:
            Average font size, or None if no blocks have font size
        """
        font_sizes = []
        for block in blocks:
            if block.style.font_size and block.text.strip():
                font_sizes.append(block.style.font_size)
        
        if not font_sizes:
            return None
        
        # Use median instead of mean to avoid outlier influence
        return median(font_sizes)
    
    def _detect_heading_candidates(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """
        Detect all heading candidates in the document.
        
        This combines text/style heuristics with positional cues.
        
        Args:
            blocks: All blocks in document (in order)
        
        Returns:
            List of detected headings with metadata
            Each entry: {
                "block": Block,
                "block_id": str,
                "level": int,
                "confidence": float,
                "reasons": list of str
            }
        """
        candidates = []
        
        for block in blocks:
            # Skip empty blocks
            if not block.text.strip():
                continue
            
            # Analyze heading potential (text + style)
            heading_info = analyze_heading_candidate(block, self.avg_font_size)
            
            if heading_info is None:
                continue
            
            # Analyze position
            position_info = analyze_position(block, blocks)
            
            # Boost confidence based on position
            final_confidence = boost_heading_confidence_by_position(
                heading_info["confidence"],
                position_info
            )
            
            # Combine reasons
            all_reasons = heading_info["reasons"] + position_info["position_hints"]
            
            # Update block metadata (but keep BlockType.UNKNOWN!)
            block.level = heading_info["level"]
            block.metadata["is_heading_candidate"] = True
            block.metadata["heading_confidence"] = final_confidence
            block.metadata["heading_reasons"] = all_reasons
            
            if heading_info["has_numbering"]:
                block.metadata["numbering_info"] = heading_info["numbering_info"]
            
            # Store candidate
            candidates.append({
                "block": block,
                "block_id": block.block_id,
                "level": heading_info["level"],
                "confidence": final_confidence,
                "reasons": all_reasons,
                "position_info": position_info
            })
        
        return candidates
    
    def _assign_section_names(
        self,
        blocks: List[Block],
        heading_candidates: List[Dict[str, Any]]
    ) -> None:
        """
        Assign section names to all blocks based on detected headings.
        
        Blocks inherit the section name from the most recent heading before them.
        
        Args:
            blocks: All blocks in document
            heading_candidates: Detected headings
        """
        # Build a mapping of block_id -> heading info
        heading_map = {h["block_id"]: h for h in heading_candidates}
        
        current_section = None
        
        for block in blocks:
            # If this block is a heading, update current section
            if block.block_id in heading_map:
                heading = heading_map[block.block_id]
                
                # Use block text as section name (cleaned)
                section_name = block.text.strip()
                
                # Remove numbering if present
                if "numbering_info" in block.metadata:
                    numbering_info = block.metadata["numbering_info"]
                    section_name = numbering_info.get("remainder", section_name)
                
                current_section = section_name
                block.section_name = current_section
            else:
                # Non-heading block inherits current section
                if current_section:
                    block.section_name = current_section
    
    def _build_hierarchy(
        self,
        blocks: List[Block],
        heading_candidates: List[Dict[str, Any]]
    ) -> None:
        """
        Build parent-child relationships between headings.
        
        A heading's parent is the nearest preceding heading with a lower level number
        (e.g., level 2's parent is the nearest level 1).
        
        Args:
            blocks: All blocks in document
            heading_candidates: Detected headings
        """
        # Build list of headings in order
        heading_stack: List[Dict[str, Any]] = []
        
        for block in blocks:
            # Check if this block is a heading
            heading_info = next(
                (h for h in heading_candidates if h["block_id"] == block.block_id),
                None
            )
            
            if heading_info is None:
                continue
            
            current_level = heading_info["level"]
            
            # Find parent: nearest heading with lower level number
            parent_id = None
            for i in range(len(heading_stack) - 1, -1, -1):
                if heading_stack[i]["level"] < current_level:
                    parent_id = heading_stack[i]["block_id"]
                    break
            
            # Set parent
            if parent_id:
                block.parent_id = parent_id
            
            # Update stack: remove headings at same or lower level
            heading_stack = [h for h in heading_stack if h["level"] < current_level]
            heading_stack.append(heading_info)


# Convenience function
def detect_structure(document: Document) -> Document:
    """
    Detect structure in a normalized document.
    
    This is a convenience wrapper around StructureDetector.
    
    Args:
        document: Normalized document
    
    Returns:
        Document with structure metadata
    
    Example:
        >>> from app.pipeline.parsing import parse_docx
        >>> from app.pipeline.normalization import normalize_document
        >>> from app.pipeline.structure_detection import detect_structure
        >>> 
        >>> doc = parse_docx("manuscript.docx", "job_123")
        >>> doc = normalize_document(doc)
        >>> doc = detect_structure(doc)
        >>> 
        >>> # Check detected structure
        >>> headings = [b for b in doc.blocks if b.metadata.get("is_heading_candidate")]
        >>> print(f"Found {len(headings)} headings")
    """
    detector = StructureDetector()
    return detector.detect(document)
