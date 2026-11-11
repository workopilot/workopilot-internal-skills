# 场景推荐与聊天草稿（.NET）

使用同一用户和应用上下文完成下列请求。固定推荐直接展示 resolve 返回的 Items；AI 推荐点击前先 generate。示例均为原始 HTTP JSON 节选。
## 解析当前场景

`POST /api/employee-recommendation/resolve`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "SceneCode": "contract_review",
    "ConfigVersion": "1",
    "Employees": [
      {
        "Id": "3001",
        "TargetRobotId": "1001",
        "TargetRobotName": "合同助手",
        "Mode": "generated",
        "Items": []
      }
    ]
  }
}
```

AppCode 和 SceneCode 为字符串。OwnerRobotId 可选，用于历史同码消歧。场景无效或停用时 data 为 null。

## 生成推荐话术

`POST /api/employee-recommendation/generate`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review",
  "RecommendEmployeeId": "3001",
  "BusinessKey": "contract:A-12",
  "Context": {
    "BusinessContext": "合同 A-12 的付款条款",
    "GenerationContext": "账期为30天，请建议需要核对的事项"
  }
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "ResultId": "result-01",
    "Items": [
      {
        "Id": "item-01",
        "Text": "帮我核对付款条款",
        "IsHighlighted": false
      }
    ],
    "Cached": false,
    "InputHash": "hash-01",
    "ExpiresAt": "2026-11-11 12:10:00"
  }
}
```

RecommendEmployeeId 取 Employees[].Id。GenerationContext 用于生成，BusinessContext 用于带入聊天；各最多 30000 字。BusinessKey 按业务记录取稳定值，可选 Force=true 重新生成。

## 将选中的推荐准备为草稿

`POST /api/employee-recommendation/prepare`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review",
  "RecommendEmployeeId": "3001",
  "BusinessKey": "contract:A-12",
  "Context": {
    "BusinessContext": "合同 A-12 的付款条款",
    "GenerationContext": "账期为30天，请建议需要核对的事项"
  },
  "ResultId": "result-01",
  "ItemId": "item-01",
  "TemplateParams": [
    {
      "Key": "contractNo",
      "Value": "A-12"
    }
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "DraftToken": "draft-01",
    "TargetRobotId": "1001",
    "ExpiresAt": "2026-11-11 12:10:00"
  }
}
```

固定推荐省略 ResultId。Context 使用最新内容，409 CONTEXT_CHANGED 时重新生成。模板变量名与场景配置一致。

## 读取本人草稿

`POST /api/employee-recommendation/draft/read`

请求体

```json
{
  "AppCode": "contracts",
  "TargetRobotId": "1001",
  "DraftToken": "draft-01"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "DraftId": "draft-id-01",
    "AppCode": "contracts",
    "SceneCode": "contract_review",
    "TargetRobotId": "1001",
    "SessionMode": "new",
    "Text": "合同 A-12 的付款条款\n帮我核对付款条款"
  }
}
```

令牌绑定用户、租户、应用及目标员工。草稿写入输入框后确认。

## 确认已接收草稿

`POST /api/employee-recommendation/draft/ack`

请求体

```json
{
  "DraftId": "draft-id-01",
  "DraftToken": "draft-01"
}
```

成功响应

```json
{
  "code": 200,
  "data": true
}
```

用户确认后再发送聊天。错误示例（HTTP 409）

```json
{
  "code": 409,
  "msg": "草稿已失效",
  "errorCode": "DRAFT_UNAVAILABLE",
  "traceId": "example"
}
```



