"""
Auto-scaling for dynamic specialist pool sizing.
"""
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import psutil
import time

logger = logging.getLogger(__name__)


class AutoScalingManager:
    """
    Manage auto-scaling of specialist agent pools.
    
    Features:
    - Monitor system resources (CPU, memory)
    - Scale specialist pool up/down dynamically
    - Load balancing across specialists
    - Resource-aware scheduling
    """
    
    def __init__(
        self,
        min_workers: int = 2,
        max_workers: int = 8,
        target_cpu_percent: float = 70.0,
        target_memory_percent: float = 80.0
    ):
        """
        Initialize auto-scaling manager.
        
        Args:
            min_workers: Minimum number of workers
            max_workers: Maximum number of workers
            target_cpu_percent: Target CPU utilization
            target_memory_percent: Target memory utilization
        """
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.target_cpu_percent = target_cpu_percent
        self.target_memory_percent = target_memory_percent
        
        self.current_workers = min_workers
        self.executor = ThreadPoolExecutor(max_workers=min_workers)
        
        self.metrics_history = []
        self.scaling_events = []
    
    def get_system_metrics(self) -> Dict[str, float]:
        """
        Get current system metrics.
        
        Returns:
            System metrics (CPU, memory, etc.)
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "timestamp": time.time()
        }
    
    def should_scale_up(self, metrics: Dict[str, float]) -> bool:
        """
        Determine if should scale up.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            True if should scale up
        """
        # Scale up if CPU is high and we have capacity
        if (metrics["cpu_percent"] > self.target_cpu_percent and
            self.current_workers < self.max_workers):
            return True
        
        # Scale up if memory is available and CPU is moderate
        if (metrics["cpu_percent"] > 50 and
            metrics["memory_percent"] < self.target_memory_percent and
            self.current_workers < self.max_workers):
            return True
        
        return False
    
    def should_scale_down(self, metrics: Dict[str, float]) -> bool:
        """
        Determine if should scale down.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            True if should scale down
        """
        # Scale down if CPU is low
        if (metrics["cpu_percent"] < 30 and
            self.current_workers > self.min_workers):
            return True
        
        # Scale down if memory is high
        if (metrics["memory_percent"] > self.target_memory_percent and
            self.current_workers > self.min_workers):
            return True
        
        return False
    
    def scale_up(self):
        """Scale up the worker pool."""
        new_workers = min(self.current_workers + 1, self.max_workers)
        
        if new_workers > self.current_workers:
            # Recreate executor with more workers
            self.executor.shutdown(wait=False)
            self.executor = ThreadPoolExecutor(max_workers=new_workers)
            
            old_workers = self.current_workers
            self.current_workers = new_workers
            
            self.scaling_events.append({
                "type": "scale_up",
                "from": old_workers,
                "to": new_workers,
                "timestamp": time.time()
            })
            
            logger.info(f"Scaled up from {old_workers} to {new_workers} workers")
    
    def scale_down(self):
        """Scale down the worker pool."""
        new_workers = max(self.current_workers - 1, self.min_workers)
        
        if new_workers < self.current_workers:
            # Recreate executor with fewer workers
            self.executor.shutdown(wait=True)
            self.executor = ThreadPoolExecutor(max_workers=new_workers)
            
            old_workers = self.current_workers
            self.current_workers = new_workers
            
            self.scaling_events.append({
                "type": "scale_down",
                "from": old_workers,
                "to": new_workers,
                "timestamp": time.time()
            })
            
            logger.info(f"Scaled down from {old_workers} to {new_workers} workers")
    
    def auto_scale(self):
        """
        Perform auto-scaling based on current metrics.
        """
        metrics = self.get_system_metrics()
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Make scaling decision
        if self.should_scale_up(metrics):
            self.scale_up()
        elif self.should_scale_down(metrics):
            self.scale_down()
    
    def get_executor(self) -> ThreadPoolExecutor:
        """
        Get current executor.
        
        Returns:
            Thread pool executor
        """
        # Trigger auto-scaling check
        self.auto_scale()
        
        return self.executor
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scaling statistics."""
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        
        avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        avg_memory = sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            "current_workers": self.current_workers,
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory,
            "total_scaling_events": len(self.scaling_events),
            "scale_up_count": sum(1 for e in self.scaling_events if e["type"] == "scale_up"),
            "scale_down_count": sum(1 for e in self.scaling_events if e["type"] == "scale_down")
        }
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)
