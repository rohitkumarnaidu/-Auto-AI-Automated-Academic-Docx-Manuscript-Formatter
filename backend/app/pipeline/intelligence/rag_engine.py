"""
RAG Engine — Local Retrieval-Augmented Generation for academic formatting guidelines.

Embedding model priority:
  1. BAAI/bge-m3  (1024d, 8192 token context, multilingual, dense+sparse)
  2. BAAI/bge-small-en-v1.5  (384d fallback if BGE-M3 fails to load)
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #
PRIMARY_MODEL = "BAAI/bge-m3"
FALLBACK_MODEL = "BAAI/bge-small-en-v1.5"

# Embedding dimensions per model (used for ChromaDB collection naming)
MODEL_DIMENSIONS = {
    PRIMARY_MODEL: 1024,
    FALLBACK_MODEL: 384,
}

# Collection names — separate collections to avoid dimension mismatches
COLLECTION_PRIMARY = "guidelines_bge_m3"       # 1024-d
COLLECTION_FALLBACK = "publisher_guidelines"    # 384-d (legacy)


class RagEngine:
    """
    Local RAG Engine for academic formatting guidelines.
    Uses ChromaDB with a resilient native fallback for Pydantic v1/v2 compatibility.

    Model loading order:
      1. Reuse model from global ModelStore (if pre-loaded at startup)
      2. Try BAAI/bge-m3  (best quality, 1024d, 8192 tokens)
      3. Fall back to BAAI/bge-small-en-v1.5  (lighter, 384d)
    """

    def __init__(self, persist_directory: Optional[str] = None):
        # Suppress ChromaDB Pydantic compatibility warnings
        import warnings
        warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")
        warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")

        if persist_directory is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            self.persist_directory = os.path.join(base_dir, "db", "semantic_store")
        else:
            self.persist_directory = os.path.abspath(persist_directory)

        os.makedirs(self.persist_directory, exist_ok=True)

        # ---- Load embedding model (with fallback) ---- #
        self.embedding_model = None
        self.active_model_name: str = ""
        self._load_embedding_model()

        # ---- Resolve collection name based on active model ---- #
        if self.active_model_name == PRIMARY_MODEL:
            self._collection_name = COLLECTION_PRIMARY
        else:
            self._collection_name = COLLECTION_FALLBACK

        # Native fallback state
        self.kb_file = os.path.join(self.persist_directory, "kb.json")
        self.knowledge_base: List[Dict[str, Any]] = []

        # Attempt ChromaDB initialization
        self.chroma_enabled = False
        self.backend = "native"

        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(self._collection_name)
            self.chroma_enabled = True
            self.backend = "chromadb"
            print(
                f"RagEngine: Initialized with backend={self.backend}, "
                f"model={self.active_model_name}, "
                f"collection={self._collection_name}"
            )
        except Exception as e:
            error_msg = str(e)
            _known_compat_errors = (
                "unable to infer type",
                "chroma_db_impl",
                "np.float_",
                "Core Pydantic V1",
                "chroma_server_nofile",
                "ConfigError",
            )
            is_known = any(s in error_msg for s in _known_compat_errors)

            if not is_known:
                print(f"RagEngine: ChromaDB unavailable ({error_msg}). Using native store.")

            self.client = None
            self.collection = None
            self.backend = "native"
            self._load_native()
            print(
                f"RagEngine: Initialized with backend={self.backend}, "
                f"model={self.active_model_name}"
            )

    # ------------------------------------------------------------------ #
    #  Model loading
    # ------------------------------------------------------------------ #
    def _load_embedding_model(self):
        """Load the embedding model with graceful fallback."""
        from sentence_transformers import SentenceTransformer

        # 1. Check ModelStore for a pre-loaded model
        from app.services.model_store import model_store
        if model_store.is_loaded("embedding_model"):
            self.embedding_model = model_store.get_model("embedding_model")
            # Determine which model it is by checking dimension
            test_dim = self.embedding_model.get_sentence_embedding_dimension()
            if test_dim == MODEL_DIMENSIONS[PRIMARY_MODEL]:
                self.active_model_name = PRIMARY_MODEL
            else:
                self.active_model_name = FALLBACK_MODEL
            print(
                f"RagEngine: Reusing global SentenceTransformer from ModelStore "
                f"(dim={test_dim}, model={self.active_model_name})."
            )
            return

        # 2. Try loading BGE-M3 (primary)
        try:
            print(f"RagEngine: Loading primary model '{PRIMARY_MODEL}'...")
            self.embedding_model = SentenceTransformer(PRIMARY_MODEL)
            self.active_model_name = PRIMARY_MODEL
            # Register in ModelStore for reuse
            model_store.set_model("embedding_model", self.embedding_model)
            print(
                f"RagEngine: ✅ Primary model loaded successfully "
                f"(dim={self.embedding_model.get_sentence_embedding_dimension()})."
            )
            return
        except Exception as exc:
            logger.warning(
                "RagEngine: Failed to load primary model '%s': %s. "
                "Falling back to '%s'.",
                PRIMARY_MODEL, exc, FALLBACK_MODEL,
            )

        # 3. Fallback to bge-small-en-v1.5
        try:
            print(f"RagEngine: Loading fallback model '{FALLBACK_MODEL}'...")
            self.embedding_model = SentenceTransformer(FALLBACK_MODEL)
            self.active_model_name = FALLBACK_MODEL
            model_store.set_model("embedding_model", self.embedding_model)
            print(
                f"RagEngine: ✅ Fallback model loaded "
                f"(dim={self.embedding_model.get_sentence_embedding_dimension()})."
            )
        except Exception as exc:
            logger.error(
                "RagEngine: Failed to load fallback model '%s': %s. "
                "Embedding will be unavailable.",
                FALLBACK_MODEL, exc,
            )
            self.active_model_name = "none"

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def add_guideline(
        self, publisher: str, section: str, text: str, metadata: Optional[Dict] = None
    ):
        """Add a guideline rule to the store."""
        full_metadata = metadata or {}
        full_metadata.update({"publisher": publisher.upper(), "section": section.lower()})

        if self.chroma_enabled:
            doc_id = f"{publisher}_{section}_{hash(text)}"
            self.collection.add(
                ids=[doc_id], documents=[text], metadatas=[full_metadata]
            )

        # Always update native store for consistent fallback
        if self.embedding_model is not None:
            embedding = self.embedding_model.encode(text).tolist()
        else:
            embedding = []
        self.knowledge_base.append(
            {"text": text, "metadata": full_metadata, "embedding": embedding}
        )
        self._save_native()

    def query_guidelines(
        self, publisher: str, intent: str, top_k: int = 3
    ) -> List[str]:
        """Retrieve the most relevant guideline text."""
        if self.chroma_enabled:
            try:
                results = self.collection.query(
                    query_texts=[intent],
                    n_results=top_k,
                    where={"publisher": publisher.upper()},
                )
                if results and results["documents"]:
                    return results["documents"][0]
            except Exception as e:
                print(f"RagEngine: Chroma query failed ({e}). Falling back to native.")

        # Native Fallback: Cosine Similarity
        if self.embedding_model is None:
            return []

        try:
            query_emb = self.embedding_model.encode(intent)
            scores = []
            for item in self.knowledge_base:
                if item["metadata"]["publisher"] == publisher.upper():
                    item_emb = np.array(item["embedding"])
                    if len(item_emb) == 0:
                        continue
                    sim = np.dot(query_emb, item_emb) / (
                        np.linalg.norm(query_emb) * np.linalg.norm(item_emb)
                    )
                    scores.append((sim, item["text"]))

            scores.sort(key=lambda x: x[0], reverse=True)
            return [s[1] for s in scores[:top_k]]
        except Exception as e:
            print(f"RagEngine: Native query failed ({e}). Returning empty list.")
            return []

    def query_rules(
        self, template_name: str, section_name: str, top_k: int = 2
    ) -> List[Dict[str, Any]]:
        """
        [PHASE-2 INTERFACE ADAPTER]
        Required by PipelineOrchestrator.
        Returns a list of rule dictionaries: [{"text": "...", "metadata": {...}}]
        """
        try:
            publisher = template_name.upper() if template_name else "IEEE"
            intent = section_name.lower() if section_name else "general"

            guidelines = self.query_guidelines(publisher, intent, top_k=top_k)

            return [
                {"text": txt, "metadata": {"publisher": publisher, "section": intent}}
                for txt in guidelines
            ]
        except Exception as e:
            print(f"RagEngine Guard: query_rules failed: {e}. Returning empty list.")
            return []

    # ------------------------------------------------------------------ #
    #  Persistence
    # ------------------------------------------------------------------ #
    def _save_native(self):
        with open(self.kb_file, "w") as f:
            json.dump(self.knowledge_base, f)

    def _load_native(self):
        if os.path.exists(self.kb_file):
            with open(self.kb_file, "r") as f:
                self.knowledge_base = json.load(f)

    def reset(self):
        """Clear all indexed guidelines."""
        if self.chroma_enabled:
            try:
                self.client.delete_collection(self._collection_name)
                self.collection = self.client.get_or_create_collection(
                    self._collection_name
                )
            except Exception:
                pass
        self.knowledge_base = []
        if os.path.exists(self.kb_file):
            os.remove(self.kb_file)


# --------------------------------------------------------------------------- #
#  Singleton Access
# --------------------------------------------------------------------------- #
_rag_engine = None


def get_rag_engine() -> RagEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RagEngine()
    return _rag_engine
