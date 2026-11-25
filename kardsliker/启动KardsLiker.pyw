"""双击启动 KardsLiker，不显示控制台窗口。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV_PYTHONW = HERE.parent / ".venv" / "Scripts" / "pythonw.exe"


def main() -> None:
    python = VENV_PYTHONW if VENV_PYTHONW.is_file() else Path(sys.executable).with_name("pythonw.exe")
    subprocess.Popen(
        [str(python), str(HERE / "app.py")],
        cwd=str(HERE),
        close_fds=True,
    )


if __name__ == "__main__":
    main()
