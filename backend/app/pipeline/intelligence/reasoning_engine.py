import json
import time
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
import requests
from app.pipeline.safety.retry_guard import retry_guard
from app.pipeline.safety.circuit_breaker import circuit_breaker
from app.pipeline.safety.validator_guard import validate_output

# Import metrics tracking
try:
    from app.services.model_metrics import get_model_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("⚠️ Model metrics unavailable")

class ReasoningEngine:
    """
    Orchestrates LLM reasoning to make pipeline decisions.
    Straddles:
    - Tier 1: NVIDIA NIM (Llama 3 70B) - Primary High Intelligence
    - Tier 2: Ollama (DeepSeek Coder/Mistral) - Fallback Local Intelligence
    - Tier 3: Heuristic Rules - Safety Net
    """
    
    def __init__(self):
        self.nvidia_api_key = "ignore" # Loaded from env in real usage
        
        # Ollama Configuration
        self.ollama_base_url = "http://localhost:11434"
        # Use more standard DeepSeek model tag
        self.fallback_model = "deepseek-r1:8b" 
        
        self.timeout = 30 # Default timeout
        
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
            try:
                self.llm = ChatOllama(
                    model=self.fallback_model,
                    base_url=self.ollama_base_url,
                    format="json",  # Ensure JSON output
                    timeout=self.timeout
                )
                print(f"✅ DeepSeek {self.fallback_model} available (fallback)")
            except Exception as e:
                print(f"⚠️ Failed to init ChatOllama: {e}")
                self.llm = None
                self.ollama_available = False
        else:
            self.llm = None
            print(f"⚠️ Ollama server unavailable at {self.ollama_base_url}")
        
        # Always have rule-based fallback
        print("✅ Rule-based heuristics available (final fallback)")
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama server is reachable and find best model."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
                
                # Check if default exists
                if self.fallback_model in model_names:
                    return True
                
                # Find best alternative (prefer deepseek)
                for m in model_names:
                    if "deepseek" in m.lower():
                        print(f"ℹ️ Auto-selected DeepSeek model: {m}")
                        self.fallback_model = m
                        return True
                
                # Fallback to any model if deepseek not found
                if model_names:
                    print(f"ℹ️ DeepSeek not found, using available model: {model_names[0]}")
                    self.fallback_model = model_names[0]
                    return True
            return False
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
    
    @retry_guard(max_retries=3)
    def _call_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Local Ollama API."""
        try:
            payload = {
                "model": self.fallback_model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2048
                }
            }
            response = requests.post(f"{self.ollama_base_url}/api/generate", json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            # Ollama's /api/generate returns a JSON object with a 'response' field containing the actual LLM output
            full_response = response.json()
            llm_output_str = full_response.get("response", "")
            
            # Try to parse the LLM output string as JSON
            try:
                result = json.loads(llm_output_str)
                return result
            except json.JSONDecodeError:
                # If direct parse fails, try to extract JSON from the string
                import re
                json_match = re.search(r'\{.*\}', llm_output_str, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        return None # Could not parse extracted JSON
                return None # No JSON found or could not parse
        except requests.exceptions.RequestException as e:
            print(f"Ollama API call failed: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during Ollama call: {e}")
            return None

    @retry_guard(max_retries=2, base_delay=0.5)
    def _call_nvidia(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call NVIDIA NIM API."""
        # ... Implementation hidden ...
        # raise NotImplementedError("Env var integration required")
        return None

    @circuit_breaker(failure_threshold=3, recovery_timeout=60)
    @validate_output(schema=dict, error_return_value={"instructions": [], "source": "heuristic_fallback"})
    def generate_instruction_set(self, semantic_blocks: List[Dict[str, Any]], rules: str, max_retries: int = 2) -> Dict[str, Any]:
        """
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
        # Prepare prompt with rich metadata
        blocks_summary = []
        for i, b in enumerate(semantic_blocks[:15]):  # Increased context to 15 blocks
            text = b.get('text', '')[:150]  # Increased text length
            
            # Add metadata hints
            hints = []
            if b.get('metadata', {}).get('heading_level'):
                hints.append(f"H{b['metadata']['heading_level']}")
            if b.get('metadata', {}).get('is_code_block'):
                hints.append(f"CODE({b['metadata']['code_language']})")
            if b.get('metadata', {}).get('is_table'):
                hints.append("TABLE")
            if b.get('metadata', {}).get('is_list_item'):
                hints.append("LIST_ITEM")
            if b.get('metadata', {}).get('font_size'):
                hints.append(f"Size:{b['metadata']['font_size']:.1f}")
            if b.get('style', {}).get('bold'):
                hints.append("BOLD")
                
            hint_str = f" [{', '.join(hints)}]" if hints else ""
            blocks_summary.append(f"Block {i}: {text}{hint_str}")
            
        blocks_summary_str = "\n".join(blocks_summary)
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert academic manuscript structure analyzer. Your task is to classify document blocks with HIGH CONFIDENCE.\n\n**Available Block Types:**\n- TITLE: Main paper title\n- AUTHOR: Author names\n- AFFILIATION: Institutional affiliations\n- ABSTRACT_HEADING: \"Abstract\" heading\n- ABSTRACT_BODY: Abstract content\n- HEADING_1: Main sections (Introduction, Methods, Results, Discussion, Conclusion)\n- HEADING_2: Subsections\n- BODY: Regular paragraph text\n- FIGURE_CAPTION: \"Figure X:\" captions\n- TABLE_CAPTION: \"Table X:\" captions\n- REFERENCES_HEADING: \"References\" heading\n- REFERENCE_ENTRY: Individual citations\n\n**Confidence Guidelines:**\n- Use 0.95-1.0 for OBVIOUS cases (e.g., \"Abstract\", numbered references)\n- Use 0.80-0.94 for CLEAR cases with minor ambiguity\n- Use 0.70-0.79 for PROBABLE cases with some uncertainty\n- Use 0.50-0.69 ONLY when genuinely unsure\n\n**Examples:**\n1. \"Abstract\" → ABSTRACT_HEADING (confidence: 0.98)\n2. \"This paper proposes a novel method...\" → ABSTRACT_BODY (confidence: 0.92)\n3. \"1 Introduction\" → HEADING_1 (confidence: 0.95)\n4. \"Figure 1: System architecture\" → FIGURE_CAPTION (confidence: 0.96)\n5. \"[1] Smith, J. et al.\" → REFERENCE_ENTRY (confidence: 0.94)\n\n**Malformed Text Handling:**\n- \"2ethodology\" → HEADING_1 (interpret as \"Methodology\", confidence: 0.88)\n- Partial/corrupted text → Use context to infer, reduce confidence accordingly\n\nReturn ONLY valid JSON. Be decisive - aim for 0.85+ confidence when possible."""
            },
            {
                "role": "user",
                "content": f"""Analyze and classify each block. Be confident in your classifications.\n\n**Document Blocks:**\n{blocks_summary}\n\n**Output Format (JSON only):**\n{{{{\n  \"blocks\": [\n    {{{{\"block_id\": \"0\", \"semantic_type\": \"ABSTRACT_HEADING\", \"confidence\": 0.95}}}},\n    {{{{\"block_id\": \"1\", \"semantic_type\": \"ABSTRACT_BODY\", \"confidence\": 0.90}}}}\n  ]\n}}}}\n\nClassify all blocks with high confidence. Use context clues."""
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
