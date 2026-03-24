# Linux Privilege Escalation (sudo) Investigation Playbook

## Overview

Unexpected sudo or setuid activity may represent local privilege escalation after initial access.

## Initial Triage (First 5 Minutes)

- [ ] Validate host criticality and owner
- [ ] Identify whether the command aligns with change tickets
- [ ] Check sudoers configuration drift

## Deep Investigation Steps

- [ ] Review full shell history and auditd (`ausearch`)
- [ ] Inspect `/tmp`, cron, systemd timers for persistence
- [ ] Correlate with inbound SSH or exploit framework indicators

## False Positive Conditions

- Automated patch orchestration using sudo
- Known admin maintenance windows

## Escalation Criteria

Escalate to P1 Incident if:

- Sudo invoked by an unexpected user from a foreign IP
- Evidence of kernel exploit or writable sensitive paths

## Remediation Actions

1. Snapshot disk and preserve auth logs off-host
2. Remove unauthorized sudoers entries and rotate keys
3. Patch kernel/userland per vendor advisory

## MITRE ATT&CK Reference

- Technique: T1548.003 — Sudo and Cached Credentials
- URL: https://attack.mitre.org/techniques/T1548/003/
