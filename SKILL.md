---
name: malaysia-uec-teacher-workflow
description: Create source-grounded lesson plans, concise school-template spreadsheets, teaching slides, and assessments for Malaysian Chinese Independent Schools (马来西亚华文独中), across junior/senior levels and subjects. Use when a teacher provides lesson materials or asks to align teaching with Dong Zong/UEC syllabi. Do not obtain or reproduce textbook content that the user has not supplied legally.
metadata:
  short-description: 马来西亚独中跨科教案、简略教案、简报与评量工作流
  author: "Chew Yen Han（朱彦翰）"
  version: "0.1.0"
---

# Malaysia UEC Teacher Workflow

把教师合法提供的课文、讲义和校本模板，转化为可直接使用的教案、简略教案、教学简报及评量。适用于马来西亚华文独中初中与高中各科，不预设历史科、固定课时或特定学校格式。

本项目为独立开发的非官方工具，与董总不存在隶属、授权或代言关系。

## 不可越过的边界

- 教材必须由教师提供。不得替用户搜寻、下载或重建受版权保护的课本、教师手册、扫描页或题库。
- 完整读取用户给的材料，包括正文、表格、图片与图注、地图、图表、公式、时间线、资料框、例题、练习及跨页内容。不能只抽取段落。
- 不得编造考纲编号、学习标准、教材事实或来源。找不到准确依据时明确标成“待教师核对”。
- 不覆盖原始课文、模板或既有教案。所有成品另存新文件。
- 不把教师材料上传到第三方服务，除非用户选择该路线并知道哪些文件会上传。

## 按需读取参考文件

- 首次使用或资料不足：读 [references/first-run.md](references/first-run.md)。
- 解析课文、讲义、PDF、DOCX 或图片：读 [references/material-intake.md](references/material-intake.md)。
- 对照董总/统考考纲：读 [references/syllabus-alignment.md](references/syllabus-alignment.md)。
- 编写详细教案、评量或跨科活动：读 [references/lesson-design.md](references/lesson-design.md)。
- 制作简略教案或适配 Excel/Word 校本模板：读 [references/spreadsheet-adaptation.md](references/spreadsheet-adaptation.md)。
- 制作教学简报或选择 NotebookLM：读 [references/slides-routing.md](references/slides-routing.md)。
- 处理版权、隐私、署名或发布问题：读 [references/copyright-and-privacy.md](references/copyright-and-privacy.md)。

## 工作流程

### 1. 收齐本次真正需要的资料

先读取现有教师配置；没有配置才按 `references/first-run.md` 一次问齐必要资料。优先从用户当前消息和所附文件推断，已知内容不要重复询问。

最少需要：科目、年级、课题、课时长度、教师提供的课文/讲义，以及本次要哪些产物。只有在用户要写入校本简略教案时才要求其 Excel/Word 模板。

### 2. 建立教材内容清单

按原顺序读取材料，先产出内部内容清单，再写教案。清单必须记录每种教学元素的数量、位置、标题或摘要；不存在的类别写“未发现”。

对表格逐格读取，并保留行列关系。对图片、地图、图表和公式，不只记录“有图片”，还要说明可见信息、图注及它与正文的关系。章节边界用相邻标题、页码或文档结构核实。

### 3. 对照考纲，但以证据为准

若用户要求考纲对齐，使用官方公开来源或本机已同步缓存。首次使用时应询问是否同步完整初、高中官方考纲；获得同意后运行：

```bash
python scripts/sync_uec_syllabi.py --level all
```

只写能够从考纲原文核实的科目、级别、范围与编号，并记录文件名、版本/年份及页码。官方页面暂时不可访问时，不得用记忆补编号；继续完成基于课文的教案，并列出待核项目。

### 4. 先做目标—活动—评量对齐

每个具体目标都要使用可观察动词，并对应：

1. 学生实际完成的活动；
2. 教师如何收集学习证据；
3. 什么表现算达标；
4. 未达标时立即怎样补教；
5. 已掌握时怎样延伸。

活动应由科目内容、学生程度、课时和材料决定。不要为了形式强塞讨论、角色扮演、Bloom 全层级或三领域目标。

### 5. 生成用户要求的产物

可独立或组合输出：

- 详细教案：按 `references/lesson-design.md` 的最小完整结构。
- 简略教案：先读用户模板，再按 `references/spreadsheet-adaptation.md` 映射。
- 教学简报：按 `references/slides-routing.md` 选择当前环境最合适的路线。
- 教师讲稿、课堂练习、评分规准或补教材料：从同一组目标和证据派生，避免互相矛盾。

工具选择以质量、可编辑性、隐私、费用和用户偏好为准。先检查当前 AI 的原生文档、简报、图像和表格能力；只有 NotebookLM 或其他专门工具能带来明确价值且用户选择时才使用。不要因本 skill 提到某个工具就强制安装或调用它。

### 6. 验收后才交付

至少检查：

- 课时分钟数合计与教师提供的时长一致；
- 每个目标均能追踪到活动、评量、标准及补教；
- 教材表格、图片、公式、资料框和练习没有漏读；
- 所有事实、数字、术语、公式及考纲编号有来源；
- 详细教案、简略教案、简报和讲稿彼此一致；
- 电子表格保留模板结构、公式、合并单元格与其他班级内容；
- 简报页数、顺序、文字和画面经实际检查；
- 原始文件没有被覆盖，成品路径清楚。

报告具体验收数，例如“通过 8/8 项”；不能只说“检查完成”。

## 输出目录建议

沿用教师配置的输出目录；没有配置时，在当前工作目录建立：

```text
lesson-output/
└── {subject}-{grade}-{topic}/
    ├── source-inventory.md
    ├── detailed-lesson-plan.md
    ├── concise-lesson-plan.xlsx   # 用户需要且提供模板时
    ├── slides-outline.md
    ├── teacher-notes.md
    └── teaching-slides.pptx
```

只建立本次需要的文件，不制造空白占位文件。
