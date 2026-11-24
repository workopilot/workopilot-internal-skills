# 主数据查询：下拉、完整字段与全部记录

核对日期：2026-11-24。依据后端控制器、服务、查询 SQL、返回 VO/DTO 和前端实际调用核对；这是代码契约，不代表目标环境已发布。本页覆盖产品、公司、用户、部门、项目、合同；品牌和供应商的完整查询与增删改查见 [品牌与供应商](brand-supplier.md)。

## 目录

- [接口分类总表](#接口分类总表)
- [接入及全部记录的含义](#接入及全部记录的含义)
- [产品](#产品)
- [公司](#公司)
- [用户](#用户)
- [部门](#部门)
- [项目](#项目)
- [合同](#合同)
- [错误处理与尚缺能力](#错误处理与尚缺能力)

## 接口分类总表

本表故意包含网关前缀，便于辨认 Java 与 .NET；后续各节写相对基址的路径。若请求库已配置基址，不要再拼一次 /prod-api 或 /net-api。

| 主数据 | 下拉/候选接口 | 完整字段列表 / 获取全部记录 | 单条详情 | 范围与限制 |
| --- | --- | --- | --- | --- |
| 产品 | GET /prod-api/mst/commonData/pageForDown?tagCode=PRODUCT | POST /net-api/api/ProductManager/GetPharmaSkuList；JSON 中 Status="ALL"，逐页读取 | GET /net-api/api/ProductManager/GetPharmaSku?id={id} | 当前租户；列表默认仅启用；下拉仅选取商品标识/名称等少量字段 |
| 公司 | GET /prod-api/mst/commonData/pageForDown?tagCode=COMPANY | GET /prod-api/mst/commonData/list?tagCode=COMPANY 不分页；大数据量用 /mst/commonData/page 分页 | GET /prod-api/mst/commonData/getInfo?id={id} | 当前租户通用主数据；不传 status 包含启停；公司下拉当前实际复用完整 VO |
| 用户 | GET /prod-api/pm/user-options | GET /prod-api/system/user/list，逐页读取，不传 status | GET /prod-api/system/user/{userId}，用户在 data.user | 当前会话可见用户；排除删除和匹配系统账号过滤规则的记录；不含密码，不代表数据库所有列 |
| 部门 | GET /prod-api/system/dept/optionselect | GET /prod-api/system/dept/list，不分页，不传 status | GET /prod-api/system/dept/{deptId} | 权限范围内未删除部门；list?status=0 只是正常部门；optionselect 只正常部门 |
| 项目 | GET /prod-api/task/task/projects/options | GET /prod-api/pm/projects/manage-page?scope=portfolio，逐页读取 | GET /prod-api/pm/projects/{projectId} | 当前租户项目台账，默认不排除未立项/草稿/结项；scope=mine 进一步缩小范围 |
| 合同 | 尚无专用合同记录下拉；可在有权限的本人列表上做选择器 | GET /prod-api/aichat/contractRecord/list，逐页读取，仅本人生成记录 | GET /prod-api/aichat/contractRecord/{id} | 尚不能获取租户全部合同；列表是摘要，正文结构需要详情 |
| 品牌 | GET /net-api/api/mst/brands/options | GET /net-api/api/mst/brands/page，逐页读取 | GET /net-api/api/mst/brands/{id} | 当前租户；page 默认含启停；options 仅启用；需目标环境部署 |
| 供应商 | GET /net-api/api/mst/suppliers/options | GET /net-api/api/mst/suppliers/page，逐页读取 | GET /net-api/api/mst/suppliers/{id} | 当前租户；page 默认全部评级/状态/启停；options 仅启用且 active；需目标环境部署 |

## 接入及全部记录的含义

- 先按 [技能入口](../SKILL.md) 检查当前项目的运行环境、Token 来源、现有 HTTP 请求封装及解包层级。统一使用用户 Token：Authorization: Bearer <token>。不要用 API Key 替代，不把超级管理员会话交给第三方应用。
- Java 基址：测试 https://agenttest.workopilot.com/prod-api，生产 https://agent.workopilot.com/prod-api。.NET 基址：测试 https://agenttest.workopilot.com/net-api，生产 https://agent.workopilot.com/net-api。
- GET 没有 JSON 请求体。下文 GET 的 JSON 表示请求库 params 对象，最终编码进 URL；省略可选筛选项，不发送字符串 "null"。POST 产品列表使用 JSON body 和 Content-Type: application/json。
- “完整字段”指接口公开的 VO/DTO 字段，**不是数据库所有列**；“全部记录”指逐页读完当前租户、权限和筛选范围内的数据，不包括已删除项或不可见记录。详情、列表、下拉不互相替代。
- Java 普通返回读 body.data；普通分页读 body.rows/body.total；项目台账例外为 body.data.rows/body.data.total。.NET 产品列表读 body.rows/body.total，其行字段是 PascalCase；品牌/供应商行字段是显式 lowerCamelCase。
- Java Long 字段由序列化配置决定安全整数/十进制字符串表现，客户端保留精度；.NET long/long? 非空值固定十进制字符串。不要 Number(id)。本文 Java 示例用小整数，String 类型的项目 ID 用字符串。
- 示例值均为虚构；为展示字段清单，示例保留可空字段。Java 空字段可能因序列化配置省略，翻译字段也可能无值。不要将示例 null 当作实际记录一定为空；对可选字段作空值兼容。响应示例省略不影响读取的 msg 等元数据。
- 分页从 1 开始，显式传 pageNum/pageSize。Java 通用 PageQuery 未传 pageSize 时默认 Integer.MAX_VALUE，不要依赖这个默认去拉大表；集成端建议每页 20–100 条。每页成功后累积并按主键去重，读取到累计覆盖 total 或空页停止；遇到失败停止并保留已读页，不把失败当空列表。同步期间增删可能影响总数，接口不提供跨页快照或变更游标。
- 名称筛选、status、mine 等条件会改变“全部”的范围；同步全部可见状态时按各节要求清除筛选。业务界面只选一个对象时使用下拉；数字员工的目录查询菜单/MCP 使用完整列表；需要正文或编辑回显再读详情。

## 产品

### 完整字段分页

`POST /api/ProductManager/GetPharmaSkuList`，.NET。完整测试 URL：https://agenttest.workopilot.com/net-api/api/ProductManager/GetPharmaSkuList。

请求 JSON：

```json
{
  "pageNum": 1,
  "pageSize": 20,
  "keyWord": "",
  "Category": null,
  "Company": null,
  "Status": "ALL"
}
```

| 请求字段 | JSON 类型 | 默认 / 规则 |
| --- | --- | --- |
| pageNum | integer | 从 1 开始，<=0 按 1 |
| pageSize | integer | <=0 按 15；建议显式 20–100，当前接口未设同样的上限校验 |
| keyWord | string / null | 按 Code、Name、GenericName、Manufacturer 包含匹配，注意 W 大写 |
| Category | string / null | 精确匹配分类名称 |
| Company | string / null | 精确匹配 CompanyCode |
| Status | string / null | ALL 或 全部：所有启停状态；启用/1：1；停用/0：0；省略、空或其他值默认只查 1 |

成功正文（Product 完整字段，字段名保留 PascalCase）：

```json
{
  "code": 200,
  "rows": [
    {
      "Id": "9007199254740993",
      "TenantId": "demo",
      "Code": "SKU001",
      "Name": "示例产品",
      "GenericName": null,
      "BrandName": "示例品牌",
      "Manufacturer": null,
      "ApprovalNo": null,
      "OriginName": null,
      "CategoryCode": null,
      "Category": null,
      "SubCategoryCode": null,
      "SubCategory": null,
      "Introduction": null,
      "IndicationTags": "[]",
      "DeptTags": "[]",
      "KeywordTags": "[]",
      "Spec": null,
      "DosageForm": null,
      "Unit": null,
      "PackQty": 1,
      "InsuranceType": null,
      "ListPrice": 100.0,
      "SalePrice": null,
      "StockQty": 0,
      "StockUnit": null,
      "ImageUrl": null,
      "DetailUrl": null,
      "Enabled": 1,
      "SortIndex": 0,
      "CompanyCode": "COMP001",
      "CompanyName": "示例公司",
      "IntColumn1": 0,
      "CreateBy": null,
      "CreateTime": "2026-11-24 10:00:00",
      "UpdateBy": null,
      "UpdateTime": null
    }
  ],
  "total": 1,
  "msg": "success",
  "data": null
}
```

类型：Id/CreateBy/UpdateBy 为字符串 ID（后两项可空）；PackQty/StockQty/Enabled/SortIndex/IntColumn1 为整数；ListPrice/SalePrice 为 number 或 null；CreateTime/UpdateTime 为日期时间字符串或 null；其余为字符串或 null。IndicationTags、DeptTags、KeywordTags 是存储 JSON 的字符串，不是直接数组；需要时解析并容错。Enabled 为 1 启用、0 停用。

### 单条完整详情

`GET /api/ProductManager/GetPharmaSku?id=9007199254740993`。参数对象：

```json
{
  "id": "9007199254740993"
}
```

成功正文（与列表行同一 Product 结构）：

```json
{
  "code": 200,
  "data": {
    "Id": "9007199254740993",
    "TenantId": "demo",
    "Code": "SKU001",
    "Name": "示例产品",
    "GenericName": null,
    "BrandName": "示例品牌",
    "Manufacturer": null,
    "ApprovalNo": null,
    "OriginName": null,
    "CategoryCode": null,
    "Category": null,
    "SubCategoryCode": null,
    "SubCategory": null,
    "Introduction": null,
    "IndicationTags": "[]",
    "DeptTags": "[]",
    "KeywordTags": "[]",
    "Spec": null,
    "DosageForm": null,
    "Unit": null,
    "PackQty": 1,
    "InsuranceType": null,
    "ListPrice": 100.0,
    "SalePrice": null,
    "StockQty": 0,
    "StockUnit": null,
    "ImageUrl": null,
    "DetailUrl": null,
    "Enabled": 1,
    "SortIndex": 0,
    "CompanyCode": "COMP001",
    "CompanyName": "示例公司",
    "IntColumn1": 0,
    "CreateBy": null,
    "CreateTime": "2026-11-24 10:00:00",
    "UpdateBy": null,
    "UpdateTime": null
  },
  "msg": "success",
  "rows": null,
  "total": 0
}
```

未找到返回 body.code=404、msg="产品不存在"；此旧接口返回 ApiResult，并未把该业务码主动映射为 HTTP 404，必须同时判断 body.code。查询异常 body.code=500。详情不要求 Enabled=1，可回显历史引用。

### 下拉与完整查询的区别

`GET /mst/commonData/pageForDown`，Java；参数：

```json
{
  "tagCode": "PRODUCT",
  "dataKey": "示例",
  "pageNum": 1,
  "pageSize": 20
}
```

```json
{
  "code": 200,
  "rows": [
    {
      "id": 1001,
      "tenantId": "demo",
      "tagCode": "PRODUCT",
      "dataKey": "示例产品",
      "dataValue": "SKU001",
      "dataConfig": "{\"imageUrl\":null}"
    }
  ],
  "total": 1
}
```

这是 SQL 投影的有效业务字段：id、tenantId、tagCode、dataKey=产品名称、dataValue=产品编码、dataConfig（含 imageUrl 的 JSON 字符串）。通用 VO 的其他字段可能为空。dataKey 是名称模糊筛选；不要假定通用 dataValue/status 筛选在 PRODUCT 特殊 SQL 中同样生效，也不要假定下拉必然排除停用商品。完整产品资料使用上面的 .NET 接口。

不要将 `/mst/commonData/page?tagCode=PRODUCT` 当作产品完整查询：该通用接口查询 mst_common_data，并不会走 PRODUCT 下拉所用的 mst_product 分支。

## 公司

### 完整列表、分页和详情

Java 接口：

| 用途 | 相对地址 | 参数及返回 |
| --- | --- | --- |
| 不分页读取全部匹配记录 | GET /mst/commonData/list | tagCode=COMPANY；data 数组 |
| 逐页读取完整记录 | GET /mst/commonData/page | tagCode=COMPANY + pageNum/pageSize；rows、total |
| 详情 | GET /mst/commonData/getInfo | 必填 query id，非路径 ID；data 对象 |
| 下拉分页 | GET /mst/commonData/pageForDown | tagCode=COMPANY + pageNum/pageSize；rows、total |
| 不分页下拉 | GET /mst/commonData/listForDown | tagCode=COMPANY；data 数组 |

列表/下拉公共筛选：tagCode 必须显式为 COMPANY，dataKey 为名称包含匹配，dataValue 为编码包含匹配，status 为字符串 "1" 启用、"0" 停用；不传 status 时两者都包括。无需也不应从客户端覆盖 tenantId。按 sortIndex 升序、createTime 降序。公司下拉当前没有裁剪专用 DTO，实际复用下列完整 VO；界面通常只消费 id/dataKey/dataValue。

完整不分页请求参数：

```json
{
  "tagCode": "COMPANY"
}
```

```json
{
  "code": 200,
  "data": [
    {
      "id": 1001,
      "tenantId": "demo",
      "tagCode": "COMPANY",
      "dataKey": "示例公司",
      "dataValue": "COMP001",
      "dataKeyEn": null,
      "dataConfig": "{}",
      "remark": null,
      "status": "1",
      "statusName": "启用",
      "sortIndex": 0,
      "isCorrelation": "0",
      "isCorrelationName": null,
      "correlationDataConfig": null,
      "companyGroupId": null,
      "configKey": null,
      "parentId": null,
      "isRelationGroup": null,
      "boolColumn1": null,
      "boolColumn2": null,
      "boolColumn3": null,
      "boolColumn4": null,
      "boolColumn5": null,
      "intColumn1": null,
      "intColumn2": null,
      "intColumn3": null,
      "intColumn4": null,
      "intColumn5": null,
      "strColumn1": null,
      "strColumn2": null,
      "strColumn3": null,
      "strColumn4": null,
      "strColumn5": null,
      "strColumn1Name": null,
      "strColumn2Name": null,
      "strColumn3Name": null,
      "strColumn4Name": null,
      "strColumn5Name": null,
      "floatColumn1": null,
      "floatColumn2": null,
      "floatColumn3": null,
      "floatColumn4": null,
      "floatColumn5": null,
      "dateColumn1": null,
      "dateColumn2": null,
      "dateColumn3": null,
      "dateColumn4": null,
      "dateColumn5": null,
      "createBy": null,
      "createTime": "2026-11-24 10:00:00",
      "updateBy": null,
      "updateTime": null
    }
  ]
}
```

MstCommonDataVo 字段类型：id/parentId/createBy/updateBy 为 Long ID；sortIndex、intColumn1…intColumn5 为整数；boolColumn1…boolColumn5 为 boolean；floatColumn1…floatColumn5 为 number；dateColumn1…dateColumn5/createTime/updateTime 为日期字符串；其余为 string，可空。dataConfig/correlationDataConfig 是 JSON **字符串**。status/isCorrelation/isRelationGroup 也是字符串，不能按数字 0/1 严格比较。扩展列的业务含义由 COMPANY 的字段配置定义，不把通用列名猜成税号等固定含义。

分页请求参数：

```json
{
  "tagCode": "COMPANY",
  "pageNum": 1,
  "pageSize": 20
}
```

分页成功正文同一 VO，以下为嵌套节选；单行完整键名见上面：

```json
{
  "code": 200,
  "rows": [
    {
      "id": 1001,
      "tagCode": "COMPANY",
      "dataKey": "示例公司",
      "dataValue": "COMP001",
      "status": "1"
    }
  ],
  "total": 1
}
```

详情请求参数：

```json
{
  "id": 1001
}
```

详情成功正文同一 VO，以下为嵌套节选：

```json
{
  "code": 200,
  "data": {
    "id": 1001,
    "tagCode": "COMPANY",
    "dataKey": "示例公司",
    "dataValue": "COMP001",
    "status": "1"
  }
}
```

详情不存在时服务抛“通用主数据不存在: {id}”，交给 Java 统一异常处理；不要约定为成功 data=null。核对时发现旧前端 commonDataInfo 仍拼接 /mst/commonData/{id}，与本次后端的 /getInfo?id=... 不一致；新集成按本文已核实的后端路径，复用旧 helper 前先校正路径并验证目标环境。

## 用户

### 完整公开资料分页

`GET /system/user/list?pageNum=1&pageSize=20`，Java。这里的完整资料以公开 SysUserVo 为准，不提供密码/密码哈希/重置凭据。

请求参数（全状态，不传 status）：

```json
{
  "pageNum": 1,
  "pageSize": 20
}
```

| 参数 | 类型 | 作用 |
| --- | --- | --- |
| pageNum / pageSize | integer | 显式分页 |
| userId | Long ID | 精确 ID |
| accountId | Long ID | 精确匹配所属账号 ID |
| userIds | string | 逗号分隔 ID |
| excludeUserIds | string | 逗号分隔的排除用户 ID |
| userName / nickName / phonenumber | string | 账号、昵称、手机号包含匹配 |
| deptId | Long ID | 部门及其下级范围 |
| status | string | "0" 正常、"1" 停用；省略包含两种 |
| params[beginTime] / params[endTime] | 日期字符串 | 创建时间范围；沿用现有请求库的 query 编码 |

只返回未删除用户，按服务端 superuser_% 模式过滤系统账号，受当前租户和数据权限约束，按 createTime 倒序。创建时间范围只有 beginTime/endTime 同时提供才生效。不要把数据范围不足当作可通过改 tenantId 解决的问题。成功示例（公开 VO 顶层字段；角色/岗位关联在本例为空）：

```json
{
  "code": 200,
  "rows": [
    {
      "userId": 1001,
      "accountId": 2001,
      "tenantId": "demo",
      "tenantName": null,
      "tenantType": null,
      "tenantList": [],
      "deptId": 101,
      "userName": "demo.user",
      "userCode": "U001",
      "nickName": "示例用户",
      "userType": "sys_user",
      "email": null,
      "phonenumber": null,
      "sex": null,
      "avatar": null,
      "logoRectangle": null,
      "logoSquare": null,
      "status": "0",
      "loginIp": null,
      "loginDate": null,
      "remark": null,
      "language": "zh_CN",
      "createTime": "2026-11-24 10:00:00",
      "deptName": "研发部",
      "roles": [],
      "roleIds": [],
      "postIds": [],
      "roleId": null,
      "userAccount": null,
      "userDisplayName": null,
      "cellPhoneNo": null
    }
  ],
  "total": 1
}
```

类型：userId/accountId/deptId/roleId 为 Long ID；roleIds/postIds 为 ID 数组；tenantList 为字符串数组；roles 为角色对象数组；loginDate/createTime 为日期时间；头像与 Logo 字段由 OSS 翻译转换器处理，集成不要强行转 number；其他标量为 string 或 null。用户基础主数据只依赖 userId、userName/userDisplayName/nickName、deptId/deptName、status；roles 等管理信息无需复制到业务库。

SysUserVo.password 标记 JsonIgnore；客户端不得读取、存储或回显密码字段。当前 /list 的 email/phonenumber 脱敏注解处于注释状态，不能承诺联系人已自动脱敏；仅在授权业务需要时使用，不把完整返回直接转发到公开日志或模型上下文。

### 用户详情

`GET /system/user/1001`，无 query/body，路径 userId 必填。需 system:user:query，后端另检查用户数据范围。成功正文（user 为上面完整 SysUserVo；此处仅展示其基础字段以突出嵌套）：

```json
{
  "code": 200,
  "data": {
    "user": {
      "userId": 1001,
      "userName": "demo.user",
      "nickName": "示例用户",
      "deptId": 101,
      "status": "0"
    },
    "roleIds": [],
    "roles": [],
    "postIds": [],
    "posts": []
  }
}
```

读取 body.data.user，不能直接读 body.data.userId。外层 roleIds/postIds 是当前用户已关联的 ID；roles/posts 是管理编辑所需的可选角色/岗位对象列表，不等于当前用户已拥有全部这些角色/岗位。

### 其他用户查询如何选择

- 下拉使用 `GET /pm/user-options?keyword=demo&limit=20`，详见 [已有候选接口](token-apis.md)。返回 data 数组，每项 userId/realName/deptId；limit 默认 50、最大 200。这不是完整人员目录。
- `GET /system/user/userList` 返回不分页 data 数组，但默认 status="0"，且会清空 email/phonenumber；不能替代含停用用户的全部资料列表。优先使用有明确分页的 /list。
- `GET /system/user/listAll` 是超级管理员跨租户功能，而且仍分页；**不要当作三方集成的“全量用户”接口**。

## 部门

### 完整可见部门列表

`GET /system/dept/list`，Java，无分页；需 system:dept:list。获取全部可见启停状态，参数传空对象：

```json
{}
```

可选 query：deptId、parentId 精确；deptName、deptCategory 包含匹配；belongDeptId 限定部门子树；status 字符串 "0" 正常、"1" 停用，省略不筛状态。只查未删除且当前会话可见的部门，按 ancestors、parentId、orderNum、deptId 排序。成功正文：

```json
{
  "code": 200,
  "data": [
    {
      "deptId": 101,
      "parentId": 100,
      "parentName": "示例公司",
      "ancestors": "0,100",
      "deptName": "研发部",
      "deptCategory": null,
      "orderNum": 1,
      "leader": 1001,
      "leaderName": "示例用户",
      "phone": null,
      "email": null,
      "status": "0",
      "createTime": "2026-11-24 10:00:00",
      "children": []
    }
  ]
}
```

deptId/parentId/leader 为 Long ID，orderNum 为整数，其余标量为字符串或 null。children 是可选子部门集合；/list 主要返回扁平节点，按 parentId 组树，不要只遍历 children 而漏掉平铺节点。

### 部门详情

`GET /system/dept/101`，无 body/query。需 system:dept:query，后端检查部门数据范围；data 为相同 SysDeptVo：

```json
{
  "code": 200,
  "data": {
    "deptId": 101,
    "parentId": 100,
    "parentName": "示例公司",
    "ancestors": "0,100",
    "deptName": "研发部",
    "deptCategory": null,
    "orderNum": 1,
    "leader": 1001,
    "leaderName": "示例用户",
    "phone": null,
    "email": null,
    "status": "0",
    "createTime": "2026-11-24 10:00:00",
    "children": []
  }
}
```

### 专用下拉

`GET /system/dept/optionselect`，需 system:dept:query。可选 deptIds（逗号分隔 Long ID 数组）用于指定候选集合，省略查可选正常部门；参数例：

```json
{
  "deptIds": "101,102"
}
```

成功有效业务字段节选：

```json
{
  "code": 200,
  "data": [
    {
      "deptId": 101,
      "deptName": "研发部",
      "leader": 1001
    }
  ]
}
```

此查询只选 deptId、deptName、leader，且 status="0"；其余 VO 属性可能为空，不含完整层级信息。原先的 `/system/dept/list?status=0` 是过滤后的完整部门列表，可用于正常部门树，不能标成含停用项的全量，也不等于此专用轻量下拉。

## 项目

### 完整台账分页

`GET /pm/projects/manage-page`，Java。获取当前租户全状态台账的 params：

```json
{
  "scope": "portfolio",
  "pageNum": 1,
  "pageSize": 20
}
```

| 参数 | 类型 | 规则 |
| --- | --- | --- |
| scope | string | portfolio 默认全部台账范围；mine 仅当前用户参与；不要从客户端传 userId 冒充他人，服务会丢弃该入参 |
| pageNum | integer | 默认/非法值按 1 |
| pageSize | integer | 默认 10，最大 100 |
| keyword | string | 名称、客户、项目经理姓名包含匹配 |
| status | string | pending/drafting/running/closed；省略不筛状态 |
| typeCode | string | 项目类型编码精确匹配，取目标环境配置 |
| health | string | 健康度精确匹配，取环境字典；要全量则省略 |

成功正文（注意 rows/total 在 data 内，主键 projectId 不叫 id）：

```json
{
  "code": 200,
  "data": {
    "rows": [
      {
        "projectId": "1001",
        "code": "PRJ001",
        "name": "示例项目",
        "customer": "示例客户",
        "typeCode": null,
        "deptId": "101",
        "deptName": "研发部",
        "managerId": "1001",
        "managerName": "示例用户",
        "sponsorId": null,
        "sponsorName": null,
        "createBy": "1001",
        "startDate": null,
        "dueDate": null,
        "status": "running",
        "closeType": null,
        "closedAt": null,
        "stage": null,
        "progress": 30,
        "health": null,
        "initiationStep": 3,
        "createTime": "2026-11-24 10:00:00",
        "taskTotal": 10,
        "taskDone": 3
      }
    ],
    "total": 1,
    "counts": {
      "totalProjects": 1,
      "riskProjects": 0,
      "watchProjects": 0,
      "blockedProjects": 0
    }
  }
}
```

列表各 ID 是字符串；progress 为 0–100 整数；initiationStep/taskTotal/taskDone 为整数；startDate/dueDate/closedAt/createTime 为日期字符串或 null；其他为 string 或 null。closeType 非空时 normal/interrupted/cancelled。counts 是统计卡数据，健康度筛选口径与 rows 可不同；翻页结束依据 data.total，不用 counts.totalProjects。

普通 `GET /pm/projects` 默认排除 pending/drafting，不是覆盖所有立项状态的完整台账。不要把它或下拉接口当全状态目录。

### 项目详情

`GET /pm/projects/1001`，无 body/query，路径 projectId 为字符串。data 是聚合详情，不是单表所有列。示例列出顶层字段；关联列表为空仅为样例，主数据同步不必展开业务任务/阶段树：

```json
{
  "code": 200,
  "data": {
    "projectId": "1001",
    "code": "PRJ001",
    "name": "示例项目",
    "customer": "示例客户",
    "summary": null,
    "deptId": "101",
    "deptName": "研发部",
    "typeCode": null,
    "managerId": "1001",
    "managerName": "示例用户",
    "sponsorId": null,
    "sponsorName": null,
    "createBy": "1001",
    "canManageTasks": false,
    "projectTaskRole": "member",
    "startDate": null,
    "dueDate": null,
    "status": "running",
    "stage": null,
    "currentStageId": null,
    "templateId": null,
    "templateVersionId": null,
    "templateName": null,
    "initiationMode": null,
    "sourceProjectId": null,
    "sourceProjectName": null,
    "progress": 30,
    "health": null,
    "latestEvalJson": null,
    "openHighRiskCount": 0,
    "unfinishedTaskCount": 7,
    "initiationStep": 3,
    "initiatedAt": null,
    "closeType": null,
    "closeNote": null,
    "closedAt": null,
    "closedBy": null,
    "charter": null,
    "stages": [],
    "members": [],
    "followers": [],
    "reporters": [],
    "files": []
  }
}
```

详情特有标量：canManageTasks 为 boolean；projectTaskRole 为 admin/manager/creator/member/none，应使用后端结果决定任务操作；templateVersionId 仍为字符串 ID，不是数字版本计数；initiationMode 为 template/project（null 按 template）；latestEvalJson 为 JSON 字符串；charter 是对象；openHighRiskCount/unfinishedTaskCount/initiationStep 为整数；closedBy 为 Long ID。stages、members、followers、reporters、files 是对应阶段、成员、关注人、汇报人、资料的业务对象数组，超出基础主数据的同步范围；不要把它们转成字符串 ID 数组。

### 项目候选

`GET /task/task/projects/options?limit=20&excludeClosed=true` 的入参、轻量字段和特殊失败语义见 [项目候选接口](token-apis.md)。excludeClosed=false 只改变结项过滤，limit 仍限制条数、无分页总数；不等于全量项目。

## 合同

### 本人合同记录分页

`GET /aichat/contractRecord/list`，Java。只覆盖当前用户生成的合同记录，服务强制 owner_user_id=当前用户；不能通过增加 ownerUserId/tenantId 参数查别人。

参数：pageNum/pageSize 显式分页，keyword 可选关键词，typeId 可选合同类型 Long ID。读取本人全部记录时省略两个筛选：

```json
{
  "pageNum": 1,
  "pageSize": 20
}
```

```json
{
  "code": 200,
  "rows": [
    {
      "id": 1001,
      "recordNo": "CT001",
      "title": "示例采购合同",
      "partyName": "示例公司",
      "templateVersion": 1,
      "templateName": "采购合同模板",
      "referenceType": null,
      "referenceGeneratedId": null,
      "createTime": "2026-11-24 10:00:00",
      "types": [
        {
          "typeId": 101,
          "typeName": "采购合同"
        }
      ]
    }
  ],
  "total": 1
}
```

列表是摘要：id/referenceGeneratedId 是 Long ID；templateVersion 是整数；createTime 是日期字符串；types 为 {typeId: Long ID, typeName: string} 数组；其余为字符串或 null。需要正文、信息卡、生成文件或关联会话时再读详情。

### 本人合同详情

`GET /aichat/contractRecord/1001`，无 query/body；同样检查本人归属。成功正文：

```json
{
  "code": 200,
  "data": {
    "id": 1001,
    "recordNo": "CT001",
    "title": "示例采购合同",
    "partyName": "示例公司",
    "ownerUserId": 1001,
    "templateId": 101,
    "templateVersion": 1,
    "templateName": "采购合同模板",
    "infoCardJson": "{}",
    "clauseJson": "[]",
    "tableDataJson": "[]",
    "ossId": null,
    "fileName": null,
    "referenceType": null,
    "referenceGeneratedId": null,
    "sessionId": null,
    "createTime": "2026-11-24 10:00:00",
    "types": [
      {
        "typeId": 101,
        "typeName": "采购合同"
      }
    ]
  }
}
```

详情新增 ownerUserId/templateId/ossId 为 Long ID；infoCardJson/clauseJson/tableDataJson 为 JSON **字符串**，具体内容随模板定义，示例空对象/数组不代表固定业务结构；fileName/sessionId 为字符串。没有专用合同记录下拉，也没有已确认可供第三方调用的“当前租户全部合同台账”接口；不得把本人的 list 标注为该能力。

## 错误处理与尚缺能力

1. 所有请求检查 HTTP 状态及业务 code；非 200 业务码不能当成功，即便 HTTP 200。401 交给已有授权/续期，权限不足联系管理员检查当前租户与数据权限，不切换超级管理员绕过。
2. Java 查询沿用统一异常响应，错误通常提供 code/msg，不能假定和新 .NET 主数据一样具有 HTTP 404/409。没有查到列表应是成功空数组；详情的无记录/越权按对应服务错误处理，不能合成空档案。产品 GetPharmaSku 的业务 404 已在上文明确。
3. 新品牌/供应商的 HTTP 400/401/403/404/409/500、乐观锁、唯一性及完整请求响应见 [专用契约](brand-supplier.md)。不向这些接口传 Java 页码以外的通用筛选或产品 PascalCase 行字段。
4. 当前仍缺：租户范围合同完整目录及专用合同记录候选、通用跨页一致快照/增量同步游标。不要在集成中虚构 /all、/export 或 /options 路由。若业务需要超出本页范围，请实施方确认可用服务或另提接口开发。
5. 品牌/供应商接口已在代码实现，首次接入仍需确认目标环境程序和 3.122 表迁移；平台菜单另需 3.124。让当前 Agent 使用 wk-setup 核对环境/资源，迁移由版本发布执行，不要求调用方直接建表。

核对依据：.NET ProductManagerController/ProductService/Product/BasePager/PharmaSkuPageRequest 与 MVC 序列化配置；Java MstCommonData、SysUser、SysDept、PmProject、CtContractRecord 的 Controller/Service/VO、PageQuery，以及 WiseMstCommonDataMapper 的 PRODUCT 投影。Java 核对版本 dda8dbb3e；目标环境的发布版本需另行确认。
