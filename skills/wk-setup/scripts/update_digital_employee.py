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
    first_model_value,
)


def main():
    parser = add_common_args(argparse.ArgumentParser(description="更新喔壳数字员工"))
    parser.add_argument("--employee-id", type=int, required=True, help="数字员工 ID")
    args = parser.parse_args()
    base_url, api_key = resolve_config(args)
    payload = load_json_config(args.config)
    employee_id = args.employee_id

    print("\n" + "=" * 60)
    print("更新数字员工")
    print("=" * 60 + "\n")

    # 先获取现有数字员工信息
    print(f"🔍 查询数字员工信息 (ID: {employee_id})")
    existing = request_json(base_url, api_key, "GET", f"/api/ai/robot/profile/by-id/{employee_id}")

    if not isinstance(existing, dict) or existing.get("code") != 200 or not existing.get("data"):
        print(f"❌ 未找到 ID 为 {employee_id} 的数字员工")
        raise SystemExit(1)

    current_data = existing["data"]
    print(f"   名称: {current_data.get('robotName')}")
    print(f"   编码: {current_data.get('robotCode')}")
    print(f"   状态: {'启用' if current_data.get('isActive') == 1 else '停用'}")

    # 如果 payload 中指定了新的 chatModelId，验证模型是否可用
    new_model_id = payload.get("chatModelId") or payload.get("ChatModelId")
    if new_model_id:
        models = get_models(base_url, api_key)
        found = False
        for model in models:
            model_id = first_model_value(model, "aiModelId", "AiModelId", "modelId", "ModelId", "id", "Id")
            if model_id == new_model_id:
                model_name = first_model_value(model, "modelName", "ModelName") or "未命名"
                print(f"   ✅ 将使用模型: {model_name} (ID: {new_model_id})")
                found = True
                break

        if not found:
            print(f"   ⚠️  警告: 指定的模型 ID {new_model_id} 不在可用模型列表中")

    # 打印将要更新的字段
    print("\n📝 更新的字段:")
    update_fields = []
    for key, value in payload.items():
        # 排除空值
        if value is None or value == "":
            continue

        # 获取当前值
        current_value = current_data.get(key)

        # 简单显示
        if key == "quickQuestions":
            update_fields.append(f"   - {key}: {len(value)} 条")
        elif key in ["systemPrompt", "welcomeMessage", "description"] and value:
            # 对于长文本只显示前50个字符
            display_value = value[:50] + "..." if len(str(value)) > 50 else value
            update_fields.append(f"   - {key}: {display_value}")
        else:
            update_fields.append(f"   - {key}: {value}")

    if update_fields:
        for field_info in update_fields:
            print(field_info)
    else:
        print("   (无更新内容)")

    # 执行更新
    print(f"\n   ⏳ 正在更新...")
    result = request_json(base_url, api_key, "PUT", f"/api/ai/robot/external/{employee_id}", payload)
    require_success(result, "更新数字员工")

    data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}

    print(f"   ✅ 更新成功")
    print(f"      ID: {data.get('id')}")
    print(f"      名称: {data.get('robotName')}")
    print(f"      编码: {data.get('robotCode')}")

    print("\n" + "=" * 60)
    print("✅ 数字员工更新完成")
    print("=" * 60)

    # 打开管理页面
    open_management_page("digital_employee", "查看已更新的数字员工")

    print("\n📄 详细结果:")
    print_json({"updated": True, "result": result})


if __name__ == "__main__":
    main()
