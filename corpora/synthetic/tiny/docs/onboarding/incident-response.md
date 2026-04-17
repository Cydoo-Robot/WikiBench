# Incident Response Runbook

## Severity Levels

| Level | SLA (ack) | SLA (resolve) | Example |
|-------|-----------|---------------|---------|
| SEV-1 | 5 min     | 1 hr          | Complete outage of api-gateway |
| SEV-2 | 15 min    | 4 hr          | Billing service degraded |
| SEV-3 | 2 hr      | 24 hr         | Non-critical background job failure |

## On-Call Process

1. PagerDuty alerts fire; on-call engineer acknowledges within SLA.
2. Open a `#inc-YYYY-MM-DD` Slack channel.
3. Diagnose using Datadog dashboards and `kubectl logs`.
4. Mitigate first; root-cause analysis follows in a post-mortem.

## Post-Mortem Policy

All SEV-1 and SEV-2 incidents require a blameless post-mortem within **48 hours**.
Post-mortems are stored in Confluence under `Engineering > Incidents`.

> **Note:** The on-call rotation runs weekly, not monthly.
