import sys
import os
sys.path.append("backend")

print("Importing Validator v3...", file=sys.stderr)
from backend.app.pipeline.validation.validator_v3 import DocumentValidator
print("Import Success", file=sys.stderr)
