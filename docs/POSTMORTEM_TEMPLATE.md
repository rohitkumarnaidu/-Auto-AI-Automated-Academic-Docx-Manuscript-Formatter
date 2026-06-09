# Incident Postmortem Template

**Incident ID:** INC-YYYY-NNN  
**Date:** YYYY-MM-DD  
**Author:** [Name]  
**Status:** Draft / Review / Complete

---

## Summary

| Field | Value |
|-------|-------|
| **Title** | Brief description of incident |
| **Severity** | P0 / P1 / P2 / P3 |
| **Duration** | Start time → End time (X minutes) |
| **Impact** | Number of users affected, revenue impact |
| **Root Cause** | Single sentence root cause |

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
| HH:MM | Incident begins (first symptom) |
| HH:MM | Alert fires |
| HH:MM | On-call acknowledges |
| HH:MM | Mitigation applied |
| HH:MM | Service recovered |
| HH:MM | Incident resolved |

---

## Impact Assessment

- **Users affected:** X
- **Requests failed:** X
- **Error budget consumed:** X%
- **Revenue impact:** $X (if applicable)
- **Data loss:** None / X records

---

## Root Cause Analysis

### What happened?
[Detailed description]

### Why did it happen?
[5 Whys analysis]

1. Why? →
2. Why? →
3. Why? →
4. Why? →
5. Why? →

### Contributing Factors
- [ ] Monitoring gap
- [ ] Missing alert
- [ ] Insufficient testing
- [ ] Configuration error
- [ ] Dependency failure
- [ ] Other:

---

## Resolution

### Immediate Fix
[What was done to resolve the incident]

### Long-term Fix
[What needs to be done to prevent recurrence]

---

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add monitoring for X | @name | YYYY-MM-DD | Open |
| Fix root cause Y | @name | YYYY-MM-DD | Open |
| Update runbook Z | @name | YYYY-MM-DD | Open |
| Add test for scenario W | @name | YYYY-MM-DD | Open |

---

## Lessons Learned

### What went well
- [ ] Alert fired correctly
- [ ] On-call responded quickly
- [ ] Runbook was helpful
- [ ] Communication was clear

### What went wrong
- [ ] Alert was delayed
- [ ] Runbook was outdated
- [ ] Fix took too long
- [ ] Communication was unclear

### Where we got lucky
- [ ] Incident happened during low-traffic hours
- [ ] Right person was on-call
- [ ] Backup system worked

---

## Review

| Role | Name | Date | Sign-off |
|------|------|------|----------|
| Author | | | ☐ |
| Engineering Lead | | | ☐ |
| On-Call | | | ☐ |
