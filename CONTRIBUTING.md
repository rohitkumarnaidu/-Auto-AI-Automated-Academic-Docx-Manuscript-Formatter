# Contributing to ScholarForm AI

First off, thanks for taking the time to contribute!

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to see if the bug has already been reported.
2. **Open a new issue** with a clear title and description. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots / logs if applicable
   - Environment details (OS, Python version, Node version)

### Suggesting Features

1. Open a feature request issue with:
   - A clear description of the problem you're solving
   - Proposed solution (optional)
   - Alternatives you've considered

### Pull Requests

1. **Fork** the repo and create your branch from `main`.
2. **Follow code conventions**:
   - Python: Ruff linting, type annotations via mypy
   - Frontend: ESLint with `--max-warnings 0`
3. **Write tests** — we maintain 70%+ coverage. Run:
   ```bash
   cd backend
   pytest tests -m "not integration and not llm" -x -q --cov=app
   ```
4. **Lint your code**:
   ```bash
   cd backend && ruff check app --config ruff.toml
   cd frontend && npm run lint
   ```
5. **Commit using conventional commits**:
   - `feat:` new feature
   - `fix:` bug fix
   - `refactor:` code change without feature/fix
   - `docs:` documentation
   - `test:` adding tests
   - `ci:` CI/CD changes
6. **Open a PR** against `main`. Reference any related issues.

## Development Setup

See the [README](README.md#quick-setup) for full setup instructions.

### Quick Start

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```
backend/
  app/                    # FastAPI application
    routers/              # API routes (34 endpoints)
    services/             # Business logic (25 services)
    pipeline/             # Document processing pipeline
    tasks/                # Celery background tasks
  tests/                  # Pytest test suite
  db/                     # Database migrations & semantic store

frontend/
  src/app/                # Next.js 14 App Router pages
  src/components/         # React components
  src/context/            # React context providers
  e2e/                    # Playwright E2E tests
```

## Questions?

Open a discussion or reach out to the maintainers.
