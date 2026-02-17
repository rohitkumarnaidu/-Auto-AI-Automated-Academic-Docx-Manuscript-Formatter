"""
Custom LLM support for local models (Ollama, etc.).
"""
import os
import logging
from typing import Optional, List, Any
from langchain.llms.base import LLM
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class CustomLLMFactory:
    """
    Factory for creating LLM instances with support for various providers.
    
    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Ollama (local models)
    - Custom endpoints
    """
    
    @staticmethod
    def create_llm(
        provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.0,
        **kwargs
    ) -> LLM:
        """
        Create an LLM instance.
        
        Args:
            provider: LLM provider ("openai", "anthropic", "ollama", "custom")
            model: Model name
            temperature: Temperature for generation
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLM instance
        """
        if provider == "openai":
            return CustomLLMFactory._create_openai(model, temperature, **kwargs)
        elif provider == "anthropic":
            return CustomLLMFactory._create_anthropic(model, temperature, **kwargs)
        elif provider == "ollama":
            return CustomLLMFactory._create_ollama(model, temperature, **kwargs)
        elif provider == "custom":
            return CustomLLMFactory._create_custom(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_openai(model: str, temperature: float, **kwargs) -> ChatOpenAI:
        """Create OpenAI LLM."""
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **{k: v for k, v in kwargs.items() if k not in ["api_key"]}
        )
    
    @staticmethod
    def _create_anthropic(model: str, temperature: float, **kwargs):
        """Create Anthropic LLM."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")
        
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **{k: v for k, v in kwargs.items() if k not in ["api_key"]}
        )
    
    @staticmethod
    def _create_ollama(model: str, temperature: float, **kwargs) -> Ollama:
        """Create Ollama LLM for local models."""
        base_url = kwargs.get("base_url", "http://localhost:11434")
        
        logger.info(f"Creating Ollama LLM with model: {model} at {base_url}")
        
        return Ollama(
            model=model,
            temperature=temperature,
            base_url=base_url,
            **{k: v for k, v in kwargs.items() if k not in ["base_url"]}
        )
    
    @staticmethod
    def _create_custom(**kwargs):
        """Create custom LLM from endpoint."""
        raise NotImplementedError("Custom LLM endpoints not yet implemented")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available providers based on installed packages."""
        providers = []
        
        # Check OpenAI
        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")
        
        # Check Anthropic
        try:
            import langchain_anthropic
            if os.getenv("ANTHROPIC_API_KEY"):
                providers.append("anthropic")
        except ImportError:
            pass
        
        # Check Ollama (assume available if running locally)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                providers.append("ollama")
        except:
            pass
        
        return providers
    
    @staticmethod
    def get_recommended_models(provider: str) -> List[str]:
        """Get recommended models for a provider."""
        recommendations = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "ollama": ["llama2", "mistral", "codellama", "phi", "neural-chat"]
        }
        return recommendations.get(provider, [])
