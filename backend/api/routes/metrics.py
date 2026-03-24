from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Alert, Event

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    ranges = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
    }

    def count_since(ts: datetime):
        return db.query(Alert).filter(Alert.timestamp >= ts).count()

    total_alerts = count_since(ranges["24h"])

    by_severity: dict[str, int] = defaultdict(int)
    for sev, cnt in (
        db.query(Alert.severity, func.count())
        .filter(Alert.timestamp >= ranges["7d"])
        .group_by(Alert.severity)
        .all()
    ):
        by_severity[sev] = int(cnt)

    by_status: dict[str, int] = defaultdict(int)
    for st, cnt in db.query(Alert.status, func.count()).group_by(Alert.status).all():
        by_status[st] = int(cnt)

    tech_counts: dict[str, int] = defaultdict(int)
    for row in db.query(Alert.mitre_techniques).filter(Alert.timestamp >= ranges["30d"]).all():
        for t in row[0] or []:
            tech_counts[str(t)] += 1
    top_techniques = sorted(tech_counts.items(), key=lambda x: -x[1])[:10]

    # Alerts over time: last 7 days daily buckets
    start = now - timedelta(days=7)
    alerts_over_time: list[dict] = []
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(8):
        d0 = day + timedelta(days=i)
        d1 = d0 + timedelta(days=1)
        c = db.query(Alert).filter(Alert.timestamp >= d0, Alert.timestamp < d1).count()
        alerts_over_time.append({"date": d0.date().isoformat(), "count": c})

    # MTTD: avg minutes from event to alert, grouped by alert severity
    mttd_by_severity: dict[str, float] = {}
    for sev in ["critical", "high", "medium", "low"]:
        pairs = (
            db.query(Event.timestamp, Alert.timestamp)
            .join(Alert, Alert.event_id == Event.id)
            .filter(Alert.severity == sev)
            .limit(5000)
            .all()
        )
        if not pairs:
            mttd_by_severity[sev] = 0.0
            continue
        deltas = [(a - e).total_seconds() / 60.0 for e, a in pairs]
        mttd_by_severity[sev] = round(sum(deltas) / len(deltas), 2)

    # FP rate by rule
    fp_rate_by_rule: dict[str, dict[str, float]] = {}
    for rule_id, st, cnt in (
        db.query(Alert.rule_id, Alert.status, func.count())
        .group_by(Alert.rule_id, Alert.status)
        .all()
    ):
        fp_rate_by_rule.setdefault(rule_id, {"false_positive": 0, "total": 0})
        fp_rate_by_rule[rule_id]["total"] += int(cnt)
        if st == "false_positive":
            fp_rate_by_rule[rule_id]["false_positive"] += int(cnt)
    fp_out = {
        rid: {
            "fp_rate": round(v["false_positive"] / v["total"], 4) if v["total"] else 0.0,
            "fp_count": v["false_positive"],
            "total": v["total"],
        }
        for rid, v in fp_rate_by_rule.items()
    }

    open_alerts = db.query(Alert).filter(Alert.status.in_(["new", "investigating", "escalated"])).count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "critical", Alert.status != "resolved").count()
    avg_mttd = (
        sum(mttd_by_severity.values()) / max(len([x for x in mttd_by_severity.values() if x > 0]), 1) or 0.0
    )

    return {
        "totals_by_period": {k: count_since(v) for k, v in ranges.items()},
        "total_alerts_24h": total_alerts,
        "by_severity": dict(by_severity),
        "by_status": dict(by_status),
        "by_technique_top10": [{"technique": t, "count": c} for t, c in top_techniques],
        "alerts_over_time": alerts_over_time,
        "mttd_by_severity": mttd_by_severity,
        "fp_rate_by_rule": fp_out,
        "summary_cards": {
            "open_alerts": open_alerts,
            "critical_alerts": critical_alerts,
            "avg_mttd_minutes": round(avg_mttd, 2),
        },
    }


@router.get("/attack-heatmap")
def attack_heatmap(db: Session = Depends(get_db)):
    tech_counts: dict[str, int] = defaultdict(int)
    for row in db.query(Alert.mitre_techniques).all():
        for t in row[0] or []:
            tech_counts[str(t)] += 1
    return dict(sorted(tech_counts.items()))
