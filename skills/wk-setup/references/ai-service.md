## 创建 AI 服务

```http
POST /api/aiagent/external/create
```

请求体：

```json
{
  "serviceName": "合同审核",
  "serviceCode": "contract_review",
  "description": "根据合同正文和审核重点输出风险点",
  "systemPrompt": "你是合同审核助手。请基于以下合同内容进行审核：{{contract_text}}。重点关注：{{review_focus}}。请以 JSON 输出 riskItems 数组，每项包含 title、reason、suggestion。",
  "outputType": "JSON",
  "isAsync": 0,
  "inputs": [
    {
      "name": "contract_text",
      "type": "string",
      "desc": "合同全文",
      "ui": "textarea"
    },
    {
      "name": "review_focus",
      "type": "string",
      "desc": "审核重点",
      "ui": "input"
    }
  ],
  "aiModelId": 789
}
```

响应示例：

```jsonc
{
  "code": 200,
  "msg": null,
  "data": {
    "id": 123, // 新建 AI 服务 ID
    "serviceName": "发票识别",
    "serviceCode": "invoice_extract", // 后续执行服务必须保存这个值
    "description": "提取发票字段并返回 JSON",
    "executionMode": "CHAT",
    "outputType": "JSON", // 执行结果期望格式
    "isActive": 1, // 1=启用
    "isAsync": 0, // 1=异步服务
    "tags": "[\"外部Agent\"]",
    "groupId": 456,
    "createTime": "2026-06-15T10:00:00",
    "updateTime": null
  },
  "total": 0,
  "rows": null
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.id` | long | 新建 AI 服务 ID |
| `data.serviceCode` | string | 后续执行服务时的关键字段，必须保存 |
| `data.isAsync` | int | 创建后的异步配置 |

模型兜底规则：

1. 优先使用 `aiModelId`
2. 其次使用 `modelProvider + modelName`
3. 再使用租户默认聊天模型
4. 如果没有可用模型，返回 `500`

Agent 使用：创建完成后至少记录 `data.serviceCode`；如需立即验证，调用 `/api/aiagent/run`。
