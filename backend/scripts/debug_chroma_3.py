import os
import sys

# Ensure backend path is included
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    import chromadb
    print(f"ChromaDB version: {chromadb.__version__}")
    
    print("Attempting to initialize EphemeralClient...")
    client = chromadb.EphemeralClient()
    print("SUCCESS: EphemeralClient initialized.")
    
    collection = client.get_or_create_collection("test_col")
    print("SUCCESS: Collection created.")
    
except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
