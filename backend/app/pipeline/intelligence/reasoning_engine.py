import json
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama

class ReasoningEngine:
    """
    Semantic Reasoning Engine powered by DeepSeek (Local via Ollama).
    Generates a "Semantic Instruction Set" for document orchestration.
    """
    
    def __init__(self, model: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(
            model=model,
            base_url=base_url,
            format="json"  # Ensure JSON output
        )
        
    def generate_instruction_set(self, semantic_blocks: List[Dict[str, Any]], rules: str) -> Dict[str, Any]:
        """
        Request a Semantic Instruction Set from DeepSeek.
        Strictly forbids layout or formatting instructions.
        """
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
        """
        
        try:
            response = self.llm.invoke(prompt)
            # The format="json" in ChatOllama ensures the content is a JSON string
            return json.loads(response.content)
        except Exception as e:
            print(f"DeepSeek Reasoning Error: {e}")
            return {"error": "REASONING_FAILED", "details": str(e)}

# Singleton Access
_reasoning_engine = None

def get_reasoning_engine() -> ReasoningEngine:
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
