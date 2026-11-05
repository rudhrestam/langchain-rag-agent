# Backup and Restore Policy

## Schedule
- Full backups: nightly at 02:30, retained for 35 days.
- Transaction log backups: every 15 minutes, retained for 7 days.
- Monthly archive: copied to cold storage on the 1st, retained for 13 months.

## Restore procedure
1. Restores to production require a change ticket and a second engineer's
   approval. Restores to the sandbox environment need neither.
2. Restore the most recent full backup, then replay log backups to the
   requested point in time.
3. Verify with the standard row-count and checksum pack before handing the
   system back.

## Testing
Restore drills run quarterly. A backup that has never been test-restored is
treated as no backup at all: drill results are reported to the platform lead.
