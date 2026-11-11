# 用实施 API 配置数字员工菜单

先用 `create_digital_employee.py` 创建或复用员工，记下返回的员工 ID。每次请求给一个员工创建或更新一项菜单。首次创建会自动启用员工的应用入口。若业务人员要从业务端员工目录进入，请选对话型员工，任务型员工不会出现在该目录。

## 确认目标页面

- 喔壳托管 AI 应用使用 `menuType: "ai-app"`。在目标租户打开员工配置 → 添加应用菜单，选择已开通的 AI 应用及具体页面。记录应用编码和页面完整路由（含父级路径和业务查询参数）。也可以依据目标环境已发布的路由配置核对。应用名称、组件文件路径、布局容器和含未填动态参数的路由都不能直接用作页面绑定。
- 独立部署的第三方页面使用 `menuType: "iframe"`，提供绝对 HTTP(S) 地址。已有 iframe 请求可以继续省略 `menuType`。
- AI 应用的嵌入地址由后端构造，自动设为 `showMenu=false`，认证由子应用 SDK 处理。实施接口验证路径并保存绑定。目标应用是否已开通、目标角色是否能进入页面和读写数据，需要在目标租户验证。

## 请求

| 操作 | 方法与相对路径 |
| --- | --- |
| 创建 | `POST /api/ai/robot/external/{robotId}/app-menu` |
| 部分更新 | `PUT /api/ai/robot/external/{robotId}/app-menu/{menuKey}`，路径中填原菜单编码 |

在目标环境的 .NET 根地址后拼接相对路径。测试环境为 `https://agenttest.workopilot.com/net-api`，生产环境为 `https://agent.workopilot.com/net-api`。请求头为 `API-KEY: <目标租户具有 ai 权限的实施 Key>` 和 `Content-Type: application/json`。

| JSON 字段 | 类型 | 如何填写 |
| --- | --- | --- |
| `title` | string | 创建必填，菜单显示名称 |
| `menuKey` | string | 建议提供稳定的英文、数字、下划线或短横线编码，最长 64 字符。创建时省略则由标题生成，纯中文标题会生成随机编码。更新时传新值表示改名 |
| `menuType` | string | 创建可选 `ai-app` 或 `iframe`，默认 `iframe`。更新省略时保留原类型 |
| `aiAppCode` | string | 创建或切换到 AI 应用时必填，目标租户已开通的应用编码（字母、数字、下划线、短横线，最长 128 字符） |
| `aiMenuPath` | string | 创建或切换到 AI 应用、更换应用编码时必填。同一应用内换页可单独传此字段。可带查询参数和片段，路径及生成地址均不超过 1000 字符；不传 `runtimeToken` |
| `iframeUrl` | string | 创建或切换到第三方 iframe 时必填，绝对 HTTP(S) URL，AI 应用菜单省略此字段 |
| `displayMode` | string | `card` 或 `fullscreen`，实施接口创建默认 `fullscreen`，更新省略时保留 |
| `icon` | string | 例如 `lucide:search`，简写 `search` 自动补前缀。创建默认 `lucide:file-text` |
| `sort` | integer | 值小靠前，创建省略时追加到末尾 |
| `isEnabled` | boolean | 创建默认 `true`，传 `false` 停用该项 |

### 创建 AI 应用菜单

将[示例文件](../examples/ai-app-menu.json)复制到目标项目，例如保存为 `menu.json`。以下编码和路径是示例，请换成已核实的目标页面。

```json
{
  "title": "药品查询",
  "menuKey": "drug-search",
  "menuType": "ai-app",
  "aiAppCode": "pharma-tools",
  "aiMenuPath": "/drugs/search?status=active",
  "displayMode": "card",
  "icon": "lucide:search",
  "sort": 10,
  "isEnabled": true
}
```

从技能目录执行（将 123 换成员工 ID，环境变量 `WORKOPILOT_API_KEY` 提供实施凭据）。

```powershell
py -3 scripts/configure_app_menu.py --base-url $env:WORKOPILOT_BASE_URL --employee-id 123 --action create --config menu.json
```

成功响应的外层字段为小写，`data` 内菜单字段为 PascalCase，雪花 ID 为字符串。

```json
{
  "code": 200,
  "msg": "应用菜单创建成功",
  "data": {
    "Id": "90001",
    "MenuType": "ai-app",
    "DisplayMode": "card",
    "MenuKey": "drug-search",
    "Title": "药品查询",
    "Icon": "lucide:search",
    "RoutePath": "drug-search",
    "ComponentPath": null,
    "IframeUrl": "/apps/pharma-tools/drugs/search?status=active&showMenu=false",
    "AiAppCode": "pharma-tools",
    "AiMenuPath": "/drugs/search?status=active",
    "DirectUrl": null,
    "Sort": 10,
    "IsEnabled": true,
    "ModelViewId": null,
    "SourceAppId": null,
    "SourceMenuId": null
  },
  "total": 0,
  "rows": null
}
```

### 更新页面或改用第三方 iframe

保存下列请求为 `menu-update.json`。只改当前应用内的页面和排序时，省略应用编码即可。

```json
{
  "aiMenuPath": "/drugs/list?status=active",
  "sort": 20
}
```

```powershell
py -3 scripts/configure_app_menu.py --base-url $env:WORKOPILOT_BASE_URL --employee-id 123 --action update --menu-key drug-search --config menu-update.json
```

更新成功响应与创建具有相同的字段，`msg` 为“应用菜单更新成功”。只改标题、排序或启用状态会保留页面绑定。更换 AI 应用时同时传新编码与新路径。将现有菜单切换到独立部署的网页时，更新请求如下。

```json
{
  "menuType": "iframe",
  "iframeUrl": "https://portal.example.com/drugs/search"
}
```

直接创建第三方菜单时另加必填的 `title`，建议一并传入稳定的 `menuKey`。切换成功后 `AiAppCode` 和 `AiMenuPath` 均为 null。反向切换时传 `menuType: "ai-app"`、`aiAppCode` 和 `aiMenuPath`。

### 失败与验收

缺少 Key 返回 HTTP 401，Key 无效或权限不足返回 HTTP 403。控制器内的业务错误看响应体的 `code` 与 `msg`。例如给 AI 应用菜单传了不可用的页面地址时，响应如下。

```json
{
  "code": 500,
  "msg": "请选择有效的 AI 应用及页面",
  "data": null,
  "total": 0,
  "rows": null
}
```

同一员工下重复创建相同 `menuKey` 会失败。根据返回消息核对已有菜单，使用原编码更新。若目标环境仍提示 AI 应用必须填写 iframeUrl，先部署支持 AI 应用的实施接口，再重试。交付前核对返回的 `MenuType`、`AiAppCode`、`AiMenuPath`、`IframeUrl`，并用目标业务角色从员工菜单打开页面。
