from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from .config import PROFILES_FILE


@dataclass
class Profile:
    name: str = "Guest"
    total_score: int = 0


def get_guest_profile() -> Profile:
    path = Path(PROFILES_FILE)
    if not path.exists():
        return Profile()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Profile(**data)
    except Exception:
        return Profile()


def save_profile(profile: Profile) -> None:
    path = Path(PROFILES_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
