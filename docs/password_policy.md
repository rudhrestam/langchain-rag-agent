# Password and Account Lockout Policy

## Password rules
- Minimum 14 characters; passphrases encouraged.
- Passwords expire every 365 days (no forced 30-day rotation).
- The last 10 passwords cannot be reused.
- Shared accounts are prohibited; service accounts are vaulted and owned by a
  named engineer.

## Lockouts
- User accounts lock after 5 failed attempts, for 30 minutes.
- Help desk can unlock early after verifying two identity factors.
- Three lockouts in one day triggers a security review of the account.

## Resets
Self-service reset requires MFA. Help-desk-assisted resets are logged and the
user must change the temporary password at first login.
