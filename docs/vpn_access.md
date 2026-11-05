# VPN and Remote Access Policy

## Getting access
New staff request VPN access through the IT service portal (Access > VPN).
Manager approval is required; access is provisioned within one business day.

## Rules
- Multi-factor authentication is mandatory for every VPN session.
- VPN accounts lock after 5 failed login attempts and unlock after 30 minutes,
  or immediately via the help desk after identity verification.
- Split tunnelling is disabled: all traffic routes through the company gateway
  while connected.
- Dormant accounts (no login for 60 days) are disabled automatically and need
  a fresh access request to reactivate.

## Troubleshooting
"Certificate expired" errors mean the device certificate needs renewal —
re-enrol the device from the IT portal rather than reinstalling the client.
