# 文档、附件、审核与语音

全部接口相对 .NET 网关。JSON 示例可按所示拼写发送。响应示例展示关键字段。文件 URL、员工 ID、分类编码、方案及业务数据按目标环境替换。
## 生成 Markdown 报告 PDF

`POST /api/Document/ConvertMarkdownToPdf`

请求体

```json
{
  "Content": "# 合同摘要\n30 天内付款。",
  "Theme": "default"
}
```

成功响应

```json
{
  "code": 200,
  "data": "https://files.example.com/contract.pdf"
}
```

Content 必填。Theme 可选。读取 data 的下载地址。空内容时 code=0。

## 将 HTML 转为 PDF

`POST /api/Document/ConvertHtmlToPdf`

请求体

```json
{
  "Content": "<h1>合同摘要</h1><p>30 天内付款。</p>"
}
```

成功响应

```json
{
  "code": 200,
  "data": "https://files.example.com/contract.pdf"
}
```

使用 Content 字符串。

## 上传本地文件

`POST /api/Document/UploadDocument/Upload`

multipart/form-data。字段名 file，值是带文件名的文件字节，例如 curl 表单参数 `-F "file=@contract.pdf"`。

成功响应

```json
{
  "code": 200,
  "data": "https://files.example.com/contract.pdf"
}
```

上传成功后把 data 传给分类、取数或其他接受 URL 的接口。

## OCR 提取文字

`POST /api/Document/OcrDocument/Ocr`

multipart/form-data。上传文件用 `-F "file=@contract.pdf"`，已有文件地址用 `-F "url=https://files.example.com/contract.pdf"`。

成功响应

```json
{
  "code": 200,
  "data": "合同约定收到发票后30天付款。"
}
```

至少传 file 或 url。缺少输入或未配置 OCR 默认模型时可能返回 HTTP 200、业务 code=0。

## 导出 Excel

`POST /api/Document/WriteExcelDocument/WriteExcel`

请求体

```json
{
  "Columns": [
    {
      "col_filed": "amount",
      "col_name": "金额"
    }
  ],
  "Data": [
    {
      "amount": "3580.50"
    }
  ],
  "IsCloud": true
}
```

成功响应

```json
{
  "code": 200,
  "data": "https://files.example.com/export.xlsx"
}
```

列键按服务端拼写 col_filed。IsCloud=false 时响应为 xlsx 文件字节，按 Content-Type 区分文件和 JSON 错误。

## 列出可用附件分类

`GET /api/Classfication/GetCategoryData`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": [
    {
      "Id": "101",
      "Code": "CONTRACT",
      "Name": "合同"
    }
  ]
}
```

路径中的 Classfication 为服务端拼写。取 data[].Code 作为后续 categoryCode。

## 自动分类文件

`POST /api/Classfication/ClassifyFile`

请求体

```json
{
  "fileUrls": [
    {
      "url": "https://files.example.com/contract.pdf",
      "fileName": "contract.pdf"
    }
  ],
  "extractFields": true,
  "categoryCodes": [
    "CONTRACT"
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": "batch-01"
}
```

fileUrls 指定上传后的文件；可选 categoryCodes 限定范围、extractFields 同时抽取字段。返回批次号。

## 按已知分类提取字段

`POST /api/Classfication/ExtractFile`

请求体

```json
{
  "categoryCode": "CONTRACT",
  "extractMode": "DOCUMENT",
  "fileUrls": [
    {
      "url": "https://files.example.com/contract.pdf",
      "fileName": "contract.pdf"
    }
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": "batch-01"
}
```

分类编码必须与租户配置一致。extractMode 取 PAGE 或 DOCUMENT，默认 PAGE。

## 查询附件批次

`GET /api/Classfication/GetClassificationResult?batchNo=batch-01`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "Code": 1,
    "Progress": 100,
    "Result": [
      {
        "FileName": "contract.pdf",
        "ClassificationResults": [
          {
            "CategoryCode": "CONTRACT",
            "ExtractDataJson": "{\"amount\":3580.5}"
          }
        ]
      }
    ]
  }
}
```

外层 code=200 表示查询成功，内层 data.Code=0 处理中、1 完成。ExtractDataJson 是字符串，字段结构取决于分类规则。

## 确认审核方案

`POST /api/Scheme/QueryAuditScheme`

请求体

```json
{"BillTypeCode":"TRAVEL_EXPENSE"}
```

成功响应节选

```json
{"code":200,"data":[{"Id":"101","SchemeName":"差旅审核","AppCode":"YONYOU","BillTypeCode":"TRAVEL_EXPENSE","Rules":[]}]}
```

使用匹配方案的 AppCode 和 BillTypeCode 组装采集请求。没有适用方案时，使用喔壳资源实施技能核对目标租户配置。

## 采集待审核单据

`POST /api/BillAudit/BillCollect`

请求体

```json
{
  "RequestId": 202607140001,
  "IsAudit": false,
  "Method": "API",
  "BillHeader": {
    "BillId": "TRAVEL-20260714-001",
    "BillCode": "BX202607140001",
    "AppCode": "YONYOU",
    "SourceType": 2,
    "BillTypeCode": "TRAVEL_EXPENSE",
    "TotalAmount": 3580.5,
    "RequestUserId": "EMP001",
    "CompanyId": "COMP001",
    "SubmitTime": "2026-07-14 10:30:00",
    "ExtendJsonData": {
      "employeeName": "张三",
      "department": "销售部",
      "travelPurpose": "客户拜访",
      "fromCity": "上海",
      "toCity": "北京",
      "projectCode": "PRJ-2026-001"
    }
  },
  "BillDetails": [
    {
      "LineNo": "1",
      "ItemCode": "TRAFFIC",
      "Amount": 1280.5,
      "ExtendJsonData": {
        "expenseType": "交通费",
        "transport": "高铁",
        "from": "上海虹桥",
        "to": "北京南"
      }
    },
    {
      "LineNo": "2",
      "ItemCode": "HOTEL",
      "Amount": 2300,
      "ExtendJsonData": {
        "expenseType": "住宿费",
        "city": "北京",
        "nights": 2,
        "hotelName": "北京示例酒店"
      }
    }
  ],
  "BillAttachments": []
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "BusinessId": "801",
    "StatusCode": 0,
    "BatchNo": null
  }
}
```

示例租户业务编码须替换；字段说明见 [单据组装](audit-payload.md)。IsAudit=false 只采集，StatusCode=1 表示单据重复、2 表示执行审核失败。采集已触发审核时复用返回的批次。

## 开始智能审核

`POST /api/BillAudit/BillAudit`

请求体

```json
{
  "BillNo": "BX202607140001"
}
```

成功响应

```json
{
  "code": 200,
  "data": "audit-batch-01"
}
```

按单据编号 BillNo 或业务单据 ID BillId 定位。

## 获取审核报告

`GET /api/BillAudit/GetBillAuditResult?BillNo=BX202607140001`

无请求体。查询参数见地址。

成功响应

```json
{
  "code": 200,
  "data": {
    "BillNo": "BX202607140001",
    "BillId": "TRAVEL-20260714-001",
    "ReportId": "901",
    "HeaderAuditItems": [],
    "DetailAuditItems": [],
    "ClassificationFailedAttachments": []
  }
}
```

按 BillNo 或 BillId 查询。报告项取自 data，保留单号以便查询；轮询设置超时。

## 音频转文字

`POST /api/ai/robot/voice/asr`

multipart/form-data，例如 `-F "File=@voice.wav" -F "RobotId=1001"`。员工也可用 RobotCode 定位；SessionId 可选。

成功响应

```json
{
  "code": 200,
  "data": {
    "Text": "请查看合同",
    "AudioUrl": "https://files.example.com/voice.wav",
    "DurationMs": "2400"
  }
}
```

DurationMs 为可空 long，原始 JSON 中非空时为字符串。需要员工配置可用识别模型。

## 文字转语音

`POST /api/ai/robot/voice/tts`

请求体

```json
{
  "RobotId": "1001",
  "Text": "请查看合同。"
}
```

成功返回音频字节，Content-Type 为模型提供的音频类型。用二进制响应或 Blob 读取。
可传 SessionId、ChunkIndex。请求头 Accept: audio/*,application/json，失败时按响应内容类型读取错误。


