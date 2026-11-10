"""Rhythm menu-bar app (rumps). Falls back to CLI if rumps is unavailable."""

from __future__ import annotations

from datetime import datetime

from . import brief, notifier, recorder, storage


def run_app() -> None:
    try:
        import rumps
    except ImportError:
        print("rumps not installed. Run: pip install rumps")
        print('Or use the CLI: python -m rhythm add "..."')
        return

    class RhythmApp(rumps.App):
        def __init__(self):
            super().__init__("♪", quit_button="Quit Rhythm")
            self.menu = [
                "记一条",
                "今天的便条",
                None,
                "晨间简报",
                "午间检查",
                "傍晚复盘",
            ]

        @rumps.clicked("记一条")
        def add_note(self, _):
            window = rumps.Window(
                title="记一条",
                message="想到什么写什么，比如：周五交稿 / Python 学 20 分钟",
                default_text="",
                ok="记下",
                cancel="取消",
                dimensions=(320, 80),
            )
            response = window.run()
            if response.clicked and response.text.strip():
                note = recorder.add(response.text.strip())
                rumps.notification(
                    "Rhythm",
                    f"已记下 [{note.category}]",
                    note.text,
                )

        @rumps.clicked("今天的便条")
        def show_today(self, _):
            notes = storage.load_day(datetime.now().date())
            if not notes:
                msg = "今天还没记什么。"
            else:
                msg = "\n".join(
                    f"{'✓' if n.done else '•'} [{n.category}] {n.text}" for n in notes
                )
            rumps.Window(title="今天", message=msg, dimensions=(360, 240)).run()

        @rumps.clicked("晨间简报")
        def morning(self, _):
            title, body = brief.morning_brief()
            notifier.notify(title, body)
            rumps.Window(title=title, message=body, dimensions=(380, 280)).run()

        @rumps.clicked("午间检查")
        def noon(self, _):
            title, body = brief.noon_brief()
            notifier.notify(title, body)
            rumps.Window(title=title, message=body, dimensions=(380, 200)).run()

        @rumps.clicked("傍晚复盘")
        def evening(self, _):
            title, body = brief.evening_brief()
            notifier.notify(title, body)
            rumps.Window(title=title, message=body, dimensions=(380, 240)).run()

    RhythmApp().run()
