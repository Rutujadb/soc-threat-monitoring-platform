# LSASS Access Investigation Playbook

## Overview

Process access to `lsass.exe` is a high-fidelity signal for credential theft tooling.

## Initial Triage (First 5 Minutes)

- [ ] Identify the accessing image path and signer
- [ ] Confirm whether an EDR/backup agent is expected to touch LSASS
- [ ] Snapshot volatile data if policy allows

## Deep Investigation Steps

- [ ] Review Sysmon Event ID 10 chains and call traces
- [ ] Search for handle grants (`GrantedAccess`) typical of dump tools
- [ ] Correlate with prior suspicious PowerShell or WMI activity

## False Positive Conditions

- Approved AV mini-filter drivers with documented access patterns
- Legacy backup agents on Windows Server

## Escalation Criteria

Escalate to P1 Incident if:

- Access originates from userland unsigned binaries
- Lsass dump files appear on disk or in memory strings

## Remediation Actions

1. Contain the endpoint and collect forensic image
2. Rotate credentials for sessions active on the device
3. Enable Credential Guard / LSASS PPL where compatible

## MITRE ATT&CK Reference

- Technique: T1003.001 — LSASS Memory
- URL: https://attack.mitre.org/techniques/T1003/001/
