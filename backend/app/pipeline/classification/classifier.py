"""
Content Classifier - Assigns semantic types to blocks.

This module determines the semantic role of each block (Title, Author,
Heading, Body, etc.) based on the structure detected in the previous stage.

Input: Document with structure metadata (headings, sections)
Output: Document with BlockType assigned
"""

import re
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from app.models import Document, Block, BlockType


class ContentClassifier:
    """
    Assigns semantic BlockTypes to blocks based on structure and heuristics.
    
    Rules:
    - Headings identified in structure detection get HEADING_* types (or specific ones like ABSTRACT_HEADING)
    - Content between headings gets BODY type (or specific ones like ABSTRACT_BODY)
    - Front matter (before first section) is analyzed for Title, Author, Affiliation
    - References section gets REFERENCE_ENTRY types
    """
    
    def __init__(self):
        """Initialize the classifier."""
        # Keywords that indentify specific section types
        self.abstract_keywords = {"abstract"}
        self.keywords_keywords = {"keywords", "key words"}
        self.references_keywords = {"references", "bibliography", "works cited"}
        
        # Heuristics for affiliation detection
        self.affiliation_indicators = {
            "university", "college", "department", "institute", "school", 
            "laboratory", "center", "centre", "hospital", "clinic",
            "corp", "inc", "ltd", "gmbh", "foundation", "limited",
            "road", "st.", "street", "ave", "avenue", "box",
            "email", "@", "ph.", "fax", "tel"
        }

    def classify(self, document: Document) -> Document:
        """
        Classify all blocks in the document.
        
        Args:
            document: Document with structure detection results
        
        Returns:
            Document with updated BlockTypes
        """
        start_time = datetime.utcnow()
        
        blocks = document.blocks
        if not blocks:
            return document
            
        # 1. Identify key structural landmarks
        first_section_index = self._find_first_section_index(blocks)
        references_start_index = self._find_references_start_index(blocks)
        
        # 2. Iterate and classify based on zones
        # Zone 1: Front Matter (Start -> First Section)
        self._classify_front_matter(blocks, 0, first_section_index)
        
        # Zone 2: Body (First Section -> References)
        # If references not found, go to end
        body_end = references_start_index if references_start_index is not None else len(blocks)
        self._classify_body(blocks, first_section_index, body_end)
        
        # Zone 3: References (References -> End)
        if references_start_index is not None:
            self._classify_references(blocks, references_start_index, len(blocks))
            
        # 3. Post-processing / Validation
        # Ensure no UNKNOWN remains (default to BODY if needed, though logic should cover it)
        count_unknown = 0
        for block in blocks:
            if block.block_type == BlockType.UNKNOWN:
                # Default fallback
                block.block_type = BlockType.BODY
                block.metadata["classification_method"] = "fallback"
                count_unknown += 1
                
        # Update processing history
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        document.add_processing_stage(
            stage_name="classification",
            status="success",
            message=f"Classified {len(blocks)} blocks",
            duration_ms=duration_ms
        )
        
        document.updated_at = datetime.utcnow()
        
        return document
    
    def _find_first_section_index(self, blocks: List[Block]) -> int:
        """Find the index of the first heading block."""
        for i, block in enumerate(blocks):
            if block.metadata.get("is_heading_candidate"):
                return i
        return len(blocks)  # No sections found
        
    def _find_references_start_index(self, blocks: List[Block]) -> Optional[int]:
        """Find the index of the References heading."""
        for i, block in enumerate(blocks):
            if not block.metadata.get("is_heading_candidate"):
                continue
                
            # Check section name or text
            section = (block.section_name or "").lower()
            text = block.text.strip().lower()
            
            # Simple check
            if any(k in section for k in self.references_keywords) or \
               any(k in text for k in self.references_keywords):
                
                # Verify it's not a generic sentence like "See references for more info"
                # Headings usually short.
                if len(text) < 50:
                    return i
        return None

    def _classify_front_matter(self, blocks: List[Block], start_idx: int, end_idx: int):
        """
        Classify blocks before the first section heading.
        Types: TITLE, AUTHOR, AFFILIATION
        """
        if start_idx >= end_idx:
            return

        # Find first non-empty block -> TITLE
        title_found = False
        
        for i in range(start_idx, end_idx):
            block = blocks[i]
            text = block.text.strip()
            
            if not text:
                continue
                
            if not title_found:
                # First non-empty block is the TITLE
                block.block_type = BlockType.TITLE
                title_found = True
                block.metadata["classification_method"] = "position_front_first"
            else:
                # Subsequent blocks: AUTHOR or AFFILIATION
                # Heuristic: Affiliations look like addresses or have specific keywords
                is_affiliation = self._is_likely_affiliation(text)
                
                if is_affiliation:
                    block.block_type = BlockType.AFFILIATION
                else:
                    block.block_type = BlockType.AUTHOR
                
                block.metadata["classification_method"] = "heuristic_front"

    def _classify_body(self, blocks: List[Block], start_idx: int, end_idx: int):
        """
        Classify blocks in the main body.
        Types: HEADING_*, BODY, ABSTRACT_*, KEYWORDS_*
        """
        current_section_type = "generic" # generic, abstract, keywords
        
        for i in range(start_idx, end_idx):
            block = blocks[i]
            text = block.text.strip()
            
            # 1. Is it a Heading?
            if block.metadata.get("is_heading_candidate"):
                level = block.metadata.get("level", 1)  # Default to 1 if missing
                
                # Determine specific heading type based on text/section
                # Use the clean section name which should have been set by structure detector
                section_name = (block.section_name or "").lower()
                
                if any(k in section_name for k in self.abstract_keywords):
                    block.block_type = BlockType.ABSTRACT_HEADING
                    current_section_type = "abstract"
                elif any(k in section_name for k in self.keywords_keywords):
                    block.block_type = BlockType.KEYWORDS_HEADING
                    current_section_type = "keywords"
                else:
                    # Regular heading
                    if level == 1:
                        block.block_type = BlockType.HEADING_1
                    elif level == 2:
                        block.block_type = BlockType.HEADING_2
                    elif level == 3:
                        block.block_type = BlockType.HEADING_3
                    else:
                        block.block_type = BlockType.HEADING_4
                    
                    current_section_type = "generic"
                
                block.metadata["classification_method"] = "structure_heading"
                
            # 2. It is Content (Body)
            else:
                if not text:
                    # Empty blocks default to BODY for now (spacer)
                    block.block_type = BlockType.BODY
                    continue
                    
                # Assign type based on current section context
                if current_section_type == "abstract":
                    block.block_type = BlockType.ABSTRACT_BODY
                elif current_section_type == "keywords":
                    block.block_type = BlockType.KEYWORDS_BODY
                else:
                    block.block_type = BlockType.BODY
                
                block.metadata["classification_method"] = "structure_context"

    def _classify_references(self, blocks: List[Block], start_idx: int, end_idx: int):
        """
        Classify blocks in the references section.
        Types: REFERENCES_HEADING, REFERENCE_ENTRY
        """
        # First block is the heading
        if start_idx < end_idx:
            heading_block = blocks[start_idx]
            heading_block.block_type = BlockType.REFERENCES_HEADING
            heading_block.metadata["classification_method"] = "structure_ref_heading"
            
            # Subsequent blocks are entries
            for i in range(start_idx + 1, end_idx):
                block = blocks[i]
                if block.text.strip():
                    # Check if it looks like a sub-heading?
                    # Generally in refs, everything else is an entry unless it's a new main section
                    # But we assume the refs section goes to the end or next main header.
                    # Given `_classify_references` is called with a specific range, we assume it's safe.
                    
                    # Exception: If we accidentally swallowed an Appendix heading because we went to len(blocks).
                    # But `_classify_body` only went up to `references_start_index`.
                    # Does `_classify_references` need to stop at next heading?
                    # structure_detection doesn't explicitly guarantee "References" is last.
                    # But typically it is.
                    # Let's check if this block is a LEVEL 1 Heading which is NOT references.
                    if block.metadata.get("is_heading_candidate"):
                        # If it's a heading inside references, is it an Appendix?
                        # If detecting structure marked it as a heading, we should respect that?
                        # But `references_start_index` find logic was simple.
                        # Let's assume for now Reference section contains entries.
                        # If we encounter a LEVEL 1 heading, we might want to switch back to normal classification?
                        # For simplicity/robustness, we'll treat structure headings as headings still, 
                        # but if they are small (Level 2+), maybe they are groups in refs.
                        # If Level 1, probably new section.
                        
                        if block.level == 1:
                            # It's a new main section (e.g. Appendix)
                            # Fallback to standard heading classification
                            block.block_type = BlockType.HEADING_1
                            if "appendix" in block.text.lower():
                                block.block_type = BlockType.HEADING_1 # Or specific if we had it
                            continue # Don't mark as reference entry
                    
                    block.block_type = BlockType.REFERENCE_ENTRY
                    block.metadata["classification_method"] = "structure_ref_entry"
                else:
                    block.block_type = BlockType.BODY # Spacer

    def _is_likely_affiliation(self, text: str) -> bool:
        """
        Check if text looks like an affiliation/address.
        """
        text_lower = text.lower()
        
        # Check explicit keywords
        for indicator in self.affiliation_indicators:
            if indicator in text_lower:
                return True
                
        # Check pattern: City, Country
        # (Very simple heuristic)
        if "," in text and len(text.split(",")) > 2:
            return True
            
        return False


# Convenience function
def classify_content(document: Document) -> Document:
    """
    Classify content in a structured document.
    
    Args:
        document: Document to classify
    
    Returns:
        Document with classified blocks
    """
    classifier = ContentClassifier()
    return classifier.classify(document)
