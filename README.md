# 马来西亚独中教师 AI 教学工作流

## Malaysia UEC Teacher Workflow

[![Status](https://img.shields.io/badge/status-public%20beta-f59e0b)](#项目状态)
[![Docs](https://img.shields.io/badge/docs-中文%20%7C%20English-2563eb)](#english-summary)
[![License](https://img.shields.io/badge/content-CC%20BY--NC--SA%204.0-16a34a)](LICENSE.md)

一个面向马来西亚华文独中教师的跨科 AI Skill。教师提供自己合法持有的课文、讲义与校本模板，AI 负责完整读取材料，并生成详细教案、简略教案、教学简报、教师讲稿与课堂评量。

适用于初中、高中及不同科目，不绑定某所学校、不内置受版权保护的董总教材，也不强制使用某一家 AI、PPT 或生图工具。

> 本项目由 **Chew Yen Han（朱彦翰）** 独立开发，并非董总官方项目，与董总不存在隶属、授权或代言关系。

## 为什么做这个项目

一般 AI 很容易漏读教材里的表格、图片、图表、公式、史料框或练习，也容易写出“目标很好看，但课堂无法判断学生有没有学会”的教案。本 workflow 把几个关键动作固定下来：

- 完整盘点教材，而非只读取正文段落；
- 依据教师提供的课文，不擅自补写教材内容；
- 对齐目标、学生活动、评量证据、达标标准与补教；
- 适配教师自己的简略教案 Excel/Word 模板；
- 根据当前 AI 能力选择原生简报、NotebookLM 或其他路线；
- 对照董总/统考官方公开考纲，同时保留来源与版本信息。

## 可以生成什么

- 详细教案（Markdown、Word 或教师指定格式）
- 校本简略教案（Excel/Word 模板适配）
- 教学简报大纲、PPTX 与教师讲稿
- 诊断性、形成性及总结性评量
- 补教、延伸与差异化任务
- 教材内容清单及考纲对照记录

## 不包含什么

- 董总课本、教师手册、扫描页或题库
- 未经授权复制的教材图片、地图或表格
- 某位教师的私人讲义、学校 Excel、班级资料或本机路径
- 固定 35/40/45 分钟、固定周次或固定 PPT 风格
- 强制依赖特定 AI 模型、图片生成器或 MCP

## 安装

推荐从 [最新 Release](https://github.com/chewyenhan/malaysia-uec-teacher-workflow/releases/latest) 下载完整 ZIP；Release 附件的下载次数可供项目维护者统计。也可以使用 Git clone：

下载或 clone 本仓库，把整个 `malaysia-uec-teacher-workflow` 文件夹放入你的 AI 助手所使用的 skills 目录。不同工具的目录位置不同，请以该工具当前版本的官方说明为准。

```bash
git clone https://github.com/chewyenhan/malaysia-uec-teacher-workflow.git
```

也可以保留为独立仓库，再从 AI 助手的 skills 目录建立链接。不要只复制 `SKILL.md`；`references/` 和 `scripts/` 也是工作流的一部分。

## 第一次使用

教师只需提供本次需要的资料。一个典型请求：

```text
使用 $malaysia-uec-teacher-workflow。
我是初二科学老师，一节课 40 分钟。
请根据我附上的课文和学校 Excel 模板，生成详细教案、简略教案和教学 PPT。
PPT 希望可编辑；课文中的实验表格和安全提醒都要读取。
```

第一次使用时，AI 会询问必要的默认设置，例如学校课时、常用输出格式和输出目录。示例见 [`teacher-profile.example.yml`](teacher-profile.example.yml)。配置不是强制；没有配置也能按单次请求工作。

## 统考考纲同步

仓库不重新分发董总文件，只保存官方入口。需要时可把官方公开考纲同步到本机缓存：

```bash
python scripts/sync_uec_syllabi.py --level all
```

只查看即将下载的文件：

```bash
python scripts/sync_uec_syllabi.py --level all --list-only
```

脚本只接受董总官方域名及官方域名内的重定向，并为下载文件记录来源网址、时间与 SHA-256。当前完整性基线为初中 8 科、高中 25 科；任何入口、科目页或文件失败都会标记为不完整并返回错误。网页结构若改变，脚本会停止并请使用者直接查看官方入口，不会改从非官方网站下载。

## 简报路线

本 skill 不假定“某种 PPT 做法永远最好”。AI 应先比较当前可用能力：

1. 原生简报/生图工具：适合高质量、可编辑或需要定制视觉的成品；
2. NotebookLM：适合快速制作以教师来源为依据的简报；
3. 仅生成大纲与讲稿：当环境暂时没有可靠的简报工具时使用。

NotebookLM 是可选项。若使用者的 AI 没有相应接口，AI 应说明情况，并在取得同意后协助配置兼容的连接方式；不得静默下载安装第三方工具。

## 项目结构

```text
malaysia-uec-teacher-workflow/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
├── tests/
├── evals/evals.json
├── teacher-profile.example.yml
├── LICENSE.md
├── NOTICE.md
└── CONTRIBUTING.md
```

## 项目状态

目前核心版本免费公开，方便独中教师试用、检验不同科目与校本格式并提供意见。已经发布的版本继续受当时许可证约束；未来的新组件或服务可能采用不同授权，并可能提供收费培训、安装配置、校本模板定制、批量工具及技术支持。

## 版权与教材边界

- 教师必须自行提供有权使用的教材或讲义。
- 本仓库不会提供或协助寻找未经授权的课本副本。
- “教学用途”不自动等于可以公开上传或重新分发教材。
- 本项目名称中的 Dong Zong / 董总 / UEC 只用于说明适用场景，不表示官方认可。

完整说明见 [版权与隐私](references/copyright-and-privacy.md)。

## 授权方式

- `SKILL.md`、README、`references/`、示例配置与评测内容：**CC BY-NC-SA 4.0**
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

欢迎不同科目的独中老师提交使用案例、问题与改进建议。请勿在 Issue、Pull Request 或测试资料中上传课本扫描页、学生个人资料、学校内部文件或 API 密钥。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## English summary

**Malaysia UEC Teacher Workflow** is an unofficial, cross-subject AI skill for teachers in Malaysian Chinese Independent Schools. Teachers provide lesson materials they are legally entitled to use; the AI inventories all content—including tables, figures, formulas and exercises—then produces aligned lesson plans, school-template spreadsheets, slides and assessments.

The repository does not bundle Dong Zong textbooks or private school materials. It supports junior and senior levels, adapts to each school's timetable and templates, and selects presentation tools according to the user's needs and the AI environment's actual capabilities.

Search terms: 马来西亚独中、华文独中、董总、统考、教案、简略教案、教学简报、UEC、Dong Zong、Chinese Independent School、lesson plan、teacher workflow、AI skill.
