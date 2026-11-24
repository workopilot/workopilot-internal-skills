# 主数据、本人待办和消息发送

路径相对对应环境网关，GET 参数放 URL。示例为原始 HTTP 正文节选。Java 分页取 rows、total，普通查询取 data。ID 在客户端保留精度。

[主数据下拉/完整查询总表与 JSON 契约](master-data-queries.md) · [品牌与供应商查询及增删改查](brand-supplier.md)

本文的候选接口用于选择器，不代表全部记录。公司下拉当前复用完整 VO；部门 list 是完整部门列表的筛选用法。同步资料应按总表选完整列表/分页，并检查状态、权限与分页范围。

[文件、语音及审核](files-audit.md) · [迁移、快捷指令与成果](resources.md)
## 获取正常可见部门（完整列表筛选） · Java 网关

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

可选 deptName（名称）、status（字符串 "0" 正常、"1" 停用）；需要 system:dept:list 权限。使用 parentId 建树。要包含停用项则省略 status；专用轻量下拉使用 /system/dept/optionselect，完整契约见主数据总表。

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

同一分页协议，PRODUCT 特殊 SQL 从 mst_product 投影 id/tenantId/tagCode/dataKey/dataValue/dataConfig（imageUrl），不是完整产品字段。完整产品列表用 .NET /api/ProductManager/GetPharmaSkuList，包含停用项必须传 Status="ALL"；见主数据总表。

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

## 项目主数据候选项 · Java 网关

用于业务表单的关联项目下拉、按名称或治理编号搜索项目，以及通过已有项目 ID 确认名称。数据来自 `pm_project`，返回轻量字段。选择后将 `id` 作为业务表单中的 `projectId` 保存，展示名使用 `name`。

### 地址与鉴权

`GET /task/task/projects/options?limit=20&excludeClosed=true`

| 环境 | 完整请求地址 |
| --- | --- |
| 测试 | `https://agenttest.workopilot.com/prod-api/task/task/projects/options?limit=20&excludeClosed=true` |
| 生产 | `https://agent.workopilot.com/prod-api/task/task/projects/options?limit=20&excludeClosed=true` |

使用当前用户 Token，请求头为 `Authorization: Bearer <token>`。已有 SDK 或请求库沿用其会话与 Java 网关配置。租户隔离与逻辑删除由后端框架处理。员工菜单内调用时沿用已有封装传递的 `X-Wise-Robot-Id`；平台前端仅在路由带有员工 ID 时附加此头。

### 查询参数

GET 无 JSON 请求体，参数放 URL。下面的 JSON 表示交给请求库的查询参数对象。

```json
{
  "keyword": "合同",
  "limit": 20,
  "excludeClosed": true
}
```

| 字段 | 类型 | 必填 | 规则 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 匹配项目名称或治理编号，去除首尾空白。可解析为 Long 的纯数字还会精确匹配项目 ID。省略或空白时返回按 ID 倒序排列的最近项目 |
| `limit` | integer | 否 | 默认 20，小于 1 时按 20 处理，超过 50 时按 50 处理 |
| `excludeClosed` | boolean | 否 | 默认 `false`。传 `true` 在 SQL 中排除 `status = closed`，保留状态为空的历史数据。需要查询已结项项目时传 `false` 或省略 |

接口按 ID 倒序排序后限制条数。返回候选数组，没有分页总数；需要缩小范围时继续传 `keyword` 搜索。

### JSON 返回值与大小写

成功响应示例为原始 HTTP 正文节选，`msg` 随语言环境变化。所有下列键名区分大小写。

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": "20890001000000001",
      "name": "合同管理升级",
      "code": "PMO-202611-003",
      "status": "running"
    }
  ]
}
```

| 项目字段 | 类型 | 使用方式 |
| --- | --- | --- |
| `id` | string 或安全整数 | 项目主键，Java Long 超过 JavaScript 安全整数范围时序列化为字符串。调用方统一保留为字符串，避免用 Number 转换雪花 ID |
| `name` | string | 项目名称，用作下拉展示文字 |
| `code` | string，可空 | 治理编号，立项后才有，支持缺失或 null |
| `status` | string，可空 | `pending` 未立项、`drafting` 立项草稿、`running` 执行中、`closed` 已结项。兼容历史空值 |

外层 `code` 是业务成功状态，值为 200；项目对象中的 `code` 是治理编号。数组读取 `body.data`。无匹配时成功返回 `data: []`。登录失效或权限错误按当前项目统一错误处理流程处理，避免将失败响应显示成“无项目”。

### 接入示例

已有请求库返回解包后数据时可按平台前端的方式调用。先确认客户端已指向 Java 网关并注入 Token。

```typescript
const projects = await requestClient.get('/task/task/projects/options', {
  params: { keyword: searchText, limit: 20, excludeClosed: true },
});
const options = projects.map((project) => ({
  value: String(project.id),
  label: project.name,
}));
```

若当前库返回原始 JSON 正文，先验证 `body.code === 200`，再取 `body.data` 映射。下拉首次展开可省略关键词加载最近项目，输入时防抖搜索。编辑历史记录时保留已选项目的展示信息，尤其当它已结项而当前候选排除了已结项项目。

契约初次核对于 2026-11-18 的 `cef655e41`，本次 2026-11-24 再对 Java 远端 master 的 `dda8dbb3e` 中 `TkTaskController.projectOptions`、`TaskProjectServiceImpl.search` 复核，契约一致；并对照平台前端的 `taskProjectOptions` 和 `useRemoteProjects`。较早版本的控制器仅接收 `keyword`、`limit`，会忽略 `excludeClosed`。首次接入时用目标环境的已结项项目验证过滤行为，若仍返回该项目，核对 Java 服务部署版本。

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

