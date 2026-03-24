from pathlib import Path
from typing import Any

import yaml


def load_rules_from_dir(rules_dir: Path) -> list[dict[str, Any]]:
    if not rules_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(rules_dir.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and data.get("id"):
                out.append(data)
    return out
