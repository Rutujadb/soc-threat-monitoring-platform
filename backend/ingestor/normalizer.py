import json
from datetime import datetime, timezone
from typing import Any

from dateutil import parser as dtparser

from ingestor.schemas import UnifiedEventDTO


def _parse_ts(val: Any) -> datetime:
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val
    if val is None:
        return datetime.now(timezone.utc)
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val, tz=timezone.utc)
    return dtparser.parse(str(val)).replace(tzinfo=timezone.utc)


def _get(d: dict, *keys: str, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def normalize_event(raw_log: dict[str, Any], source_type: str) -> UnifiedEventDTO:
    """Map vendor-specific logs to unified schema."""
    st = (source_type or "").lower().strip()
    raw_str = json.dumps(raw_log) if not isinstance(raw_log.get("_raw"), str) else raw_log["_raw"]

    if st == "windows_auth":
        eid = str(_get(raw_log, "EventID", "EventId", "event_id", default=""))
        user = _get(raw_log, "SubjectUserName", "TargetUserName", "user", "username")
        ip = _get(raw_log, "IpAddress", "ip_address", "SourceNetworkAddress", "source_ip")
        host = _get(raw_log, "WorkstationName", "Computer", "hostname", "host")
        status = _get(raw_log, "Status", "status", default="")
        substatus = _get(raw_log, "SubStatus", default="")
        failure = status not in ("0x0", "0", "") or substatus not in ("0x0", "0", "", None)
        action_parts = [f"EventID:{eid}"]
        if raw_log.get("LogonType") is not None:
            action_parts.append(f"LogonType:{raw_log.get('LogonType')}")
        # Kerberos ticket indicator
        if eid in ("4769", 4769):
            action_parts.append("KerberosServiceTicket")
        if "LocalGroupMembershipChanged" in str(raw_log.get("Message", "")):
            action_parts.append("LocalGroupMembershipChanged Administrators")
        ntlm = "NTLM" in str(raw_log.get("AuthenticationPackageName", ""))
        lt = str(raw_log.get("LogonType", ""))
        if ntlm and lt == "3":
            action_parts.append("NTLM Network Logon")
        action = " ".join(action_parts)
        result = "failure" if failure else "success"
        return UnifiedEventDTO(
            timestamp=_parse_ts(_get(raw_log, "TimeCreated", "timestamp")),
            source_type="windows_auth",
            source_ip=str(ip or "") or None,
            destination_ip=None,
            hostname=str(host or "") or None,
            username=str(user or "") or None,
            action=action,
            result=result,
            raw=raw_str,
            extra={"event_id_windows": eid, **{k: v for k, v in raw_log.items() if k not in ("TimeCreated",)}},
        )

    if st == "dns":
        q = _get(raw_log, "query_name", "QueryName", "name", "query")
        client = _get(raw_log, "client_ip", "ClientIp", "src_ip", "source_ip")
        return UnifiedEventDTO(
            timestamp=_parse_ts(_get(raw_log, "timestamp", "time")),
            source_type="dns",
            source_ip=str(client or "") or None,
            destination_ip=None,
            hostname=None,
            username=None,
            action=str(q or ""),
            result=str(_get(raw_log, "response_code", "rcode", default="NOERROR")),
            raw=raw_str,
            extra={"query_name": str(q or ""), **raw_log},
        )

    if st == "sysmon":
        eid = str(_get(raw_log, "EventID", "EventId", default="1"))
        img = _get(raw_log, "Image", "image", default="")
        cmd = _get(raw_log, "CommandLine", "command_line", default="")
        parent = _get(raw_log, "ParentImage", "parent_image", default="")
        user = _get(raw_log, "User", "user", default="")
        target = _get(raw_log, "TargetFilename", "target_filename", default="")
        action = f"EventID:{eid} {img} {cmd} {parent} {target}".strip()
        if "lsass" in str(img).lower() or "lsass" in str(target).lower():
            action = f"{action} lsass.exe"
        return UnifiedEventDTO(
            timestamp=_parse_ts(_get(raw_log, "UtcTime", "timestamp")),
            source_type="sysmon",
            source_ip=None,
            destination_ip=None,
            hostname=_get(raw_log, "Computer", "hostname"),
            username=str(user or "") or None,
            action=action,
            result="success",
            raw=raw_str,
            extra=raw_log,
        )

    if st == "netflow":
        src = _get(raw_log, "src_ip", "source_ip")
        dst = _get(raw_log, "dst_ip", "destination_ip")
        port = _get(raw_log, "dst_port", "destination_port")
        proto = _get(raw_log, "protocol", "proto", default="tcp")
        desc = _get(raw_log, "description", "service", default="")
        action = f"{proto}:{port} {desc}".strip()
        blob = f"{desc} {raw_log}".lower()
        if any(x in blob for x in ("psexec", "admin$", "ipc$", "445")):
            action = f"{action} psexec ADMIN$ IPC$"
        return UnifiedEventDTO(
            timestamp=_parse_ts(_get(raw_log, "timestamp", "time")),
            source_type="netflow",
            source_ip=str(src or "") or None,
            destination_ip=str(dst or "") or None,
            hostname=None,
            username=None,
            action=action,
            result="success",
            raw=raw_str,
            extra=raw_log,
        )

    if st == "linux_auth":
        user = _get(raw_log, "user", "username", "User")
        sip = _get(raw_log, "source_ip", "rhost", "src_ip")
        res = str(_get(raw_log, "result", "success", default="success")).lower()
        method = _get(raw_log, "method", "action", default="")
        cmd = _get(raw_log, "command", "cmdline", default="")
        action = f"{method} {cmd}".strip() or str(raw_log.get("message", ""))
        failure = res in ("failure", "failed", "fail", "0")
        return UnifiedEventDTO(
            timestamp=_parse_ts(_get(raw_log, "timestamp", "time")),
            source_type="linux_auth",
            source_ip=str(sip or "") or None,
            destination_ip=None,
            hostname=_get(raw_log, "hostname", "host"),
            username=str(user or "") or None,
            action=action,
            result="failure" if failure else "success",
            raw=raw_str,
            extra=raw_log,
        )

    # generic
    return UnifiedEventDTO(
        timestamp=_parse_ts(_get(raw_log, "timestamp", "time")),
        source_type=st or "generic",
        source_ip=str(_get(raw_log, "source_ip", "src_ip") or "") or None,
        destination_ip=str(_get(raw_log, "destination_ip", "dst_ip") or "") or None,
        hostname=_get(raw_log, "hostname", "host"),
        username=_get(raw_log, "username", "user"),
        action=str(_get(raw_log, "action", "message", default="")),
        result=str(_get(raw_log, "result", default="success")).lower(),
        raw=raw_str,
        extra=raw_log,
    )
