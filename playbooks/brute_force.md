# Brute Force Authentication Investigation Playbook

## Overview

Multiple failed authentication attempts from one source often indicate password guessing or credential stuffing against exposed services.

## Initial Triage (First 5 Minutes)

- [ ] Confirm the target host and service are production assets
- [ ] Identify whether the account is interactive or a shared/service principal
- [ ] Compare alert volume in the last 24h for the same source IP

## Deep Investigation Steps

- [ ] Pivot on source IP to other auth, VPN, and proxy logs
- [ ] Check for successful logons from the same IP after failures
- [ ] Review geo-ASN and threat intel reputation for the source

## False Positive Conditions

- Scheduled vulnerability scanners with documented IPs
- Known automation accounts with forgot-password workflows

## Escalation Criteria

Escalate to P1 Incident if:

- Successful logon follows a brute-force burst on a privileged account
- Lateral movement patterns appear from the same host within the same window

## Remediation Actions

1. Temporarily block or rate-limit the offending source at the perimeter
2. Force password reset and MFA enrollment for impacted accounts
3. Hunt for persistence on any host where authentication succeeded

## MITRE ATT&CK Reference

- Technique: T1110 — Brute Force
- URL: https://attack.mitre.org/techniques/T1110/
