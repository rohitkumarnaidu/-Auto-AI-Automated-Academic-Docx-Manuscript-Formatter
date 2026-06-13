# ScholarForm AI Release Process

## Versioning

ScholarForm AI follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (1.x.x) — Incompatible API or breaking database migrations
- **MINOR** (x.1.x) — Backward-compatible feature additions
- **PATCH** (x.x.1) — Backward-compatible bug fixes

Pre-release suffixes: `-alpha.N`, `-beta.N`, `-rc.N`.

## Release Cadence

| Release Type | Cadence | Examples |
|-------------|---------|----------|
| Major | ~6 months | 1.0.0, 2.0.0 |
| Minor | ~6-8 weeks | 1.1.0, 1.2.0 |
| Patch | As needed (hotfix) | 1.0.1, 1.0.2 |
| Pre-release | Before each major/minor | 1.1.0-beta.1 |

## Release Manager

Rotating role among Core Team. Responsible for shepherding the release from branch to production.

## Release Workflow

### 1. Branch & Changelog

```bash
git checkout -b release/v1.1.0
```

- Update `CHANGELOG.md` with all changes since last release
- Ensure `CITATION.cff` `version` and `date-released` are current
- Bump version in `backend/pyproject.toml` (if exists) and `frontend/package.json`

### 2. Testing Gate

All CI must pass on the release branch:

- Backend: `ruff check app && mypy app && pytest tests -m "not integration and not llm" -x -q`
- Frontend: `npm run lint && npm test && npm run build`
- E2E: `npm run test:e2e` (full suite, not just critical path)
- Docs freshness: `docs-freshness` workflow (manual trigger)

### 3. Release Candidate

```bash
git tag v1.1.0-rc.1
git push origin v1.1.0-rc.1
```

- Deploy RC to staging environment
- Run full E2E suite against staging
- 48-hour testing window for community feedback
- Fix any regressions and cut new RC if needed

### 4. Final Tag & Release

```bash
git tag v1.1.0
git push origin v1.1.0
```

- Create GitHub Release from the tag
- Attach release notes (auto-generated from CHANGELOG)
- Build Docker images and push to container registry

### 5. Deploy

- Production deployment via `deploy-production.yml` workflow (manual trigger)
- Monitor SLO dashboards for 1 hour post-deploy
- If regression detected: trigger rollback (see [Rollback Runbook](docs/runbooks/rollback.md))

### 6. Post-Release

- Create a new `v1.2.0` milestone in GitHub Issues
- Move any unfinished issues from the released milestone
- Update `docs/API.md` if API changes were made
- Update `docs/MIGRATION_GUIDES.md` if migration steps are needed

## Hotfix Process

For critical bugs in production:

1. Branch from the release tag: `git checkout -b hotfix/v1.0.1 v1.0.0`
2. Apply the fix with a single commit
3. Run minimal CI (backend fast tests + frontend lint)
4. Tag and release following step 4-5 above
5. Merge hotfix back to `main`

## Backport Policy

- Security fixes: backported to last 2 minor versions
- Critical bugs: backported to latest minor only
- Features: never backported

## Deprecation Policy

- API endpoints: deprecated for 2 minor versions before removal
- Configuration flags: deprecated for 1 minor version
- Template contracts: deprecated with migration guide

---

*Last updated: June 2026*
