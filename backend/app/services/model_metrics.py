"""
Model Performance Metrics - Track AI model performance and quality.

Tracks:
- Model usage statistics
- Response times (latency)
- Success/failure rates
- Quality scores (when available)
- Fallback frequency
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict


class ModelMetrics:
    """Track and analyze AI model performance metrics."""
    
    def __init__(self):
        """Initialize metrics storage."""
        self.metrics = {
            "nvidia": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency": 0.0,
                "avg_latency": 0.0,
                "last_used": None
            },
            "deepseek": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency": 0.0,
                "avg_latency": 0.0,
                "last_used": None
            },
            "rules": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency": 0.0,
                "avg_latency": 0.0,
                "last_used": None
            }
        }
        
        self.fallback_chain = []  # Track fallback sequences
        self.quality_scores = []  # Track quality when available
    
    def record_call(
        self,
        model: str,
        success: bool,
        latency: float,
        quality_score: Optional[float] = None
    ):
        """
        Record a model API call.
        
        Args:
            model: Model name ('nvidia', 'deepseek', 'rules')
            success: Whether call succeeded
            latency: Response time in seconds
            quality_score: Optional quality score (0.0 to 1.0)
        """
        model_key = model.lower()
        if model_key not in self.metrics:
            return
        
        metrics = self.metrics[model_key]
        metrics["total_calls"] += 1
        
        if success:
            metrics["successful_calls"] += 1
        else:
            metrics["failed_calls"] += 1
        
        metrics["total_latency"] += latency
        metrics["avg_latency"] = metrics["total_latency"] / metrics["total_calls"]
        metrics["last_used"] = datetime.utcnow().isoformat()
        
        if quality_score is not None:
            self.quality_scores.append({
                "model": model,
                "score": quality_score,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def record_fallback(self, from_model: str, to_model: str, reason: str):
        """Record a fallback event."""
        self.fallback_chain.append({
            "from": from_model,
            "to": to_model,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "models": self.metrics,
            "fallback_rate": len(self.fallback_chain) / max(1, sum(m["total_calls"] for m in self.metrics.values())),
            "total_fallbacks": len(self.fallback_chain),
            "avg_quality_scores": {
                model: sum(s["score"] for s in self.quality_scores if s["model"] == model) / max(1, len([s for s in self.quality_scores if s["model"] == model]))
                for model in ["nvidia", "deepseek", "rules"]
            }
        }
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Compare model performance."""
        return {
            "nvidia_vs_deepseek": {
                "nvidia_success_rate": self.metrics["nvidia"]["successful_calls"] / max(1, self.metrics["nvidia"]["total_calls"]),
                "deepseek_success_rate": self.metrics["deepseek"]["successful_calls"] / max(1, self.metrics["deepseek"]["total_calls"]),
                "nvidia_avg_latency": self.metrics["nvidia"]["avg_latency"],
                "deepseek_avg_latency": self.metrics["deepseek"]["avg_latency"],
                "nvidia_faster": self.metrics["nvidia"]["avg_latency"] < self.metrics["deepseek"]["avg_latency"]
            }
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file."""
        data = {
            "metrics": self.metrics,
            "fallback_chain": self.fallback_chain,
            "quality_scores": self.quality_scores,
            "summary": self.get_summary(),
            "comparison": self.get_model_comparison(),
            "exported_at": datetime.utcnow().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Metrics exported to {filepath}")


# Global metrics instance
_model_metrics = ModelMetrics()


def get_model_metrics() -> ModelMetrics:
    """Get global metrics instance."""
    return _model_metrics
