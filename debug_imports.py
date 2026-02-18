import sys
import os
# Insert current dir (root) to path so we can import 'backend'
sys.path.insert(0, os.getcwd())

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    log(f"sys.path: {sys.path}")
    
    log("Importing backend.app...")
    import backend.app
    log(f"backend.app file: {getattr(backend.app, '__file__', 'unknown')}")

    log("Importing Validator via backend...")
    from backend.app.pipeline.validation.validator_v3 import DocumentValidator
    log("Import Validator success")

except Exception as e:
    log(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    log(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

    print("Importing StructureDetector...")
    from app.pipeline.structure_detection.detector import StructureDetector
    print("Import Detector success")
    
    print("Importing Routers...")
    from app.routers.documents import router
    print("Import Routers success")

except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
