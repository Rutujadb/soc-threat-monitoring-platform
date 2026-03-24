from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Alert, Case, CaseAlert

router = APIRouter(prefix="/api/cases", tags=["cases"])


class CaseOut(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    description: str | None
    alert_count: int

    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    title: str
    severity: str = "medium"
    description: str | None = None


class CasePatch(BaseModel):
    title: str | None = None
    severity: str | None = None
    status: str | None = None
    description: str | None = None


class LinkAlertBody(BaseModel):
    alert_id: str


@router.get("/{case_id}/detail")
def case_detail(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404)
    links = db.query(CaseAlert.alert_id).filter(CaseAlert.case_id == case_id).all()
    alert_ids = [x[0] for x in links]
    alerts_min = []
    for aid in alert_ids:
        a = db.query(Alert).filter(Alert.id == aid).first()
        if a:
            alerts_min.append(
                {
                    "id": a.id,
                    "rule_name": a.rule_name,
                    "severity": a.severity,
                    "timestamp": a.timestamp.isoformat(),
                }
            )
    n = len(alert_ids)
    return {
        "case": CaseOut(
            id=c.id,
            title=c.title,
            severity=c.severity,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
            description=c.description,
            alert_count=n,
        ),
        "alerts": alerts_min,
    }


@router.get("")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    out = []
    for c in cases:
        n = db.query(CaseAlert).filter(CaseAlert.case_id == c.id).count()
        out.append(
            CaseOut(
                id=c.id,
                title=c.title,
                severity=c.severity,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
                description=c.description,
                alert_count=n,
            )
        )
    return out


@router.post("", response_model=CaseOut)
def create_case(body: CaseCreate, db: Session = Depends(get_db)):
    c = Case(
        title=body.title,
        severity=body.severity.lower(),
        status="open",
        description=body.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return CaseOut(
        id=c.id,
        title=c.title,
        severity=c.severity,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        description=c.description,
        alert_count=0,
    )


@router.patch("/{case_id}", response_model=CaseOut)
def patch_case(case_id: str, body: CasePatch, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404)
    if body.title is not None:
        c.title = body.title
    if body.severity is not None:
        c.severity = body.severity
    if body.status is not None:
        c.status = body.status
    if body.description is not None:
        c.description = body.description
    c.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(c)
    n = db.query(CaseAlert).filter(CaseAlert.case_id == c.id).count()
    return CaseOut(
        id=c.id,
        title=c.title,
        severity=c.severity,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        description=c.description,
        alert_count=n,
    )


@router.post("/{case_id}/alerts")
def link_alert(case_id: str, body: LinkAlertBody, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404)
    a = db.query(Alert).filter(Alert.id == body.alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    exists = db.query(CaseAlert).filter_by(case_id=case_id, alert_id=body.alert_id).first()
    if not exists:
        db.add(CaseAlert(case_id=case_id, alert_id=body.alert_id))
        c.updated_at = datetime.now(timezone.utc)
        db.commit()
    return {"ok": True}
