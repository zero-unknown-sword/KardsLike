"""KardsLiker 本地服务与 API 骨架。

启动后会提供一个浏览器 IDE：

- 项目文件浏览
- Python 文件编辑与运行
- KL 语言检查
- 原版 KARDS DIY 卡面制作器
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kl import KLError, parse as parse_kl

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
GAME_ROOT = PROJECT_ROOT / "kardslike"
WEB_ROOT = HERE / "web"
FORGE_ROOT = HERE / "forge" / "kards_diy_web"
EDIT_ROOTS = (GAME_ROOT / "mods", GAME_ROOT)
MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
}


def safe_file(relative: str) -> Path | None:
    """把项目相对路径限制在允许编辑的目录内。"""
    path = (PROJECT_ROOT / relative).resolve()
    for root in EDIT_ROOTS:
        try:
            path.relative_to(root.resolve())
            return path if path.is_file() else None
        except ValueError:
            continue
    return None


class KardsLikerHandler(BaseHTTPRequestHandler):
    """KardsLiker HTTP 处理器。"""

    server_version = "KardsLiker/0.1"

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> object:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def serve_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", MIME.get(path.suffix.lower(), "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/files":
            files: list[str] = []
            for root in EDIT_ROOTS:
                if not root.is_dir():
                    continue
                for path in sorted(root.rglob("*")):
                    if path.is_file() and path.suffix in {".py", ".json", ".md", ".txt", ".kl"}:
                        files.append(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
            self.send_json({"ok": True, "files": files[:1000]})
            return
        if parsed.path == "/api/file":
            relative = parse_qs(parsed.query).get("path", [""])[0]
            path = safe_file(relative)
            if path is None:
                self.send_json({"ok": False, "error": "文件不在可编辑目录内"}, 404)
                return
            self.send_json({"ok": True, "path": relative, "content": path.read_text(encoding="utf-8")})
            return
        if parsed.path.startswith("/forge/"):
            relative = parsed.path[len("/forge/") :] or "index.html"
            self.serve_file((FORGE_ROOT / relative).resolve())
            return
        relative = parsed.path.lstrip("/") or "index.html"
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT in candidate.parents or candidate == WEB_ROOT:
            self.serve_file(candidate)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
        except (ValueError, UnicodeDecodeError) as exc:
            self.send_json({"ok": False, "error": f"JSON 无效: {exc}"}, 400)
            return
        if parsed.path == "/api/file":
            if not isinstance(payload, dict):
                self.send_json({"ok": False, "error": "请求体必须是对象"}, 400)
                return
            relative = payload.get("path")
            content = payload.get("content")
            if not isinstance(relative, str) or not isinstance(content, str):
                self.send_json({"ok": False, "error": "需要 path 和 content"}, 400)
                return
            path = safe_file(relative)
            if path is None:
                # 允许保存尚未存在的新文件
                candidate = (PROJECT_ROOT / relative).resolve()
                if any(str(candidate).startswith(str(root.resolve())) for root in EDIT_ROOTS):
                    candidate.parent.mkdir(parents=True, exist_ok=True)
                    path = candidate
            if path is None:
                self.send_json({"ok": False, "error": "文件不在可编辑目录内"}, 403)
                return
            path.write_text(content, encoding="utf-8")
            self.send_json({"ok": True, "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")})
            return
        if parsed.path == "/api/run":
            if not isinstance(payload, dict) or not isinstance(payload.get("path"), str):
                self.send_json({"ok": False, "error": "需要 path"}, 400)
                return
            path = safe_file(payload["path"])
            if path is None or path.suffix != ".py":
                self.send_json({"ok": False, "error": "只能运行可编辑目录内的 .py 文件"}, 403)
                return
            try:
                result = subprocess.run(
                    [sys.executable, str(path)],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.send_json(
                    {
                        "ok": True,
                        "returncode": result.returncode,
                        "stdout": result.stdout[-20000:],
                        "stderr": result.stderr[-20000:],
                    }
                )
            except subprocess.TimeoutExpired:
                self.send_json({"ok": False, "error": "运行超时（30 秒）"}, 408)
            except OSError as exc:
                self.send_json({"ok": False, "error": str(exc)}, 500)
            return
        if parsed.path == "/api/kl":
            if not isinstance(payload, dict) or not isinstance(payload.get("source"), str):
                self.send_json({"ok": False, "error": "需要 source"}, 400)
                return
            try:
                result = parse_kl(payload["source"])
            except KLError as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "ast": result})
            return
        self.send_json({"ok": False, "error": "未知 API"}, 404)


def main() -> None:
    parser = argparse.ArgumentParser(description="KardsLiker 本地 IDE")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not WEB_ROOT.is_dir():
        raise SystemExit(f"缺少 web 目录: {WEB_ROOT}")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), KardsLikerHandler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"KardsLiker: {url}")
    print(f"Card Forge: {url}forge/")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
