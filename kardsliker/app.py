"""KardsLiker 原生 GUI 入口。

启动本地 HTTP 服务后，用 Qt WebEngine 创建桌面窗口。
用户只会看到一个窗口，不会出现浏览器地址栏或 CMD 窗口。
"""
from __future__ import annotations

import argparse
import sys
import threading
from http.server import ThreadingHTTPServer

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow

from server import KardsLikerHandler


class KardsLikerWindow(QMainWindow):
    """承载 KardsLiker 前端的原生窗口。"""

    def __init__(self, url: str) -> None:
        super().__init__()
        self.setWindowTitle("KardsLiker")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("background: #131715;")

        view = QWebEngineView(self)
        view.setUrl(QUrl(url))
        view.page().setBackgroundColor(QColor("#131715"))
        self.setCentralWidget(view)

    def closeEvent(self, event: object) -> None:
        QApplication.quit()
        super().closeEvent(event)  # type: ignore[arg-type]


def create_server(port: int) -> ThreadingHTTPServer:
    """创建只监听本机的后台服务。"""
    server = ThreadingHTTPServer(("127.0.0.1", port), KardsLikerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="KardsLiker 原生窗口")
    parser.add_argument("--port", type=int, default=0, help="0 表示自动选择空闲端口")
    args = parser.parse_args()

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    server = create_server(args.port)
    port = server.server_address[1]
    window = KardsLikerWindow(f"http://127.0.0.1:{port}/")
    window.show()
    try:
        app.exec()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
