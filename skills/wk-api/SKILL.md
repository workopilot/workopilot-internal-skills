---
name: wk-api
description: 在第三方项目或喔壳 AI 应用中设计数字员工、业务菜单、MCP 工具和业务设置，并用用户 Token 对接喔壳 HTTP API。适用于数字员工、AI 服务、场景推荐、主数据、待办、应用主动发消息、附件、审核、文档和语音等开发任务。
---

# 喔壳应用接口集成

## 什么是喔壳，业务如何落地

喔壳是以数字员工为日常办公入口的企业 AI 平台。设计一个业务时，先明确谁在什么场景处理哪条业务记录、可以做哪些操作，再决定数字员工的职责、菜单、MCP 工具和 AI 应用设置。

| 谁在做什么 | 放在哪里 | 设计时写清楚什么 |
| --- | --- | --- |
| 业务人员日常查数据、办事情 | 数字员工承接问答、协作或独立任务。员工菜单提供列表、详情、查询和编辑页面 | 员工服务哪个岗位，菜单查哪些记录，哪些字段和状态允许修改 |
| 业务人员要求数字员工代查、代办 | 将菜单所用的业务接口封装为 MCP 工具，绑定给对应数字员工 | 每个工具的用途、业务 ID、输入、返回、失败条件。菜单和 MCP 调用同一业务服务，沿用租户、用户权限和状态校验 |
| 管理员维护业务运行规则 | AI 应用承接业务设置页面 | 哪些角色可改审批规则、模板、业务字典和通知事件编码；保存后影响哪些员工和业务流程 |
| 业务状态变化后需要人处理或知悉 | 应用按业务事件创建、更新、取消待办，或用已配置的 eventCode 主动发送消息 | 待办归属人、关联的业务记录和待办 ID；通知接收人、模板变量及重试幂等键 |

例如做合同管理，法务在“合同助手”的“合同台账”菜单里查询合同、修改自己有权编辑的条款，也可对员工说“把 A-12 的付款期限改为 30 天”。菜单和员工的 MCP 工具都调用合同更新接口，由后端检查操作权限和合同状态。管理员在“合同管理”AI 应用中设置复核规则和消息编码。合同进入复核时按归属创建待办，截止日变化时更新原待办，撤回复核时取消待办；需要告知结果时，应用用已配置的编码发送消息。
开发前先把具体需求映射成“业务角色 → 员工与菜单 → 业务 API → 对应 MCP 工具 → AI 应用设置”，再补上需要触发的待办与消息。已有业务 API 优先复用。

## 编写代码前先检查调用方

1. 在当前项目查看开发约定、运行入口、构建命令和实际启用的环境配置。找到一个已工作的请求，确认 API 基址、相对路径拼接、Token 来源、加密、错误处理，以及请求库返回完整响应还是已解包的 data。记录环境名和网关地址，凭据只在运行时使用。
2. 喔壳 AI 应用通常已初始化宿主 SDK。沿用实例和会话，选择对应的 Java 或 .NET 网关。例如已有 @workopilot/webapp-sdk 的项目，可用 sdk.get('/pm/user-options', {keyword})；调用 .NET 可用 sdk.request('/api/aiagent/run', {base:'net', method:'POST', bodyType:'json', body:payload})。SDK 已设置基址时只传接口路径。文件下载和 SSE 沿用项目的二进制或流式请求方式。
3. 自有框架沿用现有 HTTP 客户端。配置两个基址，把下面的相对地址接到对应基址之后。使用该环境已有的平台登录或宿主授权流程提供的用户 Token，原始 HTTP 加 Authorization: Bearer <token>。若项目只有自己的业务登录，先确定喔壳会话来源。401 交给已有登录/续期流程，403 检查租户和用户权限。
4. 从应用配置读取资源编码。AI 服务需 serviceCode、已定义的 inputs 和可选 routeCode；数字员工需 robotCode 或 robotId 及类型；场景推荐需 appCode、sceneCode；消息使用应用已配置的 eventCode、受众及模板参数。附件分类、审核、语音还分别依赖分类编码、审核方案、员工模型。标识缺失、配置状态未知或接口返回资源不可用时，让当前 Agent 使用 **wk-setup（喔壳资源实施）** 核对目标环境和租户。缺少实施技能时向实施方索取对应配置。实际创建、修改按用户的实施需求执行。

## 环境与网关

| 目标环境 | Java 基址 | .NET 基址 |
| --- | --- | --- |
| 测试 | https://agenttest.workopilot.com/prod-api | https://agenttest.workopilot.com/net-api |
| 生产 | https://agent.workopilot.com/prod-api | https://agent.workopilot.com/net-api |

自有项目可将两列分别映射到自己的 WORKOPILOT_JAVA_BASE_URL 和 WORKOPILOT_NET_BASE_URL。宿主项目可能通过同源 /prod-api、/net-api 和本地代理进行转发；以生效的代理目标确认环境。网关前缀 /prod-api 在测试环境也使用。不同环境分别配置资源编码和会话。示例完整测试地址为 https://agenttest.workopilot.com/net-api/api/aiagent/run。

## HTTP 正文与字段大小写

文档展示请求库解包前的 HTTP 正文。使用已有 SDK 时先确认它返回 HTTP 响应、响应正文，还是正文中的 data；下文用 body 指代原始 JSON 正文。示例中的编码、业务内容和数据值仅用于说明。响应节选省略未使用的元数据，保留实际嵌套和键名。

| 调用 | 成功判断 | 结果字段 |
| --- | --- | --- |
| AI 服务执行 /api/aiagent/run | body.Code === 0 | 同步 body.Data，异步 body.TaskId |
| AI 服务调试 /api/aiagent/runtest | body.code === 200 且 body.data.Code === 0 | body.data.Data 或 body.data.TaskId |
| 异步 AI 服务结果 /api/aiagent/task/result | body.code === 200 后判断 body.data.TaskStatusId | body.data.Output、body.data.ErrorMsg |
| 任务型员工 POST /api/ai/robot/task-runs | HTTP 202 且 body.code === 200 | body.data.Id 是运行 ID，body.data.AssistantMessageId 是消息 ID |
| .NET 分页 ApiResult | body.code === 200 | body.rows、body.total 与 data 同层 |

.NET MVC 使用 Newtonsoft.Json 的 DefaultContractResolver 保留属性原名。ApiResult 定义了小写 code、msg、data、rows、total；多数业务 DTO 使用 PascalCase。显式 JSON 别名和匿名对象按接口示例读取，例如 HTML 成果的 data.revisionId、迁移包的 data.services。long 和非空 long? 输出十进制字符串，保留为字符串以免丢失精度。int、boolean 保持 JSON 原类型。动态 inputs 的键、模板参数、模型业务输出按目标配置原样传递。SSE 使用独立事件编码。

## 按场景查看请求与响应

- [AI 服务执行、轮询与聊天 SSE](references/ai-runtime.md)
- [任务型数字员工的创建、列表、详情、取消、重试与删除](references/task-runs.md)
- [场景推荐、生成话术与草稿交接](references/recommendations.md)
- [组织与商品、用户、创建/更新/取消个人待办、应用主动发送消息](references/token-apis.md)
- [PDF、文件上传、OCR、Excel、附件取数、智能审核、语音](references/files-audit.md)
- [资源迁移、指令模板、HTML 成果与 Markdown 文档](references/resources.md)

