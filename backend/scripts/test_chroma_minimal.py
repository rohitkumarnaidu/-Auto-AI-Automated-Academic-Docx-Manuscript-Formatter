import os
import chromadb
from chromadb.config import Settings

try:
    print("Testing ChromaDB EphemeralClient...")
    client = chromadb.EphemeralClient()
    print("SUCCESS: EphemeralClient initialized.")
    
    print("\nTesting ChromaDB PersistentClient...")
    db_path = os.path.abspath("backend/db/test_chroma")
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    print(f"SUCCESS: PersistentClient initialized at {db_path}.")
    
    collection = client.get_or_create_collection("test_collection")
    collection.add(ids=["1"], documents=["test document"])
    res = collection.query(query_texts=["test"], n_results=1)
    print(f"SUCCESS: Query returned {res['documents']}")

except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
