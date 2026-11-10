"""Background daemon: fires compact notifications at configured times.

Run with: python -m rhythm daemon
Stays in foreground, check every 30 seconds.
"""

from __future__ import annotations

import time
from datetime import datetime

from . import brief, config, notifier


SCHEDULE = [
    ("morning_time", brief.morning_notification, brief.morning_brief),
    ("noon_time", brief.noon_notification, brief.noon_brief),
    ("evening_time", brief.evening_notification, brief.evening_brief),
]


def _hhm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def run() -> None:
    print("♪ Rhythm daemon 已启动。到点自动弹通知。")
    print("  按 Ctrl+C 退出。")
    print()

    fired_today: set = set()

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_min = now.hour * 60 + now.minute

        cfg = config.load()

        for key, notify_fn, _ in SCHEDULE:
            target = cfg.get(key, "09:00")
            target_min = _hhm_to_minutes(target)
            mark = f"{today_str}:{key}"

            # Fire if we're at or past the target time, and haven't fired today
            if now_min >= target_min and mark not in fired_today:
                title, msg = notify_fn()
                notifier.notify(title, msg)
                print(f"[{now.strftime('%H:%M')}] 已推送：{title} — {msg}")
                fired_today.add(mark)

        # Reset at midnight
        if now.hour == 0 and now.minute == 0:
            fired_today.clear()

        time.sleep(30)
