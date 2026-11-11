---
name: wk-setup
description: 喔壳业务设计与资源实施。用户要求在指定租户创建或复用 AI 服务、对话型或任务型数字员工，更新员工、注册 iframe 卡片、配置应用菜单，或梳理路由、场景推荐、消息通知的人工配置时，用 API Key 交付资源及标识。业务页面接入已有资源交给 wk-api。
---

# 喔壳资源实施

## 什么是喔壳，业务如何落地

喔壳是以数字员工为日常办公入口的企业 AI 平台。设计一个业务时，先明确谁在什么场景处理哪条业务记录、可以做哪些操作，再决定数字员工的职责、菜单、MCP 工具和 AI 应用设置。

| 谁在做什么 | 放在哪里 | 设计时写清楚什么 |
| --- | --- | --- |
| 业务人员日常查数据、办事情 | 数字员工承接问答、协作或独立任务。员工菜单提供列表、详情、查询和编辑页面 | 员工服务哪个岗位，菜单查哪些记录，哪些字段和状态允许修改 |
| 业务人员要求数字员工代查、代办 | 将菜单所用的业务接口封装为 MCP 工具，绑定给对应数字员工 | 每个工具的用途、业务 ID、输入、返回、失败条件。菜单和 MCP 调用同一业务服务，沿用租户、用户权限和状态校验 |
| 管理员维护业务运行规则 | AI 应用承接业务设置页面 | 哪些角色可改审批规则、模板、业务字典和通知事件编码；保存后影响哪些员工和业务流程 |
| 业务状态变化后需要人处理或知悉 | 应用按业务事件创建、更新、取消待办，或用已配置的 eventCode 主动发送消息 | 待办归属人、关联的业务记录和待办 ID；通知接收人、模板变量及重试幂等键 |

例如做合同管理，法务在“合同助手”的“合同台账”菜单里查询合同、修改自己有权编辑的条款，也可对员工说“把 A-12 的付款期限改为 30 天”。菜单和员工的 MCP 工具都调用合同更新接口，由后端检查操作权限和合同状态。管理员在“合同管理”AI 应用中设置复核规则和消息编码。合同进入复核时按归属创建待办，截止日变化时更新原待办，撤回复核时取消待办；需要告知结果时，应用用已配置的编码发送消息。
实施前列出数字员工、业务菜单、需绑定的 MCP 工具、AI 应用设置和环境依赖，逐项标出已有资源与待配置项。交付时给开发提供实际编码和 ID。

1. 确定目标环境、租户、资源类型和稳定的 serviceCode 或 robotCode。要求“写创建页面”属于开发，要求“帮我创建一个员工”才执行实施。
2. 在目标项目准备配置 JSON。数字员工可从本技能 examples/robot.json 起步，替换名称、编码和指令。AI 服务根据[AI 服务创建说明](references/ai-service.md) 的创建字段编写，systemPrompt 用 {{字段名}} 引用 inputs。模型以该租户可选项为准。
3. 从当前进程读取 WORKOPILOT_API_KEY，显式指定 WORKOPILOT_BASE_URL 为目标 .NET API 根地址。执行前核对环境和配置，凭据留在执行环境中。在技能目录按资源类型运行一条命令：

```powershell
py -3 scripts/create_ai_service.py --base-url $env:WORKOPILOT_BASE_URL --config <服务配置路径>
py -3 scripts/create_digital_employee.py --base-url $env:WORKOPILOT_BASE_URL --config <员工配置路径>
```

4. 默认按编码检查已有资源。区分复用与新建，核对返回的业务状态及资源标识。超时后先按编码查询再重试。交付环境、资源类型、code 和返回的 ID；后续页面接入将这些标识交给 wk-api。



## 实施分工与交接

内部脚本目前覆盖员工与服务的基础创建。先盘点目标租户的已有资源；需要高级配置时，让实施人员在管理页面保存并回读，再交付标识。返回“复用”只说明找到了资源，需另查类型和配置。

| 需求 | 实施动作 | 交给开发 |
| --- | --- | --- |
| 多轮咨询 | 数字员工选择聊天型 CHAT；历史空类型按 CHAT。可用创建脚本。 | robotId、robotCode、可访问的用户 |
| 独立执行并取结果 | 创建前选 TASK，明确默认任务说明；需要结构化结果时开启结果约束并填写合法 JSON Schema。可通过创建脚本透传 employeeType，当前没有专门的类型及 Schema 校验工具，先在员工配置页核对。已有会话或运行记录的员工有类型变更限制。 | robotId、输入示例、结果格式 |
| AI 服务分支 | 单提示词场景沿用默认关闭。需要分支时在 AI 服务管理手动打开路由，选择 CODE 或 INTENT，配置启用的分支编码、名称和提示词；INTENT 另配意图识别提示词。保留可用的主提示词。 | serviceCode、inputs、模式、可用 routeCode、默认行为 |
| 页面场景推荐 | 数字员工中心 → 数字员工场景推荐：新建或复用场景、启用并添加目标员工，选择固定话术或 AI 推荐并保存。AI 推荐需核对系统服务 wk_sys_ai_employee_recommend 及模型可用。 | appCode、sceneCode、模板变量、测试用户 |
| 业务消息通知 | 在消息管理中核对事件编码及占位符，配置渠道、模板绑定和订阅。使用一个测试收件人验证。 | eventCode、模板参数键、受众类型与 ID、预期渠道 |

目前先手工维护任务专项配置、路由规则、推荐场景和通知事件/模板/渠道/订阅。交接时分别标出“已配置”“待手配”“已联调”，只报告实际完成的步骤。

## 更新资源及注册业务入口

在技能目录运行下列命令，环境变量 WORKOPILOT_API_KEY 提供实施身份。用实际配置路径、员工 ID 替换示例值。

```powershell
py -3 scripts/update_digital_employee.py --base-url $env:WORKOPILOT_BASE_URL --employee-id 123 --config employee-update.json
py -3 scripts/register_iframe_card.py --base-url $env:WORKOPILOT_BASE_URL --config card.json
py -3 scripts/configure_app_menu.py --base-url $env:WORKOPILOT_BASE_URL --employee-id 123 --action create --config menu.json
```

更新已有菜单时用 --action update --menu-key 指定原菜单编码。卡片用于对话内展示，配置 url 和 triggerPrompt；菜单用 menuKey 和 iframeUrl 固定挂在员工入口。按本技能的[员工配置](references/digital-employee.md)、[卡片配置](references/iframe-skill-card.md)和[菜单配置](references/app-menu-iframe.md) 准备完整字段。执行后在目标员工验证更新值、卡片触发和菜单打开。

跨环境迁移员工、AI 服务以及维护快捷指令先在管理页面操作；在目标租户核对模型、关联技能、菜单地址、路由和访问权限，用目标环境的标识交付开发。



