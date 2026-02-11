"""
NLP Content Analyzer - Enriches document with AI/NLP hints (Read-Only).
"""

import re
from typing import List, Dict, Any
from app.models import PipelineDocument as Document, Block, BlockType

try:
    # import spacy
    # NLP_AVAILABLE = True
    NLP_AVAILABLE = False
except ImportError:
    NLP_AVAILABLE = False

from app.pipeline.base import PipelineStage

class ContentAnalyzer(PipelineStage):
    """
    Analyzes document content to provide advisory hints.
    Does NOT modify content or block types.
    """
    
    def __init__(self):
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                # Load small English model
                # We attempt to load, if fails (model not downloaded), we warn
                if not spacy.util.is_package("en_core_web_sm"):
                     print("Warning: spacy model 'en_core_web_sm' not found. NLP analysis will be limited.")
                else:
                    self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"Warning: Failed to load spacy model: {e}")

    def process(self, document: Document) -> Document:
        """
        Run analysis on the document blocks.
        Populates block.metadata["ai_hints"].
        """
        # Load model if strictly needed here, or use initialized one
        
        for block in document.blocks:
            hints = {}
            
            # 1. Section Confidence Estimation
            # Simple heuristic + Entity analysis if available
            section_conf = self._estimate_section_confidence(block)
            if section_conf:
                hints["predicted_section"] = section_conf["section"]
                hints["confidence"] = section_conf["confidence"]
                hints["notes"] = section_conf["notes"]

            # 2. Caption Quality
            # If block might be a caption (starts with Fig/Table)
            if self._is_potential_caption(block.text):
                quality = self._evaluate_caption_quality(block.text)
                hints["caption_quality"] = quality

            # 3. Readability (Abstract)
            # If we think it's abstract body
            if block.block_type == BlockType.ABSTRACT_BODY or methods_detect_abstract(block.text):
                readability = self._check_readability(block.text)
                hints["readability"] = readability
                
            # Attach hints if any
            if hints:
                if not block.metadata:
                    block.metadata = {}
                block.metadata["ai_hints"] = hints
                
        return document

    def _estimate_section_confidence(self, block: Block) -> Dict:
        """Estimate if block is a section header."""
        text = block.text.strip().lower()
        if not text:
            return None
            
        # Rules
        headers = {
            "abstract": 0.95,
            "introduction": 0.9,
            "methods": 0.8,
            "methodology": 0.8,
            "results": 0.8,
            "discussion": 0.8,
            "conclusion": 0.8,
            "references": 0.95, 
            "bibliography": 0.95
        }
        
        # Exact match (ignoring numbering "1. Introduction")
        clean = re.sub(r'^[\d\.]+\s*', '', text)
        if clean in headers:
            return {
                "section": clean.title(),
                "confidence": headers[clean],
                "notes": ["Keyword match"]
            }
            
        return None

    def _is_potential_caption(self, text: str) -> bool:
        return text.lstrip().lower().startswith(("fig", "table", "chart"))

    def _evaluate_caption_quality(self, text: str) -> str:
        """Rate caption: Good, Short, Vague."""
        words = text.split()
        if len(words) < 5:
            return "Short"
        
        vague_words = ["image", "chart", "diagram", "below", "above"]
        if any(w in text.lower() for w in vague_words) and len(words) < 10:
            return "Possibly Vague"
            
        return "Good"

    def _check_readability(self, text: str) -> str:
        """Simple readability check."""
        # Sentence length
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        if not sentences:
            return "N/A"
            
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 30:
            return "Complex (Long Sentences)"
        elif avg_len < 8:
            return "Simple (Short Sentences)"
        return "Standard"

def methods_detect_abstract(text: str) -> bool:
    """Helper to detect abstract-like text."""
    # Heuristic
    return "background" in text.lower() and "results" in text.lower() and len(text) > 200
