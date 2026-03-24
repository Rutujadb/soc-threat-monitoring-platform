from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session, joinedload

from api.db import get_db
from api.models import Alert, AlertNote, Event
from detection.rule_loader import load_rules_from_dir

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertNoteOut(BaseModel):
    id: str
    timestamp: datetime
    author: str
    content: str

    class Config:
        from_attributes = True


class AlertListItem(BaseModel):
    id: str
    timestamp: datetime
    rule_id: str
    rule_name: str
    severity: str
    status: str
    mitre_techniques: list
    affected_host: str | None
    source_ip: str | None
    assigned_to: str | None
    summary: str | None

    class Config:
        from_attributes = True


class AlertDetail(AlertListItem):
    event_id: str
    playbook_path: str | None
    raw_event: dict
    notes: list[AlertNoteOut]
    rule_yaml: dict | None = None


class AlertPatch(BaseModel):
    status: str | None = None
    assigned_to: str | None = None
    note_content: str | None = None
    note_author: str | None = "analyst"


class AlertsPage(BaseModel):
    items: list[AlertListItem]
    total: int


@router.get("", response_model=AlertsPage)
def list_alerts(
    db: Session = Depends(get_db),
    status: str | None = None,
    severity: str | None = None,
    mitre_technique: str | None = None,
    hostname: str | None = None,
    q: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
):
    qry = db.query(Alert).join(Event, Alert.event_id == Event.id)
    if status:
        qry = qry.filter(Alert.status == status)
    if severity:
        qry = qry.filter(Alert.severity == severity.lower())
    if mitre_technique:
        qry = qry.filter(cast(Alert.mitre_techniques, String).like(f"%{mitre_technique}%"))
    if hostname:
        qry = qry.filter(
            or_(
                Alert.affected_host.ilike(f"%{hostname}%"),
                Event.hostname.ilike(f"%{hostname}%"),
            )
        )
    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(Alert.source_ip.ilike(like), Event.source_ip.ilike(like), Alert.rule_name.ilike(like)))
    if start_date:
        qry = qry.filter(Alert.timestamp >= start_date)
    if end_date:
        qry = qry.filter(Alert.timestamp <= end_date)

    total = qry.count()
    rows = (
    qry.order_by(Alert.timestamp.desc())
        .offset(max(0, offset))
        .limit(min(500, max(1, limit)))
        .all()
    )
    return AlertsPage(items=rows, total=total)


@router.get("/{alert_id}", response_model=AlertDetail)
def get_alert(alert_id: str, request: Request, db: Session = Depends(get_db)):
    repo_root = request.app.state.repo_root

    a = (
        db.query(Alert)
        .options(joinedload(Alert.notes), joinedload(Alert.event))
        .filter(Alert.id == alert_id)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    ev = a.event
    raw_event = {
        "id": ev.id,
        "timestamp": ev.timestamp.isoformat(),
        "source_type": ev.source_type,
        "source_ip": ev.source_ip,
        "hostname": ev.hostname,
        "username": ev.username,
        "action": ev.action,
        "result": ev.result,
        "raw": ev.raw,
        "extra": ev.extra or {},
    }
    rules = load_rules_from_dir(repo_root / "rules")
    rule_yaml = next((r for r in rules if r.get("id") == a.rule_id), None)
    return AlertDetail(
        id=a.id,
        timestamp=a.timestamp,
        rule_id=a.rule_id,
        rule_name=a.rule_name,
        severity=a.severity,
        status=a.status,
        mitre_techniques=a.mitre_techniques or [],
        affected_host=a.affected_host,
        source_ip=a.source_ip,
        assigned_to=a.assigned_to,
        summary=a.summary,
        event_id=a.event_id,
        playbook_path=a.playbook_path,
        raw_event=raw_event,
        notes=sorted(a.notes, key=lambda n: n.timestamp),
        rule_yaml=rule_yaml,
    )


@router.patch("/{alert_id}", response_model=AlertListItem)
def patch_alert(alert_id: str, body: AlertPatch, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    if body.status:
        a.status = body.status
    if body.assigned_to is not None:
        a.assigned_to = body.assigned_to
    if body.note_content:
        db.add(AlertNote(alert_id=a.id, author=body.note_author or "analyst", content=body.note_content))
    db.commit()
    db.refresh(a)
    return a
