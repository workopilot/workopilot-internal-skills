#!/usr/bin/env python3
import argparse
import sys
from urllib.parse import urlparse

from workopilot_http import add_common_args, load_json_config, print_json, request_json, require_success, resolve_config


def warn_if_local_url(url):
    if not url:
        return
    parsed = urlparse(url)
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        print(
            "提醒：当前 iframe 卡片 URL 是本地测试地址，发布后请更新为正式可访问地址。",
            file=sys.stderr,
        )


def main():
    parser = add_common_args(argparse.ArgumentParser(description="注册喔壳 iframe 技能卡片"))
    args = parser.parse_args()
    base_url, api_key = resolve_config(args)
    payload = load_json_config(args.config)
    warn_if_local_url(payload.get("url") or payload.get("drawerUrl"))
    if not payload.get("triggerPrompt"):
        print("提醒：建议配置 triggerPrompt，说明数字员工何时调用 showCard 打开卡片。", file=sys.stderr)
    result = request_json(base_url, api_key, "POST", "/api/ai/skill-registry/external/iframe-card", payload)
    require_success(result, "注册 iframe 技能卡片")
    print_json(result)


if __name__ == "__main__":
    main()
