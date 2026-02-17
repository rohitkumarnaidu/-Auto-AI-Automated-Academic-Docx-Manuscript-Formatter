"""
Orchestrator V2 - Agent-based orchestration with fallback and metrics.
"""
import logging
import os
from typing import Optional
from app.models import PipelineDocument
from app.pipeline.agents.document_agent import DocumentAgent
from app.pipeline.agents.metrics import PerformanceTracker
from app.pipeline.orchestrator import PipelineOrchestrator as LegacyOrchestrator
from app.cache.redis_cache import redis_cache

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Agent-based orchestrator with fallback to legacy implementation.
    
    Enhanced with:
    - Performance metrics tracking
    - Streaming support
    - Custom LLM providers
    - Agent memory
    """
    
    def __init__(
        self,
        use_agent: bool = True,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        grobid_url: str = "http://localhost:8070",
        enable_metrics: bool = True,
        enable_streaming: bool = False,
        enable_memory: bool = True
    ):
        """
        Initialize the agent orchestrator.
        
        Args:
            use_agent: Whether to use agent-based orchestration (default: True)
            llm_provider: LLM provider ("openai", "anthropic", "ollama")
            llm_model: LLM model for the agent
            grobid_url: GROBID service URL
            enable_metrics: Enable performance tracking (default: True)
            enable_streaming: Enable streaming responses (default: False)
            enable_memory: Enable agent memory (default: True)
        """
        self.use_agent = use_agent and self._check_llm_available(llm_provider)
        
        # Initialize performance tracker
        self.tracker = PerformanceTracker() if enable_metrics else None
        
        if self.use_agent:
            try:
                self.agent = DocumentAgent(
                    llm_provider=llm_provider,
                    llm_model=llm_model,
                    grobid_url=grobid_url,
                    enable_memory=enable_memory,
                    enable_streaming=enable_streaming
                )
                logger.info(f"Agent orchestrator initialized with {llm_provider}/{llm_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize agent: {e}. Falling back to legacy.")
                self.use_agent = False
        
        # Always initialize legacy orchestrator as fallback
        self.legacy_orchestrator = LegacyOrchestrator()
        logger.info("Legacy orchestrator initialized as fallback")
    
    def _check_llm_available(self, provider: str) -> bool:
        """Check if LLM provider is available."""
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY") is not None
        elif provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY") is not None
        elif provider == "ollama":
            # Assume Ollama is available if running locally
            return True
        return False
    
    def process(self, document: PipelineDocument) -> PipelineDocument:
        """
        Process a document using agent or legacy orchestrator.
        
        Args:
            document: PipelineDocument to process
            
        Returns:
            Processed PipelineDocument
        """
        # Start metrics tracking
        if self.tracker:
            orchestrator_type = "agent" if self.use_agent else "legacy"
            self.tracker.start_tracking(document.document_id, orchestrator_type)
        
        try:
            # Try agent-based processing if enabled
            if self.use_agent:
                return self._process_with_agent(document)
            else:
                return self._process_with_legacy(document)
                
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            
            # End tracking with error
            if self.tracker:
                self.tracker.end_tracking(
                    success=False,
                    error_message=str(e)
                )
            
            raise
    
    def _process_with_agent(self, document: PipelineDocument) -> PipelineDocument:
        """Process with agent orchestrator."""
        try:
            logger.info(f"Processing document {document.document_id} with agent orchestrator")
            
            # Run agent analysis
            agent_result = self.agent.process_document(
                file_path=document.source_path,
                document=document
            )
            
            # Record tool usage
            if self.tracker:
                for step in agent_result.get("intermediate_steps", []):
                    if len(step) >= 1:
                        tool_name = getattr(step[0], 'tool', 'unknown')
                        self.tracker.record_tool_use(tool_name)
            
            # Check if agent succeeded and doesn't recommend fallback
            if agent_result.get("success") and not agent_result.get("should_fallback"):
                logger.info("Agent processing completed successfully")
                logger.info(f"Agent analysis: {agent_result.get('analysis', '')[:200]}...")
                
                # Process with legacy pipeline (hybrid approach)
                result = self.legacy_orchestrator.process(document)
                
                # End tracking with success
                if self.tracker:
                    self.tracker.end_tracking(
                        success=True,
                        document=result,
                        fallback_triggered=False
                    )
                
                return result
            else:
                logger.warning("Agent recommended fallback or failed. Using legacy orchestrator.")
                return self._fallback_to_legacy(document, fallback_triggered=True)
                
        except Exception as e:
            logger.error(f"Agent processing failed: {e}. Falling back to legacy.")
            
            # Record retry
            if self.tracker:
                self.tracker.record_retry()
            
            return self._fallback_to_legacy(document, fallback_triggered=True)
    
    def _process_with_legacy(self, document: PipelineDocument) -> PipelineDocument:
        """Process with legacy orchestrator."""
        logger.info(f"Processing document {document.document_id} with legacy orchestrator")
        result = self.legacy_orchestrator.process(document)
        
        # End tracking
        if self.tracker:
            self.tracker.end_tracking(
                success=True,
                document=result,
                fallback_triggered=False
            )
        
        return result
    
    def _fallback_to_legacy(
        self,
        document: PipelineDocument,
        fallback_triggered: bool = True
    ) -> PipelineDocument:
        """
        Fallback to legacy orchestrator.
        
        Args:
            document: PipelineDocument to process
            fallback_triggered: Whether this is a fallback from agent
            
        Returns:
            Processed PipelineDocument
        """
        logger.info(f"Processing document {document.document_id} with legacy orchestrator (fallback)")
        result = self.legacy_orchestrator.process(document)
        
        # End tracking
        if self.tracker:
            self.tracker.end_tracking(
                success=True,
                document=result,
                fallback_triggered=fallback_triggered
            )
        
        return result
    
    def get_performance_summary(self):
        """Get performance metrics summary."""
        if self.tracker:
            return self.tracker.get_summary()
        return None
    
    def get_comparison(self):
        """Get agent vs legacy comparison."""
        if self.tracker:
            return self.tracker.get_comparison()
        return None


# Convenience function for backward compatibility
def create_orchestrator(
    use_agent: bool = True,
    llm_provider: str = "openai",
    enable_metrics: bool = True
) -> AgentOrchestrator:
    """
    Create an orchestrator instance.
    
    Args:
        use_agent: Whether to use agent-based orchestration
        llm_provider: LLM provider to use
        enable_metrics: Enable performance tracking
        
    Returns:
        AgentOrchestrator instance
    """
    return AgentOrchestrator(
        use_agent=use_agent,
        llm_provider=llm_provider,
        enable_metrics=enable_metrics
    )
