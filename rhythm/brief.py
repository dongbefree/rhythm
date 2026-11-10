"""Generate the three daily briefings: morning, noon, evening."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import List, Tuple

from . import config, storage
from .storage import Note


def _upcoming_due(notes: List[Note]) -> List[Tuple[Note, int]]:
    """Return notes with a due date within the next 7 days, sorted by due."""
    today = date.today()
    items = []
    for n in notes:
        if n.due:
            delta = (n.due - today).days
            if 0 <= delta <= 7:
                items.append((n, delta))
    items.sort(key=lambda x: x[1])
    return items


def study_streak() -> int:
    """Count consecutive days with at least one study note.

    Today doesn't break the streak until it's over — if today has no study
    note yet, we start counting from yesterday.
    """
    today = date.today()
    notes_today = storage.load_day(today)
    if any(n.category == "study" for n in notes_today):
        streak = 1
        d = today - timedelta(days=1)
    else:
        streak = 0
        d = today - timedelta(days=1)

    while True:
        notes = storage.load_day(d)
        if any(n.category == "study" for n in notes):
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak


def morning_brief() -> Tuple[str, str]:
    """Return (title, body) for the morning briefing."""
    today = date.today()
    week = storage.load_range(today - timedelta(days=7), today)
    upcoming = _upcoming_due(week)

    # Today's notes
    today_notes = storage.load_day(today)

    # Study line health: did we record anything study in the last 3 days?
    recent = storage.load_range(today - timedelta(days=3), today)
    study_notes = [n for n in recent if n.category == "study" and not n.done]

    lines = []

    # Top priorities today
    today_todos = [n for n in today_notes if not n.done]
    if today_todos:
        lines.append("今天压着的事：")
        for n in today_todos[:3]:
            lines.append(f"  • {n.text}")
    else:
        lines.append("今天还没记什么，趁早上理一理？")

    # Upcoming due dates (preview, not just today)
    if upcoming:
        lines.append("")
        lines.append("接下来几天的事：")
        for n, delta in upcoming[:3]:
            if delta == 0:
                lines.append(f"  • 今天截止：{n.text}")
            elif delta == 1:
                lines.append(f"  • 明天：{n.text}")
            else:
                lines.append(f"  • {delta}天后（{n.due.strftime('%m/%d')}）：{n.text}")

    # Study line nudge with streak
    lines.append("")
    streak = study_streak()
    if streak > 0:
        lines.append(f"🔥 学习已连续 {streak} 天——今天哪怕 15 分钟，别断。")
    else:
        lines.append("学习线最近没动静了——今天从 20 分钟开始，建一条新的连续记录。")

    return "Rhythm · 晨间简报", "\n".join(lines)


def noon_brief() -> Tuple[str, str]:
    """Return (title, body) for the noon check-in."""
    today = date.today()
    notes = storage.load_day(today)
    pending = [n for n in notes if not n.done]
    done = [n for n in notes if n.done]

    lines = ["上午小结："]
    if done:
        lines.append(f"  已完成 {len(done)} 件")
    else:
        lines.append("  上午还没勾掉什么")

    lines.append("")
    if pending:
        lines.append(f"下午还剩 {len(pending)} 件：")
        for n in pending[:3]:
            lines.append(f"  • [{n.category}] {n.text}")
    else:
        lines.append("下午没有压着的事，节奏不错。")

    return "Rhythm · 午间检查", "\n".join(lines)


def evening_brief() -> Tuple[str, str]:
    """Return (title, body) for the evening review."""
    today = date.today()
    notes = storage.load_day(today)

    cat_counts = Counter(n.category for n in notes)
    total = len(notes) or 1

    lines = ["今日复盘："]
    lines.append(f"  共记 {len(notes)} 条")
    for cat in ("work", "study", "life"):
        c = cat_counts.get(cat, 0)
        pct = int(c / total * 100)
        lines.append(f"  {cat:6s} {c:2d} 条 ({pct}%)")

    # Study check with streak
    study_today = cat_counts.get("study", 0)
    streak = study_streak()
    lines.append("")
    if study_today > 0:
        lines.append(f"🔥 连续学习 {streak} 天，今天又保住了。")
    else:
        if streak > 0:
            lines.append(f"今天学习线是空的——你已经连续 {streak} 天了，明天别断。")
        else:
            lines.append("今天学习线是空的。明天 20 分钟，从零建一条连续记录。")

    # Tomorrow preview
    tomorrow = today + timedelta(days=1)
    tomorrow_notes = storage.load_day(tomorrow)
    tomorrow_due = [n for n in tomorrow_notes if n.due]
    if tomorrow_due:
        lines.append("")
        lines.append("明天有截止的事：")
        for n in tomorrow_due:
            lines.append(f"  • {n.text}")

    return "Rhythm · 傍晚复盘", "\n".join(lines)


# ---- Compact one-line notifications (for popups) ----

def morning_notification() -> Tuple[str, str]:
    """One-line popup: most urgent thing + streak."""
    today = date.today()
    today_notes = storage.load_day(today)
    todos = [n for n in today_notes if not n.done]
    cfg = config.load()

    parts = []
    if todos:
        parts.append(f"今天：{todos[0].text}")
    else:
        # Check upcoming due
        week = storage.load_range(today, today + timedelta(days=3))
        upcoming = _upcoming_due(week)
        if upcoming:
            n, delta = upcoming[0]
            if delta == 0:
                parts.append(f"今天截止：{n.text}")
            elif delta == 1:
                parts.append(f"明天：{n.text}")
            else:
                parts.append(f"{delta}天后：{n.text}")
        else:
            parts.append("今天还没记什么")

    if cfg.get("show_streak", True):
        streak = study_streak()
        if streak > 0:
            parts.append(f"🔥{streak}天")

    return "☀️ 晨间", " · ".join(parts)


def noon_notification() -> Tuple[str, str]:
    """One-line popup: how many done / remaining."""
    today = date.today()
    notes = storage.load_day(today)
    done = len([n for n in notes if n.done])
    pending = len([n for n in notes if not n.done])

    if pending == 0:
        msg = "上午记的都清了，下午节奏不错"
    else:
        msg = f"上午记了 {len(notes)} 条，下午还剩 {pending} 件"

    return "🍜 午间", msg


def evening_notification() -> Tuple[str, str]:
    """One-line popup: breakdown + streak."""
    today = date.today()
    notes = storage.load_day(today)
    cfg = config.load()

    cat_counts = Counter(n.category for n in notes)
    parts = []
    if cfg.get("show_breakdown", False):
        parts.append(
            f"工作{cat_counts.get('work', 0)}"
            f"/学习{cat_counts.get('study', 0)}"
            f"/生活{cat_counts.get('life', 0)}"
        )
    else:
        parts.append(f"今天记了 {len(notes)} 条")

    if cfg.get("show_streak", True):
        streak = study_streak()
        if streak > 0:
            parts.append(f"🔥{streak}天")

    return "🌆 复盘", " · ".join(parts)
