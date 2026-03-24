"""
Synthetic SOC log generator. POSTs normalized-shaped payloads to /api/ingest.
Run from repo root: python -m ingestor.simulate_logs
Or from backend: python -m ingestor.simulate_logs
"""
from __future__ import annotations

import argparse
import random
import string
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
from faker import Faker

fake = Faker()


def _rand_subnet_ip() -> str:
    return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def noise_event() -> dict:
    st = random.choices(
        ["windows_auth", "dns", "sysmon", "netflow", "linux_auth"],
        weights=[0.3, 0.25, 0.2, 0.15, 0.1],
    )[0]
    now = datetime.now(timezone.utc)
    if st == "windows_auth":
        return {
            "source_type": "windows_auth",
            "log": {
                "TimeCreated": now.isoformat(),
                "EventID": 4624,
                "SubjectUserName": fake.user_name(),
                "IpAddress": _rand_subnet_ip(),
                "WorkstationName": fake.hostname(),
                "LogonType": random.choice([3, 10, 2]),
                "Status": "0x0",
                "SubStatus": "0x0",
            },
        }
    if st == "dns":
        sub = fake.lexify(text="????").lower()
        return {
            "source_type": "dns",
            "log": {
                "timestamp": now.isoformat(),
                "query_name": f"{sub}.{fake.domain_name()}",
                "client_ip": _rand_subnet_ip(),
                "response_code": "NOERROR",
            },
        }
    if st == "sysmon":
        img = random.choice([r"C:\Windows\explorer.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
        return {
            "source_type": "sysmon",
            "log": {
                "UtcTime": now.isoformat(),
                "EventID": 1,
                "Image": img,
                "CommandLine": img,
                "ParentImage": r"C:\Windows\System32\svchost.exe",
                "User": fake.user_name(),
                "Computer": fake.hostname(),
            },
        }
    if st == "netflow":
        return {
            "source_type": "netflow",
            "log": {
                "timestamp": now.isoformat(),
                "src_ip": _rand_subnet_ip(),
                "dst_ip": fake.ipv4_public(),
                "dst_port": random.choice([80, 443, 53]),
                "protocol": "tcp",
                "description": "https",
            },
        }
    return {
        "source_type": "linux_auth",
        "log": {
            "timestamp": now.isoformat(),
            "user": fake.user_name(),
            "source_ip": _rand_subnet_ip(),
            "hostname": fake.hostname(),
            "result": "success",
            "method": "sshd",
        },
    }


def attack_bruteforce() -> list[dict]:
    now = datetime.now(timezone.utc)
    ip = fake.ipv4()
    host = fake.hostname()
    out = []
    for _ in range(10):
        out.append(
            {
                "source_type": "windows_auth",
                "log": {
                    "TimeCreated": now.isoformat(),
                    "EventID": 4625,
                    "SubjectUserName": fake.user_name(),
                    "IpAddress": ip,
                    "WorkstationName": host,
                    "LogonType": 3,
                    "Status": "0xC000006D",
                    "SubStatus": "0xC000006A",
                },
            }
        )
    return out


def attack_password_spray() -> list[dict]:
    now = datetime.now(timezone.utc)
    user = "svc_backup"
    out = []
    for _ in range(4):
        out.append(
            {
                "source_type": "windows_auth",
                "log": {
                    "TimeCreated": now.isoformat(),
                    "EventID": 4625,
                    "SubjectUserName": user,
                    "IpAddress": fake.ipv4(),
                    "WorkstationName": fake.hostname(),
                    "LogonType": 3,
                    "Status": "0xC000006D",
                    "SubStatus": "0xC000006A",
                },
            }
        )
    return out


def attack_dns_tunnel_freq() -> list[dict]:
    now = datetime.now(timezone.utc)
    client = _rand_subnet_ip()
    return [
        {
            "source_type": "dns",
            "log": {
                "timestamp": (now + timedelta(milliseconds=i * 10)).isoformat(),
                "query_name": f"{fake.lexify(text='???')}.example.com",
                "client_ip": client,
                "response_code": "NOERROR",
            },
        }
        for i in range(55)
    ]


def attack_dns_tunnel_long() -> dict:
    long_sub = "".join(random.choices(string.ascii_lowercase + string.digits, k=45))
    now = datetime.now(timezone.utc)
    return {
        "source_type": "dns",
        "log": {
            "timestamp": now.isoformat(),
            "query_name": f"{long_sub}.tunnel.example.com",
            "client_ip": _rand_subnet_ip(),
            "response_code": "NOERROR",
        },
    }


def attack_sudo() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "linux_auth",
        "log": {
            "timestamp": now.isoformat(),
            "user": "deploy",
            "source_ip": _rand_subnet_ip(),
            "hostname": fake.hostname(),
            "result": "success",
            "method": "sudo",
            "command": "sudo sh -c 'chmod +s /tmp/backdoor'",
        },
    }


def attack_pth() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "windows_auth",
        "log": {
            "TimeCreated": now.isoformat(),
            "EventID": 4624,
            "SubjectUserName": "Administrator",
            "IpAddress": _rand_subnet_ip(),
            "WorkstationName": fake.hostname(),
            "LogonType": 3,
            "AuthenticationPackageName": "NTLM",
            "Status": "0x0",
            "SubStatus": "0x0",
        },
    }


def attack_kerberoast() -> list[dict]:
    now = datetime.now(timezone.utc)
    user = "svc_sql"
    return [
        {
            "source_type": "windows_auth",
            "log": {
                "TimeCreated": (now + timedelta(seconds=i)).isoformat(),
                "EventID": 4769,
                "SubjectUserName": user,
                "IpAddress": _rand_subnet_ip(),
                "WorkstationName": fake.hostname(),
                "Status": "0x0",
                "SubStatus": "0x0",
            },
        }
        for i in range(12)
    ]


def attack_psexec_netflow() -> list[dict]:
    now = datetime.now(timezone.utc)
    src = _rand_subnet_ip()
    dst = _rand_subnet_ip()
    return [
        {
            "source_type": "netflow",
            "log": {
                "timestamp": (now + timedelta(seconds=i)).isoformat(),
                "src_ip": src,
                "dst_ip": dst,
                "dst_port": 445,
                "protocol": "tcp",
                "description": "psexec ADMIN$ IPC$ lateral",
            },
        }
        for i in range(25)
    ]


def attack_lsass_sysmon() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "sysmon",
        "log": {
            "UtcTime": now.isoformat(),
            "EventID": 10,
            "Image": r"C:\Windows\System32\rundll32.exe",
            "CommandLine": "rundll32.exe",
            "TargetFilename": r"C:\Windows\System32\lsass.exe",
            "User": "SYSTEM",
            "Computer": fake.hostname(),
        },
    }


def attack_new_admin() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "windows_auth",
        "log": {
            "TimeCreated": now.isoformat(),
            "EventID": 4732,
            "SubjectUserName": "evil_local",
            "Message": "LocalGroupMembershipChanged Administrators",
            "IpAddress": _rand_subnet_ip(),
            "WorkstationName": fake.hostname(),
            "Status": "0x0",
            "SubStatus": "0x0",
        },
    }


def attack_after_hours() -> dict:
    t = datetime.now(timezone.utc).replace(hour=22, minute=15, second=0, microsecond=0)
    return {
        "source_type": "windows_auth",
        "log": {
            "TimeCreated": t.isoformat(),
            "EventID": 4624,
            "SubjectUserName": fake.user_name(),
            "IpAddress": _rand_subnet_ip(),
            "WorkstationName": fake.hostname(),
            "LogonType": 10,
            "Status": "0x0",
            "SubStatus": "0x0",
        },
    }


def attack_portscan() -> list[dict]:
    now = datetime.now(timezone.utc)
    src = _rand_subnet_ip()
    return [
        {
            "source_type": "netflow",
            "log": {
                "timestamp": (now + timedelta(seconds=i * 0.2)).isoformat(),
                "src_ip": src,
                "dst_ip": _rand_subnet_ip(),
                "dst_port": 4000 + i,
                "protocol": "tcp",
                "description": "syn",
            },
        }
        for i in range(25)
    ]


def attack_powershell() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "sysmon",
        "log": {
            "UtcTime": now.isoformat(),
            "EventID": 1,
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "CommandLine": "powershell.exe -nop -w hidden -enc JABBA=",
            "ParentImage": r"C:\Windows\explorer.exe",
            "User": fake.user_name(),
            "Computer": fake.hostname(),
        },
    }


def attack_scheduled_task() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "sysmon",
        "log": {
            "UtcTime": now.isoformat(),
            "EventID": 1,
            "Image": r"C:\Windows\System32\schtasks.exe",
            "CommandLine": r'schtasks.exe /create /tn "Updater" /tr malware.exe',
            "ParentImage": r"C:\Windows\System32\cmd.exe",
            "User": "SYSTEM",
            "Computer": fake.hostname(),
        },
    }


def attack_new_service() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "source_type": "sysmon",
        "log": {
            "UtcTime": now.isoformat(),
            "EventID": 1,
            "Image": r"C:\Windows\System32\sc.exe",
            "CommandLine": "sc.exe create evil_svc binPath= C:\\Windows\\Temp\\beacon.exe start= auto",
            "ParentImage": r"C:\Windows\System32\cmd.exe",
            "User": "SYSTEM",
            "Computer": fake.hostname(),
        },
    }


def flatten_attack(attack_ratio: float) -> list:
    pool = [
        ("bf", attack_bruteforce),
        ("spray", attack_password_spray),
        ("dnsf", attack_dns_tunnel_freq),
        ("dnss", lambda: [attack_dns_tunnel_long()]),
        ("sudo", lambda: [attack_sudo()]),
        ("pth", lambda: [attack_pth()]),
        ("kr", attack_kerberoast),
        ("psx", attack_psexec_netflow),
        ("lsass", lambda: [attack_lsass_sysmon()]),
        ("adm", lambda: [attack_new_admin()]),
        ("ah", lambda: [attack_after_hours()]),
        ("scan", attack_portscan),
        ("ps", lambda: [attack_powershell()]),
        ("task", lambda: [attack_scheduled_task()]),
        ("svc", lambda: [attack_new_service()]),
    ]

    def pick():
        if random.random() < attack_ratio:
            _, fn = random.choice(pool)
            evs = fn()
            if isinstance(evs, dict):
                return [evs]
            return evs
        return [noise_event()]

    return pick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    ap.add_argument("--rate", type=float, default=3.0, help="Events per second (approx)")
    ap.add_argument("--attack-ratio", type=float, default=0.2, dest="attack_ratio")
    ap.add_argument("--duration", type=int, default=0, help="Seconds; 0 = run until Ctrl+C")
    args = ap.parse_args()

    interval = 1.0 / max(0.1, args.rate)
    deadline = time.time() + args.duration if args.duration > 0 else None
    n = 0
    print(f"Sending to {args.base_url}/api/ingest at ~{args.rate} ev/s, attack_ratio={args.attack_ratio}")
    try:
        while True:
            if deadline and time.time() >= deadline:
                break
            batch = flatten_attack(args.attack_ratio)()
            for payload in batch:
                url = f"{args.base_url.rstrip('/')}/api/ingest"
                try:
                    r = requests.post(url, json=payload, timeout=5)
                    if r.status_code >= 400:
                        print("ingest error", r.status_code, r.text[:200])
                except requests.RequestException as e:
                    print("request failed:", e, file=sys.stderr)
            n += len(batch)
            time.sleep(interval * len(batch))
    except KeyboardInterrupt:
        pass
    print(f"Stopped after ~{n} events posted.")


if __name__ == "__main__":
    main()
