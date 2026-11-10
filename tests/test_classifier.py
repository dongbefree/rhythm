"""Tests for the Chinese date parser in rhythm.classifier."""

from __future__ import annotations

from datetime import date

from rhythm.classifier import parse_date, classify, analyze


def _parse(text, today):
    cleaned, due = parse_date(text, today)
    return cleaned, due


def test_today():
    today = date(2026, 11, 10)
    cleaned, due = _parse("今天交报告", today)
    assert due == date(2026, 11, 10)
    assert cleaned == "交报告"


def test_tonight():
    today = date(2026, 11, 10)
    _, due = _parse("今晚开会", today)
    assert due == date(2026, 11, 10)


def test_tomorrow():
    today = date(2026, 11, 10)
    cleaned, due = _parse("明天交稿", today)
    assert due == date(2026, 11, 11)
    assert cleaned == "交稿"


def test_day_after_tomorrow():
    today = date(2026, 11, 10)
    _, due = _parse("后天考试", today)
    assert due == date(2026, 11, 12)


def test_n_days_later():
    today = date(2026, 11, 10)
    cleaned, due = _parse("3天后上线", today)
    assert due == date(2026, 11, 13)
    assert cleaned == "上线"


def test_weekday_next_week():
    # 2026-11-10 is a Tuesday. "周五" should land on Friday 11-13.
    today = date(2026, 11, 10)
    _, due = _parse("周五交稿", today)
    assert due == date(2026, 11, 13)


def test_weekday_same_day_rolls_to_next_week():
    # "周二" on a Tuesday → next Tuesday (7 days later).
    today = date(2026, 11, 10)
    _, due = _parse("周二交稿", today)
    assert due == date(2026, 11, 17)


def test_xingqi_variant():
    today = date(2026, 11, 10)
    _, due = _parse("星期三交稿", today)
    assert due == date(2026, 11, 11)


def test_month_day():
    today = date(2026, 11, 10)
    _, due = _parse("11月8日交稿", today)
    # Already past → rolls to next year
    assert due == date(2027, 11, 8)


def test_month_day_future():
    today = date(2026, 11, 10)
    _, due = _parse("12月1日交稿", today)
    assert due == date(2026, 12, 1)


def test_no_date():
    today = date(2026, 11, 10)
    cleaned, due = _parse("随便记一条", today)
    assert due is None
    assert cleaned == "随便记一条"


def test_classify_study():
    assert classify("学 20 分钟 Python") == "study"


def test_classify_work():
    assert classify("周五交报告给老板") == "work"


def test_classify_life():
    assert classify("去超市买菜") == "life"


def test_analyze_pipeline():
    today = date(2026, 11, 10)
    category, cleaned, due = analyze("明天学 Python")
    assert category == "study"
    assert cleaned == "学 Python"
    assert due == date(2026, 11, 11)
