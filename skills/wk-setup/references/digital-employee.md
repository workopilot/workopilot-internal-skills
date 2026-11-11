## 创建数字员工

```http
POST /api/ai/robot/external/create
```

请求体：

```json
{
  "robotName": "合同审核助手",
  "robotCode": "contract_review_agent",
  "avatarUrl": "https://example.com/avatar.png",
  "businessLine": "legal",
  "description": "辅助审核合同风险点",
  "chatModelId": 1,
  "systemPrompt": "你是一个严谨的合同审核助手。",
  "welcomeMessage": "你好，我可以帮你审核合同。",
  "quickQuestions": [
    {
      "text": "帮我检查违约条款",
      "sort": 1
    }
  ],
  "enableHistory": 1,
  "maxHistory": 10,
  "skills": [
    {
      "skillRegistryId": 21,
      "isActive": 1,
      "sortIndex": 0
    }
  ],
  "mcpTools": []
}
```

响应示例：

```jsonc
{
  "code": 200,
  "msg": "数字员工创建成功",
  "data": {
    "id": 1001, // 新建数字员工 ID；后续开放聊天和 iframe 嵌入使用
    "robotCode": "contract_review_agent", // 后续按编码查询时使用
    "robotName": "合同审核助手",
    "avatarUrl": "https://example.com/avatar.png",
    "welcomeMessage": "你好，我可以帮你审核合同。",
    "quickQuestions": [],
    "enableSuggestedReplies": 0,
    "enableToolCallDisplay": 1,
    "businessLine": "legal",
    "businessLineName": "法务",
    "isActive": 1,
    "enableAgentCollaboration": 0,
    "collaborationScope": null,
    "appMenus": [],
    "chatModelId": 1, // 实际绑定的聊天模型
    "skillRegistryIds": [21], // 实际绑定的技能 ID
    "mcpToolIds": [] // 实际绑定的 MCP 工具 ID
  },
  "total": 0,
  "rows": null
}
```

实际创建时建议必填：

- `robotName`
- `systemPrompt`

Agent 使用：创建成功后保存 `data.id`、`data.robotCode`。如果下一步要嵌入，调用 `/api/ai/open/robots` 获取 `shareUrl`。
