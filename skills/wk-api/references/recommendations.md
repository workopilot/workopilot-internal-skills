# 页面场景推荐：后台配置、iframe 侧滑栏与聊天草稿

场景推荐把**当前数字员工的业务页面，与其他能协助处理当前业务的数字员工连接起来**。例如，用户正在“项目经理”数字员工下面查看项目详情，可以打开“项目协作建议”，看到“会议助理”“任务助理”分别建议下一步做什么。用户选择建议后，带着当前项目的信息进入对应员工的聊天页，检查草稿并发送，让该员工继续办理。

嵌入喔壳主应用的 iframe 页面优先使用下面的 postMessage 协议，由主应用处理推荐与草稿交接。需要自建推荐界面的调用方再使用后文的 .NET HTTP 接口；沿用当前项目的请求封装与用户 Token。

## 目录

- [先理解业务场景：项目经理如何联动其他员工](#先理解业务场景项目经理如何联动其他员工)
- [开发者需要准备什么](#开发者需要准备什么)
- [先在当前环境配置场景](#先在当前环境配置场景)
- [从 iframe 打开场景推荐侧滑栏](#从-iframe-打开场景推荐侧滑栏)
- [消息字段与 HTTP 字段的区别](#消息字段与-http-字段的区别)
- [联调与排查](#联调与排查)
- HTTP： [解析场景](#解析当前场景)、[生成推荐](#生成推荐话术)、[准备草稿](#将选中的推荐准备为草稿)、[读取草稿](#读取本人草稿)、[确认接收](#确认已接收草稿)

## 先理解业务场景：项目经理如何联动其他员工

假设用户从“项目经理”数字员工的菜单进入“示例交付项目”的详情页：项目处于联调阶段，进度 60%，有 3 项延期任务，本周还没有安排周会。这时用户可以点击“项目协作建议”，在右侧同时看到多个相关员工及其建议：

| 推荐的其他数字员工 | 根据当前项目可给出的操作建议 | 用户选择后由谁接手 |
| --- | --- | --- |
| 会议助理 | “帮示例交付项目预约一次联调协调会” | 会议助理继续确认时间、参会人等信息，调用其已接入的会议能力 |
| 会议助理 | “帮这个项目安排本周周会” | 会议助理结合项目上下文协助安排周会 |
| 任务助理 | “给张三创建一个跟进联调问题的任务” | 任务助理确认任务内容、负责人及截止时间后，调用任务创建能力 |
| 任务助理 | “查询当前项目的延期任务” | 任务助理根据项目标识查询有权访问的任务，并整理结果 |

以上是业务设计示例，实际展示哪些员工由场景配置决定；员工能否完成操作取决于其已接入的业务 API/MCP 工具及当前用户权限。实施时要同时检查这些能力，不能仅添加推荐话术就宣称支持预约会议或创建任务。

用户的完整使用过程是：

1. **进入当前员工的页面**：在“项目经理”下面打开某个项目详情。
2. **查看其他员工可以如何帮忙**：点击“项目协作建议”，右侧展示配置的会议助理、任务助理及各自建议。
3. **选择要做的事**：例如点击任务助理的“查询当前项目的延期任务”。
4. **带着项目资料进入目标员工聊天**：主应用将当前项目上下文与所选建议准备成草稿，打开任务助理聊天页。用户无需再手动复制项目名称和标识。
5. **由用户确认后继续办理**：用户检查或补充草稿后发送，目标员工按自己的能力与权限处理；缺少会议时间、任务负责人等必要信息时继续询问。

这样，项目经理负责项目入口与整体信息，会议助理负责会议，任务助理负责任务，各员工围绕同一个项目衔接工作。这个功能连接的是“当前页面 → 相关员工 → 具体建议 → 带上下文的聊天交接”；点击推荐本身只准备草稿，不会自动发送消息、预约会议或创建任务，也不表示多个员工已经在后台自动互相调用。

## 开发者需要准备什么

先区分以下概念，再写按钮和消息：

| 概念 | 在本例中是什么 | 如何确定 |
| --- | --- | --- |
| 当前/所属员工 | 项目经理 | 用户从哪个员工的菜单进入页面；iframe 场景由宿主提供 ownerRobotId 上下文 |
| 当前业务页面与对象 | 项目详情页、示例交付项目 | 页面已有数据，至少准备稳定项目标识与项目名称 |
| 场景 | 项目协作建议，编码 pm_suggestion | 后台维护的一个推荐配置；同一场景可配置多位目标员工 |
| 推荐/目标员工 | 会议助理、任务助理 | 后台为场景选定，不由子页面在 postMessage 中指定 |
| 建议 | 安排周会、创建任务、查询延期任务等 | 每位推荐员工分别配置固定话术或自动生成提示词 |

**开发者**负责在项目详情页提供入口，把当前项目事实传给宿主；**实施人员**用 wk-setup 检查场景、推荐员工、工具和权限并保存配置；**喔壳主应用**负责侧滑栏、推荐展示、聊天跳转与草稿交接。开发业务页面时无需重复开发会议、任务或员工聊天界面。

要让建议随项目情况变化，有两种方式：

- **固定话术**：例如会议助理配置 `帮 {{project_name}} 安排本周周会`，任务助理配置 `查询 {{project_name}} 的延期任务`。页面通过 templateParams 替换项目名或负责人。固定话术按配置展示，变量替换不会自行判断项目是否延期。
- **自动生成**：分别为会议助理、任务助理填写符合其职责的推荐生成提示词。页面通过 generationContext 提供阶段、进度、延期情况、近期会议等真实信息，生成不同建议。它不会自动读取整张业务页面，也不会自动补出页面没有提供的事实；推荐目标员工仍来自已保存的场景配置。

上下文应包含目标员工继续办理所需的业务标识。例如将项目 ID、名称和当前状态放进 businessContext，必要时带上负责人用户 ID；不要只传“这个项目”或仅把 ID 放进 businessKey。businessKey 用于稳定识别当前业务对象，并不替代聊天草稿中的业务资料。员工真正查询或修改时，仍通过自己的业务接口重新核对权限及最新状态。

## 先在当前环境配置场景

**使用前，管理员必须在当前租户的“管理后台 → 数字员工 → 员工场景推荐”中配置、启用并保存场景。** 页面上也可能显示“数字员工场景推荐”。编码缺失、配置未知或场景不可用时，让当前 Agent 使用 **wk-setup** 检查已有场景和目标员工；缺少实施技能时，按以下步骤把配置交给管理员。

| 环境 | 后台配置入口 |
| --- | --- |
| 生产 | [员工场景推荐](https://agent.workopilot.com/ai-employee/scene-recommendations) |
| 测试 | [员工场景推荐（测试）](https://agenttest.workopilot.com/ai-employee/scene-recommendations) |

执行接入任务的 Agent 应先识别当前运行环境，向实施人员说明该页面用途，并使用当前 Agent 可用的浏览器/打开链接工具帮助打开对应入口；没有此能力时提供可点击链接。核对当前登录租户，必要时由管理员登录。打开页面仅代表进入配置入口，不代表场景已配置成功；实际保存后才能标记“已配置”。

以项目建议场景为例：

1. 在列表中查找 `pm_suggestion`。已有场景直接打开；首次创建时填写名称“项目协作建议”、编码 `pm_suggestion`，开启“启用场景”。该场景由项目经理下面的项目详情页调用。优先复用现有编码，避免创建同名重复场景。
2. 添加并启用“会议助理”“任务助理”等推荐员工，分别维护建议。选择测试用户有权访问且已开启聊天的员工，并检查会议/任务 API 或 MCP 能力是否已接入；推荐目标由这里的配置决定，不在 iframe 消息里指定目标员工。
3. 验证参数替换时选择“固定话术”：会议助理添加 `帮 {{project_name}} 安排本周周会`；任务助理添加 `查询 {{project_name}} 的延期任务`，也可添加 `给 {{assignee_name}} 创建一个跟进 {{project_name}} 联调问题的任务`。占位符名必须与调用方 templateParams[].key 一致；不要漏写占位符。
4. 需要动态建议时选择“自动生成”，按员工分别填写提示词。例如会议助理：“根据项目进度、阻塞事项与已有会议，推荐适合该项目的会议安排”；任务助理：“根据延期任务与待跟进事项，推荐需要查询或创建的任务，信息不足时提出补充问题，不编造负责人或截止时间”。由 wk-setup 核对系统 AI 服务 `wk_sys_ai_employee_recommend` 与模型可用性。
5. 点击“保存”，确认场景及推荐员工仍处于启用状态。交给开发实际 `sceneCode`、模板变量、目标员工、环境及测试用户。调用方的 `sceneCode` 必须与保存的编码一致。

## 从 iframe 打开场景推荐侧滑栏

在“项目协作建议”等业务按钮的点击事件中，把对象直接发送给**承载业务页面的直接父窗口**。`hostOrigin` 使用喔壳主应用的实际来源（协议、域名、端口），不含路径、/prod-api 或 /net-api，也不是子页面自己的来源。生产示例为 `https://agent.workopilot.com`，测试为 `https://agenttest.workopilot.com`；自定义域名和本地代理以实际宿主配置为准，不使用 `*`。

```javascript
function openProjectSuggestions(hostOrigin) {
  if (window.parent === window) {
    throw new Error('请从项目经理的项目详情页打开项目协作建议');
  }
  window.parent.postMessage({
    type: 'wk.recommendations.open',
    sceneCode: 'pm_suggestion',
    businessKey: 'project:001',
    businessContext: '项目ID：001\n项目：示例交付项目\n负责人：张三（用户ID：1008）\n当前阶段：联调测试\n进度：60%\n延期任务：3项\n本周尚未安排周会',
    generationContext: '项目处于联调阶段，进度60%，有3项延期任务，本周尚未安排周会。请结合各推荐员工职责给出下一步建议。',
    templateParams: [
      { key: 'project_name', value: '示例交付项目' },
      { key: 'assignee_name', value: '张三' },
    ],
  }, hostOrigin);
}

// 在业务按钮点击时调用；实际项目从已确认的宿主环境配置取得来源。
// openProjectSuggestions('https://agent.workopilot.com');
```

以上项目、人员 ID 和业务状态均为示例。接入时替换成当前页面有权读取的真实数据，每次点击读取最新数据；没有延期统计或会议信息时省略相应陈述，不把未知情况写成事实。不要 JSON.stringify 消息对象；不用自行传 Token、appCode、ownerRobotId 或 targetRobotId。主应用从当前页面取得应用编码及所属员工上下文，再按场景配置找到推荐目标员工。

消息对象的 JSON 形式（不是 HTTP 请求体）：

```json
{
  "type": "wk.recommendations.open",
  "sceneCode": "pm_suggestion",
  "businessKey": "project:001",
  "businessContext": "项目ID：001\n项目：示例交付项目\n负责人：张三（用户ID：1008）\n当前阶段：联调测试\n进度：60%\n延期任务：3项\n本周尚未安排周会",
  "generationContext": "项目处于联调阶段，进度60%，有3项延期任务，本周尚未安排周会。请结合各推荐员工职责给出下一步建议。",
  "templateParams": [
    { "key": "project_name", "value": "示例交付项目" },
    { "key": "assignee_name", "value": "张三" }
  ]
}
```

| 消息字段 | 类型 | 必填 | 语义与约束 |
| --- | --- | --- | --- |
| type | string | 是 | 固定为 `wk.recommendations.open`，大小写及点号不能改变 |
| sceneCode | string | 是 | 已保存的场景编码；去首尾空白后 1–64 字符，以字母或数字开头，后续仅字母、数字、点、下划线、短横线；与后台一致，建议小写 |
| businessKey | string | 否 | 当前业务对象的稳定标识，例如 `project:001`；切换对象时更新，不使用每次随机生成的值 |
| businessContext | string | 否 | 当前业务上下文，会进入聊天草稿；最多 30000 字符 |
| generationContext | string | 否 | 供 AI 生成推荐的补充信息，最多 30000 字符；不会因传入此字段就自动附到聊天草稿 |
| templateParams | array | 否 | 模板参数对象数组，不是键值字典；省略即不传变量 |
| templateParams[].key | string | 是 | 非空白变量名，如 `project_name` 对应 `{{project_name}}`；大小写一致 |
| templateParams[].value | string / number / boolean / null | 否 | 主应用转换为文本再准备草稿；省略或 null 按空文本处理，不支持对象或数组 |

未提供的顶层可选字段直接省略，不传 null。缺失模板变量会被替换为空文本，因此联调时应确认“示例交付项目”实际出现在话术和草稿中。

## 消息字段与 HTTP 字段的区别

postMessage 协议固定使用 lowerCamelCase：`sceneCode`、`businessContext`、`templateParams[].key/value`。后文 .NET DTO 则使用 `SceneCode`、`Context.BusinessContext`、`TemplateParams[].Key/Value`；不要把 HTTP 请求体直接作为 iframe 消息发送。接入现有侧滑栏时，无需在子页面重复实现 resolve/generate/prepare/draft/read/ack。

`window.parent.postMessage` 不返回业务 JSON，当前宿主接收器也没有定义响应消息或 requestId/ACK 协议；调用未抛异常不代表已经打开。以侧栏呈现、推荐内容和后续聊天草稿验证结果，不要等待虚构的 `wk.recommendations.open.result`。

## 联调与排查

1. 用测试用户从“项目经理”的实际菜单打开项目详情 iframe 页面，点击“项目协作建议”。预期右侧展示配置的会议助理、任务助理及各自建议。
2. 会议助理固定话术应显示“帮 示例交付项目 安排本周周会”，任务助理应显示“查询 示例交付项目 的延期任务”。分别选择建议，确认跳转到对应目标员工而非始终留在项目经理；检查草稿包含正确项目 ID/名称与所选话术，由用户决定发送。切换到另一项目后再验证一次，确保不带入上一项目的信息。
3. 完全不打开：检查消息对象和字段大小写、hostOrigin、是否是直接子 iframe，以及宿主是否已部署接收组件。宿主只接受当前承载 iframe 的 contentWindow，且 event.origin 必须匹配配置 iframe URL 的来源；跨源重定向、来源为 null 的沙箱或自行改为 window.top 都可能使消息被忽略。宿主还必须识别到当前 appCode。
4. 侧栏打开但为空：按提示核对当前环境/租户、场景编码、启用及保存状态、推荐员工访问权限和聊天开关；固定模式检查是否配置话术。AI 生成失败时进一步核对推荐系统服务与模型，而不是反复创建新场景。

消息契约于 2026-11-25 对照 Vue 远端 master 的 iframe-recommendations.vue、runtime-renderer.vue，以及推荐组件的模板替换和 .NET 草稿服务核对。宿主接收器与业务 iframe 需配套部署；后台配置仍需按目标租户核实。

以下为自建推荐界面使用的 .NET HTTP 契约。使用同一用户和应用上下文完成下列请求。固定推荐直接展示 resolve 返回的 Items；AI 推荐点击前先 generate。示例均为原始 HTTP JSON 节选。
## 解析当前场景

`POST /api/employee-recommendation/resolve`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "SceneCode": "contract_review",
    "ConfigVersion": "1",
    "Employees": [
      {
        "Id": "3001",
        "TargetRobotId": "1001",
        "TargetRobotName": "合同助手",
        "Mode": "generated",
        "Items": []
      }
    ]
  }
}
```

AppCode 和 SceneCode 为字符串。OwnerRobotId 可选，用于历史同码消歧。场景无效或停用时 data 为 null。

## 生成推荐话术

`POST /api/employee-recommendation/generate`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review",
  "RecommendEmployeeId": "3001",
  "BusinessKey": "contract:A-12",
  "Context": {
    "BusinessContext": "合同 A-12 的付款条款",
    "GenerationContext": "账期为30天，请建议需要核对的事项"
  }
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "ResultId": "result-01",
    "Items": [
      {
        "Id": "item-01",
        "Text": "帮我核对付款条款",
        "IsHighlighted": false
      }
    ],
    "Cached": false,
    "InputHash": "hash-01",
    "ExpiresAt": "2026-11-11 12:10:00"
  }
}
```

RecommendEmployeeId 取 Employees[].Id。GenerationContext 用于生成，BusinessContext 用于带入聊天；各最多 30000 字。BusinessKey 按业务记录取稳定值，可选 Force=true 重新生成。

## 将选中的推荐准备为草稿

`POST /api/employee-recommendation/prepare`

请求体

```json
{
  "AppCode": "contracts",
  "SceneCode": "contract_review",
  "RecommendEmployeeId": "3001",
  "BusinessKey": "contract:A-12",
  "Context": {
    "BusinessContext": "合同 A-12 的付款条款",
    "GenerationContext": "账期为30天，请建议需要核对的事项"
  },
  "ResultId": "result-01",
  "ItemId": "item-01",
  "TemplateParams": [
    {
      "Key": "contractNo",
      "Value": "A-12"
    }
  ]
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "DraftToken": "draft-01",
    "TargetRobotId": "1001",
    "ExpiresAt": "2026-11-11 12:10:00"
  }
}
```

固定推荐省略 ResultId。Context 使用最新内容，409 CONTEXT_CHANGED 时重新生成。模板变量名与场景配置一致。

## 读取本人草稿

`POST /api/employee-recommendation/draft/read`

请求体

```json
{
  "AppCode": "contracts",
  "TargetRobotId": "1001",
  "DraftToken": "draft-01"
}
```

成功响应

```json
{
  "code": 200,
  "data": {
    "DraftId": "draft-id-01",
    "AppCode": "contracts",
    "SceneCode": "contract_review",
    "TargetRobotId": "1001",
    "SessionMode": "new",
    "Text": "合同 A-12 的付款条款\n帮我核对付款条款"
  }
}
```

令牌绑定用户、租户、应用及目标员工。草稿写入输入框后确认。

## 确认已接收草稿

`POST /api/employee-recommendation/draft/ack`

请求体

```json
{
  "DraftId": "draft-id-01",
  "DraftToken": "draft-01"
}
```

成功响应

```json
{
  "code": 200,
  "data": true
}
```

用户确认后再发送聊天。错误示例（HTTP 409）

```json
{
  "code": 409,
  "msg": "草稿已失效",
  "errorCode": "DRAFT_UNAVAILABLE",
  "traceId": "example"
}
```



