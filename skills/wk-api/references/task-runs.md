# 任务型数字员工（.NET）

先由实施确认 RobotId 对应已启用的 TASK 员工。所有响应中的运行标识读取 data.Id，路径占位符 runId 使用该值。示例省略部分时间字段。
## 创建独立任务

`POST /api/ai/robot/task-runs`

请求体

```json
{
  "RobotId": "1001",
  "Content": "生成周报",
  "ContextData": {
    "week": "2026-W45"
  },
  "Files": []
}
```

成功响应

```json
{
  "code": 200,
  "msg": "任务已创建",
  "data": {
    "Id": "20890001",
    "TaskTitle": "生成周报",
    "RobotId": "1001",
    "RobotCode": "weekly_report",
    "SessionId": "s-01",
    "AssistantMessageId": "20890002",
    "TriggerType": "MANUAL",
    "Status": "QUEUED",
    "RequestContent": "生成周报",
    "Files": [],
    "ContextData": {
      "week": "2026-W45"
    },
    "ResultText": null,
    "ResultJson": null,
    "ErrorCode": null,
    "ErrorMessage": null
  }
}
```

HTTP 202。传文本或文件，Files 为 URL 数组。新会话由平台创建。结构化结果依员工配置。

## 查询本人可访问的运行

`GET /api/ai/robot/task-runs?robotId=1001&status=QUEUED&pageNum=1&pageSize=20`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "rows": [
    {
      "Id": "20890001",
      "TaskTitle": "生成周报",
      "RobotId": "1001",
      "RobotCode": "weekly_report",
      "SessionId": "s-01",
      "AssistantMessageId": "20890002",
      "TriggerType": "MANUAL",
      "Status": "QUEUED",
      "RequestContent": "生成周报",
      "Files": [],
      "ContextData": {
        "week": "2026-W45"
      },
      "ResultText": null,
      "ResultJson": null,
      "ErrorCode": null,
      "ErrorMessage": null
    }
  ],
  "total": 1
}
```

可选 keyword、startDate、endDate。读取 rows 数组。

## 查看结果

`GET /api/ai/robot/task-runs/20890001`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "Id": "20890001",
    "TaskTitle": "生成周报",
    "RobotId": "1001",
    "RobotCode": "weekly_report",
    "SessionId": "s-01",
    "AssistantMessageId": "20890002",
    "TriggerType": "MANUAL",
    "Status": "SUCCEEDED",
    "RequestContent": "生成周报",
    "Files": [],
    "ContextData": {
      "week": "2026-W45"
    },
    "ResultText": "完成周报",
    "ResultJson": {
      "summary": "完成合同评审"
    },
    "ErrorCode": null,
    "ErrorMessage": null
  }
}
```

状态 QUEUED、RUNNING 时继续查询；SUCCEEDED、FAILED、CANCELLED 时停止。失败读取 ErrorCode 和 ErrorMessage。不存在返回业务 code=404。

## 取消

`POST /api/ai/robot/task-runs/20890001/cancel`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "msg": "任务已取消",
  "data": true
}
```

不允许取消时 code=409、data=false。

## 重试

`POST /api/ai/robot/task-runs/20890001/retry`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "msg": "重试任务已创建",
  "data": {
    "Id": "20890003",
    "TaskTitle": "生成周报",
    "RobotId": "1001",
    "RobotCode": "weekly_report",
    "SessionId": "s-02",
    "AssistantMessageId": "20890004",
    "TriggerType": "MANUAL",
    "Status": "QUEUED",
    "RequestContent": "生成周报",
    "Files": [],
    "ContextData": {
      "week": "2026-W45"
    },
    "ResultText": null,
    "ResultJson": null,
    "ErrorCode": null,
    "ErrorMessage": null
  }
}
```

HTTP 202。保存新 data.Id。

## 删除终态历史

`DELETE /api/ai/robot/task-runs/20890001`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": true,
  "msg": "任务历史已删除"
}
```

运行中或不存在时 code=409、data=false。

