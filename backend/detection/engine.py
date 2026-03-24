from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from api.models import Event as DBEvent
from detection.baseline import BaselineTracker
from detection.rule_loader import load_rules_from_dir


def get_field(event: DBEvent, name: str) -> Any:
    if hasattr(event, name):
        v = getattr(event, name)
        if v is not None:
            return v
    extra = event.extra or {}
    return extra.get(name)


def _event_matches_filters(event: DBEvent, cond: dict) -> bool:
    st = cond.get("source_type")
    if st and event.source_type != st:
        return False
    if "result" in cond and cond["result"] is not None:
        if (event.result or "").lower() != str(cond["result"]).lower():
            return False
    fld = cond.get("field")
    val = cond.get("value")
    if fld is not None and val is not None:
        ev = get_field(event, str(fld))
        if ev is None or str(ev) != str(val):
            # allow substring for action-heavy fields
            if str(val) not in str(ev):
                return False
    return True


def _business_hours(dt: datetime) -> bool:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if dt.weekday() >= 5:
        return False
    h = dt.hour
    return 8 <= h < 18


@dataclass
class SequenceState:
    """Last seen timestamps for sequence rules per host."""

    last: dict[tuple[str, str, str], datetime] = field(default_factory=dict)


class DetectionEngine:
    def __init__(self, rules_dir: Path):
        self.rules_dir = rules_dir
        self.baseline = BaselineTracker()
        self._threshold_windows: dict[tuple[str, str], list[datetime]] = defaultdict(list)
        self._seq = SequenceState()

    def reload_rules(self) -> list[dict[str, Any]]:
        return load_rules_from_dir(self.rules_dir)

    def _clean_window(self, window: list[datetime], now: datetime, seconds: int) -> None:
        cutoff = now - timedelta(seconds=seconds)
        window[:] = [t for t in window if t >= cutoff]

    def evaluate(self, event: DBEvent) -> list[dict]:
        rules = self.reload_rules()
        fired: list[dict] = []
        now = event.timestamp
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        for rule in rules:
            cond = rule.get("conditions") or {}
            ctype = cond.get("type")
            if ctype == "threshold":
                if self._eval_threshold(rule, cond, event, now):
                    fired.append(rule)
            elif ctype == "pattern":
                if self._eval_pattern(rule, cond, event):
                    fired.append(rule)
            elif ctype == "after_hours":
                if self._eval_after_hours(rule, cond, event):
                    fired.append(rule)
            elif ctype == "sequence":
                r = self._eval_sequence(rule, cond, event, now)
                if r:
                    fired.append(rule)
            elif ctype == "anomaly":
                if self._eval_anomaly(rule, cond, event):
                    fired.append(rule)
        return fired

    def _eval_threshold(self, rule: dict, cond: dict, event: DBEvent, now: datetime) -> bool:
        if not _event_matches_filters(event, cond):
            return False
        # Optional field=value filter using cond field
        group_field = cond.get("group_by", "source_ip")
        group_val = str(get_field(event, group_field) or "")
        key = (rule["id"], group_val)
        win_sec = int(cond.get("window_seconds", 60))
        need = int(cond.get("count", 5))
        window = self._threshold_windows[key]
        self._clean_window(window, now, win_sec)
        prev_len = len(window)
        window.append(now)
        return prev_len < need <= len(window)

    def _eval_pattern(self, rule: dict, cond: dict, event: DBEvent) -> bool:
        if cond.get("source_type") and event.source_type != cond["source_type"]:
            return False
        field_name = cond.get("field")
        regex = cond.get("regex")
        if not field_name or not regex:
            return False
        val = get_field(event, str(field_name))
        if val is None:
            return False
        try:
            return re.search(str(regex), str(val), re.IGNORECASE | re.DOTALL) is not None
        except re.error:
            return False

    def _eval_after_hours(self, rule: dict, cond: dict, event: DBEvent) -> bool:
        if cond.get("source_type") and event.source_type != cond["source_type"]:
            return False
        # Successful interactive logon indicator
        if (event.result or "").lower() == "failure":
            return False
        dt = event.timestamp
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if not _business_hours(dt):
            action = str(event.action or "")
            if "4624" in action or "EventID:4624" in action or "logon" in action.lower():
                return True
        return False

    def _eval_sequence(self, rule: dict, cond: dict, event: DBEvent, now: datetime) -> bool:
        host = event.hostname or event.source_ip or "unknown"
        a = cond.get("first_action_contains", "")
        b = cond.get("second_action_contains", "")
        within = int(cond.get("within_seconds", 300))
        sk = (rule["id"], host, "B")
        if a and a in str(event.action or ""):
            self._seq.last[(rule["id"], host, "A")] = now
            return False
        if b and b in str(event.action or ""):
            la = self._seq.last.get((rule["id"], host, "A"))
            if la and (now - la).total_seconds() <= within:
                self._seq.last[sk] = now
                return True
        return False

    def _eval_anomaly(self, rule: dict, cond: dict, event: DBEvent) -> bool:
        metric = str(cond.get("metric", "dns_queries"))
        host = event.hostname or event.source_ip or "*"
        field = cond.get("field", "count")
        val = get_field(event, str(field))
        try:
            v = float(val) if val is not None else 1.0
        except (TypeError, ValueError):
            v = 1.0
        z = self.baseline.zscore(metric, host, v)
        self.baseline.record(metric, host, v, event.timestamp)
        thr = float(cond.get("zscore_threshold", 3.0))
        return z is not None and abs(z) >= thr
