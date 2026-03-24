import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from api.models import Event
from detection.engine import DetectionEngine


def _repo_rules() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "rules"


def make_event(**kwargs) -> Event:
    defaults = dict(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        source_type="windows_auth",
        source_ip="10.0.0.1",
        destination_ip=None,
        hostname="h1",
        username="user1",
        action="EventID:4625 LogonType:3",
        result="failure",
        raw="{}",
        extra={},
    )
    defaults.update(kwargs)
    return Event(**defaults)


def test_threshold_fires_after_enough_failures():
    eng = DetectionEngine(_repo_rules())
    now = datetime.now(timezone.utc)
    rule = next(r for r in eng.reload_rules() if r["id"] == "RULE-001")
    cond = rule["conditions"]
    count = cond["count"]
    saw_fire = False
    for i in range(count):
        ev = make_event(
            timestamp=now + timedelta(seconds=i),
            source_ip="1.2.3.4",
            result="failure",
        )
        hits = eng.evaluate(ev)
        if any(h["id"] == "RULE-001" for h in hits):
            saw_fire = True
            break
    assert saw_fire


def test_threshold_does_not_fire_below_threshold():
    eng = DetectionEngine(_repo_rules())
    now = datetime.now(timezone.utc)
    for i in range(3):
        ev = make_event(timestamp=now + timedelta(seconds=i), source_ip="9.9.9.9", result="failure")
        hits = [h["id"] for h in eng.evaluate(ev)]
        assert "RULE-001" not in hits


def test_pattern_dns_long_subdomain():
    eng = DetectionEngine(_repo_rules())
    longq = "a" * 45 + ".evil.com"
    ev = make_event(
        source_type="dns",
        source_ip="10.2.2.2",
        action=longq,
        result="success",
        extra={"query_name": longq},
    )
    ids = [h["id"] for h in eng.evaluate(ev)]
    assert "RULE-004" in ids


def test_after_hours_weekend_logon():
    eng = DetectionEngine(_repo_rules())
    sat = datetime(2024, 3, 2, 21, 0, tzinfo=timezone.utc)  # Saturday
    ev = make_event(
        timestamp=sat,
        result="success",
        action="EventID:4624 LogonType:10",
    )
    ids = [h["id"] for h in eng.evaluate(ev)]
    assert "RULE-011" in ids


def test_sequence_detector_two_step():
    eng = DetectionEngine(_repo_rules())
    rule = {
        "id": "RULE-SEQ-TEST",
        "conditions": {
            "type": "sequence",
            "first_action_contains": "stageA",
            "second_action_contains": "stageB",
            "within_seconds": 120,
        },
    }
    host = "work1"
    t0 = datetime.now(timezone.utc)
    ev1 = make_event(hostname=host, action="stageA download", timestamp=t0)
    ev2 = make_event(hostname=host, action="stageB payload", timestamp=t0 + timedelta(seconds=5))
    assert not eng._eval_sequence(rule, rule["conditions"], ev1, t0)  # noqa: SLF001
    assert eng._eval_sequence(rule, rule["conditions"], ev2, t0 + timedelta(seconds=5))  # noqa: SLF001
