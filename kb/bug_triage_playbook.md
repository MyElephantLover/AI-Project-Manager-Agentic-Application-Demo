## Bug Triage Playbook

### Purpose

This document defines how bugs are evaluated, prioritized, and assigned.

**Severity Levels**
- Sev 1 (Critical)
System outage
App completely unusable
Security issue
- Sev 2 (High)
Major feature not working
Many users impacted
- Sev 3 (Medium)
Partial issue or workaround exists
- Sev 4 (Low)
Minor issue, cosmetic bug

### Priority Mapping

| Severity | Priority |
| -------- | -------- |
| Sev 1 | P0 |
| Sev 2 | P1 |
| Sev 3 | P2 |
| Sev 4 | P3 |

### Assignment Rules

- Frontend Team → UI issues, buttons, layout
- Backend Team → APIs, server errors
- Data Team → data issues, pipelines
- Platform Team → infrastructure, deployments

### Triage Steps

- Confirm it is a bug (not a feature request)
- Identify severity level
- Assign priority
- Assign team
- Define next step:
Fix immediately (P0/P1)
Add to backlog (P2/P3)