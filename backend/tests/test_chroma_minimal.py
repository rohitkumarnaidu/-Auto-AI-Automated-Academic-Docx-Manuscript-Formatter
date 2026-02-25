"""
Minimal ChromaDB smoke tests.

NOTE: ChromaDB's pydantic v1 shim is broken on Python >=3.14 due to
ForwardRef._evaluate API removal. Tests are skipped automatically on
those versions. They run normally on Python 3.11.
"""
import os
import sys
import pytest

CHROMA_SKIP_REASON = (
    "ChromaDB pydantic-v1 shim is incompatible with Python >= 3.14 "
    "(ForwardRef._evaluate removed). Upgrade chromadb to >=0.5 for native pydantic-v2 support."
)
requires_chroma = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason=CHROMA_SKIP_REASON,
)


@requires_chroma
def test_chroma_ephemeral_client():
    """ChromaDB EphemeralClient should initialise without errors."""
    import chromadb
    client = chromadb.EphemeralClient()
    assert client is not None


@requires_chroma
def test_chroma_persistent_client_and_query(tmp_path):
    """ChromaDB PersistentClient should store and query a document."""
    import chromadb
    db_path = str(tmp_path / "test_chroma")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("test_collection")
    collection.add(ids=["1"], documents=["test document"])
    result = collection.query(query_texts=["test"], n_results=1)
    assert result["documents"], "Expected at least one document returned"
