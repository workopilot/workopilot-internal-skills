#!/usr/bin/env python3
import argparse
import sys
from urllib.parse import urlparse

from workopilot_http import (
    add_common_args,
    load_json_config,
    open_management_page,
    print_json,
    request_json,
    require_success,
    resolve_config,
)


def normalize_icon(payload):
    icon = payload.get("icon")
    if isinstance(icon, str) and icon.strip() and ":" not in icon:
        payload["icon"] = f"lucide:{icon.strip()}"


def warn_if_local_url(url):
    if not url:
        return
    parsed = urlparse(url)
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        print(
            "提醒：当前应用菜单 iframeUrl 是本地测试地址，发布后请用 update 动作更新为正式 HTTPS 地址。",
            file=sys.stderr,
        )


def print_menu_summary(payload):
    print("📝 菜单配置:")
    print(f"   标题: {payload.get('title') or '(未传，更新时保持原值)'}")
    print(f"   编码: {payload.get('menuKey') or '(未传，创建时由后端生成)'}")
    print(f"   地址: {payload.get('iframeUrl') or '(未传，更新时保持原值)'}")
    print(f"   图标: {payload.get('icon') or '(默认 lucide:file-text 或保持原值)'}")
    if payload.get("sort") is not None:
        print(f"   排序: {payload.get('sort')}")
    if payload.get("isEnabled") is not None:
        print(f"   启用: {'是' if payload.get('isEnabled') else '否'}")


def main():
    parser = add_common_args(argparse.ArgumentParser(description="配置喔壳数字员工应用菜单 iframe"))
    parser.add_argument("--employee-id", type=int, required=True, help="数字员工 ID")
    parser.add_argument(
        "--action",
        choices=["create", "update"],
        default="create",
        help="配置动作：create 新增菜单，update 更新已有菜单",
    )
    parser.add_argument("--menu-key", default=None, help="更新时要定位的菜单编码；不传则使用配置文件中的 menuKey")
    args = parser.parse_args()

    base_url, api_key = resolve_config(args)
    payload = load_json_config(args.config)
    normalize_icon(payload)
    warn_if_local_url(payload.get("iframeUrl"))

    print("\n" + "=" * 60)
    print("配置数字员工应用菜单")
    print("=" * 60 + "\n")
    print(f"数字员工 ID: {args.employee_id}")
    print(f"动作: {'新增菜单' if args.action == 'create' else '更新菜单'}")
    print_menu_summary(payload)

    if args.action == "create":
        result = request_json(
            base_url,
            api_key,
            "POST",
            f"/api/ai/robot/external/{args.employee_id}/app-menu",
            payload,
        )
        require_success(result, "创建应用菜单")
        print("\n✅ 应用菜单创建成功")
    else:
        menu_key = args.menu_key or payload.get("menuKey")
        if not menu_key:
            raise SystemExit("更新应用菜单需要 --menu-key，或在配置文件中提供 menuKey")
        result = request_json(
            base_url,
            api_key,
            "PUT",
            f"/api/ai/robot/external/{args.employee_id}/app-menu/{menu_key}",
            payload,
        )
        require_success(result, "更新应用菜单")
        print("\n✅ 应用菜单更新成功")

    data = result.get("data", {}) if isinstance(result, dict) and isinstance(result.get("data"), dict) else {}
    if data:
        print(f"   菜单编码: {data.get('menuKey')}")
        print(f"   菜单标题: {data.get('title')}")
        print(f"   iframeUrl: {data.get('iframeUrl')}")

    open_management_page("digital_employee", "查看数字员工应用菜单配置")

    print("\n📄 详细结果:")
    print_json(result)


if __name__ == "__main__":
    main()
