"""User config: notification times, what to show, compact mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULTS: Dict[str, Any] = {
    "morning_time": "09:00",
    "noon_time": "12:30",
    "evening_time": "18:00",
    "compact": True,           # 弹窗只显示一行最核心的
    "show_streak": True,       # 🔥 连续天数
    "show_upcoming": True,     # 接下来几天的事
    "show_breakdown": False,   # 工作/学习/生活占比（默认不弹窗显示）
}


def _config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "config.json"


def load() -> Dict[str, Any]:
    """Load config, falling back to defaults for missing keys."""
    path = _config_path()
    cfg = dict(DEFAULTS)
    if path.exists():
        try:
            user = json.loads(path.read_text(encoding="utf-8"))
            cfg.update(user)
        except Exception:
            pass
    return cfg


def save(cfg: Dict[str, Any]) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def get(key: str) -> Any:
    return load().get(key, DEFAULTS.get(key))


def set_key(key: str, value: str) -> None:
    """Set a config key from a string value (used by CLI)."""
    cfg = load()
    # Try to parse as bool/int, else keep as string
    if value.lower() in ("true", "yes", "on"):
        cfg[key] = True
    elif value.lower() in ("false", "no", "off"):
        cfg[key] = False
    else:
        try:
            cfg[key] = int(value)
        except ValueError:
            cfg[key] = value
    save(cfg)
