#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

# 默认使用生产环境
# 生产环境: https://agent.workopilot.com/net-api
# 测试环境: https://agenttest.workopilot.com/net-api
DEFAULT_BASE_URL = "https://agent.workopilot.com/net-api"

# Web 管理页面地址
WEB_URLS = {
    "api_key": "https://agent.workopilot.com/smart/api-key",
    "attachment_config": "https://agent.workopilot.com/agent/platform/config",
    "ai_service": "https://agent.workopilot.com/smart/service-mgmt",
    "digital_employee": "https://agent.workopilot.com/ai-employee/agent-config",
}


def open_browser(url):
    """尝试在浏览器中打开 URL"""
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def load_env_file(path):
    values = {}
    if not path:
        return values
    p = Path(path)
    if not p.exists():
        return values
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def find_env_file(explicit=None):
    if explicit:
        return explicit
    cwd = Path.cwd()
    for candidate in (".env.workopilot", ".env.local"):
        p = cwd / candidate
        if p.exists():
            return str(p)
    return None


def add_common_args(parser):
    parser.add_argument("--base-url", default=None, help="喔壳 baseUrl")
    parser.add_argument("--api-key", default=None, help="喔壳 APIKEY")
    parser.add_argument("--env-file", default=None, help=".env.workopilot 文件路径")
    parser.add_argument("--config", default=None, help="JSON 配置文件路径")
    return parser


def resolve_config(args):
    env_file = find_env_file(getattr(args, "env_file", None))
    file_values = load_env_file(env_file)
    base_url = (
        getattr(args, "base_url", None)
        or os.environ.get("WORKOPILOT_BASE_URL")
        or file_values.get("WORKOPILOT_BASE_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")
    api_key = (
        getattr(args, "api_key", None)
        or os.environ.get("WORKOPILOT_API_KEY")
        or file_values.get("WORKOPILOT_API_KEY")
    )
    if not api_key or api_key == "replace_with_your_api_key":
        print("\n❌ 缺少 WORKOPILOT_API_KEY")
        print("\n请先创建 API Key：")
        print(f"   🔗 {WEB_URLS['api_key']}")

        # 尝试打开浏览器
        if open_browser(WEB_URLS['api_key']):
            print("   ✅ 已在浏览器中打开")

        print("\n创建后，请通过以下方式之一配置：")
        print("   1. 在项目根目录创建 .env.workopilot 文件")
        print("   2. 设置环境变量 WORKOPILOT_API_KEY")
        print("   3. 使用 --api-key 参数传入")
        print("\n⚠️  不要把真实 APIKEY 提交到 Git 仓库中！")
        raise SystemExit(1)
    return base_url, api_key


def load_json_config(path):
    if not path:
        raise SystemExit("缺少 --config 配置文件路径")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def request_json(base_url, api_key, method, path, body=None, query=None):
    url = base_url + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = None
    headers = {"API-KEY": api_key}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8")
            if not text:
                return None
            return json.loads(text)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP 请求失败：{exc.code} {method} {url}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"请求失败：{method} {url}\n{exc}") from exc


def print_json(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def require_success(result, label):
    if isinstance(result, dict) and result.get("code") not in (None, 200):
        raise SystemExit(f"{label}失败：\n{json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def get_models(base_url, api_key):
    """获取租户下的所有模型"""
    print("获取可用模型列表...")
    result = request_json(base_url, api_key, "GET", "/api/aiagent/external/models")
    require_success(result, "获取模型列表")

    models = result.get("rows") or result.get("data") or []
    if not models:
        print("未找到可用模型")
        return []

    print(f"找到 {len(models)} 个可用模型：")
    for model in models:
        model_id = first_model_value(model, "aiModelId", "AiModelId", "modelId", "ModelId", "id", "Id")
        model_name = first_model_value(model, "modelName", "ModelName") or "未命名"
        model_code = first_model_value(model, "modelCode", "ModelCode") or ""
        print(f"   - ID: {model_id} | {model_name} ({model_code})")

    return models


def first_model_value(model, *keys):
    for key in keys:
        value = model.get(key)
        if value not in (None, ""):
            return value
    return None


def select_model(models, purpose="对话", prefer_models=None):
    """从模型列表中选择合适的模型

    Args:
        models: 模型列表
        purpose: 用途描述
        prefer_models: 优先的模型关键词列表，按优先级排序
    """
    if not models:
        print(f"❌ 没有可用的{purpose}模型")
        raise SystemExit(1)

    # 如果没有指定优先模型，使用默认策略
    if not prefer_models:
        prefer_models = ["gpt-4", "gpt4", "gpt-3.5", "gpt35"]

    # 按优先级查找模型
    for preferred in prefer_models:
        preferred_lower = preferred.lower()
        for model in models:
            model_type = str(first_model_value(model, "modelType", "ModelType") or "").lower()
            if model_type and model_type not in ("chat", "vision", "vl", "llm"):
                continue
            model_code = str(first_model_value(model, "modelCode", "ModelCode") or "").lower()
            model_name = str(first_model_value(model, "modelName", "ModelName") or "").lower()
            if preferred_lower in model_code or preferred_lower in model_name:
                model_id = first_model_value(model, "aiModelId", "AiModelId", "modelId", "ModelId", "id", "Id")
                print(f"选择模型: {first_model_value(model, 'modelName', 'ModelName')} (ID: {model_id})")
                return model_id

    # 默认选择第一个
    chat_models = [
        model for model in models
        if str(first_model_value(model, "modelType", "ModelType") or "").lower() in ("chat", "vision", "vl", "llm")
    ]
    first_model = chat_models[0] if chat_models else models[0]
    model_id = first_model_value(first_model, "aiModelId", "AiModelId", "modelId", "ModelId", "id", "Id")
    print(f"选择模型: {first_model_value(first_model, 'modelName', 'ModelName')} (ID: {model_id})")
    return model_id


def open_management_page(page_type, message="查看"):
    """打开管理页面"""
    url = WEB_URLS.get(page_type)
    if not url:
        return

    print(f"\n🌐 {message}：")
    print(f"   {url}")

    if open_browser(url):
        print("   ✅ 已在浏览器中打开")
    else:
        print("   ℹ️  请手动复制链接到浏览器打开")


if __name__ == "__main__":
    print("workopilot_http.py 是共享工具模块，请运行具体任务脚本。")
