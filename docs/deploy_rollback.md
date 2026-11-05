# Deployment Rollback Runbook

## When to roll back
Roll back a release when, within 30 minutes of deployment, error rates exceed
2% of requests, p95 latency doubles against the previous hour, or a SEV1/SEV2
incident is linked to the release.

## Procedure
1. Freeze further deployments in the release channel.
2. Roll back with the deployment tool's one-click rollback to the previous
   known-good version; database migrations are NOT rolled back automatically.
3. If the release included a data migration, check the migration log: forward-
   only migrations need a compensating script approved by the data lead.
4. Verify health checks pass and error rates return to baseline for 15
   minutes before declaring the rollback complete.
5. File the rollback report the same day: version, trigger metric, and the
   fix-forward plan.

## Communication
Post in the release channel at rollback start and completion. Customer support
gets a summary within one hour if the release was customer-facing.
