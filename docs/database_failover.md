# Database Failover Runbook

## When to fail over
Fail over the primary reporting database when the primary is unreachable for
more than 3 minutes, or when replication lag on the standby exceeds 10 minutes
and the primary shows disk errors.

## Procedure
1. Announce the failover in the ops channel before starting.
2. Stop the nightly batch scheduler so no new jobs start mid-failover.
3. Promote the standby using the cluster manager: `dbctl promote standby-02`.
4. Repoint the reporting connection string to the promoted host.
5. Run the smoke query pack (row counts on the five core tables) and compare
   against the last known-good snapshot.
6. Restart the batch scheduler and watch the first job end to end.

## Rollback
If smoke queries fail after promotion, do not fail back automatically. Keep
the promoted host as primary, open a SEV1, and restore from the last snapshot
only on the incident commander's instruction.
