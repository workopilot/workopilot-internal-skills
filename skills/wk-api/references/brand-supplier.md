# 品牌与供应商主数据 · .NET 网关

契约核对：2026-11-24。已实现 6 个查询和 6 个写入接口，并通过本地 HTTP 测试；本次未验证测试/生产是否已经部署。首次接入先确认目标环境已发布这些接口并执行 3.122 建表迁移；平台管理菜单另需 3.124 菜单迁移。

用于选择品牌/供应商、同步完整档案，以及在数字员工菜单中维护资料。菜单和 MCP 工具调用同一接口；新增、修改、删除按当前业务操作意图执行，资源实施仍由 wk-setup 核对环境。不要把这些 Token 接口当作 API Key 实施接口。

## 目录

- [接入约定](#接入约定) · [环境地址](#环境地址)
- [接口与使用场景](#接口与使用场景) · [查询参数](#查询参数)
- [下拉请求与完整返回示例](#下拉请求与完整返回示例)
- [品牌分页](#品牌分页请求与完整返回示例) · [品牌详情](#品牌详情请求与完整返回示例)
- [供应商分页](#供应商分页请求与完整返回示例) · [供应商详情](#供应商详情请求与完整返回示例)
- [字段定义](#字段定义) · [错误语义](#错误语义)
- [写入接口与更新约定](#写入接口管理页面配套)
- [品牌新增及更新](#品牌请求与响应) · [供应商新增及更新](#供应商请求与响应)
- [删除及错误响应](#删除及错误响应)

## 接入约定

- 先按 [wk-api 入口](../SKILL.md) 检查调用方已有请求封装和 Token 来源。本文地址相对 .NET 基址；请求库已包含 /net-api 时直接传 /api/mst/...，不要重复前缀。
- 查询使用 GET，无 JSON 请求体。参数放 URL query，详情 ID 放路径。写入接口见文末：POST 新增、PUT 更新、DELETE 删除。请求头：`Authorization: Bearer <当前用户Token>`。API Key 不能替代用户 Token。
- 服务端路由不含 /net-api，网关转发时去掉该前缀。
- 登录身份必须包含租户。全部查询强制限定当前租户，不接受 tenantId 作为查询条件。当前为租户内登录用户可读目录，无额外部门/负责人过滤或主数据专用角色授权。
- 响应 Content-Type 为 application/json。外层为 `code/msg/data/total/rows`；内层字段由 JsonProperty 显式固定为 lowerCamelCase。不要套用其他 .NET 接口的 PascalCase。
- 所有 ID（id、logoFileId、ownerUserId、createBy、updateBy）为十进制字符串或 null，避免 JavaScript 精度丢失。enabled 是数字 0/1，version、sortIndex、total 是数字。日期为 `yyyy-MM-dd HH:mm:ss`，遵循现有系统时间约定，不带时区。
- 列表读取 `rows` 和 `total`，详情/下拉读取 `data`；无记录时列表 rows=[]、total=0，下拉 data=[]。全量是完整资料字段，全部记录需要逐页读取；跨页查询不提供快照一致性。
- 列表、详情按显式实体模型返回品牌 20 个、供应商 29 个字段，包含档案、评级、状态、联系人及审计信息。未返回银行账户等不存在的字段。下拉只投影 id/code/name/shortName。
- 排序固定为 sortIndex 升序，再 id 升序；不接受 SQL 排序表达式。

## 环境地址

| 环境 | .NET 基址 | 品牌下拉完整地址示例 |
| --- | --- | --- |
| 测试 | https://agenttest.workopilot.com/net-api | https://agenttest.workopilot.com/net-api/api/mst/brands/options?limit=20 |
| 生产 | https://agent.workopilot.com/net-api | https://agent.workopilot.com/net-api/api/mst/brands/options?limit=20 |

完整 URL = .NET 基址 + 下列相对地址。宿主 SDK 选择 net 网关，自有框架从环境配置读取基址；此处列出地址不代表目标环境已部署。

## 接口与使用场景

| 场景 | 方法及相对地址 | 返回位置 |
| --- | --- | --- |
| 品牌选择器 | GET /api/mst/brands/options | data 数组；仅 enabled=1 |
| 品牌目录、同步档案 | GET /api/mst/brands/page | rows、total；默认包含停用 |
| 品牌详情、历史引用回显 | GET /api/mst/brands/{id} | data；允许读取停用档案 |
| 可合作供应商选择器 | GET /api/mst/suppliers/options | data 数组；仅 enabled=1 且 status=active |
| 供应商目录、评级/状态筛选 | GET /api/mst/suppliers/page | rows、total；默认全部状态及启停 |
| 供应商详情、历史引用回显 | GET /api/mst/suppliers/{id} | data；允许读取停用或非合作状态 |

新建表没有预置业务数据，可通过品牌/供应商管理页面或文末写入接口维护；暂不提供批量导入接口。

## 查询参数

两类 options 通用：

| 参数 | 类型 | 必填/默认 | 规则 |
| --- | --- | --- | --- |
| keyword | string | 否 | 最长 200 字符；去首尾空白后，按编码、名称或简称包含匹配；空白等同不筛选 |
| limit | integer | 否，20 | 1–100；超过返回 400；无分页总数，更多记录使用 page |

两类 page 通用：

| 参数 | 类型 | 必填/默认 | 规则 |
| --- | --- | --- | --- |
| keyword | string | 否 | 同下拉查询 |
| pageNum | integer | 否，1 | 1–1000000 |
| pageSize | integer | 否，20 | 1–200 |
| enabled | integer | 否 | 0 停用，1 启用；省略包含两者 |

suppliers/page 额外支持：

| 参数 | 类型 | 必填/默认 | 规则 |
| --- | --- | --- | --- |
| status | string | 否 | pending 待审核、active 正常合作、suspended 暂停合作、terminated 终止合作；严格小写 |
| rating | string | 否 | A、B、C、D；严格大写 |
| unratedOnly | boolean | 否，false | true 仅返回 rating IS NULL；不得与 rating 同时传入 |

两类详情的 id 为必填路径参数，正的 Int64 十进制字符串，范围 1–9223372036854775807。

## 查询参数 JSON 示例

以下是交给当前请求库的 params 对象，不是 GET 请求体。省略筛选项代表不筛选；不要发 JSON null 文本作为 query 值。

下拉：
```json
{"keyword":"示例","limit":20}
```
品牌分页（含停用）：
```json
{"pageNum":1,"pageSize":20}
```
供应商分页（启用、正常合作、A 级）：
```json
{"pageNum":1,"pageSize":20,"enabled":1,"status":"active","rating":"A"}
```
供应商未评级：
```json
{"pageNum":1,"pageSize":20,"unratedOnly":true}
```
详情路径参数：
```json
{"id":"9007199254740993"}
```

## 下拉请求与完整返回示例

品牌：
`GET /api/mst/brands/options?keyword=BR&limit=20`

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": "9007199254740993",
      "code": "BR-001",
      "name": "示例品牌",
      "shortName": null
    }
  ],
  "total": 0,
  "rows": null
}
```

供应商：
`GET /api/mst/suppliers/options?keyword=SUP&limit=20`

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": "9007199254740993",
      "code": "SUP-001",
      "name": "示例供应商",
      "shortName": null
    }
  ],
  "total": 0,
  "rows": null
}
```

此处 total=0 是公共响应模型默认值，不能作为下拉匹配数量。下拉数量取 data.length。

## 品牌分页请求与完整返回示例

`GET /api/mst/brands/page?pageNum=1&pageSize=20&enabled=1&keyword=BR`

```json
{
  "code": 200,
  "msg": "success",
  "data": null,
  "total": 1,
  "rows": [
    {
      "id": "9007199254740993",
      "tenantId": "tenant-demo",
      "code": "BR-001",
      "name": "示例品牌",
      "shortName": null,
      "nameEn": null,
      "logoFileId": null,
      "websiteUrl": null,
      "originCountryCode": null,
      "ownerName": null,
      "description": null,
      "enabled": 1,
      "sortIndex": 0,
      "ownerUserId": null,
      "remark": null,
      "version": 0,
      "createBy": null,
      "createTime": "2026-11-24 10:00:00",
      "updateBy": null,
      "updateTime": "2026-11-24 10:00:00"
    }
  ]
}
```

## 品牌详情请求与完整返回示例

`GET /api/mst/brands/9007199254740993`

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": "9007199254740993",
    "tenantId": "tenant-demo",
    "code": "BR-001",
    "name": "示例品牌",
    "shortName": null,
    "nameEn": null,
    "logoFileId": null,
    "websiteUrl": null,
    "originCountryCode": null,
    "ownerName": null,
    "description": null,
    "enabled": 1,
    "sortIndex": 0,
    "ownerUserId": null,
    "remark": null,
    "version": 0,
    "createBy": null,
    "createTime": "2026-11-24 10:00:00",
    "updateBy": null,
    "updateTime": "2026-11-24 10:00:00"
  },
  "total": 0,
  "rows": null
}
```

## 供应商分页请求与完整返回示例

`GET /api/mst/suppliers/page?pageNum=1&pageSize=20&enabled=1&status=active&rating=A&keyword=SUP`

查询未评级供应商改用 `?pageNum=1&pageSize=20&unratedOnly=true`，不再传 rating。

```json
{
  "code": 200,
  "msg": "success",
  "data": null,
  "total": 1,
  "rows": [
    {
      "id": "9007199254740993",
      "tenantId": "tenant-demo",
      "code": "SUP-001",
      "name": "示例供应商",
      "shortName": null,
      "nameEn": null,
      "entityType": "enterprise",
      "registrationCountryCode": null,
      "registrationIdType": null,
      "registrationNo": null,
      "legalRepresentative": null,
      "registeredAddress": null,
      "businessAddress": null,
      "contactName": null,
      "contactPhone": null,
      "contactEmail": null,
      "websiteUrl": null,
      "businessScope": null,
      "rating": "A",
      "status": "active",
      "enabled": 1,
      "sortIndex": 0,
      "ownerUserId": null,
      "remark": null,
      "version": 0,
      "createBy": null,
      "createTime": "2026-11-24 10:00:00",
      "updateBy": null,
      "updateTime": "2026-11-24 10:00:00"
    }
  ]
}
```

## 供应商详情请求与完整返回示例

`GET /api/mst/suppliers/9007199254740993`

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": "9007199254740993",
    "tenantId": "tenant-demo",
    "code": "SUP-001",
    "name": "示例供应商",
    "shortName": null,
    "nameEn": null,
    "entityType": "enterprise",
    "registrationCountryCode": null,
    "registrationIdType": null,
    "registrationNo": null,
    "legalRepresentative": null,
    "registeredAddress": null,
    "businessAddress": null,
    "contactName": null,
    "contactPhone": null,
    "contactEmail": null,
    "websiteUrl": null,
    "businessScope": null,
    "rating": "A",
    "status": "active",
    "enabled": 1,
    "sortIndex": 0,
    "ownerUserId": null,
    "remark": null,
    "version": 0,
    "createBy": null,
    "createTime": "2026-11-24 10:00:00",
    "updateBy": null,
    "updateTime": "2026-11-24 10:00:00"
  },
  "total": 0,
  "rows": null
}
```

## 字段定义

字段类型、含义、空值与数据库列的一一映射如下。可空字段的 null 会保留；不会省略键。

### 品牌（mst_brand）

| JSON 字段 | JSON 类型 | 可空 | 含义 / 数据库列 |
| --- | --- | --- | --- |
| id | string | 否 | 档案 ID；id |
| tenantId | string | 否 | 当前租户 ID；tenant_id |
| code | string | 否 | 租户内唯一编码；code |
| name | string | 否 | 品牌正式名 / 供应商主体全称；name |
| shortName | string | 是 | 简称；short_name |
| nameEn | string | 是 | 英文名；name_en |
| logoFileId | string | 是 | Logo 文件 ID，访问地址由文件服务解析；logo_file_id |
| websiteUrl | string | 是 | 官网；website_url |
| originCountryCode | string | 是 | 品牌来源国家/地区编码；origin_country_code |
| ownerName | string | 是 | 品牌权利人名称；owner_name |
| description | string | 是 | 品牌介绍；description |
| enabled | number | 否 | 档案启用：0/1；enabled |
| sortIndex | number | 否 | 排序值，越小越前；sort_index |
| ownerUserId | string | 是 | 内部维护负责人 ID；owner_user_id |
| remark | string | 是 | 备注；remark |
| version | number | 否 | 乐观锁版本；查询不修改；version |
| createBy | string | 是 | 创建人 ID；create_by |
| createTime | string | 否 | 创建时间；create_time |
| updateBy | string | 是 | 修改人 ID；update_by |
| updateTime | string | 否 | 修改时间；update_time |

### 供应商（mst_supplier）

| JSON 字段 | JSON 类型 | 可空 | 含义 / 数据库列 |
| --- | --- | --- | --- |
| id | string | 否 | 档案 ID；id |
| tenantId | string | 否 | 当前租户 ID；tenant_id |
| code | string | 否 | 租户内唯一编码；code |
| name | string | 否 | 品牌正式名 / 供应商主体全称；name |
| shortName | string | 是 | 简称；short_name |
| nameEn | string | 是 | 英文名；name_en |
| entityType | string | 否 | enterprise 企业 / individual_business 个体工商户 / individual 自然人 / other 其他；entity_type |
| registrationCountryCode | string | 是 | 登记国家/地区编码；registration_country_code |
| registrationIdType | string | 是 | 登记证件类型，如 CN_USCC；registration_id_type |
| registrationNo | string | 是 | 登记号码，如统一社会信用代码；登记三项同时填写或同时为空；registration_no |
| legalRepresentative | string | 是 | 法定代表人；legal_representative |
| registeredAddress | string | 是 | 注册地址；registered_address |
| businessAddress | string | 是 | 经营地址；business_address |
| contactName | string | 是 | 主联系人；contact_name |
| contactPhone | string | 是 | 联系电话；contact_phone |
| contactEmail | string | 是 | 联系邮箱；contact_email |
| websiteUrl | string | 是 | 官网；website_url |
| businessScope | string | 是 | 供货/服务范围；business_scope |
| rating | string | 是 | A/B/C/D；null 为未评级；rating |
| status | string | 否 | pending/active/suspended/terminated；status |
| enabled | number | 否 | 档案启用：0/1；enabled |
| sortIndex | number | 否 | 排序值，越小越前；sort_index |
| ownerUserId | string | 是 | 内部维护负责人 ID；owner_user_id |
| remark | string | 是 | 备注；remark |
| version | number | 否 | 乐观锁版本；查询不修改；version |
| createBy | string | 是 | 创建人 ID；create_by |
| createTime | string | 否 | 创建时间；create_time |
| updateBy | string | 是 | 修改人 ID；update_by |
| updateTime | string | 否 | 修改时间；update_time |

## 错误语义

HTTP 状态应先于解析业务数据检查。不同错误阶段沿用 ASP.NET Core 现有机制：

| HTTP | 情况 | 响应 |
| --- | --- | --- |
| 400 | 参数类型/范围/枚举错误，由 ApiController 自动校验 | 标准 ValidationProblemDetails，含 status=400 和 errors 字段；不要依赖 code 存在 |
| 400 | id<=0、rating 与 unratedOnly 冲突 | ApiResult，code=400 |
| 401 | 无 Token、Token 无效或过期 | 现有认证中间件处理；不能假设响应有 JSON 数据 |
| 403 | 已认证但缺少租户 | ApiResult，code=403 |
| 404 | ID 不存在或属于其他租户 | ApiResult，code=404；两种情况不区分 |
| 500 | 数据库或其他内部错误 | ApiResult，code=500；只返回通用提示，详细异常记录日志 |

供应商未找到（HTTP 404）：
```json
{
  "code": 404,
  "msg": "供应商不存在",
  "data": null,
  "total": 0,
  "rows": null
}
```

筛选条件冲突（HTTP 400）：
```json
{
  "code": 400,
  "msg": "rating 与 unratedOnly=true 不能同时使用",
  "data": null,
  "total": 0,
  "rows": null
}
```

参数范围错误（HTTP 400，traceId 是运行时生成值）：
```json
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Limit": [
      "The field Limit must be between 1 and 100."
    ]
  },
  "traceId": "<运行时追踪ID>"
}
```

表未建或数据库故障也返回 HTTP 500，不伪装成空列表。由实施/发布方确认 3.122 建表已执行，再使用已部署版本访问以上接口。

## 写入接口（管理页面配套）

统一网关前缀 `/net-api`，沿用用户 Token；额外要求当前身份有有效 userId。缺租户/用户为 HTTP 403。租户内登录用户可维护，与现有商品管理相同；菜单可见范围不等于接口级角色授权。

| 方法 / 相对地址 | 场景 | 参数 |
| --- | --- | --- |
| POST /api/mst/brands | 新增品牌 | BrandWriteRequest JSON |
| PUT /api/mst/brands/{id} | 更新品牌 | 相同 JSON + 必填 version |
| DELETE /api/mst/brands/{id}?version=0 | 删除品牌 | 路径 id + 必填 query version，无请求体 |
| POST /api/mst/suppliers | 新增供应商 | SupplierWriteRequest JSON |
| PUT /api/mst/suppliers/{id} | 更新供应商 | 相同 JSON + 必填 version |
| DELETE /api/mst/suppliers/{id}?version=0 | 删除供应商 | 路径 id + 必填 query version，无请求体 |

### 参数与更新约定

- JSON 使用 lowerCamelCase，`Content-Type: application/json`。id 是路径中的正 Int64 字符串。
- code、name 必填，分别最长 100/200 字符；去首尾空格，空白非法。code 租户内唯一，冲突 HTTP 409，数据库唯一索引兜底并发冲突。
- enabled 数字 0/1，省略默认 1；sortIndex 为 Int32，省略默认 0；version 更新必填，范围 0–2147483646，新建不必传 version，若传仍校验范围，实际保存固定为 0。删除 version 是非负 Int32。
- 两类共有可写字符串：shortName(100)、nameEn(200)、websiteUrl(500)、remark(1000)。websiteUrl 有值时必须为 http/https 绝对 URL。
- 品牌额外可写：originCountryCode(32)、ownerName(200)、description(20000)。括号为最大字符数。
- 供应商额外可写：entityType(32，默认 enterprise，枚举同查询)、registrationCountryCode(32)、registrationIdType(32)、registrationNo(100)、legalRepresentative(100)、registeredAddress(500)、businessAddress(500)、contactName(100)、contactPhone(50)、contactEmail(254)、businessScope(1000)、rating(1，可空 A/B/C/D)、status(20，默认 pending，严格小写枚举同查询)。
- 可选字符串省略或空白转 null。登记三项必须同时填写或同时留空；国家、证件类型转大写，CN_USCC 号码转大写。联系邮箱有值时验证格式。重复登记主体 HTTP 409。
- **PUT 是完整表单更新**：发送全部要保留的可写字段，省略的可选字段会清空/恢复默认值；不是 PATCH。应先 GET 详情，再提交修改内容及其 version。
- id、tenantId、ownerUserId、logoFileId、createBy/createTime/updateBy/updateTime 不属于写入模型，客户端不能覆盖。原有 ownerUserId/logoFileId 在更新中保持不变；新增默认为空。审计人来自会话，审计时间由服务端生成。
- 更新同时检查 id、tenantId、version，并递增 version。旧版本返回 HTTP 409，提示重新加载；不要自动重试覆盖。
- 删除为物理删除；页面要求用户确认名称、编码并提示不可恢复，需保留历史时用 enabled=0 停用。当前两表无业务关联，未来增加引用时必须同步增加引用保护。

### 品牌请求与响应

`POST /api/mst/brands`：
```json
{
  "code": "BR-002",
  "name": "示例品牌二",
  "shortName": null,
  "nameEn": null,
  "websiteUrl": null,
  "remark": null,
  "originCountryCode": null,
  "ownerName": null,
  "description": null,
  "enabled": 1,
  "sortIndex": 0
}
```

创建成功 HTTP 200：
```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "code": "BR-002",
    "name": "示例品牌二",
    "shortName": null,
    "nameEn": null,
    "websiteUrl": null,
    "remark": null,
    "originCountryCode": null,
    "ownerName": null,
    "description": null,
    "enabled": 1,
    "sortIndex": 0,
    "logoFileId": null,
    "id": "9007199254740994",
    "tenantId": "tenant-demo",
    "ownerUserId": null,
    "version": 0,
    "createBy": "42",
    "createTime": "2026-11-24 10:00:00",
    "updateBy": "42",
    "updateTime": "2026-11-24 10:00:00"
  },
  "total": 0,
  "rows": null
}
```

完整更新请求 `PUT /api/mst/brands/9007199254740994`：

```json
{
  "code": "BR-002",
  "name": "示例品牌二（已更新）",
  "shortName": null,
  "nameEn": null,
  "websiteUrl": null,
  "remark": null,
  "originCountryCode": null,
  "ownerName": null,
  "description": null,
  "enabled": 1,
  "sortIndex": 0,
  "version": 0
}
```

更新成功 HTTP 200：

```json
{
  "code": 200,
  "msg": "保存成功",
  "data": {
    "code": "BR-002",
    "name": "示例品牌二（已更新）",
    "shortName": null,
    "nameEn": null,
    "websiteUrl": null,
    "remark": null,
    "originCountryCode": null,
    "ownerName": null,
    "description": null,
    "enabled": 1,
    "sortIndex": 0,
    "logoFileId": null,
    "id": "9007199254740994",
    "tenantId": "tenant-demo",
    "ownerUserId": null,
    "version": 1,
    "createBy": "42",
    "createTime": "2026-11-24 10:00:00",
    "updateBy": "42",
    "updateTime": "2026-11-24 11:00:00"
  },
  "total": 0,
  "rows": null
}
```



更新保留 createBy/createTime；updateBy/updateTime 记录本次操作者和时间。

### 供应商请求与响应

`POST /api/mst/suppliers`：
```json
{
  "code": "SUP-002",
  "name": "示例供应商二",
  "shortName": null,
  "nameEn": null,
  "websiteUrl": null,
  "remark": null,
  "entityType": "enterprise",
  "registrationCountryCode": null,
  "registrationIdType": null,
  "registrationNo": null,
  "legalRepresentative": null,
  "registeredAddress": null,
  "businessAddress": null,
  "contactName": null,
  "contactPhone": null,
  "contactEmail": null,
  "businessScope": null,
  "rating": null,
  "status": "pending",
  "enabled": 1,
  "sortIndex": 0
}
```

创建成功 HTTP 200：
```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "code": "SUP-002",
    "name": "示例供应商二",
    "shortName": null,
    "nameEn": null,
    "websiteUrl": null,
    "remark": null,
    "entityType": "enterprise",
    "registrationCountryCode": null,
    "registrationIdType": null,
    "registrationNo": null,
    "legalRepresentative": null,
    "registeredAddress": null,
    "businessAddress": null,
    "contactName": null,
    "contactPhone": null,
    "contactEmail": null,
    "businessScope": null,
    "rating": null,
    "status": "pending",
    "enabled": 1,
    "sortIndex": 0,
    "id": "9007199254740994",
    "tenantId": "tenant-demo",
    "ownerUserId": null,
    "version": 0,
    "createBy": "42",
    "createTime": "2026-11-24 10:00:00",
    "updateBy": "42",
    "updateTime": "2026-11-24 10:00:00"
  },
  "total": 0,
  "rows": null
}
```

完整更新请求 `PUT /api/mst/suppliers/9007199254740994`：

```json
{
  "code": "SUP-002",
  "name": "示例供应商二（已更新）",
  "shortName": null,
  "nameEn": null,
  "websiteUrl": null,
  "remark": null,
  "entityType": "enterprise",
  "registrationCountryCode": null,
  "registrationIdType": null,
  "registrationNo": null,
  "legalRepresentative": null,
  "registeredAddress": null,
  "businessAddress": null,
  "contactName": null,
  "contactPhone": null,
  "contactEmail": null,
  "businessScope": null,
  "rating": null,
  "status": "pending",
  "enabled": 1,
  "sortIndex": 0,
  "version": 0
}
```

更新成功 HTTP 200：

```json
{
  "code": 200,
  "msg": "保存成功",
  "data": {
    "code": "SUP-002",
    "name": "示例供应商二（已更新）",
    "shortName": null,
    "nameEn": null,
    "websiteUrl": null,
    "remark": null,
    "entityType": "enterprise",
    "registrationCountryCode": null,
    "registrationIdType": null,
    "registrationNo": null,
    "legalRepresentative": null,
    "registeredAddress": null,
    "businessAddress": null,
    "contactName": null,
    "contactPhone": null,
    "contactEmail": null,
    "businessScope": null,
    "rating": null,
    "status": "pending",
    "enabled": 1,
    "sortIndex": 0,
    "id": "9007199254740994",
    "tenantId": "tenant-demo",
    "ownerUserId": null,
    "version": 1,
    "createBy": "42",
    "createTime": "2026-11-24 10:00:00",
    "updateBy": "42",
    "updateTime": "2026-11-24 11:00:00"
  },
  "total": 0,
  "rows": null
}
```



更新成功规则与品牌相同。仅记录 status，不自动执行审批工作流。

### 删除及错误响应

`DELETE /api/mst/suppliers/9007199254740994?version=1`；品牌替换资源为 brands。

删除成功 HTTP 200：
```json
{
  "code": 200,
  "msg": "删除成功",
  "data": true,
  "total": 0,
  "rows": null
}
```

更新发生版本冲突 HTTP 409：
```json
{
  "code": 409,
  "msg": "档案已被修改，请重新加载后再编辑",
  "data": null,
  "total": 0,
  "rows": null
}
```

重复编码/登记主体同为 HTTP 409，msg 指明冲突项。跨租户和不存在统一返回 HTTP 404。删除服务返回的 404/409 使用 ApiResult<bool>，data 为 false；控制器捕获的参数、身份或内部异常使用 ApiResult<object>，data 为 null。其他字段仍为 code/msg/total/rows；调用方必须检查 HTTP/code，不应依赖 data 判断错误类型。非法字段 HTTP 400，自动模型校验或服务校验的两种响应结构沿用前述错误语义。数据库内部错误 HTTP 500，仅记录完整日志。

### 核对依据

依据 MasterDataController、MasterDataQueryService（查询和写入）、MasterDataQuery/WriteRequest、MstBrand/MstSupplier 的 JSON 别名及 MVC 序列化配置，并对照平台前端 master-data.ts。26 项隔离 HTTP 测试覆盖查询/写入、跨租户、字段大小写、大整数 ID、非法参数、唯一性与并发版本冲突。目标环境部署状态仍需首次接入验证。
