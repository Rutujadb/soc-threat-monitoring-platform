from datetime import datetime, timezone

from sqlalchemy.orm import Session

from api.models import Alert, Event


def create_alert(
    db: Session,
    *,
    event: Event,
    rule: dict,
    summary: str | None = None,
) -> Alert:
    sev = str(rule.get("severity", "medium")).lower()
    techniques = list(rule.get("mitre_techniques") or [])
    pb = rule.get("playbook")
    a = Alert(
        timestamp=datetime.now(timezone.utc),
        rule_id=str(rule["id"]),
        rule_name=str(rule.get("name", rule["id"])),
        severity=sev,
        status="new",
        mitre_techniques=techniques,
        affected_host=event.hostname,
        source_ip=event.source_ip,
        event_id=event.id,
        assigned_to=None,
        summary=summary or rule.get("description"),
        playbook_path=str(pb) if pb else None,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
