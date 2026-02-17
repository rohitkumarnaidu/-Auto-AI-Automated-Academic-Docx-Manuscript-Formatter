"""
Adaptive strategies that auto-tune based on metrics.
"""
import logging
from typing import Dict, Any, Optional, List
from app.pipeline.agents.metrics import PerformanceTracker
from app.pipeline.agents.ml_patterns import MLPatternDetector

logger = logging.getLogger(__name__)


class AdaptiveStrategy:
    """
    Auto-tune agent behavior based on performance metrics.
    
    Adjusts:
    - Tool selection
    - Retry counts
    - Timeout values
    - Fallback thresholds
    """
    
    def __init__(
        self,
        tracker: PerformanceTracker,
        ml_detector: Optional[MLPatternDetector] = None
    ):
        """
        Initialize adaptive strategy.
        
        Args:
            tracker: Performance tracker
            ml_detector: Optional ML pattern detector
        """
        self.tracker = tracker
        self.ml_detector = ml_detector
        self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "max_retries": 3,
            "timeout_seconds": 60,
            "fallback_threshold": 0.5,
            "enable_caching": True,
            "tool_priority": [
                "extract_metadata",
                "analyze_layout",
                "validate_document",
                "extract_references",
                "analyze_figures"
            ]
        }
    
    def adapt(self) -> Dict[str, Any]:
        """
        Adapt configuration based on metrics.
        
        Returns:
            Updated configuration
        """
        summary = self.tracker.get_summary()
        
        if not summary or "agent" not in summary:
            return self.config
        
        agent_stats = summary["agent"]
        
        # Adapt retry count based on success rate
        success_rate = agent_stats.get("success_rate", 0)
        if success_rate < 0.7:
            # Low success rate - increase retries
            self.config["max_retries"] = min(5, self.config["max_retries"] + 1)
            logger.info(f"Increased max_retries to {self.config['max_retries']} due to low success rate")
        elif success_rate > 0.95:
            # High success rate - can reduce retries
            self.config["max_retries"] = max(2, self.config["max_retries"] - 1)
            logger.info(f"Decreased max_retries to {self.config['max_retries']} due to high success rate")
        
        # Adapt timeout based on average duration
        avg_duration = agent_stats.get("avg_duration", 60)
        self.config["timeout_seconds"] = int(avg_duration * 1.5)  # 1.5x average
        
        # Adapt fallback threshold based on fallback rate
        fallback_rate = agent_stats.get("fallback_rate", 0)
        if fallback_rate > 0.3:
            # High fallback rate - make threshold more lenient
            self.config["fallback_threshold"] = min(0.7, self.config["fallback_threshold"] + 0.1)
            logger.info(f"Increased fallback_threshold to {self.config['fallback_threshold']}")
        elif fallback_rate < 0.1:
            # Low fallback rate - can be stricter
            self.config["fallback_threshold"] = max(0.3, self.config["fallback_threshold"] - 0.1)
            logger.info(f"Decreased fallback_threshold to {self.config['fallback_threshold']}")
        
        # Use ML patterns if available
        if self.ml_detector and self.ml_detector.patterns:
            self._adapt_from_ml_patterns()
        
        return self.config
    
    def _adapt_from_ml_patterns(self):
        """Adapt based on ML-detected patterns."""
        patterns = self.ml_detector.get_pattern_summary()
        
        if not patterns["patterns"]:
            return
        
        # Find best performing pattern
        best_pattern = max(
            patterns["patterns"],
            key=lambda p: p.get("success_rate", 0)
        )
        
        # Adapt tool priority based on best pattern
        if best_pattern.get("common_tools"):
            self.config["tool_priority"] = best_pattern["common_tools"]
            logger.info(f"Adapted tool priority from ML patterns: {self.config['tool_priority']}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def recommend_strategy(self, document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend processing strategy for a document.
        
        Args:
            document_metadata: Document metadata
            
        Returns:
            Recommended strategy
        """
        # Check if we have ML patterns
        if self.ml_detector:
            # Create dummy metrics for prediction
            dummy_metrics = {
                "duration_seconds": 30,
                "references_count": 20,
                "figures_count": 5,
                "validation_errors": 0,
                "validation_warnings": 0,
                "retry_count": 0,
                "fallback_triggered": False,
                "tools_used": []
            }
            
            pattern = self.ml_detector.predict_pattern(dummy_metrics)
            if pattern:
                return {
                    "strategy": "ml_guided",
                    "expected_duration": pattern.get("avg_duration", 30),
                    "recommended_tools": pattern.get("common_tools", []),
                    "confidence": pattern.get("success_rate", 0.5)
                }
        
        # Default strategy
        return {
            "strategy": "default",
            "expected_duration": 30,
            "recommended_tools": self.config["tool_priority"],
            "confidence": 0.5
        }
