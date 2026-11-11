## 创建和更新应用菜单

应用菜单是数字员工的附属配置。使用 APIKEY 创建或更新时，不需要传完整 `RobotAppConfigDto`，只传菜单必要字段；后端会自动把菜单配置为 `iframe` 类型，并自动启用该数字员工的应用菜单入口。

### 创建菜单

```http
POST /api/ai/robot/external/{robotId}/app-menu
API-KEY: <WORKOPILOT_API_KEY>
Content-Type: application/json
```

请求示例：

```jsonc
{
  "title": "报价单历史", // 菜单显示名称，必填
  "menuKey": "quote-history", // 可选但强烈建议传；使用英文、数字、下划线、短横线，中文标题不传时会生成随机 menu-xxxx
  "iframeUrl": "http://localhost:5173/quote-history?appCode=quotation&robotId=10001&menuKey=quote-history", // 必填，本地测试可用 localhost
  "icon": "lucide:history", // 可选；使用 lucide 图标库，也可简写为 "history"
  "sort": 10, // 可选；不传时自动排在最后
  "isEnabled": true // 可选；默认 true
}
```

响应示例：

```jsonc
{
  "code": 200,
  "msg": "应用菜单创建成功",
  "data": {
    "id": 90001,
    "menuType": "iframe",
    "displayMode": "fullscreen",
    "menuKey": "quote-history",
    "title": "报价单历史",
    "icon": "lucide:history",
    "routePath": "quote-history",
    "componentPath": null,
    "iframeUrl": "http://localhost:5173/quote-history?appCode=quotation&robotId=10001&menuKey=quote-history",
    "directUrl": null,
    "sort": 10,
    "isEnabled": true
  }
}
```

### 更新菜单

```http
PUT /api/ai/robot/external/{robotId}/app-menu/{menuKey}
API-KEY: <WORKOPILOT_API_KEY>
Content-Type: application/json
```

请求体为部分更新，未传字段保持原值。发布后把本地测试地址更新为正式 HTTPS 地址：

```jsonc
{
  "title": "报价单历史",
  "iframeUrl": "https://quote.example.com/history?appCode=quotation&robotId=10001&menuKey=quote-history",
  "icon": "lucide:file-clock",
  "sort": 10,
  "isEnabled": true
}
```

图标使用前端 Iconify/Lucide 图标名，推荐格式为 `lucide:<name>`。常用示例：`lucide:history`、`lucide:file-clock`、`lucide:table-2`、`lucide:clipboard-list`、`lucide:users`、`lucide:database`。如果只传 `history`，后端会自动保存为 `lucide:history`。
