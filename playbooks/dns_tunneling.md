# DNS Tunneling Investigation Playbook

## Overview

Abnormal DNS query volume or long subdomains may indicate command-and-control or data exfiltration encodings.

## Initial Triage (First 5 Minutes)

- [ ] Confirm the resolver and forwarders in use
- [ ] Determine if the client is a server, workstation, or IoT device
- [ ] Compare baseline query rate for that subnet

## Deep Investigation Steps

- [ ] Extract sample queries and decode for entropy or text payloads
- [ ] Inspect process trees on the endpoint for unexpected DNS clients
- [ ] Review firewall/proxy allow lists for DNS over HTTPS bypass

## False Positive Conditions

- AV update storms or misconfigured health checks
- Developer containers issuing noisy debug traffic

## Escalation Criteria

Escalate to P1 Incident if:

- Payloads decode to shell commands or beacon fingerprints
- Multiple assets show synchronized long-subdomain queries

## Remediation Actions

1. Block suspicious domains at the resolver with logging enabled
2. Isolate the host and collect memory + DNS cache
3. Re-image if root cause cannot be quickly disproved

## MITRE ATT&CK Reference

- Technique: T1071.004 — DNS
- URL: https://attack.mitre.org/techniques/T1071/004/
