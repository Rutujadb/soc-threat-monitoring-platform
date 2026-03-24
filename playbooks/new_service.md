# New Windows Service Investigation Playbook

## Overview

`sc.exe create` / `New-Service` may install persistence or loader stages as SYSTEM.

## Initial Triage (First 5 Minutes)

- [ ] Capture service name, binPath, and start type
- [ ] Validate publisher of the binary on disk
- [ ] Determine if deployment tooling owns the change

## Deep Investigation Steps

- [ ] Review Security 7045 / System 7036 surrounding telemetry
- [ ] Inspect service DLL side-loading opportunities
- [ ] Correlate with earlier privilege escalation techniques

## False Positive Conditions

- Legitimate monitoring agents registered via `sc create`
- Vendor reboot-pending installers

## Escalation Criteria

Escalate to P1 Incident if:

- Service points to unusual paths (Recycle Bin, AppData)
- Service immediately spawns C2 traffic or credential tools

## Remediation Actions

1. Stop/delete service and quarantine payload binaries
2. Collect Prefetch/AmCache for binary provenance
3. Redeploy clean image if rootkit behavior suspected

## MITRE ATT&CK Reference

- Technique: T1543.003 — Windows Service
- URL: https://attack.mitre.org/techniques/T1543/003/
