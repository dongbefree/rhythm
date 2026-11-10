"""Local Markdown storage. Every note lives in a daily file under data/notes/."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional


@dataclass
class Note:
    timestamp: datetime
    category: str          # work / study / life
    text: str
    due: Optional[date] = None
    done: bool = False

    def to_line(self) -> str:
        flag = "x" if self.done else " "
        due_str = f" due:{self.due.isoformat()}" if self.due else ""
        return f"- [{flag}] [{self.timestamp.strftime('%H:%M')}] ({self.category}) {self.text}{due_str}"


def _data_dir() -> Path:
    """Return the notes directory, creating it if needed.

    Priority: $RHYTHM_HOME > project-local ./data/notes.
    """
    base = os.environ.get("RHYTHM_HOME")
    if base:
        notes_dir = Path(base) / "notes"
    else:
        # Project-local: <repo>/data/notes
        notes_dir = Path(__file__).resolve().parent.parent / "data" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    return notes_dir


def _file_for(day: date) -> Path:
    return _data_dir() / f"{day.isoformat()}.md"


def add_note(note: Note) -> Path:
    """Append a note to today's daily file."""
    f = _file_for(note.timestamp.date())
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(note.to_line() + "\n")
    return f


def parse_line(line: str, day: date) -> Optional[Note]:
    """Parse a single markdown line back into a Note."""
    line = line.strip()
    if not line.startswith("- ["):
        return None
    # - [x] [14:30] (work) 明天交报告 due:2026-11-08
    try:
        done = line[3] == "x"
        rest = line[6:].strip()
        time_str, rest = rest.split("] ", 1)
        time_str = time_str.lstrip("[")
        ts = datetime.strptime(time_str, "%H:%M").replace(
            year=day.year, month=day.month, day=day.day
        )
        cat_close = rest.index(")")
        category = rest[1:cat_close]
        rest = rest[cat_close + 2:]
        due = None
        if " due:" in rest:
            text, due_str = rest.rsplit(" due:", 1)
            due = date.fromisoformat(due_str.strip())
            rest = text
        return Note(timestamp=ts, category=category, text=rest.strip(), due=due, done=done)
    except Exception:
        return None


def load_day(day: date) -> List[Note]:
    """Load all notes for a given day."""
    f = _file_for(day)
    if not f.exists():
        return []
    notes = []
    for line in f.read_text(encoding="utf-8").splitlines():
        n = parse_line(line, day)
        if n:
            notes.append(n)
    return notes


def load_range(start: date, end: date) -> List[Note]:
    """Load notes from start..end inclusive."""
    notes = []
    d = start
    while d <= end:
        notes.extend(load_day(d))
        d += timedelta(days=1)
    return notes


def today() -> date:
    return date.today()
