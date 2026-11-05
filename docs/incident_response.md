# Incident Response — First 30 Minutes

## Severity levels
- **SEV1**: customer-facing outage or data loss risk. Page the on-call lead immediately.
- **SEV2**: major feature degraded, workaround exists. Page the service owner.
- **SEV3**: minor issue, no customer impact. File a ticket for the next business day.

## First response checklist
1. Acknowledge the page in the incident channel within 5 minutes.
2. Open an incident record and note the start time, reporter, and symptoms.
3. Check the status dashboard for related alerts before touching any system.
4. If SEV1, start a bridge call and assign an incident commander and a scribe.
5. Post a status update every 30 minutes for SEV1, every 2 hours for SEV2.

## Escalation
If the cause is not identified within 45 minutes on a SEV1, escalate to the
platform engineering manager. For vendor-caused outages, open a vendor ticket
in parallel — never wait on the vendor before starting your own diagnosis.
