# Internal Port Scan Investigation Playbook

## Overview

Rapid connections to many internal ports often precedes exploitation or worm-like behavior.

## Initial Triage (First 5 Minutes)

- [ ] Identify whether the source is a scanner appliance or server
- [ ] Map VLAN placement and default gateway exposure
- [ ] Check vulnerability management calendars

## Deep Investigation Steps

- [ ] Correlate with authentication or exploit payloads to key ports
- [ ] Review endpoint process responsible for SYN floods
- [ ] Compare against known blue-team inventory sweeps

## False Positive Conditions

- Asset discovery tools with signed automation accounts
- Misconfigured monitoring probes

## Escalation Criteria

Escalate to P1 Incident if:

- Scans coincide with successful exploits on sensitive tiers
- Source is an end-user workstation with no admin role

## Remediation Actions

1. Quarantine host at NAC until scanned clean
2. Review east-west segmentation and deny-by-default rules
3. Enable NetFlow sampling on sensitive segments

## MITRE ATT&CK Reference

- Technique: T1046 — Network Service Discovery
- URL: https://attack.mitre.org/techniques/T1046/
