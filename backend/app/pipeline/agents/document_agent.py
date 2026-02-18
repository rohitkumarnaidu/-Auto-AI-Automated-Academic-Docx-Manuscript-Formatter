"""
LangChain-based document processing agent with enhancements.
"""
import os
import logging
from typing import Optional, Dict, Any, List, Callable
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.pipeline.agents.tools.metadata_tool import MetadataExtractionTool
from app.pipeline.agents.tools.layout_tool import LayoutAnalysisTool
from app.pipeline.agents.tools.validation_tool import ValidationTool
from app.pipeline.agents.tools.reference_tool import ReferenceExtractionTool
from app.pipeline.agents.tools.figure_tool import FigureAnalysisTool
from app.pipeline.agents.llm_factory import CustomLLMFactory
from app.pipeline.agents.memory import AgentMemory
from app.pipeline.agents.streaming import StreamingAgentCallback
from app.models import PipelineDocument
from app.pipeline.safety import safe_function, safe_async_function, retry_guard

logger = logging.getLogger(__name__)


class DocumentAgent:
    """
    Intelligent agent for orchestrating document processing.
    
    Enhanced with:
    - Additional tools (reference extraction, figure analysis)
    - Streaming responses for real-time updates
    - Agent memory for pattern recognition
    - Custom LLM support (Ollama, etc.)
    - Performance metrics tracking
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        temperature: float = 0.0,
        max_retries: int = 3,
        grobid_url: str = "http://localhost:8070",
        enable_memory: bool = True,
        enable_streaming: bool = False,
        streaming_callback: Optional[Callable] = None
    ):
        """
        Initialize the enhanced document agent.
        
        Args:
            llm_provider: LLM provider ("openai", "anthropic", "ollama")
            llm_model: LLM model to use
            temperature: LLM temperature (default: 0.0 for deterministic)
            max_retries: Maximum retry attempts (default: 3)
            grobid_url: GROBID service URL
            enable_memory: Enable agent memory (default: True)
            enable_streaming: Enable streaming responses (default: False)
            streaming_callback: Optional callback for streaming events
        """
        self.max_retries = max_retries
        
        # Initialize LLM using factory
        try:
            self.llm = CustomLLMFactory.create_llm(
                provider=llm_provider,
                model=llm_model,
                temperature=temperature
            )
            logger.info(f"Initialized {llm_provider} LLM with model {llm_model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
        
        # Initialize memory
        self.memory = AgentMemory() if enable_memory else None
        if self.memory:
            logger.info("Agent memory enabled")
        
        # Initialize streaming callback
        self.streaming_callback = None
        if enable_streaming:
            self.streaming_callback = StreamingAgentCallback(callback_fn=streaming_callback)
            logger.info("Streaming responses enabled")
        
        # Initialize tools (now with 5 tools!)
        self.tools = [
            MetadataExtractionTool(grobid_url=grobid_url),
            LayoutAnalysisTool(),
            ValidationTool(),
            ReferenceExtractionTool(grobid_url=grobid_url),
            FigureAnalysisTool()
        ]
        
        # Load orchestration prompt
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            "orchestration_prompt.txt"
        )
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            logger.warning(f"Orchestration prompt not found at {prompt_path}. Using default.")
            system_prompt = "You are a document processing agent. Use the available tools to analyze and process documents."
        
        # Add memory context to prompt if enabled
        if self.memory:
            memory_summary = self.memory.get_memory_summary()
            system_prompt += f"\n\n## Memory Context\n{memory_summary}"
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor with optional streaming
        executor_kwargs = {
            "agent": self.agent,
            "tools": self.tools,
            "verbose": True,
            "max_iterations": 10,
            "handle_parsing_errors": True,
            "return_intermediate_steps": True
        }
        
        if self.streaming_callback:
            executor_kwargs["callbacks"] = [self.streaming_callback]
        
        self.executor = AgentExecutor(**executor_kwargs)
    
    @safe_async_function(fallback_value={"status": "error", "message": "Agent crashed safely"}, error_message="DocumentAgent.run")
    @retry_guard(max_retries=1) # Retry once if agent fails
    async def run(self, document: PipelineDocument, job_id: str) -> Dict[str, Any]:
        """
        Run the agent on a document to fix validation errors.
        
        Args:
            document: The document object to process
            job_id: The ID of the current job
            
        Returns:
            Dict containing the processing results and agent logs
        """
        logger.info(f"Agent starting for job {job_id}")
        try:
            # Set document in validation tool if provided
            if document:
                validation_tool = next(
                    (t for t in self.tools if isinstance(t, ValidationTool)),
                    None
                )
                if validation_tool:
                    validation_tool.set_document(document.document_id, document)
            
            # Check memory for similar patterns
            context = {"document_type": "academic_paper"}  # Could be detected
            if self.memory:
                best_pattern = self.memory.get_best_pattern("document_processing", context)
                if best_pattern:
                    logger.info(f"Found similar pattern in memory: {best_pattern}")
            
            # Construct input message
            doc_path = document.filename if document else "Unknown File"
            input_message = f"""
Please analyze the document at: {doc_path}

Tasks:
1. Extract metadata using GROBID
2. Analyze the document layout
3. Extract and analyze references
4. Detect and analyze figures
5. Validate the document structure (if document ID: {document.document_id if document else 'N/A'})

Provide a comprehensive analysis and recommend the best processing approach.
"""
            
            # Execute agent with retry logic
            result = self._execute_with_retry(input_message)
            
            # Remember successful pattern
            if self.memory:
                self.memory.remember_pattern(
                    "document_processing",
                    context,
                    success=True
                )
            
            return {
                "success": True,
                "analysis": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "should_fallback": self._should_fallback(result),
                "streaming_events": self.streaming_callback.get_events() if self.streaming_callback else []
            }
            
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            
            # Remember error
            if self.memory:
                self.memory.remember_error("agent_processing", str(e))
            
            return {
                "success": False,
                "error": str(e),
                "should_fallback": True
            }
    
    def _execute_with_retry(self, input_message: str) -> Dict[str, Any]:
        """
        Execute agent with retry logic.
        
        Args:
            input_message: Input message for the agent
            
        Returns:
            Agent execution result
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Agent execution attempt {attempt + 1}/{self.max_retries}")
                
                # Clear streaming events for new attempt
                if self.streaming_callback:
                    self.streaming_callback.clear_events()
                
                result = self.executor.invoke({"input": input_message})
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Agent execution attempt {attempt + 1} failed: {e}")
                
                # Check memory for solution
                if self.memory:
                    solution = self.memory.get_error_solution("execution_error", str(e))
                    if solution:
                        logger.info(f"Found solution in memory: {solution}")
                
                if attempt < self.max_retries - 1:
                    logger.info("Retrying...")
                    continue
                else:
                    logger.error("Max retries reached. Giving up.")
                    raise last_error
        
        raise last_error
    
    def _should_fallback(self, result: Dict[str, Any]) -> bool:
        """
        Determine if we should fallback to legacy orchestrator.
        
        Args:
            result: Agent execution result
            
        Returns:
            True if fallback is recommended
        """
        # Check for multiple tool failures
        intermediate_steps = result.get("intermediate_steps", [])
        
        error_count = 0
        for step in intermediate_steps:
            if len(step) >= 2:
                tool_output = step[1]
                if isinstance(tool_output, str) and "ERROR" in tool_output:
                    error_count += 1
        
        # Fallback if more than half the tools failed
        if len(intermediate_steps) > 0 and error_count / len(intermediate_steps) > 0.5:
            logger.warning(f"High error rate detected ({error_count}/{len(intermediate_steps)}). Recommending fallback.")
            return True
        
        return False
