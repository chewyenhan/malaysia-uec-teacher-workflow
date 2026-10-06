# NotebookLM 路线：从首次接入到本机 PPTX

本文件只在教师选择 NotebookLM 时读取。工作流负责教学内容、页面结构和验收；NotebookLM 负责来源问答与 Studio 课件生成。

## 先说清楚工具和文件在哪

本流程采用社区项目 [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py)，不是 Google 官方 MCP。它的 MCP 标为实验性／预览，工具参数或行为可能变化；开始前检查上游最新的[安装说明](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)、[MCP 指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/mcp-guide.md)、[CLI 参考](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md)和[上游 Skill](https://github.com/teng-lin/notebooklm-py/blob/main/SKILL.md)。

| 运行方式 | 能做到什么 | 文件交付边界 |
|---|---|---|
| 本机 Agent + 本机 stdio MCP | Agent 直接调用 NotebookLM 工具；`studio_download` 可指定本机绝对路径并选择 PPTX | 保存后检查该路径确有完整 PPTX，才报告“已下载到本机” |
| 远程／云端 MCP | Agent 在云端连接 NotebookLM、生成课件 | 下载工具提供临时下载链接；让教师打开链接保存到电脑。未检查本机文件前，不声称已保存到教师电脑 |
| 本机终端 + `notebooklm-py` CLI | 没有 MCP 的 Agent 若仍可运行教师本机命令，也能登录、生成、查询及下载 PPTX | CLI 输出路径在实际运行命令的那台机器；先确认终端不是远端容器 |
| 以上均不可用 | 不能声称已完成 NotebookLM 自动化 | 保留教案、大纲和讲稿，说明阻碍，并让教师选择其他 PPT 路线或稍后继续 |

PPTX 是 PowerPoint 文件格式；不保证每一页中的图像、文字和版面都能像普通文本框一样编辑。按成品实际情况说明可编辑性。

## 1. 判断现有环境

教师选 NotebookLM 后，先核对 Agent 是否有 NotebookLM MCP 工具、MCP server 是否通过只读请求，以及本轮终端和文件系统究竟在本机还是云端。已连接且认证有效就直接复用，不重复安装或添加。不能把“包已安装”“凭据文件存在”或“Python 能 import”当作连接成功。

如果客户端没有 MCP，先判断两件事：客户端是否支持本机 stdio MCP；Agent 是否能在教师本机运行终端命令并读取下载文件。说明用户只需首次安装一次配套工具、亲自在浏览器完成 Google 登录；Agent 随后按本文件完成来源整理、上传、生成、轮询、PPTX 下载和检查。不要把安装任务留成只有一段链接的说明。

## 2. 安装并接入 MCP（新用户流程）

### 2.1 安装配套命令

推荐用隔离安装，不修改系统 Python：

```bash
uv tool install "notebooklm-py[browser,mcp]"
```

此命令提供 `notebooklm` CLI、交互式登录需要的浏览器组件，以及 MCP server。若没有 `uv`，按 [uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)安装；安装后新开终端，再继续。若不希望持久安装，可按上游文档用 `uvx --from "notebooklm-py[browser,mcp]" notebooklm ...` 一次性运行。不得静默改装未经核实的同名包。

### 2.2 由教师登录并验证

```bash
notebooklm login
notebooklm auth check --test --json
```

教师在弹出的 Google 登录页自行登录。只检查返回的认证状态；不要索取、回显或写入日志任何密码、Cookie、token 或 `storage_state.json` 内容。要求实时测试通过；仅凭文件存在或不带实时测试的状态不足以证明服务可访问。

### 2.3 把 MCP 接到当前 Agent

上游当前自动配置器支持以下客户端，逐字使用其支持的名称：

```bash
notebooklm mcp install claude-desktop
notebooklm mcp install claude-code
notebooklm mcp install cursor
notebooklm mcp install windsurf
```

只运行教师实际使用客户端对应的一条命令。完成后完全退出并重新启动该 Agent，检查 NotebookLM MCP 工具出现，再用只读列表工具确认账号连接成功。

其他支持 MCP 的 Agent（包括没有列入上游自动配置器的客户端），按照该客户端自己的官方 MCP 文档添加 stdio server。常见配置形状如下，但配置文件位置、字段名和重载方法以客户端文档为准：

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uvx",
      "args": ["--from", "notebooklm-py[mcp]", "notebooklm-mcp"]
    }
  }
}
```

保留配置文件中其他 server，不覆盖整个文件。检查 `uvx` 可在当前 Agent 进程环境的 PATH 中运行；保存后重启 Agent，再检查真实工具调用。不要假设上游自动安装器支持任意客户端，也不要猜客户端配置路径。

### 2.4 Agent 不支持 MCP 时：本机 CLI 备用

若 Agent 没有 MCP 支持，但能运行教师电脑上的 `notebooklm` 命令，沿用同一配套工具完成全流程。这个接口是 CLI，不称作 MCP。先确认 `notebooklm --version`、`notebooklm auth check --test --json` 和 `notebooklm list --json` 可成功；随后按第 4–6 节完成材料、生成和下载。若 Agent 只能在云端运行命令，不能把云端路径说成本机路径：改用远程下载链接给教师，或让教师选另一条可用课件路线。

给无法自动配置的客户端，可提供以下说明并继续在可用的本机 CLI 环境中完成工作：

> 请按本 Agent 的官方 MCP 文档，在不改动现有配置的前提下接入 `notebooklm-py` 的本机 stdio server。先检查 `uvx`、MCP 工具和 NotebookLM 登录状态；若当前客户端不支持 MCP，但能运行本机 `notebooklm` 命令，请明确改用上游 CLI 完成同一课件流程。Google 登录由我自己完成。生成后请把 PPTX 下载到我指定的本机课题文件夹，并核验文件。

## 3. 备齐四份来源并取得上传确认

完整备课的四份来源为：

| 角色 | 内容 | 常见文件名 |
|---|---|---|
| 教材 | 教师提供或认可的完整课文，含必要表格、图注与图像 | `source-material.txt` 或原始 PDF／DOCX |
| 教案 | 本课目标、活动、评量、课时 | `detailed-lesson-plan.md` |
| 大纲 | 稳定页码、逐页内容和视觉要求 | `slides-outline.md` |
| 讲稿 | 与大纲逐页对应的解释、问题和过渡 | `teacher-notes.md` |

材料清单不能代替教材原文；不为凑数把同一文件当作四种来源。列出准确文件名和上传账号／笔记本，移除无关学生资料。教师明确确认上传范围后，才创建／选用笔记本并上传。账号有歧义先询问；来源内容未解析完成时不开始生成。

## 4. 上传、确认来源就绪

新课题创建一个笔记本；续做先按任务记录中的 Notebook ID 核对账号与笔记本，不重复创建。为四份来源分别保存 Source ID、处理状态和文件摘要；四项来源都已就绪后再进入生成。文件更新时只处理变化项；不为清理而自动删除旧来源。日志只保留必要 ID 和状态，不写教材全文或认证凭据。

生成前确认所选来源 ID 恰好对应教材、教案、大纲、讲稿；不能只因为上传成功返回 ID 就认定来源解析完成。

CLI 备用路线若要新建笔记本，先列出现有笔记本；教师确认后再用 `notebooklm create "<课题名称>" --json`，或明确选择现有 ID。每个本机来源分别上传并等待处理完成：

```bash
notebooklm source add "D:/课程文件/本课/source-material.pdf" --type file --notebook <notebook-id> --json
notebooklm source wait <source-id> --notebook <notebook-id> --json
```

对教案、大纲、讲稿各重复一次；每次记下返回的 Source ID，确认四项 source 均已就绪后才继续。上传前仍须取得教师对具体文件和 NotebookLM 账号的确认。

## 5. 生成并持续查询同一任务

用 Studio 生成 slide deck 时，明确传入本课四个 `source_ids`、中文 `language`、与大纲一致的制作指令及适合本课的页数／风格。指令把四份来源分工写清：教材负责事实依据、教案负责课堂目标和节奏、大纲负责页面顺序与逐页内容、讲稿负责解释和提问。大纲是结构蓝本，生成结果仍须逐页核对。

MCP 路线：调用 `studio_generate`，记录返回的 `task_id`，再对同一任务调用 `studio_status` 直到完成或失败。CLI 路线：按当前 CLI 的 `generate slide-deck --help` 读取有效参数；可将长中文指令放入文件，用 `--prompt-file`，重复 `-s/--source` 指定四份 Source ID，并以 `-n/--notebook` 锁定笔记本；保存返回 ID 并用 `notebooklm artifact poll`／`wait` 查询原任务。

任务仍在生成时保存状态并继续轮询原任务；等待超时不能重新提交。只有确定失败后才诊断原因；重试前说明可能产生新的服务消耗，按教师当前指示处理。

## 6. 下载真实 PPTX 到指定位置

开始生成前，先取得教师指定的本机课题目录；未指定时使用本次任务工作文件夹并明确展示绝对路径。下载前再次识别运行环境是本机还是云端。

### 本机 MCP / 本机 CLI

MCP 使用上游 `studio_download`，指定正确的 `artifact_id`、`artifact_type="slide-deck"`、`output_format="pptx"` 和教师确认的绝对 `path`，例如：

```text
D:/AIgames/lesson plan/J1/_课题_W周/teaching-slides.pptx
```

CLI 可将指定 artifact 下载到本机绝对路径：

```bash
notebooklm download slide-deck "D:/课程文件/本课/teaching-slides.pptx" --notebook <notebook-id> --artifact <artifact-id> --format pptx
```

命令实际选项以已安装版本 `notebooklm download slide-deck --help` 为准；有同名文件时先报告并使用不会覆盖的文件名，不擅自覆盖。完成后检查指定路径中的文件确实存在、非空、PPTX/ZIP 结构可读取且页面数量与导出结果一致；再渲染或打开页面，核对中文、史实、顺序和 PPT 同步。QA 未完成就标记待核，不把“命令执行成功”当作成品验收。

### 远程／云端 MCP

远程下载返回临时 `download_ready` 链接。把链接作为下载动作展示给教师，并说明需打开后保存到本机指定文件夹。只有本机侧取得并检查文件后，才报告“PPTX 已下载到电脑”；否则状态写作“已生成，待教师下载”。链接失效时按已记录的 artifact ID 再生成下载链接，不重新生成课件。

NotebookLM 的网页界面与本社区工具的下载能力可能不同；若当前版本无法导出 PPTX，保留 PDF 为中间件并明确 PPTX 未完成，不改扩展名冒充 PPTX。上游 CLI 文档目前记录了 `--format pptx`，MCP 文档也记录 slide deck 的 `output_format=pptx`；每次仍以已安装版本和实际结果为准。

## 7. 逐页 QA、修正与恢复

逐页对照稳定页码、大纲、讲稿和教师资料，重点检查专名、事实、年代、数字、公式、地图、版面和可读性；记录通过数、修正页、待核项。PPTX 格式不自动代表所有元素可编辑，打开实际文件后才说明文字或页面元素的可编辑性。

中断时保存 notebook ID、四个 source ID、task／artifact ID、最后已完成状态、输出路径和 QA 记录；恢复时查询原任务／artifact，不重复上传或生成。失败时分类为未安装、未登录、MCP 配置、来源未就绪、服务生成、下载或 QA；交付已完成的教案、大纲、讲稿并保留 PPTX 未完成状态，让教师决定修复当前路线或切换到另一路线。

生成与后续修改均须执行 [PPT 同步关卡](ppt-synchronization.md)，保存逐页映射及成品摘要；选择风格前须读取[完整 PPT 风格库](slide-style-library.md)。
