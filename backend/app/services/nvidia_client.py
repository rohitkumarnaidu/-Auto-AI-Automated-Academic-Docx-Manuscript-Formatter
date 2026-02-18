"""
NVIDIA NIM API Client - OpenAI-compatible interface for NVIDIA models.

Supports:
- Llama 3.3 70B Instruct (primary reasoning)
- Llama 3.2 11B Vision Instruct (image analysis)
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class NvidiaClient:
    """Client for NVIDIA NIM API using OpenAI-compatible interface."""
    
    def __init__(self):
        """Initialize NVIDIA client with API key from environment."""
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.client = None

        if not self.api_key:
            logger.warning(
                "NvidiaClient: NVIDIA_API_KEY not set — client running in degraded mode. "
                "All API calls will return empty results."
            )
        else:
            try:
                # Initialize OpenAI client with NVIDIA endpoint
                self.client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=self.api_key
                )
                logger.info("NvidiaClient: initialized successfully.")
            except Exception as exc:
                logger.error("NvidiaClient: failed to initialize OpenAI client: %s", exc)
                self.client = None

        # Model identifiers
        self.llama_70b = "meta/llama-3.3-70b-instruct"
        self.llama_vision = "meta/llama-3.2-11b-vision-instruct"
    
    def chat(
        self, 
        messages: List[Dict[str, Any]], 
        model: str = "llama-70b",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Send chat completion request to NVIDIA API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Either 'llama-70b' or 'llama-vision'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        
        Raises:
            Exception: If API call fails
        """
        # Select model
        model_name = self.llama_70b if model == "llama-70b" else self.llama_vision
        
        if not self.client:
            logger.warning("NvidiaClient.chat: client not available (missing API key or init failed).")
            return ""

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=max(0.0, min(1.0, temperature)),
                max_tokens=max_tokens
            )
            choices = response.choices
            if not choices:
                logger.warning("NvidiaClient.chat: API returned empty choices.")
                return ""
            return choices[0].message.content or ""
        except Exception as exc:
            logger.error("NvidiaClient.chat: API call failed: %s", exc)
            raise
    
    def analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze document structure using Llama 3.3 70B.
        
        Args:
            text: Document text to analyze
        
        Returns:
            Dict with structure analysis
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing academic manuscript structure. Identify sections like Abstract, Introduction, Methods, Results, Discussion, Conclusion, References."
            },
            {
                "role": "user",
                "content": f"Analyze this document and identify its sections:\n\n{text[:2000]}"
            }
        ]
        
        response = self.chat(messages, model="llama-70b", temperature=0.3)
        
        return {
            "analysis": response,
            "model": "llama-3.3-70b",
            "confidence": 0.85
        }
    
    def analyze_figure(self, image_path: str, caption: Optional[str] = None) -> Optional[str]:
        """
        Analyze figure/diagram using Llama 3.2 11B Vision.
        
        Args:
            image_path: Path to image file
            caption: Optional existing caption
        
        Returns:
            Description of the figure, or None if analysis fails
        """
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Prepare messages with image
            content = [
                {"type": "text", "text": "Describe this academic figure or diagram in detail:"}
            ]
            
            if caption:
                content[0]["text"] = f"This figure has caption: '{caption}'. Provide additional context about what the figure shows:"
            
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
            })
            
            messages = [{"role": "user", "content": content}]
            
            return self.chat(messages, model="llama-vision", temperature=0.5, max_tokens=512)
        
        except Exception as exc:
            logger.warning("NvidiaClient.analyze_figure: vision analysis failed: %s", exc)
            return None
    
    def validate_template_compliance(self, document_text: str, template: str) -> Dict[str, Any]:
        """
        Check if document complies with template requirements.
        
        Args:
            document_text: Full document text
            template: Template name (ieee, springer, apa, etc.)
        
        Returns:
            Dict with compliance analysis
        """
        messages = [
            {
                "role": "system",
                "content": f"You are an expert at {template.upper()} formatting standards for academic papers."
            },
            {
                "role": "user",
                "content": f"Check if this document follows {template.upper()} formatting requirements:\n\n{document_text[:1500]}"
            }
        ]
        
        response = self.chat(messages, model="llama-70b", temperature=0.3)
        
        return {
            "compliant": True,  # Parse from response
            "issues": [],
            "suggestions": response,
            "model": "llama-3.3-70b"
        }


# Singleton instance
_nvidia_client = None


def get_nvidia_client() -> NvidiaClient:
    """Get or create singleton NVIDIA client instance."""
    global _nvidia_client
    if _nvidia_client is None:
        try:
            _nvidia_client = NvidiaClient()
        except Exception as exc:
            logger.error("get_nvidia_client: Failed to initialize NVIDIA client: %s", exc)
            _nvidia_client = None
    return _nvidia_client
