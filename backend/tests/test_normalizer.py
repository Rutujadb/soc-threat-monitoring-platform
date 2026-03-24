from datetime import datetime, timezone

from ingestor.normalizer import normalize_event


def test_windows_auth_normalize():
    raw = {
        "TimeCreated": "2024-01-01T12:00:00Z",
        "EventID": 4625,
        "SubjectUserName": "bob",
        "IpAddress": "10.0.0.5",
        "WorkstationName": "WS1",
        "LogonType": 3,
        "Status": "0xC000006D",
        "SubStatus": "0xC000006A",
    }
    e = normalize_event(raw, "windows_auth")
    assert e.source_type == "windows_auth"
    assert e.result == "failure"
    assert "4625" in e.action


def test_dns_normalize():
    raw = {"timestamp": "2024-01-01T12:00:00Z", "query_name": "a.example.com", "client_ip": "10.0.0.2"}
    e = normalize_event(raw, "dns")
    assert e.source_type == "dns"
    assert e.extra.get("query_name") == "a.example.com"


def test_sysmon_normalize():
    raw = {
        "UtcTime": "2024-01-01T12:00:00Z",
        "EventID": 1,
        "Image": r"C:\Windows\System32\lsass.exe",
        "CommandLine": "lsass.exe",
        "User": "SYSTEM",
    }
    e = normalize_event(raw, "sysmon")
    assert "lsass" in e.action.lower()


def test_netflow_normalize():
    raw = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": "10.0.0.1",
        "dst_ip": "10.0.0.2",
        "dst_port": 445,
        "protocol": "tcp",
        "description": "psexec IPC$",
    }
    e = normalize_event(raw, "netflow")
    assert e.source_type == "netflow"
    assert "psexec" in e.action.lower()


def test_linux_auth_sudo():
    raw = {
        "timestamp": "2024-01-01T12:00:00Z",
        "user": "u1",
        "source_ip": "10.0.0.3",
        "result": "success",
        "method": "sudo",
        "command": "sudo id",
    }
    e = normalize_event(raw, "linux_auth")
    assert "sudo" in e.action.lower()
