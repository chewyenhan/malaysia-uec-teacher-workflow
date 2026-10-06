# 教师备课工作流
### 独中统考适配 · 自定义课程

[![Status](https://img.shields.io/badge/status-public%20beta-f59e0b)](#项目状态)
[![Version](https://img.shields.io/badge/version-0.3.0-2563eb)](#本次更新)
[![License](https://img.shields.io/badge/content-CC%20BY--NC--SA%204.0-16a34a)](LICENSE.md)

**提供课文与教学要求，得到彼此配套的教案、课件、讲稿和评量。**

面向教师的跨科 AI Agent Skill，含马来西亚独中／UEC 统考适配，也支持按教师指定的教材、课程标准、课时与模板走自定义路线。先做好一堂课，再依据实际检查交付；不固定学校、年级、课时或课件工具。

> 由 **Chew Yen Han（朱彦翰）** 独立开发。非董总官方项目，不内置董总课本或私人学校模板。

| 你提供 | 工作流处理 | 你得到 |
|---|---|---|
| 课文、表格、图片、公式、练习 | 完整读取，核对范围与来源 | 内容清单与课程依据记录 |
| 学生程度、目标与课时 | 对齐目标、活动、评量、补教 | 详细教案与课堂任务 |
| 学校 Excel／Word 模板（需要时） | 识别位置，保留结构与其他内容 | 简略教案副本 |
| 课件偏好 | 大纲、逐页讲稿、实际课件检查 | 配套材料及验收记录 |

## 从哪条路线开始

**课程路线与课件路线分别选择：**

| 课程路线 | 适用情况 | 依据 |
|---|---|---|
| 独中／统考适配 `uec` | 教授统考内容的独中或补习教师 | 官方公开考纲＋教师材料 |
| 自定义课程 `custom` | 其他课程，或独中老师的非统考课程 | 教师指定标准／目标＋教材 |

没有外部考纲时可以先依据教材备课，会明确标注“未核对外部考纲”。自定义路线不自动下载或套用统考考纲，也不声称已认证任何国家课程。

课程体系与 PPT 制作方法分别选择。每次提供 NotebookLM MCP 来源驱动生成、AI Agent 调用当前可用生图工具生成整页图片式 PPTX 两种视觉方案；需要逐字编辑页面文字时可选 `editable`。图片式 PPTX 的文字通常不能像普通文本框逐字修改。

## 安装：交给你的 AI Agent

复制下列请求给能读取文件、安装 Skill 并执行必要工具的 AI Agent：

```text
请读取 https://github.com/chewyenhan/malaysia-uec-teacher-workflow
的 README.md 和 SKILL.md，检查我的环境是否已安装这个工作流。
如未安装，请按当前 Agent 的技能安装方式安装整个工作流及其参考文件，
保留已有配置。先告诉我需要哪些工具；只安装本次任务实际需要的依赖。
不要上传材料或安装 NotebookLM，除非我选择这条路线。
```

安装后，AI 会收齐本课真正需要的参数。普通聊天窗口未必支持安装或运行 Skill；需要兼容的 Agent 环境。首次 Google 登录仍由教师完成。

也可下载 [最新 Release](https://github.com/chewyenhan/malaysia-uec-teacher-workflow/releases/latest) 的完整 ZIP，或使用：

```bash
git clone https://github.com/chewyenhan/malaysia-uec-teacher-workflow.git
```

把完整文件夹安装或链接到当前 Agent 的技能目录，位置以该工具的当前说明为准。只复制 SKILL.md 会漏掉参考文件与检查工具。仓库、文件夹及调用名称继续使用 `malaysia-uec-teacher-workflow`，兼容原有安装；老师看到的新标题清楚说明两种课程路线。

## 第一次使用

**独中／统考适配**

```text
使用 $malaysia-uec-teacher-workflow。
我教初二历史，一节课40分钟。根据附上的课文备课并核对统考考纲。
需要详细教案、学校Excel模板的简略教案、大纲和讲稿。
PPT 选 NotebookLM，风格写实。先列出准备上传的材料。
```

**自定义课程**

```text
使用 $malaysia-uec-teacher-workflow，自定义课程路线。
我教五年级数学，一节30分钟，主题是同分母分数加法。
按附上的材料和教学目标设计，不对照统考。
要详细教案、大纲、讲稿与课末练习。PPT 请先比较 NotebookLM MCP 与 AI 生图整页两种方案。
```

第一次选择自定义课程时，Agent 会用一轮询问确定课程标准依据、常用科目／年级／课时、教学与评量偏好、PPT 默认选择，并询问这些设置是只用于本课还是保存为该课程的默认配置。教师确认后才保存；学校名称、班级人数和个人账号等非必要资料可以不填。以后沿用已确认的默认值，只问本课变化。可参考 [首次设置流程](references/first-run.md) 与 [教师配置示例](teacher-profile.example.yml)。

默认交付详细教案、逐页讲稿、PPT 大纲和真实 PPTX；教师明确限定时才缩小范围。课程设置不会自动授权把材料上传第三方服务。

先想看成果再安装？看这个完全原创的 [自定义数学案例](examples/custom-fractions/README.md)：材料、教案、大纲、讲稿、记录齐全，没有使用版权课文、私人模板或学生资料。

## NotebookLM：可选配套，完整流程

配套项目为 **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)**，本路线明确使用它提供的 NotebookLM MCP。常见本地 stdio 配置如下；不同 Agent 的配置文件位置和重载步骤按各自 MCP 文档处理：

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

先检查现有 MCP，避免重复添加。初次使用需按配套说明登录并验证实时连接；教师自行完成 Google 登录。MCP 连接后，工作流先准备教材、教案、大纲、讲稿四份来源，逐一列出上传范围，取得本课上传确认后才上传、生成和检查成品。`notebooklm-py` 为非 Google 官方社区项目，其 MCP 文档标注为实验性，接口可能变化；参阅[安装说明](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)和[MCP 指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/mcp-guide.md)。

```text
检查已有工具 → 缺少时配置配套程序与 Skill → 教师 Google 登录
    → 准备四份资料 → 列明上传范围 → 上传并确认来源就绪
    → 生成并保存任务 ID → 下载 → 逐页核对与修正 → 交付
```

四份来源是 **教材、教案、大纲、讲稿**；材料清单不能代替教材。详细指引与恢复方法在 [NotebookLM 工作流](references/notebooklm-workflow.md)。

如果当前 Agent 没有图像生成工具，可选的 AI 生图路线会如实标记受阻，不会假装生成或静默切换；其完整跨 Agent 流程见 [AI 生图整页 PPTX](references/imagegen-pptx-workflow.md)。PPTX 不自动等于文字可编辑，工作流会说明实际情况。

## 可检查，也能接着做

- 每页用同一编号连接大纲、讲稿和实际课件。
- 用本课任务记录保存进度；登录失效或远程生成未结束，不从头再做。
- 问题页单独修正，记录依据并复查关联文件。
- 保存“通过多少项、修正哪里、哪些仍待核”的验收记录。

离线结构检查不会联网、上传或更改材料：

```bash
python scripts/check_lesson_bundle.py path/to/lesson-folder
```

它检查四份来源、页面对应和已有课件格式，**不代替内容与画面检查**。详见 [验收与继续执行](references/quality-and-resume.md)。

## 独中适配：统考考纲

先查已有官方缓存。需要同步时按级别运行：

```bash
python scripts/sync_uec_syllabi.py --level junior
python scripts/sync_uec_syllabi.py --level senior
```

完整同步可选 `--level all`；查看下载清单加 `--list-only`。脚本只接受董总官方域名，记录来源、时间与 SHA-256，部分失败会报不完整。下载后仍须定位本课内容和版本；不编造编号、题型比例或“高频考点”。

## 本次更新

v0.3.0 加入自定义课程首次设置与可复用默认值；把 NotebookLM MCP 和 AI 生图整页课件设为必须介绍的两种视觉方案，补齐跨 Agent 生图步骤与图片式 PPTX 验收，并让离线检查器识别该路线。`editable` 仍用于明确需要可编辑文字的课件。此前 v0.2.1 加强默认四项交付、完整教学模板和最终完整性检查；v0.2.0 扩展两种课程入口并补齐 NotebookLM、恢复记录和离线检查。

## 项目状态

**公开 beta。** 新版自定义数学示例与本地检查已验证；不能把这些结果当成所有学科、国家课程或第三方服务均已端到端验证。NotebookLM 的真实账户生成受账号、额度、接口和教师上传授权影响，首次使用应以自己的小课题试跑。

核心版本免费公开。已发布版本的许可证保持有效；商业授权、培训与校本定制仍依以下授权说明办理。

## 版权与教材边界

- 教师必须自行提供有权使用的教材或讲义。
- 本仓库不会提供或协助寻找未经授权的课本副本。
- “教学用途”不自动等于可以公开上传或重新分发教材。
- 本项目名称中的 Dong Zong / 董总 / UEC 只用于说明适用场景，不表示官方认可。

完整说明见 [版权与隐私](references/copyright-and-privacy.md)。

## 授权方式

- `SKILL.md`、README、`references/`、`examples/`、示例配置与评测内容：**CC BY-NC-SA 4.0**
- `scripts/` 与 `tests/`：**MIT License**
- 教师自行上传的课文、模板及生成成果：不因使用本仓库而自动改变原有权属

详情见 [LICENSE.md](LICENSE.md)。

### 商业使用与授权

- 教师个人、学校内部的非商业教学使用，可依 CC BY-NC-SA 4.0 条款使用本项目的工作流与文档。
- `scripts/` 与 `tests/` 采用 MIT License，可在保留版权声明及许可文本的前提下商业使用。
- 将工作流、文档、参考资料或其改编版本用于收费培训、收费安装、商业产品、付费平台或其他主要追求商业利益的用途，不属于 CC BY-NC-SA 4.0 所允许的非商业使用；请先取得书面商业授权。
- 商业授权、培训、安装配置或校本定制需求，请通过 [商业授权咨询](https://github.com/chewyenhan/malaysia-uec-teacher-workflow/issues/new?template=commercial-license.yml) 联系。提交公开 Issue 时请勿填写电话号码、私人邮箱、学生资料、学校内部文件或 API 密钥。

如果你正在使用本项目，欢迎提交一份不含私人资料的 [使用登记](https://github.com/chewyenhan/malaysia-uec-teacher-workflow/issues/new?template=usage-report.yml)。登记完全自愿，不影响任何许可证权利。

## 参与改进

欢迎不同课程、不同科目的老师提交使用案例、问题与改进建议。请勿在 Issue、Pull Request 或测试资料中上传课本扫描页、学生个人资料、学校内部文件或 API 密钥。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。


## English summary

**Teacher Lesson Workflow**, with Malaysian UEC adaptation and a custom-curriculum route, is a source-grounded AI Agent skill. Teachers provide materials, lesson duration, requested outputs and, where relevant, curriculum standards or school templates.

The shared teaching core produces aligned lesson plans, concise school-template plans, slide outlines, teacher notes and assessments. First-time custom-curriculum users can establish reusable course defaults. PPT options include NotebookLM MCP and image-generated full-slide PPTX; editable text slides remain available when required. The local checker validates package structure, not pedagogical quality or live-service availability.

The existing repository and invocation identifier remain `malaysia-uec-teacher-workflow`. No textbooks, school records or login credentials are bundled.

AI Agent 的逐页制作步骤见 [直接生成PPTX](references/agent-pptx-workflow.md)。最终四项交付的结构检查使用 `python scripts/check_lesson_bundle.py path/to/lesson-folder --require-complete`；普通检查可用于生成前准备检查，不能证明最终完成。
