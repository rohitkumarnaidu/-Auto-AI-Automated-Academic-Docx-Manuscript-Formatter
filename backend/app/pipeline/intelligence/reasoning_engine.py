import json
import time
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
import requests

class ReasoningEngine:
    """
    Semantic Reasoning Engine powered by DeepSeek (Local via Ollama).
    Generates a "Semantic Instruction Set" for document orchestration.
    
    Features:
    - Ollama server health check
    - Graceful fallback to rule-based classification
    - Request timeout (30s)
    - JSON schema validation
    - Retry logic for transient failures
    """
    
    def __init__(self, model: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434", timeout: int = 30):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.ollama_available = self._check_ollama_health()
        
        if self.ollama_available:
            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                format="json",  # Ensure JSON output
                timeout=timeout
            )
            print(f"✅ DeepSeek {model} initialized successfully")
        else:
            self.llm = None
            print(f"⚠️  Ollama server unavailable. Falling back to rule-based classification.")
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except (requests.RequestException, Exception):
            return False
    
    def _validate_json_schema(self, data: Dict[str, Any]) -> bool:
        """Validate JSON output schema."""
        if "error" in data:
            return False
        if "blocks" not in data:
            return False
        for block in data.get("blocks", []):
            required_fields = ["block_id", "semantic_type", "confidence"]
            if not all(field in block for field in required_fields):
                return False
        return True
    
    def _rule_based_fallback(self, semantic_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rule-based classification fallback when Ollama unavailable."""
        print("⚠️  Using rule-based fallback classification")
        blocks = []
        for block in semantic_blocks:
            text = block.get("text", "").strip().lower()
            
            # Simple heuristic classification
            if len(text) < 50 and text.endswith(":"):
                semantic_type = "HEADING_1"
            elif "abstract" in text[:20]:
                semantic_type = "ABSTRACT_BODY"
            elif "introduction" in text[:20]:
                semantic_type = "HEADING_1"
            elif "reference" in text or "bibliography" in text:
                semantic_type = "REFERENCE_ENTRY"
            else:
                semantic_type = "BODY_TEXT"
            
            blocks.append({
                "block_id": block.get("block_id", f"b{block.get('index', 0)}"),
                "semantic_type": semantic_type,
                "canonical_section_name": text[:50] if len(text) < 50 else "Body",
                "confidence": 0.5  # Lower confidence for rule-based
            })
        
        return {"blocks": blocks, "fallback": True}
    
    def generate_instruction_set(self, semantic_blocks: List[Dict[str, Any]], rules: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Request a Semantic Instruction Set from DeepSeek.
        Strictly forbids layout or formatting instructions.
        
        Features:
        - Automatic fallback if Ollama unavailable
        - Retry logic for transient failures
        - JSON schema validation
        - Timeout protection
        """
        # Fallback if Ollama not available
        if not self.ollama_available or self.llm is None:
            return self._rule_based_fallback(semantic_blocks)
        
        prompt = f"""
        Analyze the following academic manuscript blocks and publisher guidelines.
        
        MANUSCRIPT BLOCKS:
        {json.dumps(semantic_blocks[:20])}  # Context window
        
        PUBLISHER RULES (RAG):
        {rules}
        
        TASK:
        Generate a JSON "Semantic Instruction Set".
        For each block, provide:
        - block_id
        - semantic_type (e.g., HEADING_1, ABSTRACT_BODY, REFERENCE_ENTRY)
        - canonical_section_name (e.g., "Introduction", "Methodology")
        - confidence (0.0 - 1.0)
        
        RULES:
        - OUTPUT JSON ONLY.
        - NO FONT SIZES, NO COLORS, NO SPACING, NO DOCX STYLES.
        - PROVIDE SEMANTIC LABELS ONLY.
        
        Return format: {{"blocks": [...]}}
        """
        
        # Retry logic
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                response = self.llm.invoke(prompt)
                latency = time.time() - start_time
                
                # Parse JSON
                result = json.loads(response.content)
                
                # Validate schema
                if not self._validate_json_schema(result):
                    raise ValueError("Invalid JSON schema from DeepSeek")
                
                # Add metadata
                result["latency"] = latency
                result["model"] = self.model
                result["fallback"] = False
                
                print(f"✅ DeepSeek reasoning completed in {latency:.2f}s")
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠️  DeepSeek JSON parsing error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    print("❌ All retries failed. Falling back to rule-based classification.")
                    return self._rule_based_fallback(semantic_blocks)
                    
            except Exception as e:
                print(f"⚠️  DeepSeek reasoning error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    print("❌ All retries failed. Falling back to rule-based classification.")
                    return self._rule_based_fallback(semantic_blocks)
        
        # Should never reach here, but fallback just in case
        return self._rule_based_fallback(semantic_blocks)

# Singleton Access
_reasoning_engine = None

def get_reasoning_engine() -> ReasoningEngine:
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
