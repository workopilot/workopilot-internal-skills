## 注册卡片

```http
POST /api/ai/skill-registry/external/iframe-card
API-KEY: <WORKOPILOT_API_KEY>
Content-Type: application/json
```

请求体：

```json
{
  "skillName": "订单详情卡片",
  "skillCode": "order_detail_iframe",
  "skillCategory": "ORDER",
  "skillDesc": "展示订单详情外部页面",
  "skillIcon": "link",
  "url": "http://localhost:5173/order-detail",
  "triggerPrompt": "当已经获得可查看的订单详情结果时，调用 showCard 展示订单详情卡片。调用时必须传入 skillCode=order_detail_iframe；如果有订单ID则传 businessId；如果已有订单摘要JSON则传 businessData。",
  "titlePrompt": "根据订单结果生成一句20字内标题",
  "drawerTitle": "订单详情",
  "drawerWidth": "wide",
  "sortIndex": 100
}
```

本地开发时，`url` 可以先配置为你当前卡片的url地址， `http://localhost:5173/...` 或 `http://127.0.0.1:5173/...` 进行测试。发布后必须更新为实际部署地址，否则终端用户无法打开卡片页面。

响应示例（`jsonc`，带注释，不可直接作为 JSON 发送）：

```jsonc
{
  "code": 200,
  "msg": "Iframe技能卡片已注册",
  "data": {
    "id": 123, // skillRegistryId；创建数字员工或绑定已有数字员工时使用
    "skillName": "订单详情卡片",
    "skillCode": "order_detail_iframe", // showCard 调用时必须传这个编码
    "skillCategory": "ORDER",
    "skillDesc": "展示订单详情外部页面",
    "skillIcon": "link",
    "skillKind": "BUSINESS_CARD",
    "skillSource": "TENANT_CUSTOM",
    "ownerTenantId": "tenant_001",
    "reviewStatus": "APPROVED",
    "defaultToolsConfig": {
      "tools": [
        {
          "code": "showCard", // 数字员工可调用的工具
          "name": "showCard",
          "is_active": true
        }
      ]
    },
    "defaultCardConfig": {
      "card_type": "iframe_card",
      "trigger_prompt": "当已经获得可查看的订单详情结果时，调用 showCard 展示订单详情卡片。",
      "title_prompt": "根据订单结果生成一句20字内标题",
      "action": "open_drawer",
      "drawer_code": "order_detail_iframe_drawer"
    },
    "defaultDrawerConfig": {
      "drawer_code": "order_detail_iframe_drawer",
      "drawer_mode": "URL",
      "title": "订单详情",
      "drawer_url": "http://localhost:5173/order-detail", // iframe 打开的页面地址
      "drawer_width": "wide"
    },
    "isActive": 1,
    "sortIndex": 100
  },
  "total": 0,
  "rows": null
}
```

Agent 读取字段：

| 字段 | 用途 |
| --- | --- |
| `data.id` | `skillRegistryId`，绑定数字员工时使用 |
| `data.skillCode` | `showCard.skillCode` 必须使用这个值 |
| `data.defaultDrawerConfig.drawer_url` | 检查当前是否仍是本地测试 URL |

## 绑定数字员工

创建数字员工时，可以直接把卡片绑定进去：

```json
{
  "robotName": "订单助手",
  "systemPrompt": "你是订单助手。查询到订单详情后，如果用户需要查看完整订单信息，调用 showCard 打开订单详情卡片。",
  "skills": [
    {
      "skillRegistryId": 123,
      "isActive": 1,
      "sortIndex": 0
    }
  ]
}
```

如果数字员工已经存在，当前 APIKEY 开放接口没有独立的“更新已有数字员工并绑定卡片”接口。可选方式：

- 使用喔壳管理台绑定技能卡片。
- 使用后台登录态接口 `POST /api/ai/robot/skill/save` 绑定，注意这是 `[Authorize]` 接口，不是 APIKEY 开放接口。

后台登录态绑定请求示例（仅用于管理台或内部集成）：

```json
{
  "robotId": 10001,
  "skillRegistryId": 123,
  "isActive": 1,
  "sortIndex": 0
}
```

Agent 不要把 `POST /api/ai/robot/skill/save` 描述成第三方 APIKEY 接口。
