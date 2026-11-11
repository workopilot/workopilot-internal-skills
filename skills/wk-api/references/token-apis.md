# 主数据、本人待办和消息发送

路径相对对应环境网关，GET 参数放 URL。示例为原始 HTTP 正文节选。Java 分页取 rows、total，普通查询取 data。ID 在客户端保留精度。

[文件、语音及审核](files-audit.md) · [迁移、快捷指令与成果](resources.md)
## 获取可见部门 · Java 网关

`GET /system/dept/list?status=0`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": [
    {
      "deptId": 101,
      "parentId": 100,
      "deptName": "研发部",
      "status": "0"
    }
  ]
}
```

可选 deptName（名称）、status（0 正常）；需要 system:dept:list 权限。使用 parentId 建树。

## 分页选择公司 · Java 网关

`GET /mst/commonData/pageForDown?tagCode=COMPANY&pageNum=1&pageSize=20`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "rows": [
    {
      "id": 1001,
      "dataKey": "示例公司",
      "dataValue": "COMP001"
    }
  ],
  "total": 1
}
```

tagCode 区分业务类型。公司展示名读 dataKey，业务编码读 dataValue。

## 分页选择产品 · Java 网关

`GET /mst/commonData/pageForDown?tagCode=PRODUCT&pageNum=1&pageSize=20`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "rows": [
    {
      "dataKey": "示例商品",
      "dataValue": "SKU001"
    }
  ],
  "total": 1
}
```

同一分页协议，PRODUCT 查询商品 SKU。

## 搜索用户候选 · Java 网关

`GET /pm/user-options?keyword=li&limit=20`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": [
    {
      "userId": "1001",
      "realName": "李明",
      "deptId": "101"
    }
  ]
}
```

keyword 可选，匹配昵称或账号；limit 默认 50，上限 200。SQL 和 VO 仅投影这三个字段。

## 个人待办 · Java 网关

业务流程需要当前登录人处理一件事时创建待办；期限或内容变化时更新同一条；业务撤回时忽略该条，使它退出未完成队列，状态为 ignored。接口使用当前用户的 Bearer Token。归属人取登录身份；为其他用户自动派发业务待办需单独核对目标环境支持的业务来源接口。员工菜单上下文可沿用宿主传递的 X-Wise-Robot-Id。

### 创建

`POST /task/todoRecord`，Content-Type: application/json。title 必填。content、dueTime、priority、visibility、parentId、attachments 可选。priority 支持 normal、important、urgent；visibility 支持 normal、private。parentId 为关联任务的 ID。

```json
{
  "title": "复核合同 A-12",
  "content": "核对付款期限与签署主体",
  "dueTime": "2026-11-13 17:00:00",
  "priority": "important",
  "visibility": "private"
}
```

成功响应示例（节选）。Java 的长 ID 可能按数值或十进制字符串返回，客户端保留精度。

```json
{"code":200,"data":"20890001000000001"}
```

### 更新

`PUT /task/todoRecord/{id}`。id 为 todo_record.id，保存与业务单据的关联。按当前前端契约提交编辑后的完整表单，title 必填。保留原关联任务时带回 parentId，省略表示解除关联。attachments 省略表示保留，空数组清空，传列表表示整体替换。只改期限时也要保留其他应继续生效的表单值。

```json
{
  "title": "复核合同 A-12",
  "content": "核对付款期限与签署主体",
  "dueTime": "2026-11-16 17:00:00",
  "priority": "important",
  "visibility": "private"
}
```

成功响应（基于前端 void 契约的节选，业务只读取 code）：

```json
{"code":200}
```

### 取消

`POST /task/todoRecord/{id}/ignore`。使用待办记录主键，无请求体。例如业务撤回后请求 `POST /task/todoRecord/20890001000000001/ignore`。由待办归属人执行。这里“取消”对应产品里的“忽略”，完成事项另有 done 动作。

```json
{"code":200}
```

**版本核对。** 当前待办中心前端约定创建返回 todo_record.id。已查看的较早 Java 版本（dev 快照 272c795a）创建返回镜像 tk_task ID，ignore 直接使用待办记录 ID，且该控制器缺少 PUT 更新。首次接入一个环境时，用本人测试账号创建一条带唯一标题的待办，在待办中心核对记录主键，再验证修改与忽略。旧版本可从 GET /task/todoRecord/myPage 对应行的 todoRecordId 取得待办主键；更新接口需部署支持该契约的版本。已有的 .NET GET /api/personal-assistant/todos 是个人简报只读投影，其 Id 不用作以上写入契约。

## 应用发送消息

`POST /openapi/message/send`

请求体

```json
{
  "eventCode": "EVT_CONTRACT_REVIEWED",
  "audience": {
    "type": "USER",
    "ids": [
      1001
    ]
  },
  "params": {
    "contractNo": "A-12"
  },
  "idempotentKey": "contract-reviewed:A-12:rev3:1001"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "messageId": 8001,
    "recipientCount": 1,
    "duplicatedKey": false,
    "outcomes": [
      {
        "userId": 1001,
        "accepted": true,
        "channels": [
          "in-site"
        ],
        "source": "TENANT_DEFAULT",
        "failureReason": null
      }
    ]
  }
}
```

Java 网关，Content-Type: application/json。eventCode 必填，替换成应用已配置的编码。audience 必填，USER、ROLE、DEPT 分别传该租户非空的用户、角色、部门 ID 数组；ALL 省略 ids。params 按模板占位符传键值。默认使用 Token 租户。幂等键可选，同一业务变更重试时复用。code=200 后逐项读 accepted 和 failureReason，外部渠道最终状态以投递记录为准。40001 检查事件编码，40002 检查受众，40004 检查参数。


| 请求字段 | 类型与约束 |
| --- | --- |
| eventCode | string，必填。取应用已配置并在本环境登记的事件编码 |
| audience | object，必填。EMAIL 受众传 emails 字符串数组，最多 200 个；USER/ROLE/DEPT 传 ids；ALL 省略两者 |
| params | object，可选。键值对应模板变量。sender_name、sender_icon_url 为平台保留键 |
| senderName、senderIconUrl | 可选字符串，分别指定发送者显示名、头像 URL |
| attachments | 可选数组，每项含 fileName、fileUrl，可带 fileSize、fileType、ossId |
| idempotentKey | 可选字符串，同一业务变更重试使用同一个键。data.duplicatedKey=true 表示回放此前的受理结果 |

不用先查收件箱或订阅。应用在状态变更后直接发送，遍历 data.outcomes；accepted=false 或 failureReason 有值时记录收件人和原因。EMAIL 结果按 email 标识收件人，userId 可空。

