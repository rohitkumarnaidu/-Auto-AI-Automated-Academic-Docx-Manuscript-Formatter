import sys
import traceback

with open("out.log", "w", encoding="utf-8") as f:
    try:
        from app.main import app
        f.write("Success\n")
    except Exception as e:
        f.write("ERROR:\n")
        traceback.print_exc(file=f)
        sys.exit(1)
