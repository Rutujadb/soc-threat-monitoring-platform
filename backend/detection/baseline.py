"""Per-field baselines for anomaly-style rules (extensible)."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class BaselineTracker:
    """Rolling numeric baselines keyed by (metric_name, host)."""

    window: timedelta = field(default_factory=lambda: timedelta(hours=24))
    _samples: dict[tuple[str, str], list[tuple[datetime, float]]] = field(default_factory=lambda: defaultdict(list))

    def record(self, metric: str, host: str, value: float, at: datetime | None = None) -> None:
        t = at or datetime.now(timezone.utc)
        key = (metric, host or "*")
        arr = self._samples[key]
        arr.append((t, float(value)))
        cutoff = t - self.window
        self._samples[key] = [(tt, v) for tt, v in arr if tt >= cutoff]

    def zscore(self, metric: str, host: str, value: float) -> float | None:
        key = (metric, host or "*")
        vals = [v for _, v in self._samples[key]]
        if len(vals) < 5:
            return None
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / max(len(vals) - 1, 1)
        std = var**0.5
        if std < 1e-9:
            return 0.0
        return (value - mean) / std
