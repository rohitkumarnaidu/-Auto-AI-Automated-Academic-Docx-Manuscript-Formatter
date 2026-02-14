import json
import time
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
import requests

# Import metrics tracking
try:
    from app.services.model_metrics import get_model_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("⚠️ Model metrics unavailable")

class ReasoningEngine:
    """
    Semantic Reasoning Engine with multi-model fallback.
    
    Model Priority:
    1. NVIDIA Llama 3.3 70B (primary - best quality)
    2. DeepSeek via Ollama (fallback - local/fast)
    3. Rule-based heuristics (final fallback - always works)
    
    Features:
    - Automatic fallback on failure
    - Health checks for all services
    - Request timeout (30s)
    - JSON schema validation
    - Retry logic for transient failures
    """
    
    def __init__(self, model: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434", timeout: int = 30):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        
        # Initialize NVIDIA client (primary)
        self.nvidia_client = None
        self.nvidia_available = False
        try:
            from app.services.nvidia_client import get_nvidia_client
            self.nvidia_client = get_nvidia_client()
            self.nvidia_available = self.nvidia_client is not None
            if self.nvidia_available:
                print("✅ NVIDIA Llama 3.3 70B available (primary)")
        except Exception as e:
            print(f"⚠️ NVIDIA unavailable: {e}")
        
        # Initialize DeepSeek/Ollama (fallback)
        self.ollama_available = self._check_ollama_health()
        
        if self.ollama_available:
            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                format="json",  # Ensure JSON output
                timeout=timeout
            )
            print(f"✅ DeepSeek {model} available (fallback)")
        else:
            self.llm = None
            print(f"⚠️ Ollama server unavailable")
        
        # Always have rule-based fallback
        print("✅ Rule-based heuristics available (final fallback)")
    
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
        Request a Semantic Instruction Set with multi-model fallback.
        
        Priority:
        1. Try NVIDIA Llama 3.3 70B (best quality)
        2. Fallback to DeepSeek via Ollama (fast local)
        3. Final fallback to rule-based heuristics (always works)
        
        Features:
        - Automatic fallback on failure
        - Retry logic for transient failures
        - JSON schema validation
        - Timeout protection
        """
        # Try NVIDIA first (if available)
        if self.nvidia_available and self.nvidia_client:
            try:
                print("🚀 Attempting NVIDIA Llama 3.3 70B...")
                start_time = time.time()
                result = self._generate_with_nvidia(semantic_blocks, rules)
                latency = time.time() - start_time
                
                if result and self._validate_json_schema(result):
                    result["latency"] = latency
                    result["model"] = "NVIDIA Llama 3.3 70B"
                    result["fallback"] = False
                    
                    # Record metrics
                    if METRICS_AVAILABLE:
                        get_model_metrics().record_call("nvidia", True, latency)
                    
                    print(f"✅ NVIDIA analysis successful ({latency:.2f}s)")
                    return result
                else:
                    # Record failure
                    if METRICS_AVAILABLE:
                        get_model_metrics().record_call("nvidia", False, latency)
                        get_model_metrics().record_fallback("nvidia", "deepseek", "Invalid schema")
                    print("⚠️ NVIDIA returned invalid schema or no result, falling back...")
            except Exception as e:
                # Record failure
                if METRICS_AVAILABLE:
                    get_model_metrics().record_call("nvidia", False, time.time() - start_time)
                    get_model_metrics().record_fallback("nvidia", "deepseek", str(e))
                print(f"⚠️ NVIDIA failed: {e}. Falling back to DeepSeek...")
        
        # Fallback to DeepSeek/Ollama
        if self.ollama_available and self.llm is not None:
            try:
                print("🔄 Attempting DeepSeek via Ollama...")
                start_time = time.time()
                result = self._generate_with_deepseek(semantic_blocks, rules, max_retries)
                latency = time.time() - start_time
                
                if result and self._validate_json_schema(result):
                    result["latency"] = latency
                    result["model"] = self.model
                    result["fallback"] = False
                    
                    # Record metrics
                    if METRICS_AVAILABLE:
                        get_model_metrics().record_call("deepseek", True, latency)
                    
                    print(f"✅ DeepSeek analysis successful ({latency:.2f}s)")
                    return result
                else:
                    # Record failure
                    if METRICS_AVAILABLE:
                        get_model_metrics().record_call("deepseek", False, latency)
                        get_model_metrics().record_fallback("deepseek", "rules", "Invalid schema")
                    print("⚠️ DeepSeek returned invalid schema or no result, falling back...")
            except Exception as e:
                # Record failure
                if METRICS_AVAILABLE:
                    get_model_metrics().record_call("deepseek", False, time.time() - start_time)
                    get_model_metrics().record_fallback("deepseek", "rules", str(e))
                print(f"⚠️ DeepSeek failed: {e}. Falling back to rules...")
        
        # Final fallback to rule-based
        print("📋 Using rule-based heuristics (final fallback)")
        return self._rule_based_fallback(semantic_blocks)
    
    def _generate_with_nvidia(self, semantic_blocks: List[Dict[str, Any]], rules: str) -> Dict[str, Any]:
        """Generate instruction set using NVIDIA Llama 3.3 70B."""
        # Prepare prompt
        # For NVIDIA, we might need a more concise prompt due to context window or specific API expectations.
        # The provided snippet uses a summary of blocks.
        blocks_summary = "\n".join([
            f"Block {i}: {b.get('text', '')[:100]}..."
            for i, b in enumerate(semantic_blocks[:10])  # Limit to first 10 for context
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing academic manuscript structure. Classify each block as HEADING_1, ABSTRACT_BODY, BODY_TEXT, REFERENCE_ENTRY, etc. Return JSON only."
            },
            {
                "role": "user",
                "content": f"Analyze these document blocks and classify them:\n\n{blocks_summary}\n\nReturn JSON with format: {{\"blocks\": [{{\"block_id\": \"...\", \"semantic_type\": \"...\", \"confidence\": 0.9}}]}}"
            }
        ]
        
        # Assuming nvidia_client.chat returns a string that might contain JSON
        response = self.nvidia_client.chat(messages, model="llama-70b", temperature=0.3, max_tokens=2048)
        
        # Parse JSON response
        try:
            import json
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from response if it's embedded in text
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    return None # Could not parse extracted JSON
            return None # No JSON found or could not parse
    
    def _generate_with_deepseek(self, semantic_blocks: List[Dict[str, Any]], rules: str, max_retries: int) -> Dict[str, Any]:
        """Generate instruction set using DeepSeek via Ollama (original logic)."""
        # Build prompt
        # The original prompt for DeepSeek is more detailed and includes publisher rules.
        blocks_json = json.dumps(semantic_blocks[:20])  # Context window from original prompt
        
        prompt = f"""
        Analyze the following academic manuscript blocks and publisher guidelines.
        
        MANUSCRIPT BLOCKS:
        {blocks_json}
        
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
        for attempt in range(max_retries + 1): # max_retries is 2, so this will run 3 times (0, 1, 2)
            try:
                response = self.llm.invoke(prompt)
                result = json.loads(response.content)
                
                
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
