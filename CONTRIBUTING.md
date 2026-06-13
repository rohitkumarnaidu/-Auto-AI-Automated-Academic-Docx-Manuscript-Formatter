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

### Documentation Contributions

1. All `.md` files must start with YAML frontmatter (see [Style Guide](docs/.docs-style-guide.md)).
2. Keep `last_updated` current — set to the month of your change.
3. Add `sidebar_position` based on the category ordering scheme.
4. Every new page must be added to `docs/README.md` index.
5. Code examples must be tested — if you add a curl command, verify it works against a running instance.
6. Use Mermaid diagrams for architecture and flow documentation (not ASCII art or screenshots of code).
7. **Broken links cause CI failure** — run the freshness check locally before pushing.
8. See the full [Documentation Style Guide](docs/.docs-style-guide.md) for formatting conventions.

### Developer Certificate of Origin

All contributions must include a `Signed-off-by` trailer in every commit, certifying that you have read and agree to the [Developer Certificate of Origin](DEVELOPER_CERTIFICATE_OF_ORIGIN.md) (DCO). Use `git commit -s` to sign off automatically.

### Pull Requests

1. **Fork** the repo and create your branch from `main`.
2. **Use the [pull request template](PULL_REQUEST_TEMPLATE.md)** — fill out the checklist.
3. **Sign off your commits** (`git commit -s`) to comply with the DCO.
4. **Build the project first**: run `BUILDING.md` instructions to verify your environment.
5. **Follow code conventions**:
   - Python: Ruff linting, type annotations via mypy
   - Frontend: ESLint with `--max-warnings 0`
6. **Write tests** — we maintain 70%+ coverage. Run:
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
  src/app/                # Next.js 16 App Router pages
  src/components/         # React components
  src/context/            # React context providers
  e2e/                    # Playwright E2E tests
```

## Questions?

Open a discussion or reach out to the maintainers.
