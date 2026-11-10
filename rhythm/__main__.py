"""Rhythm CLI — `python -m rhythm <command>`."""

from __future__ import annotations

import sys
from datetime import date

from . import brief, config, notifier, recorder, storage


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("♪ Rhythm — your personal rhythm assistant")
        print()
        print("Usage:")
        print('  python -m rhythm add <text>     随手记一条')
        print('  python -m rhythm today          看今天的便条')
        print('  python -m rhythm morning       晨间简报（完整）')
        print('  python -m rhythm noon          午间检查（完整）')
        print('  python -m rhythm evening       傍晚复盘（完整）')
        print('  python -m rhythm daemon        后台运行，到点自动弹通知')
        print('  python -m rhythm config        查看当前设置')
        print('  python -m rhythm config <key> <value>   改设置')
        return

    cmd, rest = args[0], args[1:]

    if cmd == "add":
        text = " ".join(rest)
        if not text:
            print("Usage: rhythm add <text>")
            sys.exit(1)
        note = recorder.add(text)
        print(f"✓ [{note.category}] {note.text}" + (f" (due {note.due})" if note.due else ""))

    elif cmd == "today":
        notes = storage.load_day(date.today())
        if not notes:
            print("今天还没记什么。")
        for n in notes:
            flag = "✓" if n.done else " "
            due = f" ⏰{n.due}" if n.due else ""
            print(f"[{flag}] [{n.timestamp:%H:%M}] ({n.category}) {n.text}{due}")

    elif cmd == "morning":
        title, body = brief.morning_brief()
        print(f"== {title} ==\n{body}\n")
        t, m = brief.morning_notification()
        notifier.notify(t, m)

    elif cmd == "noon":
        title, body = brief.noon_brief()
        print(f"== {title} ==\n{body}\n")
        t, m = brief.noon_notification()
        notifier.notify(t, m)

    elif cmd == "evening":
        title, body = brief.evening_brief()
        print(f"== {title} ==\n{body}\n")
        t, m = brief.evening_notification()
        notifier.notify(t, m)

    elif cmd == "daemon":
        from .daemon import run
        run()

    elif cmd == "config":
        if len(rest) == 0:
            cfg = config.load()
            print("当前设置：")
            for k, v in cfg.items():
                print(f"  {k} = {v}")
        elif len(rest) == 2:
            key, value = rest
            config.set_key(key, value)
            print(f"✓ {key} = {value}")
        else:
            print("Usage: rhythm config [key] [value]")

    elif cmd == "start":
        from .app import run_app
        run_app()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
