import os
import json
import torch
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class RagEngine:
    """
    Local RAG Engine for academic formatting guidelines.
    Uses ChromaDB with a resilient native fallback for Pydantic v1/v2 compatibility.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        # Suppress ChromaDB Pydantic compatibility warnings
        import warnings
        warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")
        warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
        
        if persist_directory is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.persist_directory = os.path.join(base_dir, "db", "semantic_store")
        else:
            self.persist_directory = os.path.abspath(persist_directory)
            
        os.makedirs(self.persist_directory, exist_ok=True)
        
        from app.services.model_store import model_store
        if model_store.is_loaded("embedding_model"):
            self.embedding_model = model_store.get_model("embedding_model")
            print("RagEngine: Reusing global SentenceTransformer from ModelStore.")
        else:
            self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        # Native fallback state
        self.kb_file = os.path.join(self.persist_directory, "kb.json")
        self.knowledge_base = []
        
        # Attempt ChromaDB initialization
        self.chroma_enabled = False
        self.backend = "native"
        
        try:
            import chromadb
            # Attempt modern PersistentClient initialization
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection("publisher_guidelines")
            self.chroma_enabled = True
            self.backend = "chromadb"
            print(f"RagEngine: Initialized with backend={self.backend}")
        except Exception as e:
            # Graceful fallback - don't spam logs with expected compatibility issues
            error_msg = str(e)
            if "unable to infer type" in error_msg or "chroma_db_impl" in error_msg:
                # Expected Pydantic compatibility issue - use native store silently
                pass
            elif "chroma_server_nofile" in error_msg:
                print(f"RagEngine: Using native store (ChromaDB environment conflict).")
            else:
                # Unexpected error - log it
                print(f"RagEngine: ChromaDB unavailable ({error_msg}). Using native store.")
            
            self.client = None
            self.collection = None
            self.backend = "native"
            self._load_native()
            print(f"RagEngine: Initialized with backend={self.backend}")
            
    def add_guideline(self, publisher: str, section: str, text: str, metadata: Optional[Dict] = None):
        """Add a guideline rule to the store."""
        full_metadata = metadata or {}
        full_metadata.update({"publisher": publisher.upper(), "section": section.lower()})
        
        if self.chroma_enabled:
            doc_id = f"{publisher}_{section}_{hash(text)}"
            self.collection.add(ids=[doc_id], documents=[text], metadatas=[full_metadata])
        
        # Always update native store for consistent fallback
        embedding = self.embedding_model.encode(text).tolist()
        self.knowledge_base.append({"text": text, "metadata": full_metadata, "embedding": embedding})
        self._save_native()

    def query_guidelines(self, publisher: str, intent: str, top_k: int = 3) -> List[str]:
        """Retrieve the most relevant guideline text."""
        if self.chroma_enabled:
            try:
                results = self.collection.query(query_texts=[intent], n_results=top_k, where={"publisher": publisher.upper()})
                if results and results['documents']:
                    return results['documents'][0]
            except Exception as e:
                print(f"RagEngine: Chroma query failed ({e}). Falling back to native.")
        
        # Native Fallback: Cosine Similarity
        try:
            query_emb = self.embedding_model.encode(intent)
            scores = []
            for item in self.knowledge_base:
                if item['metadata']['publisher'] == publisher.upper():
                    sim = np.dot(query_emb, item['embedding']) / (np.linalg.norm(query_emb) * np.linalg.norm(item['embedding']))
                    scores.append((sim, item['text']))
            
            scores.sort(key=lambda x: x[0], reverse=True)
            return [s[1] for s in scores[:top_k]]
        except Exception as e:
            print(f"RagEngine: Native query failed ({e}). Returning empty list.")
            return []

    def query_rules(self, template_name: str, section_name: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        [PHASE-2 INTERFACE ADAPTER]
        Required by PipelineOrchestrator.
        Returns a list of rule dictionaries: [{"text": "...", "metadata": {...}}]
        """
        try:
            # Normalize inputs
            publisher = template_name.upper() if template_name else "IEEE"
            intent = section_name.lower() if section_name else "general"
            
            # Delegate to query_guidelines
            guidelines = self.query_guidelines(publisher, intent, top_k=top_k)
            
            # Formated response for the orchestrator
            return [{"text": txt, "metadata": {"publisher": publisher, "section": intent}} for txt in guidelines]
        except Exception as e:
            print(f"RagEngine Guard: query_rules failed: {e}. Returning empty list.")
            return []

    def _save_native(self):
        with open(self.kb_file, 'w') as f:
            json.dump(self.knowledge_base, f)

    def _load_native(self):
        if os.path.exists(self.kb_file):
            with open(self.kb_file, 'r') as f:
                self.knowledge_base = json.load(f)

    def reset(self):
        """Clear all indexed guidelines."""
        if self.chroma_enabled:
            import chromadb
            try:
                self.client.delete_collection("publisher_guidelines")
                self.collection = self.client.get_or_create_collection("publisher_guidelines")
            except: pass
        self.knowledge_base = []
        if os.path.exists(self.kb_file): os.remove(self.kb_file)

# Singleton Access
_rag_engine = None

def get_rag_engine() -> RagEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RagEngine()
    return _rag_engine
