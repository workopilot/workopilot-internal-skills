# 单据入参整理指南

## AppCode

`AppCode` 是智能审核对接的平台编码，通常表示单据来源系统。

示例：

- `YONYOU`
- `KINGDEE`
- `FEIKONG`
- 项目实际约定的系统编码

审核前先通过 `/api/Scheme/QueryAuditScheme` 查询当前租户审核方案。若匹配到唯一方案，使用方案里的 `AppCode`；若没有方案，提醒用户联系管理员配置；若有多个可能方案且无法确认，再询问用户。

## BillTypeCode

`BillTypeCode` 是单据类型编码，决定走哪套审核规则。

示例：

- `TRAVEL_EXPENSE`
- `PURCHASE_EXPENSE`
- `DAILY_EXPENSE`
- `PAYMENT_APPLY`

审核前先通过 `/api/Scheme/QueryAuditScheme` 查询当前租户审核方案。若匹配到唯一方案，使用方案里的 `BillTypeCode`；若用户给的编码查不到对应方案，提醒用户确认编码或联系管理员配置；若有多个可能方案且无法确认，再询问用户。

## ExtendJsonData

不同单据的字段结构可能完全不同。智能审核场景下，不要强行丢字段；能收进去就收进去。

建议：

- 单据头额外字段放 `BillHeader.ExtendJsonData`。
- 明细行额外字段放 `BillDetails[].ExtendJsonData`。
- `ExtendJsonData` 必须是 JSON 字符串。
- 日期、城市、项目、部门、预算、事由、行程、供应商、合同号、发票号等都可以放进去。

示例：

```json
{
  "travelPurpose": "客户拜访",
  "fromCity": "上海",
  "toCity": "北京",
  "projectCode": "PRJ-001",
  "department": "销售部"
}
```

脚本会转为：

```json
"{\"travelPurpose\":\"客户拜访\",\"fromCity\":\"上海\"}"
```

## 本地附件

本地附件不能直接传给审核接口，需要先上传。

上传后生成：

```json
{
  "ItemLineNo": "",
  "FileUrl": "https://agent.workopilot.com/files/demo.pdf",
  "FileType": "pdf",
  "FileName": "demo.pdf"
}
```

如果附件属于某个明细行，设置 `ItemLineNo` 为明细 `LineNo`。
