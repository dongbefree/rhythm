"""Public API: add a note in one call."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from . import classifier, storage
from .storage import Note


def add(text: str) -> Note:
    """Parse, classify and persist a free-text note."""
    category, cleaned, due = classifier.analyze(text)
    note = Note(
        timestamp=datetime.now(),
        category=category,
        text=cleaned,
        due=due,
    )
    storage.add_note(note)
    return note
