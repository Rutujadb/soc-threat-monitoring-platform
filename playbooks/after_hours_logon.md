# After-Hours Logon Investigation Playbook

## Overview

Interactive success logons outside business hours can be benign shift work — or unauthorized access.

## Initial Triage (First 5 Minutes)

- [ ] Validate the user’s role and expected schedule
- [ ] Check MFA satisfaction method and device compliance
- [ ] Identify source IP / VPN pool assignment

## Deep Investigation Steps

- [ ] Compare geolocation vs. historical patterns
- [ ] Review simultaneous sessions for impossible travel
- [ ] Check for follow-on actions (RDP chaining, PowerShell)

## False Positive Conditions

- On-call engineers and offshore support teams
- Automated patching accounts with interactive rights (should be rare)

## Escalation Criteria

Escalate to P1 Incident if:

- Privilege escalation occurs within minutes of the session
- Account shows no HR record or was recently disabled

## Remediation Actions

1. Force step-up authentication and revoke refresh tokens
2. Engage manager verification for first-time anomalies
3. Tune conditional access policies for risky sign-ins

## MITRE ATT&CK Reference

- Technique: T1078 — Valid Accounts
- URL: https://attack.mitre.org/techniques/T1078/
