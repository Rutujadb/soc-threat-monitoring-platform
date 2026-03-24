# Pass-the-Hash Investigation Playbook

## Overview

NTLM network authentications without Kerberos may indicate pass-the-hash movement, especially between workstations and servers.

## Initial Triage (First 5 Minutes)

- [ ] Confirm the source host is managed and inventoried
- [ ] Determine whether Kerberos is expected for the target resource
- [ ] Map recent privileged group changes for the account

## Deep Investigation Steps

- [ ] Review Security 4624/4648 sequences and outbound SMB from the source
- [ ] Inspect LSASS protections (PPL, Credential Guard) on endpoints
- [ ] Hunt for Mimikatz or sekurlsa artifacts in EDR telemetry

## False Positive Conditions

- Legacy apps requiring NTLM in isolated VLANs
- Misconfigured SPNs forcing NTLM fallbacks with documentation

## Escalation Criteria

Escalate to P1 Incident if:

- Interactive admin sessions originate from non-jump hosts
- DCSync or Golden Ticket indicators appear in the same timeline

## Remediation Actions

1. Isolate source and reset domain credentials per IR plan
2. Enforce Kerberos-only where feasible; restrict NTLM via GPO
3. Rotate KRBTGT on confirmed domain compromise

## MITRE ATT&CK Reference

- Technique: T1550.002 — Pass the Hash
- URL: https://attack.mitre.org/techniques/T1550/002/
