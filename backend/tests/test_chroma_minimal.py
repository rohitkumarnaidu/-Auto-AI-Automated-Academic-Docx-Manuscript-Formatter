"""
Minimal ChromaDB smoke tests.

The project supports native fallback when ChromaDB cannot initialize
(for example on Python 3.14 with older chromadb builds).
These tests should pass in both environments and must not be skipped.
"""
import warnings


def _create_ephemeral_client():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter("ignore", UserWarning)
        import chromadb
        return chromadb.EphemeralClient()


def _assert_known_chroma_compat_error(exc: Exception) -> None:
    message = str(exc).lower()
    assert any(
        token in message
        for token in (
            "forwardref._evaluate",
            "core pydantic v1",
            "pydantic",
            "unable to infer type",
        )
    ), f"Unexpected ChromaDB failure: {exc}"


def test_chroma_ephemeral_client():
    """ChromaDB EphemeralClient initializes, or fails with known compat issue."""
    try:
        client = _create_ephemeral_client()
    except Exception as exc:  # pragma: no cover - compatibility-specific branch
        _assert_known_chroma_compat_error(exc)
        return

    assert client is not None


def test_chroma_persistent_client_and_query(tmp_path):
    """ChromaDB PersistentClient query works, or compat failure is detected."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            warnings.simplefilter("ignore", UserWarning)
            import chromadb

            db_path = str(tmp_path / "test_chroma")
            client = chromadb.PersistentClient(path=db_path)
            collection = client.get_or_create_collection("test_collection")
            collection.add(ids=["1"], documents=["test document"])
            result = collection.query(query_texts=["test"], n_results=1)
    except Exception as exc:  # pragma: no cover - compatibility-specific branch
        _assert_known_chroma_compat_error(exc)
        return

    assert result["documents"], "Expected at least one document returned"
