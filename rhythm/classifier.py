"""Rule-based category + Chinese date parser. Leave a hook for LLM later."""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Tuple


# Category keyword sets
_WORK_KW = [
    "报告", "会议", "邮件", "客户", "deadline", "交稿", "项目", "老板",
    "需求", "bug", "上线", "评审", "方案", "排期", "迭代", "周报",
    "汇报", "合同", "发票", "需求", "测试", "部署", "代码", "PR",
    "工作", "上班", "开会", "对接", "进度", "延期",
]

_STUDY_KW = [
    "学", "读书", "课程", "教程", "练习", "python", "英语", "笔记",
    "复习", "背诵", "单词", "网课", "看书", "备考", "考试", "论文",
    "学习", "研究", "练习", "刷题", "语法", "听力", "阅读",
]

_LIFE_KW = [
    "买", "取", "健身", "饭", "家务", "预约", "医院", "朋友",
    "快递", "理发", "缴费", "洗衣服", "打扫", "约会", "聚会",
    "药", "超市", "地铁", "机票", "酒店", "生日",
]


def classify(text: str) -> str:
    """Return one of: work / study / life."""
    t = text.lower()
    scores = {"work": 0, "study": 0, "life": 0}
    for kw in _WORK_KW:
        if kw in t:
            scores["work"] += 1
    for kw in _STUDY_KW:
        if kw in t:
            scores["study"] += 1
    for kw in _LIFE_KW:
        if kw in t:
            scores["life"] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "life"  # default bucket
    return best


# ---- Chinese date parsing ----

_WEEKDAY_MAP = {
    "一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6,
    "天": 6,
}


def parse_date(text: str, today: Optional[date] = None) -> Tuple[str, Optional[date]]:
    """Scan text for a due date, return (cleaned_text, due_date)."""
    if today is None:
        today = date.today()
    t = text.strip()

    # 今天 / 明天 / 后天
    if m := re.search(r"今天|今晚", t):
        return _strip(t, m.group()), today
    if m := re.search(r"明天|明早", t):
        return _strip(t, m.group()), today + timedelta(days=1)
    if m := re.search(r"后天", t):
        return _strip(t, m.group()), today + timedelta(days=2)

    # X天后 / X天后交稿
    if m := re.search(r"(\d+)\s*天后", t):
        days = int(m.group(1))
        return _strip(t, m.group()), today + timedelta(days=days)

    # 周X / 星期X
    if m := re.search(r"周([一二三四五六日天])", t):
        target = _WEEKDAY_MAP[m.group(1)]
        delta = (target - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return _strip(t, m.group()), today + timedelta(days=delta)

    if m := re.search(r"星期([一二三四五六日天])", t):
        target = _WEEKDAY_MAP[m.group(1)]
        delta = (target - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return _strip(t, m.group()), today + timedelta(days=delta)

    # X月X日
    if m := re.search(r"(\d{1,2})月(\d{1,2})[日号]", t):
        month, day = int(m.group(1)), int(m.group(2))
        year = today.year
        try:
            due = date(year, month, day)
            if due < today:
                due = date(year + 1, month, day)
            return _strip(t, m.group()), due
        except ValueError:
            pass

    return t, None


def _strip(text: str, needle: str) -> str:
    """Remove a matched date phrase and tidy whitespace."""
    return re.sub(r"\s+", " ", text.replace(needle, "")).strip()


def analyze(text: str) -> Tuple[str, str, Optional[date]]:
    """Full pipeline: return (category, cleaned_text, due_date)."""
    cleaned, due = parse_date(text)
    category = classify(cleaned)
    return category, cleaned, due
