import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Event
from detection.alert_generator import create_alert
from detection.engine import DetectionEngine
from ingestor.normalizer import normalize_event
from ingestor.schemas import IngestPayload

router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/ingest")
def ingest_event(body: IngestPayload, request: Request, db: Session = Depends(get_db)):
    engine: DetectionEngine = request.app.state.detection_engine
    ts = body.timestamp or datetime.now(timezone.utc)
    raw = body.log or {}
    unified = normalize_event(raw, body.source_type)
    if unified.timestamp and body.timestamp is None:
        ts = unified.timestamp

    ev = Event(
        id=str(uuid.uuid4()),
        timestamp=ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc),
        source_type=unified.source_type,
        source_ip=unified.source_ip,
        destination_ip=unified.destination_ip,
        hostname=unified.hostname,
        username=unified.username,
        action=unified.action,
        result=unified.result,
        raw=unified.raw,
        extra=unified.extra or {},
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)

    alerts_out = []
    for rule in engine.evaluate(ev):
        alev = create_alert(db, event=ev, rule=rule)
        alerts_out.append({"id": alev.id, "rule_id": alev.rule_id, "severity": alev.severity})

    return {"event_id": ev.id, "alerts": alerts_out}
