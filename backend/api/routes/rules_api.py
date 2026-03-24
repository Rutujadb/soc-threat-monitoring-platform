from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Alert
from detection.rule_loader import load_rules_from_dir

router = APIRouter(prefix="/api", tags=["rules"])


@router.get("/rules")
def list_rules(request: Request, db: Session = Depends(get_db)):
    repo_root = request.app.state.repo_root
    rules = load_rules_from_dir(repo_root / "rules")
    counts = dict(
        db.query(Alert.rule_id, func.count()).group_by(Alert.rule_id).all(),
    )
    for r in rules:
        r["trigger_count"] = int(counts.get(r["id"], 0))
    return rules


@router.get("/playbooks/{rule_id}", response_class=PlainTextResponse)
def get_playbook(rule_id: str, request: Request):
    repo_root = request.app.state.repo_root
    rules = load_rules_from_dir(repo_root / "rules")
    rule = next((r for r in rules if r.get("id") == rule_id), None)
    if not rule or not rule.get("playbook"):
        raise HTTPException(status_code=404, detail="Playbook not found")
    path = repo_root / str(rule["playbook"]).replace("\\", "/")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Playbook file missing")
    return path.read_text(encoding="utf-8")
