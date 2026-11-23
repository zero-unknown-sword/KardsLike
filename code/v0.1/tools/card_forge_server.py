"""本地启动 KARDS Card Forge 静态副本"""
from __future__ import annotations

import argparse
import http.server
import socket
import socketserver
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "card_forge_web"
PREFIX = "/KARDS-DIY-GENERATOR/"


class Handler(http.server.SimpleHTTPRequestHandler):
    """把静态副本按原站路径提供。"""

    def __init__(
        self,
        request: socket.socket,
        client_address: tuple[str, int],
        server: socketserver.BaseServer,
    ) -> None:
        super().__init__(
            request,
            client_address,
            server,
            directory=str(ROOT),
        )

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", PREFIX)
            self.end_headers()
            return
        super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="本地启动 KARDS Card Forge")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not (ROOT / "KARDS-DIY-GENERATOR" / "index.html").is_file():
        raise SystemExit(f"缺少静态副本: {ROOT}")

    url = f"http://127.0.0.1:{args.port}{PREFIX}"
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), Handler) as server:
        server.daemon_threads = True
        print(f"Card Forge: {url}")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("已停止")


if __name__ == "__main__":
    main()
