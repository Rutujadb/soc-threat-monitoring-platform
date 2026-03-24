# Suspicious PowerShell Investigation Playbook

## Overview

Encoded commands, hidden windows, and bypass flags are common in offensive PowerShell tradecraft.

## Initial Triage (First 5 Minutes)

- [ ] Identify parent process and interactive vs. service context
- [ ] Check code signing status of the script or module
- [ ] Determine if this is an IT automation account

## Deep Investigation Steps

- [ ] Decode `-enc` payloads in a sandbox
- [ ] Review Script Block logging / Module logging if enabled
- [ ] Correlate with WMI, WinRM, or inbound RDP sessions

## False Positive Conditions

- Endpoint management baselines using encoded setup scripts
- Vendor installers with documented command lines

## Escalation Criteria

Escalate to P1 Incident if:

- Payloads call home or inject into remote processes
- Same operator executes credential dumping commands next

## Remediation Actions

1. Contain host and collect PowerShell operational logs
2. Disable compromised automation principals
3. Enforce Constrained Language Mode where feasible

## MITRE ATT&CK Reference

- Technique: T1059.001 — PowerShell
- URL: https://attack.mitre.org/techniques/T1059/001/
