import torch
import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification, logging as transformers_logging
from app.models import PipelineDocument as Document, Block, BlockType
from app.pipeline.safety import safe_function

# FEAT 44: Language detection (optional dependency)
try:
    from langdetect import detect as detect_language
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    detect_language = None

logger = logging.getLogger(__name__)

# Silence non-critical transformer loading warnings
transformers_logging.set_verbosity_error()

class SemanticParser:
    """
    NLP Foundation layer for structural analysis.
    Uses local SciBERT weights for semantic classification of manuscript blocks.
    """
    
    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._is_loaded = False

    def _load_model(self):
        """Lazily load SciBERT weights only when needed, or fetch from ModelStore."""
        if self._is_loaded:
            return
            
        from app.services.model_store import model_store
        
        # Priority: Global ModelStore (Pre-loaded at startup)
        if model_store.is_loaded("scibert_tokenizer") and model_store.is_loaded("scibert_model"):
            self.tokenizer = model_store.get_model("scibert_tokenizer")
            self.model = model_store.get_model("scibert_model")
            self._is_loaded = True
            logger.info("SemanticParser: Reusing global SciBERT from ModelStore.")
            return

        logger.info("SemanticParser: Loading SciBERT model (%s)...", self.model_name)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                ignore_mismatched_sizes=True
            )
            self.model.eval()
            self._is_loaded = True
            logger.info("SemanticParser: Model loaded successfully.")
        except Exception as e:
            logger.warning("Failed to load transformer %s: %s", self.model_name, e)
            self.model = None
            self._is_loaded = True

    def detect_boundaries(self, blocks: List[Block]) -> List[Block]:
        """
        [PHASE-1 INTERFACE ADAPTER]
        Delegates to _repair_fragmented_headings with a safety guard.
        Ensures the pipeline never crashes if semantic processing fails.
        """
        try:
            return self._repair_fragmented_headings(blocks)
        except Exception as e:
            logger.warning("SemanticParser Guard: detect_boundaries failed: %s. Returning original blocks.", e)
            return blocks

    def reconcile_fragmented_headings(self, blocks: List[Block]) -> List[Block]:
        """
        [PHASE-1 INTERFACE ADAPTER]
        Delegates to _repair_fragmented_headings with a safety guard.
        """
        try:
            return self._repair_fragmented_headings(blocks)
        except Exception as e:
            logger.warning("SemanticParser Guard: reconcile_fragmented_headings failed: %s. Returning original blocks.", e)
            return blocks

    @safe_function(fallback_value=[], error_message="SemanticParser.analyze_blocks failed")
    def analyze_blocks(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """
        Produce a list of SemanticBlock structures.
        Identifies boundaries and repairs fragmented headers semantically.
        """
        self._load_model()
        semantic_blocks = []
        
        # FEAT 44: Language detection — skip SciBERT for non-English documents
        combined_text = " ".join(b.text for b in blocks[:10] if b.text)[:500]
        detected_lang = "en"
        if HAS_LANGDETECT and combined_text.strip():
            try:
                detected_lang = detect_language(combined_text)
            except Exception:
                detected_lang = "en"  # Default to English on detection failure
        
        use_transformer = detected_lang == "en" and self.model is not None
        if not use_transformer and detected_lang != "en":
            logger.warning("Non-English document detected (%s). Using heuristic-only mode.", detected_lang)
        
        # 1. Heading Repair Logic (e.g., '2' + 'ethodology')
        repaired_blocks = self._repair_fragmented_headings(blocks)
        
        for i, block in enumerate(repaired_blocks):
            if use_transformer:
                prediction = self._predict_block_type(block.text)
            else:
                # Improved Heuristic-only fallback
                prediction = {"type": "BODY", "confidence": 0.5}
                text = block.text.strip()
                upper_text = text.upper()
                
                if len(text) < 150:
                    if upper_text.startswith("ABSTRACT"):
                        prediction = {"type": "ABSTRACT", "confidence": 0.8}
                    elif upper_text.startswith("REFERENCES") or upper_text.startswith("BIBLIOGRAPHY"):
                        prediction = {"type": "REFERENCES", "confidence": 0.8}
                    elif upper_text.startswith("ACKNOWLEDGEMENTS") or upper_text.startswith("ACKNOWLEDGMENTS"):
                        prediction = {"type": "ACKNOWLEDGEMENTS", "confidence": 0.8}
                    elif upper_text.startswith("METHODOLOGY") or upper_text.startswith("METHODS"):
                        prediction = {"type": "METHODOLOGY", "confidence": 0.8}
                    elif upper_text.startswith("CONCLUSION"):
                        prediction = {"type": "CONCLUSION", "confidence": 0.8}
                    elif text.startswith("Figure") or text.startswith("Fig."):
                        prediction = {"type": "FIGURE_CAPTION", "confidence": 0.7}
                    elif text.startswith("Table"):
                        prediction = {"type": "TABLE_CAPTION", "confidence": 0.7}
                    elif text and text[0].isupper() and len(text) < 80:
                        prediction = {"type": "HEADING", "confidence": 0.6}
            
            # Create SemanticBlock Structure (as requested)
            semantic_block = {
                "block_id": i,
                "raw_text": block.text,
                "predicted_section_type": prediction["type"],
                "confidence_score": prediction["confidence"],
                "detected_language": detected_lang,
            }
            semantic_blocks.append(semantic_block)
            
        return semantic_blocks

    def _predict_block_type(self, text: str) -> Dict[str, Any]:
        """Perform semantic classification on block text."""
        # Ensure model is checked correctly
        if not self.model:
            return {"type": "UNKNOWN", "confidence": 0.0}
            
        # Actual Transformer Inference
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence, label_idx = torch.max(probs, dim=1)
            
        # Map label index to internal types (Expanded from 5 to 12)
        labels = [
            "HEADING", "ABSTRACT", "BODY", "REFERENCES", "FIGURE_CAPTION",
            "TABLE_CAPTION", "ACKNOWLEDGEMENTS", "EQUATION", "METHODOLOGY", 
            "CONCLUSION", "AUTHOR_INFO", "TITLE"
        ]
        predicted_label = labels[label_idx.item()] if label_idx.item() < len(labels) else "BODY"
        
        return {
            "type": predicted_label,
            "confidence": float(confidence.item())
        }

    def _repair_fragmented_headings(self, blocks: List[Block]) -> List[Block]:
        """Semantically re-stitch split headers using proximity and content analysis."""
        repaired = []
        i = 0
        while i < len(blocks):
            current = blocks[i]
            if i + 1 < len(blocks):
                next_block = blocks[i+1]
                # Check for heuristic fragmentation (e.g., digit followed by partial word)
                if current.text.isdigit() and next_block.text and next_block.text[0].islower():
                    combined_text = f"{current.text}. {next_block.text}"
                    current.text = combined_text
                    repaired.append(current)
                    i += 2
                    continue
            repaired.append(current)
            i += 1
        return repaired

# Silence transformers logging globally for SentenceTransformers
from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

# Singleton Access
_semantic_parser = None

def get_semantic_parser() -> SemanticParser:
    global _semantic_parser
    if _semantic_parser is None:
        _semantic_parser = SemanticParser()
    return _semantic_parser
