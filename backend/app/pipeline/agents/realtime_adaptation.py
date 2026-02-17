"""
Real-time adaptation during processing.
"""
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class RealTimeAdaptiveAgent:
    """
    Agent that adapts its strategy in real-time during processing.
    
    Features:
    - Monitor performance metrics live
    - Adjust strategy mid-processing
    - Dynamic timeout adjustment
    - Adaptive tool selection
    """
    
    def __init__(
        self,
        base_timeout: float = 60.0,
        adaptation_callback: Optional[Callable] = None
    ):
        """
        Initialize real-time adaptive agent.
        
        Args:
            base_timeout: Base timeout in seconds
            adaptation_callback: Optional callback for adaptation events
        """
        self.base_timeout = base_timeout
        self.adaptation_callback = adaptation_callback
        
        # Real-time metrics
        self.current_metrics = {
            "start_time": None,
            "elapsed_time": 0,
            "tools_executed": [],
            "errors_encountered": [],
            "current_strategy": "default"
        }
        
        # Adaptive parameters
        self.params = {
            "timeout": base_timeout,
            "retry_enabled": True,
            "tool_priority": [],
            "aggressive_mode": False
        }
    
    def start_processing(self, document_id: str):
        """
        Start processing a document.
        
        Args:
            document_id: Document ID
        """
        self.current_metrics = {
            "document_id": document_id,
            "start_time": time.time(),
            "elapsed_time": 0,
            "tools_executed": [],
            "errors_encountered": [],
            "current_strategy": "default"
        }
        
        logger.info(f"Started real-time adaptive processing for {document_id}")
    
    def record_tool_execution(
        self,
        tool_name: str,
        duration: float,
        success: bool
    ):
        """
        Record tool execution and adapt if needed.
        
        Args:
            tool_name: Name of executed tool
            duration: Execution duration
            success: Whether execution succeeded
        """
        self.current_metrics["tools_executed"].append({
            "tool": tool_name,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })
        
        if not success:
            self.current_metrics["errors_encountered"].append({
                "tool": tool_name,
                "timestamp": time.time()
            })
        
        # Update elapsed time
        self.current_metrics["elapsed_time"] = (
            time.time() - self.current_metrics["start_time"]
        )
        
        # Trigger adaptation
        self._adapt_realtime()
    
    def _adapt_realtime(self):
        """Adapt strategy based on current metrics."""
        elapsed = self.current_metrics["elapsed_time"]
        error_count = len(self.current_metrics["errors_encountered"])
        tool_count = len(self.current_metrics["tools_executed"])
        
        # Adaptation 1: Timeout adjustment
        if elapsed > self.params["timeout"] * 0.7:
            # Approaching timeout - speed up
            if not self.params["aggressive_mode"]:
                self.params["aggressive_mode"] = True
                self.params["timeout"] *= 1.5  # Extend timeout
                self._notify_adaptation("timeout_extended", {
                    "new_timeout": self.params["timeout"],
                    "reason": "approaching_timeout"
                })
        
        # Adaptation 2: Error handling
        if error_count >= 2:
            # Multiple errors - switch strategy
            if self.current_metrics["current_strategy"] != "fallback":
                self.current_metrics["current_strategy"] = "fallback"
                self.params["retry_enabled"] = False
                self._notify_adaptation("strategy_changed", {
                    "new_strategy": "fallback",
                    "reason": "multiple_errors"
                })
        
        # Adaptation 3: Tool selection
        if tool_count > 0:
            # Analyze tool performance
            successful_tools = [
                t["tool"] for t in self.current_metrics["tools_executed"]
                if t["success"]
            ]
            
            if successful_tools and not self.params["tool_priority"]:
                self.params["tool_priority"] = successful_tools
                self._notify_adaptation("tool_priority_set", {
                    "priority": successful_tools
                })
    
    def _notify_adaptation(self, event_type: str, data: Dict[str, Any]):
        """Notify about adaptation event."""
        logger.info(f"Real-time adaptation: {event_type} - {data}")
        
        if self.adaptation_callback:
            self.adaptation_callback(event_type, data)
    
    def should_continue(self) -> bool:
        """
        Check if processing should continue.
        
        Returns:
            True if should continue
        """
        elapsed = self.current_metrics["elapsed_time"]
        
        # Check timeout
        if elapsed > self.params["timeout"]:
            logger.warning("Timeout exceeded")
            return False
        
        # Check error threshold
        if len(self.current_metrics["errors_encountered"]) > 5:
            logger.warning("Too many errors")
            return False
        
        return True
    
    def get_current_params(self) -> Dict[str, Any]:
        """Get current adaptive parameters."""
        return self.params.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.current_metrics.copy()
    
    def recommend_next_tool(
        self,
        available_tools: list[str]
    ) -> Optional[str]:
        """
        Recommend next tool to execute.
        
        Args:
            available_tools: List of available tools
            
        Returns:
            Recommended tool name
        """
        # Use priority if available
        if self.params["tool_priority"]:
            for tool in self.params["tool_priority"]:
                if tool in available_tools:
                    return tool
        
        # Default: return first available
        return available_tools[0] if available_tools else None
