# Nightly Batch Failure Runbook

## Overview
The nightly batch loads the day's sales and inventory files into the
warehouse between 01:00 and 04:00. A failed batch pages the data on-call.

## Triage
1. Open the scheduler console and identify the failed step and error code.
2. Error `SRC-404`: a source file did not arrive. Check the landing bucket;
   if the file is genuinely missing, contact the upstream store systems team
   and hold downstream steps.
3. Error `DQ-210`: a data-quality rule failed (row-count variance over 5% or
   a null-rate spike). The load is automatically rolled back; inspect the
   quarantine table before deciding to reload.
4. Error `TRG-500`: the warehouse was unavailable. Wait for the platform
   team's all-clear, then rerun from the failed step.

## Rerun rules
A batch may be rerun from the failed step at most twice. After two failed
reruns, escalate to the data engineering lead and notify downstream report
owners that the morning dashboards will be late.
