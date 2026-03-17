#!/bin/bash
# Run trusted-core tests (unit tests without integration or llm or external services)
source .venv/bin/activate
pytest tests -m "not integration and not llm" -x -q
