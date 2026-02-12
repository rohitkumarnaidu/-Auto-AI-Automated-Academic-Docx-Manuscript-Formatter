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

from app.models import PipelineDocument as Document, Block, BlockType
from app.pipeline.base import PipelineStage

class ContentClassifier(PipelineStage):
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
        self.abstract_keywords = ["abstract", "summary", "resumen", "résumé"]
        self.keywords_keywords = ["keywords", "key words", "palabras clave", "mots-clés"]
        self.acknowledgements_keywords = ["acknowledgements", "acknowledgments", "funding", "conflicts of interest", "author contributions", "declaration of interest"]
        self.references_keywords = {"references", "bibliography", "works cited"}
        
        # Heuristics for affiliation detection
        self.affiliation_indicators = {
            "university", "college", "department", "institute", "school", 
            "laboratory", "center", "centre", "hospital", "clinic",
            "corp", "inc", "ltd", "gmbh", "foundation", "limited",
            "road", "st.", "street", "ave", "avenue", "box",
            "email", "@", "ph.", "fax", "tel"
        }
        
        # Keywords that exclude a block from being an AUTHOR
        self.author_exclusion_keywords = {
            "university", "college", "department", "institute", "school", 
            "laboratory", "center", "centre", "division"
        }

    def process(self, document: Document) -> Document:
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
        
        # State for classification logic
        title_found = False
        current_section_type = "generic" # generic, abstract, keywords
        
        # 2. Main Classification Loop
        for i, block in enumerate(blocks):
            # A) HARD ISOLATION GUARD: Skip protected structural blocks
            # These must never receive semantic semantic BlockType assignments
            if (block.metadata.get("is_header") or 
                block.metadata.get("is_footer") or 
                block.metadata.get("is_footnote") or 
                block.metadata.get("is_endnote")):
                continue

            # B) PROTECTED TYPE GUARD: Title fixed per structure detector
            # TITLE is authoritative from Stage 1/Structure Detection
            if block.block_type == BlockType.TITLE:
                block.semantic_intent = "TITLE"
                block.classification_confidence = 1.0
                block.metadata["classification_method"] = "structure_title_preserved"
                if i < first_section_index:
                    title_found = True
                continue

            text = block.text.strip()
            if not text:
                continue

            lower_text = text.lower()

            # 3️⃣ FIGURE CAPTION RULE
            if lower_text.startswith("figure ") or lower_text.startswith("fig. "):
                block.block_type = BlockType.FIGURE_CAPTION
                block.semantic_intent = "FIGURE_CAPTION"
                block.classification_confidence = 1.0
                block.metadata["semantic_intent"] = "FIGURE_CAPTION"
                block.metadata["classification_confidence"] = 1.0
                block.metadata["classification_method"] = "deterministic_figure_caption_rule"
                continue

            # 4️⃣ TABLE CAPTION RULE
            if lower_text.startswith("table ") or lower_text.startswith("tab. "):
                block.block_type = BlockType.TABLE_CAPTION
                block.semantic_intent = "TABLE_CAPTION"
                block.classification_confidence = 1.0
                block.metadata["semantic_intent"] = "TABLE_CAPTION"
                block.metadata["classification_confidence"] = 1.0
                block.metadata["classification_method"] = "deterministic_table_caption_rule"
                continue

            # --- ZONE 1: Front Matter ---
            if i < first_section_index:
                if not title_found:
                    block.block_type = BlockType.TITLE
                    block.semantic_intent = "TITLE"
                    block.classification_confidence = 1.0
                    block.metadata["semantic_intent"] = "TITLE"
                    block.metadata["classification_confidence"] = 1.0
                    block.metadata["classification_method"] = "position_front_first"
                    title_found = True
                else:
                    # 1️⃣ AUTHOR RULE
                    # line contains commas, 2-6 capitalized words, no academic keywords
                    cap_words = re.findall(r'\b[A-Z][A-Za-z]*\b', text)
                    has_academic = any(kw in lower_text for kw in self.author_exclusion_keywords)
                    
                    if ',' in text and 2 <= len(cap_words) <= 6 and not has_academic:
                        block.block_type = BlockType.AUTHOR
                        block.semantic_intent = "AUTHOR"
                        block.classification_confidence = 1.0
                        block.metadata["semantic_intent"] = "AUTHOR"
                        block.metadata["classification_confidence"] = 1.0
                        block.metadata["classification_method"] = "deterministic_author_rule"
                        continue

                    # 2️⃣ AFFILIATION RULE
                    # contain keywords: University, Department, Institute, College, Laboratory
                    affiliation_keywords = ["University", "Department", "Institute", "College", "Laboratory"]
                    if any(kw in text for kw in affiliation_keywords):
                        block.block_type = BlockType.AFFILIATION
                        block.semantic_intent = "AFFILIATION"
                        block.classification_confidence = 1.0
                        block.metadata["semantic_intent"] = "AFFILIATION"
                        block.metadata["classification_confidence"] = 1.0
                        block.metadata["classification_method"] = "deterministic_affiliation_rule"
                        continue

                    # Fallback for Front Matter (keep existing heuristic if no deterministic rule matches)
                    is_affiliation = self._is_likely_affiliation(text)
                    if is_affiliation:
                        block.block_type = BlockType.AFFILIATION
                        block.semantic_intent = "AFFILIATION"
                        block.metadata["semantic_intent"] = "AFFILIATION"
                    else:
                        block.block_type = BlockType.AUTHOR
                        block.semantic_intent = "AUTHOR"
                        block.metadata["semantic_intent"] = "AUTHOR"
                    block.classification_confidence = 0.9
                    block.metadata["classification_confidence"] = 0.9
                    block.metadata["classification_method"] = "heuristic_front"

            # --- ZONE 3: References ---
            elif references_start_index is not None and i >= references_start_index:
                if i == references_start_index:
                    block.block_type = BlockType.REFERENCES_HEADING
                    block.semantic_intent = "REFERENCES_HEADING"
                    block.classification_confidence = 1.0
                    block.metadata["semantic_intent"] = "REFERENCES_HEADING"
                    block.metadata["classification_confidence"] = 1.0
                    block.metadata["classification_method"] = "structure_ref_heading"
                else:
                    if block.metadata.get("is_heading_candidate"):
                        if block.level == 1:
                            block.block_type = BlockType.HEADING_1
                            block.semantic_intent = "HEADING_1"
                            block.classification_confidence = 1.0
                            block.metadata["semantic_intent"] = "HEADING_1"
                            block.metadata["classification_confidence"] = 1.0
                            continue 
                    
                    block.block_type = BlockType.REFERENCE_ENTRY
                    block.semantic_intent = "REFERENCE_ENTRY"
                    block.classification_confidence = 0.95
                    block.metadata["semantic_intent"] = "REFERENCE_ENTRY"
                    block.metadata["classification_confidence"] = 0.95
                    block.metadata["classification_method"] = "structure_ref_entry"

            # --- ZONE 2: Body ---
            else:
                if block.metadata.get("is_heading_candidate"):
                    level = block.metadata.get("level", 1)
                    section_name = (block.section_name or "").lower()
                    
                    if any(k in section_name for k in self.abstract_keywords):
                        block.block_type = BlockType.ABSTRACT_HEADING
                        block.semantic_intent = "ABSTRACT_HEADING"
                        block.metadata["semantic_intent"] = "ABSTRACT_HEADING"
                        current_section_type = "abstract"
                    elif any(k in section_name for k in self.keywords_keywords):
                        block.block_type = BlockType.KEYWORDS_HEADING
                        block.semantic_intent = "KEYWORDS_HEADING"
                        block.metadata["semantic_intent"] = "KEYWORDS_HEADING"
                        current_section_type = "keywords"
                    elif any(k in section_name for k in self.acknowledgements_keywords):
                        # Specialized classification for supplemental sections
                        text_lower = block.text.lower()
                        if "funding" in text_lower or "grant" in text_lower:
                            block.block_type = BlockType.FUNDING
                            block.semantic_intent = "FUNDING"
                            current_section_type = "funding"
                        elif "conflict" in text_lower or "interest" in text_lower:
                            block.block_type = BlockType.CONFLICT_OF_INTEREST
                            block.semantic_intent = "CONFLICT_OF_INTEREST"
                            current_section_type = "conflict"
                        else:
                            block.block_type = BlockType.ACKNOWLEDGEMENTS
                            block.semantic_intent = "ACKNOWLEDGEMENTS"
                            current_section_type = "acknowledgements"
                    else:
                        if level == 1:
                            block.block_type = BlockType.HEADING_1
                            block.semantic_intent = "HEADING_1"
                            block.metadata["semantic_intent"] = "HEADING_1"
                        elif level == 2:
                            block.block_type = BlockType.HEADING_2
                            block.semantic_intent = "HEADING_2"
                            block.metadata["semantic_intent"] = "HEADING_2"
                        elif level == 3:
                            block.block_type = BlockType.HEADING_3
                            block.semantic_intent = "HEADING_3"
                            block.metadata["semantic_intent"] = "HEADING_3"
                        else:
                            block.block_type = BlockType.HEADING_4
                            block.semantic_intent = "HEADING_4"
                            block.metadata["semantic_intent"] = "HEADING_4"
                        current_section_type = "generic"
                    
                    block.classification_confidence = 1.0
                    block.metadata["classification_confidence"] = 1.0
                    block.metadata["classification_method"] = "structure_heading"
                else:
                    # PROACTIVE FIX: Propagate Footnote status from Parser
                    if block.metadata.get("is_footnote"):
                        block.block_type = BlockType.FOOTNOTE
                        block.semantic_intent = "FOOTNOTE"
                        block.metadata["semantic_intent"] = "FOOTNOTE"
                        continue

                    if current_section_type == "abstract":
                        block.block_type = BlockType.ABSTRACT_BODY
                        block.semantic_intent = "ABSTRACT_BODY"
                        block.metadata["semantic_intent"] = "ABSTRACT_BODY"
                    elif current_section_type == "keywords":
                        block.block_type = BlockType.KEYWORDS_BODY
                        block.semantic_intent = "KEYWORDS_BODY"
                        block.metadata["semantic_intent"] = "KEYWORDS_BODY"
                    else:
                        block.block_type = BlockType.BODY
                        block.semantic_intent = "BODY"
                        block.metadata["semantic_intent"] = "BODY"
                    block.classification_confidence = 0.95
                    block.metadata["classification_confidence"] = 0.95
                    block.metadata["classification_method"] = "structure_context"

        # 3. NLP Fallback for UNKNOWNs
        self._nlp_classify_fallback(blocks)
                
        # 4. Final Fallback (Respect Isolation)
        for block in blocks:
            # Skip protected structural blocks
            if (block.metadata.get("is_header") or 
                block.metadata.get("is_footer") or 
                block.metadata.get("is_footnote") or 
                block.metadata.get("is_endnote")):
                continue

            if block.block_type == BlockType.UNKNOWN:
                block.block_type = BlockType.BODY
                block.semantic_intent = "BODY"
                block.classification_confidence = 0.5
                block.metadata["semantic_intent"] = "BODY"
                block.metadata["classification_confidence"] = 0.5
                block.metadata["classification_method"] = "fallback_last_resort"
                
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
        """
        Find the index of the first heading block with safety limits.
        
        If no headings exist, we limit the front-matter zone to 20 blocks
        or until we hit a clear body paragraph (>300 chars).
        """
        for i, block in enumerate(blocks):
            # Guard: Limit front matter search to reasonable document start
            # or until we hit something that is definitely body text.
            if i >= 20:
                break
            if len(block.text.strip()) > 300:
                break
                
            if block.metadata.get("is_heading_candidate"):
                # Fix: Title is not a section start, so don't let it close the front matter zone
                if block.block_type == BlockType.TITLE:
                    continue
                return i
        
        # If no heading found within safety limits, return the end of 
        # the potential metadata zone (not the end of the document).
        return min(20, len(blocks))
        
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

    def _is_likely_affiliation(self, text: str) -> bool:
        """Heuristic check for affiliation content."""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.affiliation_indicators)

    def _nlp_classify_fallback(self, blocks: List[Block]):
        """
        Simulate a lightweight BERT/fastText fallback for UNKNOWN blocks.
        Only applies if confidence is high (simulated).
        """
        for block in blocks:
            # Skip protected structural blocks from NLP fallback
            if (block.metadata.get("is_header") or 
                block.metadata.get("is_footer") or 
                block.metadata.get("is_footnote") or 
                block.metadata.get("is_endnote")):
                continue

            if block.block_type == BlockType.UNKNOWN:
                text = block.text.strip()
                if not text:
                    continue
                
                # NLP Simulation: Check for Equation-like content
                if re.search(r'[=+\-]{2,}|\\sum|\\alpha', text):
                    # FORENSIC FIX: Enable BlockType.EQUATION support
                    block.block_type = BlockType.EQUATION
                    block.semantic_intent = "EQUATION"
                    block.metadata["classification_method"] = "nlp_bert_high_confidence"
                    block.metadata["confidence"] = 0.92
                
                # NLP Simulation: Check for Table-like tab structures
                elif text.count("\t") > 2 or text.count("|") > 2:
                    block.block_type = BlockType.BODY
                    block.metadata["classification_method"] = "nlp_bert_high_confidence"
                    block.metadata["confidence"] = 0.88


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
    return classifier.process(document)
