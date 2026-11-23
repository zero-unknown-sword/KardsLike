"""本地启动 KARDS Card Forge 静态副本"""
from __future__ import annotations

import argparse
import http.server
import os
import socket
import socketserver
import subprocess
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parent / "card_forge_web"
PREFIX = "/KARDS-DIY-GENERATOR/"
DEFAULT_PORT = 8765


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

    def log_message(self, format: str, *args: object) -> None:
        """不刷控制台访问日志。"""
        return


class ForgeServer:
    """后台 HTTP 服务。"""

    def __init__(self, port: int) -> None:
        self.port = port
        self.httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
        self.httpd.daemon_threads = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> None:
        """启动服务线程。"""
        self.thread.start()

    def stop(self) -> None:
        """停止服务。"""
        self.httpd.shutdown()
        self.httpd.server_close()


def _browser_candidates() -> list[Path]:
    """寻找本机 Edge / Chrome 可执行文件。"""
    roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("LocalAppData", ""),
    ]
    candidates: list[Path] = []
    for root in roots:
        if not root:
            continue
        base = Path(root)
        candidates.extend(
            [
                base / "Microsoft" / "Edge" / "Application" / "msedge.exe",
                base / "Google" / "Chrome" / "Application" / "chrome.exe",
            ]
        )
    return candidates


def open_editor(url: str) -> bool:
    """优先用 Edge/Chrome 的应用窗口打开编辑器。"""
    for browser in _browser_candidates():
        if browser.is_file():
            try:
                subprocess.Popen([str(browser), f"--app={url}"])
                return True
            except OSError:
                continue
    try:
        if webbrowser.open(url):
            return True
    except OSError:
        pass
    try:
        os.startfile(url)
        return True
    except OSError:
        return False


class Launcher:
    """可见的启动器窗口。"""

    def __init__(self, server: ForgeServer, url: str) -> None:
        self.server = server
        self.url = url
        self.root = tk.Tk()
        self.root.title("KARDS Card Forge")
        self.root.geometry("460x180")
        self.root.resizable(False, False)

        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text="KARDS Card Forge 本地版",
            font=("Microsoft YaHei UI", 14, "bold"),
        ).pack(anchor="w")
        ttk.Label(frame, text=url, foreground="#555555").pack(anchor="w", pady=(8, 14))
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="打开编辑器", command=lambda: open_editor(self.url)).pack(side="left")
        ttk.Button(buttons, text="复制地址", command=self._copy).pack(side="left", padx=8)
        ttk.Button(buttons, text="退出", command=self._quit).pack(side="right")
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.after(250, lambda: open_editor(self.url))

    def _copy(self) -> None:
        """复制地址。"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url)
        messagebox.showinfo("已复制", self.url)

    def _quit(self) -> None:
        """关闭窗口并停止服务。"""
        self.server.stop()
        self.root.destroy()

    def run(self) -> None:
        """显示窗口。"""
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="本地启动 KARDS Card Forge")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-window", action="store_true", help="不显示启动器窗口")
    args = parser.parse_args()

    if not (ROOT / "KARDS-DIY-GENERATOR" / "index.html").is_file():
        raise SystemExit(f"缺少静态副本: {ROOT}")

    port = args.port
    try:
        server = ForgeServer(port)
    except OSError:
        port += 1
        server = ForgeServer(port)

    url = f"http://127.0.0.1:{port}{PREFIX}"
    server.start()
    print(f"Card Forge: {url}")
    print("如果没有自动打开浏览器，请使用启动器窗口中的『打开编辑器』。")

    if args.no_window:
        try:
            server.thread.join()
        except KeyboardInterrupt:
            server.stop()
        return

    Launcher(server, url).run()


if __name__ == "__main__":
    main()
