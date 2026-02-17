"""
Federated learning across multiple deployments.
"""
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class FederatedLearningNode:
    """
    Federated learning node for distributed learning.
    
    Features:
    - Share model updates without sharing data
    - Aggregate knowledge from multiple deployments
    - Privacy-preserving learning
    - Decentralized coordination
    """
    
    def __init__(
        self,
        node_id: str,
        storage_dir: str = ".federated_learning",
        coordinator_url: Optional[str] = None
    ):
        """
        Initialize federated learning node.
        
        Args:
            node_id: Unique node identifier
            storage_dir: Local storage directory
            coordinator_url: Optional coordinator server URL
        """
        self.node_id = node_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.coordinator_url = coordinator_url
        
        self.local_updates_file = self.storage_dir / f"node_{node_id}_updates.jsonl"
        self.global_model_file = self.storage_dir / "global_model.json"
        
        self.local_updates = []
        self.global_model = self._load_global_model()
    
    def _load_global_model(self) -> Dict[str, Any]:
        """Load global model state."""
        if self.global_model_file.exists():
            with open(self.global_model_file, 'r') as f:
                return json.load(f)
        return {
            "version": 0,
            "patterns": [],
            "statistics": {},
            "last_updated": None
        }
    
    def _save_global_model(self):
        """Save global model state."""
        with open(self.global_model_file, 'w') as f:
            json.dump(self.global_model, f, indent=2)
    
    def record_local_update(
        self,
        update_type: str,
        data: Dict[str, Any]
    ):
        """
        Record a local model update.
        
        Args:
            update_type: Type of update (pattern, metric, error, etc.)
            data: Update data
        """
        update = {
            "node_id": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "update_type": update_type,
            "data": data,
            "version": self.global_model["version"]
        }
        
        # Append to local updates
        with open(self.local_updates_file, 'a') as f:
            f.write(json.dumps(update) + '\n')
        
        self.local_updates.append(update)
        
        logger.info(f"Recorded local update: {update_type}")
    
    def get_local_updates(
        self,
        since_version: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get local updates since a specific version.
        
        Args:
            since_version: Get updates after this version
            
        Returns:
            List of updates
        """
        if since_version is None:
            return self.local_updates
        
        return [u for u in self.local_updates if u["version"] >= since_version]
    
    def push_updates_to_coordinator(self) -> bool:
        """
        Push local updates to coordinator.
        
        Returns:
            True if successful
        """
        if not self.coordinator_url:
            logger.warning("No coordinator URL configured")
            return False
        
        try:
            updates = self.get_local_updates()
            
            response = requests.post(
                f"{self.coordinator_url}/federated/updates",
                json={
                    "node_id": self.node_id,
                    "updates": updates
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Pushed {len(updates)} updates to coordinator")
                return True
            else:
                logger.error(f"Failed to push updates: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to push updates: {e}")
            return False
    
    def pull_global_model(self) -> bool:
        """
        Pull global model from coordinator.
        
        Returns:
            True if successful
        """
        if not self.coordinator_url:
            logger.warning("No coordinator URL configured")
            return False
        
        try:
            response = requests.get(
                f"{self.coordinator_url}/federated/global_model",
                timeout=10
            )
            
            if response.status_code == 200:
                new_model = response.json()
                
                # Update if newer version
                if new_model["version"] > self.global_model["version"]:
                    self.global_model = new_model
                    self._save_global_model()
                    logger.info(f"Updated to global model version {new_model['version']}")
                    return True
                else:
                    logger.info("Global model is up to date")
                    return True
            else:
                logger.error(f"Failed to pull global model: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pull global model: {e}")
            return False
    
    def aggregate_updates(
        self,
        all_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate updates from multiple nodes (coordinator function).
        
        Args:
            all_updates: Updates from all nodes
            
        Returns:
            Aggregated model
        """
        # Group updates by type
        patterns = []
        metrics = []
        
        for update in all_updates:
            if update["update_type"] == "pattern":
                patterns.append(update["data"])
            elif update["update_type"] == "metric":
                metrics.append(update["data"])
        
        # Aggregate patterns (simple averaging)
        aggregated_patterns = self._aggregate_patterns(patterns)
        
        # Aggregate metrics
        aggregated_metrics = self._aggregate_metrics(metrics)
        
        # Create new global model
        new_model = {
            "version": self.global_model["version"] + 1,
            "patterns": aggregated_patterns,
            "statistics": aggregated_metrics,
            "last_updated": datetime.utcnow().isoformat(),
            "contributing_nodes": len(set(u["node_id"] for u in all_updates))
        }
        
        return new_model
    
    def _aggregate_patterns(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Aggregate patterns from multiple nodes."""
        if not patterns:
            return []
        
        # Simple aggregation: merge similar patterns
        # In production, would use more sophisticated clustering
        return patterns[:10]  # Keep top 10
    
    def _aggregate_metrics(
        self,
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate metrics from multiple nodes."""
        if not metrics:
            return {}
        
        # Compute averages
        total_docs = sum(m.get("document_count", 0) for m in metrics)
        avg_duration = sum(m.get("avg_duration", 0) for m in metrics) / len(metrics)
        avg_success_rate = sum(m.get("success_rate", 0) for m in metrics) / len(metrics)
        
        return {
            "total_documents": total_docs,
            "avg_duration": avg_duration,
            "avg_success_rate": avg_success_rate,
            "contributing_nodes": len(metrics)
        }
    
    def sync(self) -> bool:
        """
        Synchronize with coordinator (push + pull).
        
        Returns:
            True if successful
        """
        push_success = self.push_updates_to_coordinator()
        pull_success = self.pull_global_model()
        
        return push_success and pull_success
    
    def get_status(self) -> Dict[str, Any]:
        """Get node status."""
        return {
            "node_id": self.node_id,
            "local_updates": len(self.local_updates),
            "global_model_version": self.global_model["version"],
            "coordinator_connected": self.coordinator_url is not None,
            "last_sync": self.global_model.get("last_updated")
        }


class FederatedCoordinator:
    """
    Coordinator server for federated learning.
    
    Aggregates updates from multiple nodes and distributes global model.
    """
    
    def __init__(self, storage_dir: str = ".federated_coordinator"):
        """
        Initialize federated coordinator.
        
        Args:
            storage_dir: Storage directory
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.updates_file = self.storage_dir / "all_updates.jsonl"
        self.global_model_file = self.storage_dir / "global_model.json"
        
        self.all_updates = []
        self.global_model = self._load_global_model()
        self.registered_nodes = set()
    
    def _load_global_model(self) -> Dict[str, Any]:
        """Load global model."""
        if self.global_model_file.exists():
            with open(self.global_model_file, 'r') as f:
                return json.load(f)
        return {
            "version": 0,
            "patterns": [],
            "statistics": {},
            "last_updated": None
        }
    
    def receive_updates(
        self,
        node_id: str,
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Receive updates from a node.
        
        Args:
            node_id: Node ID
            updates: List of updates
            
        Returns:
            True if successful
        """
        self.registered_nodes.add(node_id)
        
        # Store updates
        with open(self.updates_file, 'a') as f:
            for update in updates:
                f.write(json.dumps(update) + '\n')
        
        self.all_updates.extend(updates)
        
        logger.info(f"Received {len(updates)} updates from node {node_id}")
        return True
    
    def aggregate_and_update(self) -> Dict[str, Any]:
        """
        Aggregate all updates and create new global model.
        
        Returns:
            New global model
        """
        # Use FederatedLearningNode's aggregation logic
        temp_node = FederatedLearningNode("coordinator")
        temp_node.global_model = self.global_model
        
        new_model = temp_node.aggregate_updates(self.all_updates)
        
        # Save new global model
        self.global_model = new_model
        with open(self.global_model_file, 'w') as f:
            json.dump(new_model, f, indent=2)
        
        logger.info(f"Created global model version {new_model['version']}")
        return new_model
    
    def get_global_model(self) -> Dict[str, Any]:
        """Get current global model."""
        return self.global_model
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return {
            "registered_nodes": len(self.registered_nodes),
            "total_updates": len(self.all_updates),
            "global_model_version": self.global_model["version"],
            "last_aggregation": self.global_model.get("last_updated")
        }
