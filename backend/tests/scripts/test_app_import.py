
import sys
import traceback

try:
    print("Attempting to import app.main...")
    from app.main import app
    print("SUCCESS: App imported!")
except Exception:
    traceback.print_exc()
    sys.exit(1)
