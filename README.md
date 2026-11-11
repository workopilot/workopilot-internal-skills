# 喔壳业务开发技能

简体中文 · [English](README.en.md)

第三方团队可以用这两个技能在自己的项目中设计和接入喔壳业务。实施人员用 `wk-setup` 配好租户资源，开发人员用 `wk-api` 把这些资源接进业务应用。

## 安装到项目

准备好 Git，并使用**对本仓库有读取权限**的 GitHub 账号。打开终端，进入**你自己的业务项目根目录**，选择下面一组命令。命令会把仓库克隆到临时目录，再把两个完整技能复制到项目的 `.agents/skills/`，包括脚本、接口文档和示例。以下命令用于首次安装。

**macOS / Linux**

```bash
src="$(mktemp -d)" &&
git clone --depth 1 https://github.com/workopilot/workopilot-internal-skills.git "$src" &&
mkdir -p .agents/skills &&
cp -R "$src/skills/wk-setup" "$src/skills/wk-api" .agents/skills/
```

**Windows PowerShell**

```powershell
$src = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
git clone --depth 1 https://github.com/workopilot/workopilot-internal-skills.git $src
if ($LASTEXITCODE -ne 0) { throw "Git clone failed." }
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Copy-Item "$src/skills/wk-setup", "$src/skills/wk-api" -Destination .agents/skills -Recurse -ErrorAction Stop
```

只需要一个技能时，复制命令中只保留对应的源目录。安装后确认所选技能的 `.agents/skills/wk-setup/SKILL.md` 或 `.agents/skills/wk-api/SKILL.md` 存在。在 Codex 中打开这个业务项目，新建对话，输入 `$wk-setup` 或 `$wk-api` 调用。其他 AI 工具可按其项目技能目录约定安装，或直接让它读取对应的 `SKILL.md`。

## 什么时候用哪个

| 你的目标 | 选择 | 交付结果 |
| --- | --- | --- |
| 在目标租户创建或复用数字员工、AI 服务，配置员工菜单或卡片 | [wk-setup](skills/wk-setup/SKILL.md) | 用实施 API Key 配置资源，交付环境、资源编码和 ID，并列出需要手工配置的项 |
| 在自有框架或喔壳 AI 应用中调用已有能力 | [wk-api](skills/wk-api/SKILL.md) | 复用应用的用户 Token 和请求库，按 HTTP 契约处理请求、响应和错误 |

两步都需要时，先用 `wk-setup` 取得**目标环境的资源编码**，再交给 `wk-api`。例如，下方两条提示词可以依次使用。GitHub 凭据用于下载技能；运行实施脚本时，从执行环境读取喔壳 API Key。

## 可直接发给 AI 的例子

**wk-setup · 为测试租户准备合同摘要服务**

> $wk-setup 在喔壳测试租户准备一个合同摘要 AI 服务，编码为 contract_summary，输入字段 text 是合同正文，输出为中文摘要。先检查执行环境和同编码服务；已有服务就核对输入输出，缺少时用环境中配置的实施 API Key 创建。完成后告诉我环境、实际 serviceCode、输入字段和一个测试请求。请勿在回复中输出凭据。

**wk-api · 在第三方应用调用已有服务**

> $wk-api 请在当前项目的合同详情页加一个“生成摘要”按钮。测试租户已配置 contract_summary，输入 text 取当前合同正文。先检查当前应用的环境配置、登录态和请求库，沿用已有封装，用当前用户 Token 同步调用该服务。点击后显示摘要，并处理加载、登录失效和业务失败。完成后说明如何在测试环境验证。
