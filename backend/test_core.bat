@echo off
REM Run trusted-core tests (unit tests without integration or llm or external services)
.\.venv\Scripts\python.exe -m pytest tests -m "not integration and not llm" -x -q
