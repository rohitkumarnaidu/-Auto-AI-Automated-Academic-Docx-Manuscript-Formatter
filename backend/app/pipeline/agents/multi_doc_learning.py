"""
Multi-document learning for cross-document insights.
"""
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MultiDocumentLearner:
    """
    Learn patterns across multiple documents.
    
    Tracks:
    - Document type patterns
    - Author patterns
    - Venue patterns
    - Quality trends
    """
    
    def __init__(self, storage_dir: str = ".multi_doc_learning"):
        """
        Initialize multi-document learner.
        
        Args:
            storage_dir: Directory to store learning data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.document_db = self.storage_dir / "documents.jsonl"
        self.insights_file = self.storage_dir / "insights.json"
        
        self.insights = self._load_insights()
    
    def _load_insights(self) -> Dict[str, Any]:
        """Load existing insights."""
        if self.insights_file.exists():
            with open(self.insights_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "author_patterns": {},
            "venue_patterns": {},
            "document_types": {},
            "quality_trends": []
        }
    
    def _save_insights(self):
        """Save insights to file."""
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, indent=2)
    
    def record_document(
        self,
        document_id: str,
        metadata: Dict[str, Any],
        metrics: Dict[str, Any]
    ):
        """
        Record a processed document.
        
        Args:
            document_id: Document ID
            metadata: Document metadata (title, authors, venue, etc.)
            metrics: Processing metrics
        """
        record = {
            "document_id": document_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "metrics": metrics
        }
        
        # Append to document database
        with open(self.document_db, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
        
        # Update insights
        self._update_insights(metadata, metrics)
    
    def _update_insights(self, metadata: Dict[str, Any], metrics: Dict[str, Any]):
        """Update insights based on new document."""
        # Author patterns
        authors = metadata.get("authors", [])
        for author in authors:
            if author not in self.insights["author_patterns"]:
                self.insights["author_patterns"][author] = {
                    "document_count": 0,
                    "avg_references": 0,
                    "avg_quality": 0
                }
            
            pattern = self.insights["author_patterns"][author]
            pattern["document_count"] += 1
            
            # Update running averages
            n = pattern["document_count"]
            pattern["avg_references"] = (
                (pattern["avg_references"] * (n - 1) + metrics.get("references_count", 0)) / n
            )
            pattern["avg_quality"] = (
                (pattern["avg_quality"] * (n - 1) + (1 if metrics.get("success", False) else 0)) / n
            )
        
        # Venue patterns
        venue = metadata.get("venue", "unknown")
        if venue not in self.insights["venue_patterns"]:
            self.insights["venue_patterns"][venue] = {
                "document_count": 0,
                "avg_references": 0,
                "avg_figures": 0
            }
        
        venue_pattern = self.insights["venue_patterns"][venue]
        venue_pattern["document_count"] += 1
        n = venue_pattern["document_count"]
        venue_pattern["avg_references"] = (
            (venue_pattern["avg_references"] * (n - 1) + metrics.get("references_count", 0)) / n
        )
        venue_pattern["avg_figures"] = (
            (venue_pattern["avg_figures"] * (n - 1) + metrics.get("figures_count", 0)) / n
        )
        
        # Document type patterns
        doc_type = metadata.get("document_type", "unknown")
        if doc_type not in self.insights["document_types"]:
            self.insights["document_types"][doc_type] = {
                "count": 0,
                "avg_duration": 0
            }
        
        type_pattern = self.insights["document_types"][doc_type]
        type_pattern["count"] += 1
        n = type_pattern["count"]
        type_pattern["avg_duration"] = (
            (type_pattern["avg_duration"] * (n - 1) + metrics.get("duration_seconds", 0)) / n
        )
        
        # Quality trends
        self.insights["quality_trends"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "success": metrics.get("success", False),
            "errors": metrics.get("validation_errors", 0)
        })
        
        # Keep only last 100 trends
        if len(self.insights["quality_trends"]) > 100:
            self.insights["quality_trends"] = self.insights["quality_trends"][-100:]
        
        self._save_insights()
    
    def get_author_insights(self, author: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific author."""
        return self.insights["author_patterns"].get(author)
    
    def get_venue_insights(self, venue: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific venue."""
        return self.insights["venue_patterns"].get(venue)
    
    def get_similar_documents(
        self,
        metadata: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar documents based on metadata.
        
        Args:
            metadata: Document metadata
            limit: Maximum number of similar documents
            
        Returns:
            List of similar documents
        """
        if not self.document_db.exists():
            return []
        
        similar = []
        target_authors = set(metadata.get("authors", []))
        target_venue = metadata.get("venue", "")
        
        with open(self.document_db, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    doc = json.loads(line.strip())
                    doc_authors = set(doc["metadata"].get("authors", []))
                    doc_venue = doc["metadata"].get("venue", "")
                    
                    # Calculate similarity score
                    score = 0
                    if target_authors & doc_authors:  # Common authors
                        score += 2
                    if target_venue == doc_venue and target_venue:
                        score += 1
                    
                    if score > 0:
                        similar.append({
                            "document_id": doc["document_id"],
                            "similarity_score": score,
                            "metadata": doc["metadata"],
                            "metrics": doc["metrics"]
                        })
                except:
                    continue
        
        # Sort by similarity and return top N
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar[:limit]
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """Get summary of all insights."""
        return {
            "total_authors": len(self.insights["author_patterns"]),
            "total_venues": len(self.insights["venue_patterns"]),
            "document_types": len(self.insights["document_types"]),
            "quality_trend_count": len(self.insights["quality_trends"]),
            "top_authors": sorted(
                self.insights["author_patterns"].items(),
                key=lambda x: x[1]["document_count"],
                reverse=True
            )[:5],
            "top_venues": sorted(
                self.insights["venue_patterns"].items(),
                key=lambda x: x[1]["document_count"],
                reverse=True
            )[:5]
        }
