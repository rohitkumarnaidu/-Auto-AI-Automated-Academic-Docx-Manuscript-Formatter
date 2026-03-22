$ErrorActionPreference = 'Stop'; Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..')); python -m pip install --upgrade pre-commit; python -m pre_commit install --install-hooks
