#!/usr/bin/env python3
import argparse
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


def main():
    parser = add_common_args(argparse.ArgumentParser(description="创建喔壳数字员工"))
    parser.add_argument("--no-reuse", action="store_true", help="即使 robotCode 已存在也继续创建")
    args = parser.parse_args()
    base_url, api_key = resolve_config(args)
    payload = load_json_config(args.config)

    print("\n" + "=" * 60)
    print("创建数字员工")
    print("=" * 60 + "\n")

    robot_code = payload.get("robotCode") or payload.get("RobotCode")
    robot_name = payload.get("robotName") or payload.get("RobotName") or robot_code

    # 检查是否已存在
    if robot_code and not args.no_reuse:
        print(f"🔍 检查数字员工是否已存在: {robot_code}")
        existing = request_json(base_url, api_key, "GET", f"/api/ai/robot/profile/{robot_code}")
        if isinstance(existing, dict) and existing.get("code") == 200 and existing.get("data"):
            employee = existing["data"]
            employee_id = employee.get("id")
            print(f"✅ 数字员工已存在，复用 (ID: {employee_id})")
            print(f"   名称: {employee.get('robotName')}")
            print(f"   编码: {employee.get('robotCode')}")

            # 打开管理页面
            open_management_page("digital_employee", "查看数字员工配置")

            print("\n📄 详细结果:")
            print_json({"reused": True, "data": employee})
            return

    print(f"📝 创建新的数字员工: {robot_name}")

    # 获取可用模型
    models = get_models(base_url, api_key)
    if not models:
        print("\n❌ 没有可用模型，无法创建数字员工")
        print("请在喔壳平台配置模型后再试")
        raise SystemExit(1)

    # 如果配置中没有指定对话模型 ID，自动选择（数字员工优先使用 GPT）
    if not payload.get("chatModelId") and not payload.get("ChatModelId"):
        model_id = select_model(
            models,
            purpose="对话",
            prefer_models=["gpt-4", "gpt4", "gpt-3.5", "gpt35", "qwen", "deepseek"]
        )
        payload["chatModelId"] = model_id
        print(f"   设置对话模型 ID: {model_id}")

    # 处理 iframe 嵌入配置
    enable_embed = payload.get("enableEmbed", 0)
    if enable_embed == 1:
        print("   ℹ️  已配置 iframe 嵌入功能")

        # 检查是否有 embedBaseUrl
        embed_base_url = payload.get("embedBaseUrl")
        if embed_base_url:
            print(f"      嵌入基础 URL: {embed_base_url}")

        # 检查允许的来源域名
        embed_allowed_origins = payload.get("embedAllowedOrigins", [])
        if embed_allowed_origins:
            print(f"      允许的来源域名: {', '.join(embed_allowed_origins)}")

        # 检查其他嵌入配置
        if payload.get("embedHideHeader"):
            print("      隐藏头部: 是")
        if payload.get("embedHideBranding"):
            print("      隐藏品牌标识: 是")
        if payload.get("embedMaxDailyCalls"):
            print(f"      每日最大调用次数: {payload.get('embedMaxDailyCalls')}")

    # 创建数字员工
    print(f"   ⏳ 正在创建...")
    result = request_json(base_url, api_key, "POST", "/api/ai/robot/external/create", payload)
    require_success(result, "创建数字员工")

    data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}
    employee_id = data.get("id")
    employee_robot_id = data.get("robotId")
    robot_code_final = data.get("robotCode")

    print(f"   ✅ 创建成功")
    print(f"      ID: {employee_id}")
    print(f"      RobotId: {employee_robot_id}")
    print(f"      RobotCode: {robot_code_final}")

    # 显示 iframe 嵌入信息
    if enable_embed == 1 and data.get("embedUrl"):
        print(f"\n   🔗 iframe 嵌入信息:")
        print(f"      嵌入 URL: {data.get('embedUrl')}")
        print(f"      API Key ID: {data.get('embedApiKeyId')}")
        if data.get("iframeCode"):
            print(f"\n   📋 iframe 代码:")
            print(f"      {data.get('iframeCode')}")

    print("\n" + "=" * 60)
    print("✅ 数字员工配置完成")
    print("=" * 60)

    # 打开管理页面
    open_management_page("digital_employee", "查看已创建的数字员工")

    print("\n📄 详细结果:")
    print_json({"reused": False, "result": result})


if __name__ == "__main__":
    main()
