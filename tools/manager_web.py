#!/usr/bin/env python3
"""
本地网页入口：填写表单后直接生成经纪人 Skill。

用法：
    python3 tools/manager_web.py
    python3 tools/manager_web.py --port 8765 --base-dir ./managers
"""

from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from create_manager import generate_manager_skill


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"


class ManagerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json({"ok": True})
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/create":
            self._send_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0

        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "请求 JSON 格式不合法"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            skill_dir = generate_manager_skill(
                profile=payload["profile"],
                name=payload.get("name", "王牌经纪人"),
                slug=payload.get("slug") or None,
                style=payload.get("style", "professional"),
                base_dir=self.server.base_dir,
                knowledge_source="web-form",
            )
        except KeyError:
            self._send_json({"ok": False, "error": "缺少 profile 字段"}, status=HTTPStatus.BAD_REQUEST)
            return
        except ValueError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            self._send_json({"ok": False, "error": f"生成失败：{exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        meta_path = Path(skill_dir) / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self._send_json(
            {
                "ok": True,
                "skill_dir": str(skill_dir),
                "slug": meta["slug"],
                "name": meta["name"],
                "base_dir": str(self.server.base_dir),
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="经纪人.skills 本地网页入口")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8765, help="端口，默认 8765")
    parser.add_argument(
        "--base-dir",
        default=str(ROOT_DIR / "managers"),
        help="生成目录，默认仓库下的 managers/",
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), ManagerHandler)
    server.base_dir = Path(args.base_dir).expanduser()
    os.chdir(WEB_DIR)

    print(f"经纪人.skills Web 已启动：http://{args.host}:{args.port}")
    print(f"生成目录：{server.base_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
