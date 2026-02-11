import torch
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification, logging as transformers_logging
from app.models import PipelineDocument as Document, Block, BlockType

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
            print("SemanticParser: Reusing global SciBERT from ModelStore.")
            return

        print(f"SemanticParser: Loading SciBERT model ({self.model_name})...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                ignore_mismatched_sizes=True
            )
            self.model.eval()
            self._is_loaded = True
            print("SemanticParser: Model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load transformer {self.model_name}: {e}")
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
            print(f"SemanticParser Guard: detect_boundaries failed: {e}. Returning original blocks.")
            return blocks

    def reconcile_fragmented_headings(self, blocks: List[Block]) -> List[Block]:
        """
        [PHASE-1 INTERFACE ADAPTER]
        Delegates to _repair_fragmented_headings with a safety guard.
        """
        try:
            return self._repair_fragmented_headings(blocks)
        except Exception as e:
            print(f"SemanticParser Guard: reconcile_fragmented_headings failed: {e}. Returning original blocks.")
            return blocks

    def analyze_blocks(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """
        Produce a list of SemanticBlock structures.
        Identifies boundaries and repairs fragmented headers semantically.
        """
        self._load_model()
        semantic_blocks = []
        
        # 1. Heading Repair Logic (e.g., '2' + 'ethodology')
        repaired_blocks = self._repair_fragmented_headings(blocks)
        
        for i, block in enumerate(repaired_blocks):
            prediction = self._predict_block_type(block.text)
            
            # Create SemanticBlock Structure (as requested)
            semantic_block = {
                "block_id": i,
                "raw_text": block.text,
                "predicted_section_type": prediction["type"],
                "confidence_score": prediction["confidence"]
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
            
        # Map label index to internal types (Simplified)
        labels = ["HEADING", "ABSTRACT", "BODY", "REFERENCES", "FIGURE_CAPTION"]
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
