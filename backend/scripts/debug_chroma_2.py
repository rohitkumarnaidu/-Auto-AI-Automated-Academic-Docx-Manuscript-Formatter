import os
import sys

# Ensure backend path is included
sys.path.append(os.path.join(os.getcwd(), "backend"))

os.environ["ANONYMIZED_TELEMETRY"] = "False"

try:
    import chromadb
    from chromadb.config import Settings
    print(f"ChromaDB version: {chromadb.__version__}")
    
    import pydantic
    print(f"Pydantic version: {pydantic.__version__}")

    # Test initialization with explicit settings
    db_path = os.path.abspath("backend/db/test_chroma_2")
    os.makedirs(db_path, exist_ok=True)
    
    print(f"Attempting to initialize PersistentClient at: {db_path} with explicit settings")
    settings = Settings(
        is_persistent=True,
        persist_directory=db_path,
        anonymized_telemetry=False
    )
    client = chromadb.Client(settings)
    print("SUCCESS: Client initialized.")
    
    collection = client.get_or_create_collection("test_col")
    print("SUCCESS: Collection created.")
    
except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
