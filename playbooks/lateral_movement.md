# Lateral Movement (PsExec / SMB Admin Shares) Investigation Playbook

## Overview

Use of ADMIN$, IPC$, or PsExec-style transfers often signals operator movement inside the estate.

## Initial Triage (First 5 Minutes)

- [ ] Validate whether the source asset is an admin jump box
- [ ] Identify asset owners for both endpoints in the flow
- [ ] Check recent changes to SMB signing / firewall posture

## Deep Investigation Steps

- [ ] Inspect Security/Sysmon for service creation and remote scheduled tasks
- [ ] Map SMB sessions (`Get-SmbSession`) or EDR network telemetry
- [ ] Hunt for credential reuse from the same source within minutes

## False Positive Conditions

- SCCM or backup tools with documented service accounts
- Vulnerability scanners with signed permits

## Escalation Criteria

Escalate to P1 Incident if:

- Movement originates from an unmanaged host or guest VLAN
- Multiple servers touched with identical tool binaries

## Remediation Actions

1. Isolate the lateral source host pending triage
2. Disable compromised accounts and revoke Kerberos tickets
3. Enforce LAPS and tiered administration boundaries

## MITRE ATT&CK Reference

- Technique: T1021.002 — SMB/Windows Admin Shares
- URL: https://attack.mitre.org/techniques/T1021/002/
