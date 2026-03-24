# New Local Administrator Investigation Playbook

## Overview

Unexpected additions to privileged local groups can represent persistence during an intrusion.

## Initial Triage (First 5 Minutes)

- [ ] Verify the modifying account and workstation
- [ ] Check change/incident tickets for the timeframe
- [ ] Determine if imaging or helpdesk tooling could explain the change

## Deep Investigation Steps

- [ ] Review User / Group Security 4728/4732 surrounding events
- [ ] Pivot on SID histories and nested group membership
- [ ] Validate whether RDP or remote admin sessions preceded the change

## False Positive Conditions

- Golden image builds re-running sysprep scripts
- Desktop engineering pushes with approved GPO

## Escalation Criteria

Escalate to P1 Incident if:

- Shadow accounts appear without CMDB records
- Same operator chain shows tool drops or C2 beacons

## Remediation Actions

1. Remove rogue accounts and enforce LAPS resets
2. Re-image host if tampering with SAM cannot be ruled out
3. Enable enhanced auditing for privileged local group changes

## MITRE ATT&CK Reference

- Technique: T1136.001 — Local Account
- URL: https://attack.mitre.org/techniques/T1136/001/
