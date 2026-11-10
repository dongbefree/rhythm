"""Cross-platform desktop notifications — zero extra dependencies."""

from __future__ import annotations

import json
import platform
import shlex
import subprocess


def _notify_macos(title: str, message: str, subtitle: str = "") -> None:
    parts = [f"display notification {shlex.quote(message)}"]
    parts.append(f"with title {shlex.quote(title)}")
    if subtitle:
        parts.append(f"subtitle {shlex.quote(subtitle)}")
    script = ", ".join(parts)
    subprocess.run(["osascript", "-e", script], check=False,
                   capture_output=True, timeout=5)


def _notify_linux(title: str, message: str, subtitle: str = "") -> None:
    # Try notify-send (most desktop environments)
    body = f"{subtitle}\n{message}" if subtitle else message
    subprocess.run(
        ["notify-send", "--app-name=Rhythm", title, body],
        check=False, capture_output=True, timeout=5,
    )


def _notify_windows(title: str, message: str, subtitle: str = "") -> None:
    # Use PowerShell's System.Windows.Forms.NotifyIcon to show a balloon tip.
    #
    # IMPORTANT: instead of interpolating title/message into the PowerShell
    # source string (which is a code-injection risk when the note text
    # contains quotes or PowerShell metacharacters), we pass the strings
    # safely as JSON-encoded values and decode them inside PowerShell.
    body = f"{subtitle}\n{message}" if subtitle else message
    payload = json.dumps({"title": title, "body": body}, ensure_ascii=False)
    ps_cmd = (
        "$p = '" + payload.replace("'", "''") + "' | ConvertFrom-Json;"
        '[reflection.assembly]::loadwithpartialname("System.Windows.Forms") | Out-Null;'
        "$n = New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon = [System.Drawing.SystemIcons]::Information;"
        "$n.BalloonTipTitle = $p.title;"
        "$n.BalloonTipText = $p.body;"
        "$n.Visible = $true;"
        "$n.ShowBalloonTip(5000)"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            check=False, capture_output=True, timeout=5,
        )
    except Exception:
        pass


def notify(title: str, message: str, subtitle: str = "") -> None:
    """Send a native desktop notification, best-effort."""
    system = platform.system()
    try:
        if system == "Darwin":
            _notify_macos(title, message, subtitle)
        elif system == "Linux":
            _notify_linux(title, message, subtitle)
        elif system == "Windows":
            _notify_windows(title, message, subtitle)
        else:
            # Unknown platform — just print
            print(f"[{title}] {message}")
    except Exception:
        pass  # notifications are best-effort
