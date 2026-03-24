# Scheduled Task Persistence Investigation Playbook

## Overview

Creating new scheduled tasks is a common persistence and lateral movement primitive.

## Initial Triage (First 5 Minutes)

- [ ] Validate file path of the task action (`/tr` argument)
- [ ] Identify the account context (SYSTEM vs. user)
- [ ] Check software deployment tickets

## Deep Investigation Steps

- [ ] Review Security 4698 and Sysmon ImageLoad chains
- [ ] Inspect the dropped binary with AV/EDR detonation
- [ ] Look for sibling tasks across the fleet with identical names

## False Positive Conditions

- Patch management and backup suites
- Laptop vendor updater tasks with consistent hashes

## Escalation Criteria

Escalate to P1 Incident if:

- Task executes from `%TEMP%` or hidden ADS streams
- Task repeats beaconing with encoded PowerShell child processes

## Remediation Actions

1. Delete malicious tasks and clear associated autoruns
2. Roll host credentials and invalidate Kerberos tickets
3. Enable task creation auditing on servers

## MITRE ATT&CK Reference

- Technique: T1053.005 — Scheduled Task/Job
- URL: https://attack.mitre.org/techniques/T1053/005/
