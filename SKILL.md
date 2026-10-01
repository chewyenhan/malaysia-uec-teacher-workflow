---
name: malaysia-uec-teacher-workflow
description: Create source-grounded lesson plans, school-template concise plans, teaching slides, teacher notes, and assessments from teacher-provided materials. Supports Malaysian Chinese Independent School / UEC syllabus alignment and custom curricula with teacher-specified standards. Use for preparing a lesson or a coordinated set of teaching materials, not school administration or autonomous grading.
metadata:
  short-description: 教师备课工作流，含独中统考适配与自定义课程
  author: "Chew Yen Han（朱彦翰）"
  version: "0.2.0"
---

# 教师备课工作流｜独中统考适配 · 自定义课程

从同一份教学材料，生成彼此一致的教案、校本简略教案、教学简报、教师讲稿和评量。先确认课程体系，再选择课件工具；不以教师任职学校代替课程判断。

独立开发、非官方项目，与董总不存在隶属、授权或代言关系。

## 两个独立选择

| 选择 | 路线 | 使用依据 |
|---|---|---|
| 课程体系 | `uec` 独中／统考适配 | 核对初高中、科目和考纲版本；利用公开官方入口及本机缓存 |
| 课程体系 | `custom` 自定义课程 | 使用教师提供／指定的课程标准或教学目标；没有考纲时依据教材备课，标注“未核对外部考纲” |
| 课件制作 | `editable` 可编辑课件 | 使用当前环境可生成并检查真文字、图形的工具 |
| 课件制作 | `notebooklm` 来源驱动课件 | 教师选择上传范围后使用 NotebookLM；实际检查导出格式与可编辑性 |
| 课件制作 | `outline-only` 大纲＋讲稿 | 教师只需要这两项，或工具暂不可用；不冒充已完成 PPT |

其他学校或补习教师教授统考，可选 `uec`；独中教师教授其他课程，可选 `custom`。自定义课程不自动同步董总考纲，也不等于自定义 PPT。已有明确课程体系或工具选择时不要重问；不明确且影响结果时才一次问齐。

## 按需读取

- 首次设置、缺参数或迁移旧配置：[first-run.md](references/first-run.md)。
- 读取教材正文、表格、图注、公式及练习：[material-intake.md](references/material-intake.md)。
- 核证统考或教师指定考纲：[syllabus-alignment.md](references/syllabus-alignment.md)。
- 详细教案、评量、补教及跨科活动：[lesson-design.md](references/lesson-design.md)。
- 校本 Excel／Word 简略教案：[spreadsheet-adaptation.md](references/spreadsheet-adaptation.md)。
- 选课件工具、每页大纲与讲稿：[slides-routing.md](references/slides-routing.md)。
- **选择 NotebookLM 时**，读 [notebooklm-workflow.md](references/notebooklm-workflow.md)：GitHub 配套工具、安装、登录、四份来源、生成、下载与恢复。
- 多产物、长任务、中断恢复或最终交付：[quality-and-resume.md](references/quality-and-resume.md)。
- 教材权利、上传范围或公开分享：[copyright-and-privacy.md](references/copyright-and-privacy.md)。

## 执行顺序

1. **收齐必要资料。** 从消息、附件及现有配置取得科目、年级／学生程度、课题、课时、材料和交付范围。课程路线与课件路线分别确定；周次日期依据教师给的锚点。只需要教案时不安装课件工具。
2. **完整盘点材料。** 按原顺序记录正文、表格、图像及图注、地图／图表、公式、资料框、例题和练习；没有的类别写“未发现”。核实章节边界，不替教师搜集未提供的版权教材。
3. **核对课程依据。** `uec` 路线先检查官方缓存，缺失时按考纲参考文件查找；`custom` 路线核对教师指定标准。编号、比例和“高频”均须有依据；无法核实时继续基于教材设计，集中列出待核项目。
4. **先完成教学设计。** 每个目标对应学生活动、评量证据、达标标准、即时补教和延伸。时间合计须符合本课；不给所有学科硬套历史活动或固定 Bloom 层级。
5. **派生本次产物。** 从同一组目标与来源生成简略教案、大纲、逐页讲稿、课件和练习。页面采用稳定编号 `P01`、`P02` 等，修订后同步对应讲稿。先做代表页检查再批量制作；只交付用户要求的范围。
6. **检查与修正。** 打开或渲染真实成品，核对文字、事实、公式、版面、页序及模板保护；发现问题修正相应文件并复查关联产物。保存具体结果，不能凭文件存在判定内容正确。

## 可靠交付

- 原始课文、学校模板和已有成品保留；新产物另存。
- 不上传未获教师选择的材料，不保存或输出登录凭证。
- 工具失败保留已完成产物，记录状态并提供继续执行办法；不要反复创建远程任务或重装工具。
- 中文教案与讲稿应像教师实际说话：具体、自然、可用于课堂，减少空泛口号；已有合适润色工具可复用，不强制另一项 Skill。
- 长任务的记录与验收格式见 [quality-and-resume.md](references/quality-and-resume.md)。可运行离线结构检查：
  `python scripts/check_lesson_bundle.py path/to/lesson-folder`。
- 清楚区分“文件结构检查通过”“内容／画面已检查”“服务端仍在生成”。报告实际通过计数、修正项、待核项及可点击成品路径。

## 输出组织

沿用教师选择的目录，每课独立子目录。按本次需要建立文件，避免空白占位：

```text
lesson-output/{subject}-{grade}-{topic}/
├── source-inventory.md
├── source-material.txt        # 实际准备的教材副本；保留原文与来源，不公开
├── detailed-lesson-plan.md
├── concise-lesson-plan.xlsx   # 需要且有模板时；也可为 Word
├── slides-outline.md
├── teacher-notes.md
├── teaching-slides.pptx       # 真正生成并验证后才交付
├── task-state.json            # 多产物／需恢复时
└── qa-report.md               # 实际验收记录
```

教师自己的文件命名可以沿用，在任务记录中映射即可。NotebookLM 的课文来源必须是实际教材／教师认可的完整转录，内容清单不能替代课文。
