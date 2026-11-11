#!/usr/bin/env python3
import argparse
import sys
from workopilot_http import (
    add_common_args,
    get_models,
    load_json_config,
    open_management_page,
    print_json,
    request_json,
    require_success,
    resolve_config,
    select_model,
)


def warn_prompt_placeholders(payload):
    prompt = payload.get("systemPrompt") or payload.get("SystemPrompt") or ""
    inputs = payload.get("inputs") or payload.get("Inputs") or []
    missing = []
    for item in inputs:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("Name")
        if not name:
            continue
        placeholder = "{{" + str(name) + "}}"
        if placeholder not in prompt:
            missing.append(placeholder)
    if missing:
        print(
            "⚠️  警告：systemPrompt 未引用部分 inputs 占位符："
            + ", ".join(missing)
            + "。请确认提示词是否已按 {{input_name}} 使用入参。",
            file=sys.stderr,
        )


def main():
    parser = add_common_args(argparse.ArgumentParser(description="创建喔壳 AI 服务"))
    parser.add_argument("--no-reuse", action="store_true", help="即使 serviceCode 已存在也继续创建")
    args = parser.parse_args()
    base_url, api_key = resolve_config(args)
    payload = load_json_config(args.config)

    print("\n" + "=" * 60)
    print("创建 AI 服务")
    print("=" * 60 + "\n")

    warn_prompt_placeholders(payload)

    service_code = payload.get("serviceCode") or payload.get("ServiceCode")
    service_name = payload.get("serviceName") or payload.get("ServiceName") or service_code

    # 检查是否已存在
    if service_code and not args.no_reuse:
        print(f"🔍 检查 AI 服务是否已存在: {service_code}")
        existing = request_json(
            base_url,
            api_key,
            "POST",
            "/api/aiagent/external/list",
            {"serviceCode": service_code, "pageNum": 1, "pageSize": 1},
        )
        require_success(existing, "查询 AI 服务")
        rows = existing.get("rows") or []
        if rows:
            service = rows[0]
            service_id = service.get("id")
            print(f"✅ AI 服务已存在，复用 (ID: {service_id})")
            print(f"   名称: {service.get('serviceName')}")
            print(f"   编码: {service.get('serviceCode')}")

            # 打开管理页面
            open_management_page("ai_service", "查看 AI 服务管理")

            print("\n📄 详细结果:")
            print_json({"reused": True, "data": service})
            return

    print(f"📝 创建新的 AI 服务: {service_name}")

    # 获取可用模型
    models = get_models(base_url, api_key)
    if not models:
        print("\n❌ 没有可用模型，无法创建 AI 服务")
        print("请在喔壳平台配置模型后再试")
        raise SystemExit(1)

    # 如果配置中没有指定模型 ID，自动选择（AI 服务优先使用 GPT）
    if not payload.get("modelId") and not payload.get("ModelId"):
        model_id = select_model(
            models,
            purpose="AI 服务",
            prefer_models=["gpt-4", "gpt4", "gpt-3.5", "gpt35", "qwen", "deepseek"]
        )
        payload["modelId"] = model_id
        print(f"   设置模型 ID: {model_id}")

    # 创建服务
    print(f"   ⏳ 正在创建...")
    result = request_json(base_url, api_key, "POST", "/api/aiagent/external/create", payload)
    require_success(result, "创建 AI 服务")

    service_id = result.get("data", {}).get("id") if isinstance(result.get("data"), dict) else None

    print(f"   ✅ 创建成功 (ID: {service_id})")

    print("\n" + "=" * 60)
    print("✅ AI 服务配置完成")
    print("=" * 60)

    # 打开管理页面
    open_management_page("ai_service", "查看已创建的 AI 服务")

    print("\n📄 详细结果:")
    print_json({"reused": False, "result": result})


if __name__ == "__main__":
    main()
