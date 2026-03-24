# Kerberoasting Investigation Playbook

## Overview

Abnormally frequent Kerberos service ticket (TGS) requests can indicate offline hash cracking attempts against SPN-backed accounts.

## Initial Triage (First 5 Minutes)

- [ ] Identify the service account and its SPNs
- [ ] Check if password rotation is overdue
- [ ] Verify whether a red-team exercise is authorized

## Deep Investigation Steps

- [ ] Correlate with LDAP queries enumerating SPNs
- [ ] Compare ticket request rates against historical baseline
- [ ] Review hosts initiating the requests for tooling footprints

## False Positive Conditions

- Database clusters or legacy apps with aggressive reconnect timers
- Backup products using Kerberos-heavy workflows

## Escalation Criteria

Escalate to P1 Incident if:

- Administrator-tier SPNs spike without maintenance tickets
- AES tickets exfiltrated alongside crypto mining or C2

## Remediation Actions

1. Rotate the targeted service account password (>=30 chars, gMSA if possible)
2. Remove unnecessary SPNs and enforce AES-only where supported
3. Add detections for RPC/LDAP SPN enumeration

## MITRE ATT&CK Reference

- Technique: T1558.003 — Kerberoasting
- URL: https://attack.mitre.org/techniques/T1558/003/
