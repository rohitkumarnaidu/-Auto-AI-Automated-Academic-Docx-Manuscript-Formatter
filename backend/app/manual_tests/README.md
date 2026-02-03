# Manual Tests

This directory contains manual test scripts to validate individual pipeline components.

## Available Tests

- **test_models.py** - Validate all data model definitions

## Usage

Run tests from the `backend/` directory:

```bash
cd automated-manuscript-formatter/backend
python -m app.manual_tests.test_models
```

## No Automated Testing

Per project requirements, we use manual testing only.
No pytest, unittest, or CI/CD automated tests.
