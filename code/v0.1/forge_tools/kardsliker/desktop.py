"""以本地窗口方式启动 KardsLiker。

优先使用 Edge 的 app 模式，窗口不带地址栏；
没有 Edge 时退回系统默认浏览器。
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

from server import KardsLikerHandler


EDGE_PATHS = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


def find_edge() -> Path | None:
    for path in EDGE_PATHS:
        if path.is_file():
            return path
    return None


def open_window(url: str) -> subprocess.Popen[bytes] | None:
    edge = find_edge()
    if edge is None:
        webbrowser.open(url)
        return None
    profile = Path(tempfile.gettempdir()) / "kardsliker-edge"
    return subprocess.Popen(
        [
            str(edge),
            f"--app={url}",
            f"--user-data-dir={profile}",
            "--window-size=1440,900",
            "--disable-features=Translate",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="KardsLiker 桌面窗口")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--no-window", action="store_true")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), KardsLikerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{args.port}/"
    print(f"KardsLiker: {url}")
    print("关闭窗口后按 Ctrl+C 结束服务")

    process: subprocess.Popen[bytes] | None = None
    if not args.no_window:
        process = open_window(url)
    try:
        if process is None:
            while True:
                time.sleep(0.5)
        else:
            while process.poll() is None:
                time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
