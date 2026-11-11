# WorkoPilot skills for application development

[简体中文](README.md) · English

Use these skills to design and integrate WorkoPilot features in your own project. Use `wk-setup` to provision tenant resources and `wk-api` to call those resources from your application. The bundled skill instructions and API references are written in Chinese. You can give the agent the English prompts below.

## Install in your project

You need Git and a GitHub account with **read access to this repository**. Open a terminal at the **root of your own application project** and run one of the following command blocks. It clones the repository into a temporary directory, then copies both skills into your project's `.agents/skills/`, including their scripts, API references, and examples. These commands are for a first installation.

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

To install just one skill, keep only its source directory in the copy command. Verify that the selected skill has a `.agents/skills/wk-setup/SKILL.md` or `.agents/skills/wk-api/SKILL.md` file. Open your application project in Codex, start a new chat, and invoke the skill with `$wk-setup` or `$wk-api`. For another AI tool, use its project skill directory or ask the agent to read the corresponding `SKILL.md` file directly.

## Which skill to use

| Your goal | Skill | What you get |
| --- | --- | --- |
| Create or reuse a digital employee or AI service in a tenant, or configure employee menus and cards | [wk-setup](skills/wk-setup/SKILL.md) | Resources provisioned with a WorkoPilot API key, the environment, resource codes and IDs, and any remaining manual configuration |
| Call existing capabilities from your own framework or a WorkoPilot AI app | [wk-api](skills/wk-api/SKILL.md) | Integration using your application's user token and HTTP client, with request, response, and error handling |

When you need both, start with `wk-setup` and pass the **resource code for the target environment** to `wk-api`. The prompts below work as a pair. GitHub credentials grant access to download the skills. The provisioning scripts read the WorkoPilot API key from the execution environment.

## Prompts you can send to your agent

**wk-setup · Prepare a contract summary service in a test tenant**

> $wk-setup Prepare an AI service in the WorkoPilot test tenant with the code contract_summary. It takes the full contract in a field named text and returns a summary in Chinese. Check the environment and look for an existing service with that code. If it exists, verify its input and output. If it is missing, create it using the provisioning API key configured in the environment. Report the environment, actual serviceCode, input field, and a sample request. Keep credentials out of your response.

**wk-api · Use the service in a third-party application**

> $wk-api Add a “Generate summary” button to the contract detail page in this project. The test tenant has a contract_summary service whose text input takes the current contract's full text. Inspect the project's environment, sign-in flow, and HTTP client. Reuse the existing client and current user's token to call the service synchronously. Display the summary and handle loading, expired sessions, and service errors. Explain how to verify the integration in the test environment.
