# 配置迁移、指令与会话成果（.NET）

以下路径相对 .NET 网关，业务调用沿用当前用户权限。资源迁移需要源、目标租户各自的授权会话。示例响应仅展示本步使用的字段。
## 导出员工

`POST /api/ai/robot/transfer/export`

请求体

```json
{
  "RobotIds": [
    "1001"
  ],
  "Passphrase": "example-transfer-passphrase"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "CipherText": "示例密文",
    "Summary": {
      "Total": 1,
      "Success": 1,
      "Skipped": 0,
      "Failed": 0
    }
  }
}
```

将完整 CipherText 交给目标环境，口令由实施人员提供。

## 导入员工

`POST /api/ai/robot/transfer/import`

请求体

```json
{
  "CipherText": "源环境返回的完整密文",
  "Passphrase": "example-transfer-passphrase"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "Results": [
      {
        "RobotCode": "contract_helper",
        "Status": "success",
        "Warnings": []
      }
    ],
    "Summary": {
      "Total": 1,
      "Success": 1,
      "Skipped": 0,
      "Failed": 0
    }
  }
}
```

逐项读取 Status、Warnings 和失败原因。

## 导出服务配置

`POST /api/aiagent/export`

请求体

```json
{
  "Ids": [
    "101"
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "format": "workopilot.ai-services",
    "version": 1,
    "services": [
      {
        "ServiceCode": "contract_summary",
        "ServiceName": "合同摘要",
        "ExecutionMode": "CHAT",
        "AiModelId": "101",
        "OutputType": "TEXT",
        "SystemPrompt": "概括合同内容",
        "IsRouteEnabled": 0,
        "Routes": []
      }
    ]
  }
}
```

data 中 format、version、services 固定小写，services 内的 ServiceCode 等属性大写开头。请保存完整 data，示例仅列主要属性。

## 导入服务配置

`POST /api/aiagent/import`

请求体

```json
{
  "format": "workopilot.ai-services",
  "version": 1,
  "services": [
    {
      "ServiceCode": "contract_summary",
      "ServiceName": "合同摘要",
      "ExecutionMode": "CHAT",
      "AiModelId": "101",
      "OutputType": "TEXT",
      "SystemPrompt": "概括合同内容",
      "IsRouteEnabled": 0,
      "Routes": []
    }
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "Imported": 1,
    "Failed": 0,
    "Results": [
      {
        "ServiceName": "合同摘要",
        "ServiceCode": "contract_summary",
        "Success": true,
        "ServiceId": "102"
      }
    ]
  }
}
```

请求体直接使用导出 data，检查目标环境模型、工具和路由引用。

## 读取员工指令

`GET /api/ai/robot/command/list?robotId=1001`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "rows": [
    {
      "Id": "201",
      "RobotId": "1001",
      "Code": "summary",
      "Name": "生成摘要",
      "Prompt": "概括当前合同",
      "IsActive": 1,
      "SortIndex": 0
    }
  ],
  "total": 1
}
```



## 新增或更新指令

`POST /api/ai/robot/command/save`

请求体

```json
{
  "RobotId": "1001",
  "Code": "summary",
  "Name": "生成摘要",
  "Prompt": "概括当前合同",
  "IsActive": 1,
  "SortIndex": 0
}
```

成功响应

```json
{
  "code": 200,
  "data": "201"
}
```

更新时增加 Id。

## 为员工导入模板

`POST /api/ai/robot/command/import-template`

请求体

```json
{
  "RobotId": "1001",
  "TemplateIds": [
    "301"
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "Imported": 1,
    "Skipped": 0,
    "Warnings": []
  }
}
```



## 保存租户指令模板

`POST /api/ai/robot/command/save-as-template`

请求体

```json
{
  "CommandId": "201",
  "TemplateScope": "TENANT"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "Id": "301",
    "TemplateScope": "TENANT",
    "Name": "生成摘要",
    "Code": "summary"
  }
}
```



## 读取 HTML 成果

`GET /api/ai/html-artifacts/art-01`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "id": "art-01",
    "name": "合同报告",
    "revisionId": "rev1",
    "source": "<p>摘要</p>"
  }
}
```

此控制器的匿名响应对象明确使用小写字段。

## 更新 HTML 成果

`PUT /api/ai/html-artifacts/art-01`

请求体

```json
{
  "ExpectedRevisionId": "rev1",
  "Source": "<p>修订后的摘要</p>"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "revisionId": "rev2"
  }
}
```

HTTP 409 表示版本已变化；重新读取后再编辑。

## 生成预览

`POST /api/ai/html-artifacts/art-01/preview`

请求体

```json
{
  "ExpectedRevisionId": "rev2"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "path": "api/ai/html-artifacts/render/preview-token",
    "revisionId": "rev2",
    "expiresInSeconds": 300
  }
}
```



## 生成普通分享

`POST /api/ai/html-artifacts/art-01/share`

请求体

```json
{
  "ExpectedRevisionId": "rev2"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "path": "api/ai/html-artifacts/render/share-token",
    "revisionId": "rev2",
    "expiresInSeconds": 604800
  }
}
```

本例为默认分享。指定 Managed、LoginRequired、Password 或其他有效期时可走受管分享，响应包含 token 和分享策略。

## 读取会话文档

`GET /api/ai/robot/markdown/s-01?skillCode=report`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "SessionId": "s-01",
    "SkillCode": "report",
    "Title": "评审报告",
    "Summary": "合同评审",
    "VersionNo": 1,
    "MarkdownContent": "# 合同评审"
  }
}
```

skillCode 必填，versionNo 可选。无记录时 data 可为 null。

## 读取文档版本

`GET /api/ai/robot/markdown/versions/s-01?skillCode=report`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": [
    {
      "Id": "501",
      "VersionNo": 1,
      "Title": "评审报告",
      "Summary": "合同评审",
      "CreateTime": "2026-11-11 12:00:00"
    }
  ]
}
```



## 保存文档

`POST /api/ai/robot/markdown/save`

请求体

```json
{
  "SessionId": "s-01",
  "SkillCode": "report",
  "Title": "评审报告",
  "Summary": "合同评审",
  "Content": "# 新版合同评审"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "SessionId": "s-01",
    "SkillCode": "report",
    "Title": "评审报告",
    "Summary": "合同评审",
    "VersionNo": 2
  }
}
```

先读取已有文档并确认归属。

## 导出文档 PDF

`POST /api/ai/robot/markdown/export-pdf`

请求体

```json
{
  "SessionId": "s-01",
  "SkillCode": "report",
  "VersionNo": 2,
  "Theme": "default"
}
```

成功响应

```json
{
  "code": 200,
  "data": "https://files.example.com/report.pdf"
}
```



