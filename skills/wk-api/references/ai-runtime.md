# AI 服务与聊天 HTTP 接口

所有路径相对 .NET 网关。JSON 请求使用 Content-Type: application/json 和 Authorization: Bearer <用户 Token>。示例响应展示接入所需字段；可空字段和附加元数据以实际响应为准。键名及嵌套层级按原始 HTTP 正文书写。
## 同步执行已配置的 AI 服务

`POST /api/aiagent/run`

请求体

```json
{
  "serviceCode": "contract_summary",
  "inputs": {
    "text": "合同约定收到发票后30天付款。"
  },
  "isAsync": false
}
```

成功响应

```json
{
  "Code": 0,
  "Message": "Success",
  "Data": "付款期限为收到发票后30天。",
  "Usage": {
    "InputTokens": "48",
    "OutputTokens": "12",
    "TotalTokens": "60"
  },
  "ConversationId": "conversation-01",
  "TaskId": null,
  "RequestId": "b034dee3dbd6478f932ef108bc974ca6"
}
```

读取 body.Code（0 成功）、body.Data。Data 由该服务的输出配置决定，可以是文本或结构化对象。inputs 内的 text 是示例服务定义的参数名，大小写按目标服务的输入定义原样传。

|请求键（沿用现有前端发包）|JSON 类型|何时传|
|---|---|---|
|serviceCode|string|必填，租户中已启用的服务编码|
|inputs|object|按服务定义填业务字段，无参数传 {}|
|isAsync|boolean|可选；省略采用服务配置。false 同步，true 提交任务|
|routeCode|string|路由默认关闭。启用 CODE 时指定分支，INTENT 时可省略自动识别；显式值优先|
|files|string[]|可选，可访问的文件 URL|
|conversationId|string|可选，继续已有会话时传上次的 ConversationId|

服务不存在时，HTTP 可以是 200，业务失败正文示例（节选）

```json
{
  "Code": 500,
  "Message": "Service not found: contract_summary",
  "Data": null
}
```

## 异步执行并指定路由

`POST /api/aiagent/run`

请求体

```json
{
  "serviceCode": "contract_summary",
  "inputs": {
    "text": "合同约定收到发票后30天付款。"
  },
  "isAsync": true,
  "routeCode": "payment_terms",
  "files": [
    "https://files.example.com/contract.pdf"
  ],
  "conversationId": "conversation-01"
}
```

成功响应

```json
{
  "Code": 0,
  "Message": "Task Submitted",
  "Data": null,
  "Usage": null,
  "ConversationId": "conversation-01",
  "TaskId": "20890001",
  "RequestId": "b034dee3dbd6478f932ef108bc974ca6"
}
```

读取 body.TaskId，作为下一接口的 taskId。示例 routeCode 需要在目标服务上启用。

## 获取异步进度和最终输出

`GET /api/aiagent/task/result?taskId=20890001`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "Id": "20890001",
    "TraceId": "b034dee3dbd6478f932ef108bc974ca6",
    "TaskStatus": "SUCCESS",
    "TaskStatusId": 30,
    "Progress": 100,
    "Output": "付款期限为收到发票后30天。",
    "ErrorMsg": null,
    "CostTokens": 60,
    "RetryCount": 0
  }
}
```

读取 body.data.TaskStatusId。0 等待、10 处理中、30 完成、-10 失败。30 取 Output（服务端写入的原始输出，结构化输出可能是 JSON 文本），-10 取 ErrorMsg，二者均结束轮询。业务 code=404 表示任务不存在。

## 在接入测试页执行服务

`POST /api/aiagent/runtest`

请求体

```json
{
  "serviceCode": "contract_summary",
  "inputs": {
    "text": "合同约定收到发票后30天付款。"
  },
  "isAsync": true
}
```

成功响应

```json
{
  "code": 200,
  "msg": "Task Submitted",
  "data": {
    "Code": 0,
    "Message": "Task Submitted",
    "Data": null,
    "Usage": null,
    "ConversationId": "conversation-01",
    "TaskId": "20890001",
    "RequestId": "b034dee3dbd6478f932ef108bc974ca6"
  }
}
```

和 run 使用相同的输入。读取 body.code，再读 body.data.Code、body.data.TaskId 或 body.data.Data。

## 发送一轮 CHAT 对话

`POST /api/ai/robot/chat/send`

请求体

```json
{
  "RobotCode": "contract_helper",
  "Content": "概括付款条款",
  "Files": [
    "https://files.example.com/contract.pdf"
  ]
}
```

响应 Content-Type: text/event-stream。完成事件示例（data 节选）

```text
event: done
data: {"messageId":"20890002","sessionId":"s-01","message":"付款期限为30天。","attachments":[],"eventSeq":4}

```
首轮省略 SessionId，续聊传上一轮的 sessionId。可选 ContextData 为字符串键值对象。按空行分帧，读取 event 与 data，cfdata 是兼容副本。error 帧读取 data.message。

## 从断开位置恢复消息流

`GET /api/ai/robot/chat/stream/20890002?afterSeq=3`

无请求体。查询参数见地址。

响应为上述 SSE 事件流。
路径为消息 ID，afterSeq 为客户端已处理的最后序号。

[任务型员工](task-runs.md) · [场景推荐与草稿](recommendations.md)

