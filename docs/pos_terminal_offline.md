# POS Terminal Offline — Store Troubleshooting

## Symptoms
A point-of-sale terminal shows "OFFLINE — transactions will queue" and new
sales are stored locally instead of syncing to the central system.

## Steps
1. Check the store router: a solid green link light means the network is up.
2. Restart the terminal's sync service from the manager menu (option 4).
3. If sync does not resume in 10 minutes, power-cycle the terminal. Queued
   transactions are held in local storage for up to 72 hours and are not lost.
4. If three or more terminals in one store are offline, treat it as a store
   network issue, not a terminal issue, and call the network team.
5. Once sync resumes, verify the queued transaction count returns to zero on
   the store dashboard before closing the ticket.

## Do not
Do not factory-reset an offline terminal: the reset wipes the local queue and
any unsynced transactions are permanently lost.
