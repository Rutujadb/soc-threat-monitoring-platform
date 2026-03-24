# Password Spray Investigation Playbook

## Overview

Password spraying targets many accounts with a small number of common passwords to avoid per-account lockouts.

## Initial Triage (First 5 Minutes)

- [ ] Verify the account is legitimate (not a honey user)
- [ ] Check if failures share passwords or timing patterns
- [ ] Identify affected departments or business units

## Deep Investigation Steps

- [ ] Correlate failures across LDAP, VPN, cloud IdP, and mail services
- [ ] Look for one success after many failures on the same account
- [ ] Review conditional access and legacy protocol usage (NTLM, IMAP)

## False Positive Conditions

- Mobile devices with outdated cached credentials
- Service accounts misconfigured with interactive logon rights

## Escalation Criteria

Escalate to P1 Incident if:

- Administrative or break-glass accounts are targeted
- Confirm compromise via unexpected MFA prompts or new sessions

## Remediation Actions

1. Enforce smart lockout and risk-based policies
2. Invalidate Kerberos tickets / cloud sessions for impacted users
3. Reset passwords under documented IR procedure

## MITRE ATT&CK Reference

- Technique: T1110.003 — Password Spraying
- URL: https://attack.mitre.org/techniques/T1110/003/
