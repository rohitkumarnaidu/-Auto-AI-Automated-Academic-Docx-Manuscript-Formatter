# Branch Protection Settings

Apply these settings in GitHub for the `main` branch.

## Required Status Checks
- `backend-ci`
- `frontend-ci`
- `security`

## Rules
- Require pull request reviews before merging.
- Require status checks to pass before merging.
- Disallow direct pushes to `main`.
