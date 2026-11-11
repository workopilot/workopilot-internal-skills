#!/usr/bin/env python3
import argparse
import sys
from urllib.parse import urlparse

from workopilot_http import (
    DEFAULT_BASE_URL,
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


def validate_menu(payload, action):
    if not isinstance(payload, dict):
        raise SystemExit("菜单配置必须是 JSON 对象")
    kind = payload.get("menuType", "iframe" if action == "create" else None)
    if kind not in (None, "ai-app", "iframe"):
        raise SystemExit("menuType 可选 ai-app 或 iframe")
    if action == "create" and not payload.get("title"):
        raise SystemExit("创建菜单需要 title")
    if kind == "iframe" and ("aiAppCode" in payload or "aiMenuPath" in payload):
        raise SystemExit("绑定 AI 应用页面请指定 menuType 为 ai-app")
    if kind == "ai-app" and "iframeUrl" in payload:
        raise SystemExit("AI 应用页面地址由后端生成，请移除 iframeUrl")
    if action == "create":
        required = ("aiAppCode", "aiMenuPath") if kind == "ai-app" else ("iframeUrl",)
        for key in required:
            if not isinstance(payload.get(key), str) or not payload[key].strip():
                raise SystemExit(f"创建 {kind} 菜单需要 {key}")


def print_menu_summary(payload):
    print("📝 菜单配置:")
    print(f"   标题: {payload.get('title') or '(未传，更新时保持原值)'}")
    print(f"   编码: {payload.get('menuKey') or '(未传，创建时由后端生成)'}")
    for key in ("menuType", "aiAppCode", "aiMenuPath", "iframeUrl", "displayMode"):
        if key in payload:
            print(f"   {key}: {payload[key]}")
    print(f"   图标: {payload.get('icon') or '(默认 lucide:file-text 或保持原值)'}")
    if payload.get("sort") is not None:
        print(f"   排序: {payload.get('sort')}")
    if payload.get("isEnabled") is not None:
        print(f"   启用: {'是' if payload.get('isEnabled') else '否'}")


def main():
    parser = add_common_args(argparse.ArgumentParser(description="配置数字员工的托管 AI 应用页面或第三方 iframe 菜单"))
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
    validate_menu(payload, args.action)
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
    require_success(result, "保存应用菜单")
    if not isinstance(result, dict) or result.get("code") != 200 or not isinstance(result.get("data"), dict):
        raise SystemExit("响应缺少成功状态或菜单对象，请在目标环境核对保存结果")
    data = result["data"]
    # Current .NET DTOs use PascalCase. Some deployments camel-case DTO fields.
    fields = {key[:1].lower() + key[1:]: value for key, value in data.items()}
    expected_type = payload.get("menuType")
    if "aiAppCode" in payload or "aiMenuPath" in payload:
        expected_type = "ai-app"
    if expected_type and fields.get("menuType") != expected_type:
        raise SystemExit("服务端返回的菜单类型与请求不一致，请核对目标环境的接口版本与已保存菜单")
    for key in ("aiAppCode", "aiMenuPath", "displayMode"):
        if key in payload and fields.get(key) != payload[key]:
            raise SystemExit(f"服务端返回的 {key} 与请求不一致，请核对已保存菜单")
    print(f"\n✅ 已保存菜单 {fields.get('menuKey')}（{fields.get('menuType')}）")
    if base_url.rstrip("/") == DEFAULT_BASE_URL:
        open_management_page("digital_employee", "查看数字员工应用菜单配置")

    print("\n📄 详细结果:")
    print_json(result)


if __name__ == "__main__":
    main()
