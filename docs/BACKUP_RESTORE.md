# ScholarForm AI — Backup & Restore Procedures

**Last Updated:** May 21, 2026

---

## Database Backup

### Supabase Automated Backups
Supabase provides **continuous point-in-time recovery (PITR)** for Pro and Team plans.

**Verify Backup Status:**
```bash
cd backend
python scripts/verify_backup.py
```

**Restore from Backup:**
1. Go to Supabase Dashboard → Database → Backups
2. Select the restore point (PITR allows any timestamp within retention period)
3. Click "Restore"
4. Wait for restoration to complete (typically 5-15 minutes)
5. Verify data integrity:
   ```bash
   python scripts/verify_migration.py
   ```

### Manual Backup (for compliance)
```bash
# Export full database dump
pg_dump $SUPABASE_DB_URL --format=custom --file=backup_$(date +%Y%m%d_%H%M%S).dump

# Export specific tables
pg_dump $SUPABASE_DB_URL --table=documents --table=profiles --format=plain --file=schema_backup.sql
```

---

## File Storage Backup

### Uploaded Documents
Files are stored in Supabase Storage buckets. To backup:

```bash
# List all files in storage
supabase storage ls --project-ref YOUR_PROJECT_REF

# Download all files
supabase storage download --project-ref YOUR_PROJECT_REF --recursive / uploads_backup/
```

### Template Files
Templates are stored in `backend/app/templates/` and version-controlled in Git.

---

## Environment Variables Backup

### Render Environment Variables
1. Go to Render Dashboard → Environment
2. Export variables (manual copy)
3. Store encrypted backup in 1Password/LastPass

### Local .env Backup
```bash
# Encrypt and backup
gpg --symmetric --cipher-algo AES256 backend/.env
# Store the .env.gpg file securely
```

---

## Redis Backup

Redis is used for caching and rate limiting. Data is ephemeral and can be rebuilt.

**If Redis data is lost:**
1. Rate limit counters reset (acceptable)
2. Cache warms up naturally as requests come in
3. No data loss — Redis only stores transient data

---

## Restore Verification

After any restore, run these checks:

```bash
# 1. Database connectivity
python scripts/verify_backup.py

# 2. Schema sync
python scripts/verify_migration.py

# 3. Backend health
curl -s https://api.scholarform.ai/api/v1/health/live | jq

# 4. Frontend health
curl -s -o /dev/null -w "%{http_code}" https://scholarform.ai

# 5. Run smoke tests
cd backend
pytest tests/test_smoke.py -v --no-cov
```

---

## Backup Schedule

| Task | Frequency | Automation |
|------|-----------|------------|
| Supabase PITR | Continuous | Automatic |
| Manual DB dump | Weekly | Cron job |
| File storage sync | Daily | Supabase Storage API |
| Env var backup | On change | Manual |
| Backup verification | Weekly | CI/CD pipeline |
