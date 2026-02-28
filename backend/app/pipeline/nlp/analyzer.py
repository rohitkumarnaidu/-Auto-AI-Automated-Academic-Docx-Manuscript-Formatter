"""
NLP Content Analyzer - Enriches document with AI/NLP hints (Read-Only).
"""

import re
import logging
from typing import List, Dict, Any
from app.models import PipelineDocument as Document, Block, BlockType

logger = logging.getLogger(__name__)

try:
    import yake
    YAKE_AVAILABLE = True
except ImportError:
    yake = None
    YAKE_AVAILABLE = False

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KeyBERT = None  # type: ignore[assignment]
    KEYBERT_AVAILABLE = False

NLP_AVAILABLE = YAKE_AVAILABLE or KEYBERT_AVAILABLE
_KEYBERT_MODEL = None

from app.pipeline.base import PipelineStage

class ContentAnalyzer(PipelineStage):
    """
    Analyzes document content to provide advisory hints.
    Does NOT modify content or block types.
    """
    
    def __init__(self):
        self.nlp = None

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


def _get_keybert_model():
    global _KEYBERT_MODEL
    if not KEYBERT_AVAILABLE:
        return None
    if _KEYBERT_MODEL is None:
        try:
            _KEYBERT_MODEL = KeyBERT()
        except Exception as exc:
            logger.warning("KeyBERT model initialization failed: %s", exc)
            _KEYBERT_MODEL = None
    return _KEYBERT_MODEL


def extract_keywords(text: str, top_k: int = 8) -> List[str]:
    """
    Hybrid keyword extraction:
    1) YAKE for cheap candidate generation.
    2) KeyBERT re-ranking when available.
    """
    text = (text or "").strip()
    if not text:
        return []

    yake_candidates: List[str] = []
    if YAKE_AVAILABLE and yake is not None:
        try:
            extractor = yake.KeywordExtractor(lan="en", n=2, top=max(top_k * 2, 10))
            yake_candidates = [kw for kw, _score in extractor.extract_keywords(text) if kw]
        except Exception as exc:
            logger.warning("YAKE extraction failed: %s", exc)

    keybert_model = _get_keybert_model()
    if keybert_model is not None:
        try:
            kw = keybert_model.extract_keywords(
                text,
                candidates=yake_candidates or None,
                top_n=top_k,
                stop_words="english",
            )
            keywords = [item[0] for item in kw if item and item[0]]
            if keywords:
                return keywords
        except Exception as exc:
            logger.warning("KeyBERT extraction failed: %s", exc)

    if yake_candidates:
        return yake_candidates[:top_k]

    # Ultimate fallback: deterministic token frequency heuristic.
    tokens = [t.strip(".,;:!?()[]{}").lower() for t in text.split()]
    tokens = [t for t in tokens if len(t) > 3]
    freq: Dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1
    return [tok for tok, _count in sorted(freq.items(), key=lambda item: item[1], reverse=True)[:top_k]]
