# ScholarForm AI — Disaster Recovery Plan

**Last Updated:** May 21, 2026  
**RTO:** 4 hours | **RPO:** 1 hour  
**Owner:** Engineering Team

---

## Recovery Objectives

| Metric | Target | Current |
|--------|--------|---------|
| **RTO** (Recovery Time Objective) | 4 hours | < 2 hours (Render auto-deploy) |
| **RPO** (Recovery Point Objective) | 1 hour | < 15 minutes (Supabase continuous backup) |
| **MTTR** (Mean Time to Recovery) | 2 hours | < 1 hour |

---

## Disaster Scenarios

### 1. Database Failure
**Trigger:** Supabase outage, data corruption, accidental deletion

**Recovery Steps:**
1. Check Supabase status page: https://status.supabase.com
2. If Supabase is down, wait for their recovery (they handle backups)
3. If data corruption, restore from latest point-in-time backup:
   - Supabase dashboard → Database → Backups → Restore
4. Verify data integrity:
   ```bash
   python backend/scripts/verify_backup.py
   python backend/scripts/verify_migration.py
   ```
5. Restart backend to pick up restored data

**Estimated Recovery Time:** 30 minutes - 2 hours

### 2. Backend Service Failure
**Trigger:** Bad deployment, OOM crash, infrastructure failure

**Recovery Steps:**
1. Check Render dashboard for service status
2. If bad deployment, rollback:
   ```bash
   render rollback --service scholarform-backend
   ```
3. If infrastructure failure, redeploy:
   ```bash
   render deploy --service scholarform-backend
   ```
4. Verify health endpoint:
   ```bash
   curl https://api.scholarform.ai/api/v1/health/live
   ```

**Estimated Recovery Time:** 5 - 15 minutes

### 3. Frontend Service Failure
**Trigger:** Build failure, CDN outage, DNS issues

**Recovery Steps:**
1. Check Render/Vercel dashboard
2. Redeploy frontend:
   ```bash
   # If on Render:
   render deploy --service scholarform-frontend
   # If on Vercel:
   vercel --prod
   ```
3. Verify frontend loads:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://scholarform.ai
   ```

**Estimated Recovery Time:** 5 - 10 minutes

### 4. Complete Region Outage
**Trigger:** AWS/GCP region failure

**Recovery Steps:**
1. Activate secondary region (if configured)
2. Update DNS to point to secondary region
3. Restore database from cross-region backup
4. Deploy backend and frontend to secondary region
5. Verify all services

**Estimated Recovery Time:** 2 - 4 hours

---

## Backup Strategy

| Component | Backup Method | Frequency | Retention |
|-----------|--------------|-----------|-----------|
| PostgreSQL | Supabase PITR | Continuous | 7 days |
| Redis | AOF persistence | Continuous | N/A |
| Uploaded files | S3 versioning | Real-time | 30 days |
| Environment variables | Render env vars + encrypted backup | Manual | Latest |
| Code | GitHub | Every commit | Permanent |

---

## Contact List

| Role | Name | Contact |
|------|------|---------|
| On-Call Engineer | PagerDuty rotation | Via PagerDuty |
| Engineering Lead | [Name] | [Email/Slack] |
| DevOps | [Name] | [Email/Slack] |
| Supabase Support | support@supabase.com | Via dashboard |
| Render Support | support@render.com | Via dashboard |

---

## Post-Recovery Checklist

- [ ] All services responding to health checks
- [ ] Database integrity verified
- [ ] User authentication working
- [ ] Document processing pipeline functional
- [ ] API key management operational
- [ ] Monitoring dashboards showing normal metrics
- [ ] Error budget impact assessed
- [ ] Postmortem scheduled if outage > 30 minutes
