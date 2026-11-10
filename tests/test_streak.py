"""Tests for study_streak and storage round-trip."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from rhythm import storage
from rhythm.brief import study_streak
from rhythm.storage import Note


@pytest.fixture
def tmp_home(tmp_path, monkeypatch):
    """Point RHYTHM_HOME at a temp dir so tests never touch real data."""
    monkeypatch.setenv("RHYTHM_HOME", str(tmp_path))
    return tmp_path


def _note(day, category="study", text="x"):
    return Note(
        timestamp=datetime(day.year, day.month, day.day, 14, 30),
        category=category,
        text=text,
    )


def test_streak_empty(tmp_home):
    assert study_streak() == 0


def test_streak_today_only(tmp_home):
    today = date.today()
    storage.add_note(_note(today, "study"))
    assert study_streak() == 1


def test_streak_consecutive(tmp_home):
    today = date.today()
    storage.add_note(_note(today, "study"))
    storage.add_note(_note(today - timedelta(days=1), "study"))
    storage.add_note(_note(today - timedelta(days=2), "study"))
    assert study_streak() == 3


def test_streak_gap_breaks(tmp_home):
    today = date.today()
    storage.add_note(_note(today, "study"))
    storage.add_note(_note(today - timedelta(days=1), "study"))
    # gap at today-2, resume today-3
    storage.add_note(_note(today - timedelta(days=3), "study"))
    assert study_streak() == 2


def test_streak_ignores_non_study(tmp_home):
    today = date.today()
    storage.add_note(_note(today, "work"))
    assert study_streak() == 0


def test_roundtrip(tmp_home):
    today = date.today()
    note = Note(
        timestamp=datetime(today.year, today.month, today.day, 9, 5),
        category="work",
        text="明天交报告",
        due=today + timedelta(days=1),
    )
    storage.add_note(note)
    loaded = storage.load_day(today)
    assert len(loaded) == 1
    n = loaded[0]
    assert n.category == "work"
    assert n.text == "明天交报告"
    assert n.due == today + timedelta(days=1)
    assert n.done is False


def test_load_range_inclusive(tmp_home):
    today = date.today()
    storage.add_note(_note(today - timedelta(days=2), "study"))
    storage.add_note(_note(today, "study"))
    notes = storage.load_range(today - timedelta(days=2), today)
    assert len(notes) == 2
