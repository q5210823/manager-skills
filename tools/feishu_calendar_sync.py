#!/usr/bin/env python3
"""
飞书日程同步工具。

用途：
1. 在 OpenClaw / Skill 场景下，把经纪人阶段计划同步到飞书日历
2. 支持配置 App ID / App Secret
3. 支持列出日历和把阶段通告写入日程
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from create_manager import build_phase_event_plan, load_input


CONFIG_PATH = Path.home() / ".manager-skill" / "feishu_calendar_config.json"
BASE_URL = "https://open.feishu.cn/open-apis"
TIMEZONE = "Asia/Shanghai"
_TOKEN_CACHE: dict = {}


def require_requests():
    try:
        import requests as requests_lib
    except ImportError as exc:
        raise RuntimeError("请先安装 requests：pip3 install requests") from exc
    return requests_lib


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("未找到飞书日历配置，请先运行 `python3 tools/feishu_calendar_sync.py --setup`")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not config.get("app_id") or not config.get("app_secret"):
        raise RuntimeError(f"飞书配置不完整，请检查 {CONFIG_PATH}，至少需要 app_id 和 app_secret")
    return config


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def setup_config() -> None:
    print("=== 飞书日历同步配置 ===\n")
    print("请在飞书开放平台为应用开通至少以下权限：")
    print("  calendar:calendar:readonly")
    print("  calendar:event:write")
    print("  calendar:event:readonly")
    print()

    app_id = input("App ID (cli_xxx): ").strip()
    app_secret = input("App Secret: ").strip()
    calendar_id = input("默认 Calendar ID（可留空，自动选择主日历）: ").strip()

    config = {"app_id": app_id, "app_secret": app_secret}
    if calendar_id:
        config["calendar_id"] = calendar_id

    save_config(config)
    print(f"\n✅ 配置已保存到 {CONFIG_PATH}")


def get_tenant_token(config: dict) -> str:
    requests = require_requests()
    now = time.time()
    if _TOKEN_CACHE.get("token") and _TOKEN_CACHE.get("expire", 0) > now + 60:
        return _TOKEN_CACHE["token"]

    resp = requests.post(
        f"{BASE_URL}/auth/v3/tenant_access_token/internal",
        json={"app_id": config["app_id"], "app_secret": config["app_secret"]},
        timeout=10,
    )
    data = safe_json(resp)
    if data.get("code") != 0:
        raise RuntimeError(
            "获取 tenant_access_token 失败。"
            f" code={data.get('code')} msg={data.get('msg') or data.get('message')}。"
            " 请检查 app_id / app_secret 是否正确，或确认应用是否已创建。"
        )

    token = data["tenant_access_token"]
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expire"] = now + data.get("expire", 7200)
    return token


def api_get(path: str, config: dict, params: dict | None = None) -> dict:
    requests = require_requests()
    token = get_tenant_token(config)
    try:
        resp = requests.get(
            f"{BASE_URL}{path}",
            params=params or {},
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"调用飞书 GET 接口失败：{path}。请检查网络或稍后重试。原始错误：{exc}") from exc
    return safe_json(resp)


def api_post(path: str, config: dict, body: dict) -> dict:
    requests = require_requests()
    token = get_tenant_token(config)
    try:
        resp = requests.post(
            f"{BASE_URL}{path}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"调用飞书 POST 接口失败：{path}。请检查网络或稍后重试。原始错误：{exc}") from exc
    return safe_json(resp)


def safe_json(resp) -> dict:
    try:
        return resp.json()
    except Exception as exc:
        snippet = resp.text[:300] if hasattr(resp, "text") else ""
        raise RuntimeError(f"飞书返回了不可解析的响应。status={getattr(resp, 'status_code', 'unknown')} body={snippet}") from exc


def list_calendars(config: dict) -> list[dict]:
    data = api_get("/calendar/v4/calendars", config)
    if data.get("code") != 0:
        raise RuntimeError(format_feishu_error("获取日历列表失败", data))

    payload = data.get("data", {})
    calendars = payload.get("items") or payload.get("calendar_list") or payload.get("calendars") or []
    return calendars


def resolve_calendar_id(config: dict) -> str:
    if config.get("calendar_id"):
        return config["calendar_id"]

    calendars = list_calendars(config)
    if not calendars:
        raise RuntimeError("未找到可用日历。请确认账号下已有飞书日历，或在配置中手动填写 calendar_id")

    for calendar in calendars:
        if calendar.get("is_primary") or calendar.get("primary"):
            return calendar.get("calendar_id") or calendar.get("id")

    return calendars[0].get("calendar_id") or calendars[0].get("id")


def create_event(config: dict, calendar_id: str, event: dict) -> dict:
    payload = {
        "summary": event["title"],
        "description": event["description"],
        "start_time": {
            "timestamp": str(int(event["start"].timestamp())),
            "timezone": TIMEZONE,
        },
        "end_time": {
            "timestamp": str(int(event["end"].timestamp())),
            "timezone": TIMEZONE,
        },
    }
    data = api_post(f"/calendar/v4/calendars/{calendar_id}/events", config, payload)
    if data.get("code") != 0:
        raise RuntimeError(format_feishu_error("创建日程失败", data, calendar_id=calendar_id, event_title=event["title"]))
    return data


def format_feishu_error(prefix: str, data: dict, calendar_id: str | None = None, event_title: str | None = None) -> str:
    code = data.get("code")
    msg = data.get("msg") or data.get("message") or "未知错误"
    detail = [f"{prefix}。code={code} msg={msg}"]

    if calendar_id:
        detail.append(f"calendar_id={calendar_id}")
    if event_title:
        detail.append(f"title={event_title}")

    if "permission" in msg.lower() or code in {99991663, 99991661}:
        detail.append("请检查应用是否开通了 calendar:calendar:readonly / calendar:event:write 权限，并确认账号对该日历有权限。")
    elif "tenant_access_token" in msg.lower() or code in {99991671, 99991668}:
        detail.append("请检查 app_id / app_secret 是否正确，以及飞书应用是否可用。")
    elif "calendar" in msg.lower() and "not found" in msg.lower():
        detail.append("请检查 calendar_id 是否正确，可先运行 --list-calendars 查看可用日历。")
    else:
        detail.append("可先运行 --list-calendars 验证日历权限，或检查飞书开放平台权限配置。")

    return " ".join(detail)


def sync_profile(profile_path: Path, manager_name: str, config: dict, days_limit: int | None = None) -> list[dict]:
    profile = load_input(profile_path)
    calendar_id = resolve_calendar_id(config)
    events = build_phase_event_plan(profile, manager_name)
    if days_limit is not None and days_limit > 0:
        events = events[:days_limit]

    created = []
    for event in events:
        result = create_event(config, calendar_id, event)
        created.append(
            {
                "title": event["title"],
                "start": event["start"].isoformat(),
                "end": event["end"].isoformat(),
                "event_id": result.get("data", {}).get("event", {}).get("event_id")
                or result.get("data", {}).get("event_id"),
            }
        )
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="飞书日程同步工具")
    parser.add_argument("--setup", action="store_true", help="初始化飞书日历配置")
    parser.add_argument("--list-calendars", action="store_true", help="列出当前账号可用日历")
    parser.add_argument("--input", help="艺人档案 JSON 路径")
    parser.add_argument("--manager-name", default="王牌经纪人", help="经纪人名称")
    parser.add_argument("--days-limit", type=int, help="仅同步前 N 个日程块，便于测试")
    args = parser.parse_args()

    try:
        if args.setup:
            setup_config()
            return 0

        config = load_config()

        if args.list_calendars:
            calendars = list_calendars(config)
            if not calendars:
                print("未找到可用日历")
                return 0
            print("可用日历：")
            for item in calendars:
                calendar_id = item.get("calendar_id") or item.get("id")
                summary = item.get("summary") or item.get("name") or "未命名日历"
                print(f"- {summary} ({calendar_id})")
            return 0

        if not args.input:
            print("错误：需要 --input，或使用 --setup / --list-calendars", file=sys.stderr)
            return 1

        created = sync_profile(Path(args.input).expanduser(), args.manager_name, config, args.days_limit)
        print(f"✅ 已同步 {len(created)} 个飞书日程")
        for item in created[:10]:
            print(f"- {item['title']} | {item['start']}")
        return 0
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        print("建议：先执行 `--setup` 配置飞书，再执行 `--list-calendars` 验证权限，最后再跑同步。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
