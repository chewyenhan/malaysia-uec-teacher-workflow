# 自定义课程示例：同分母分数加法

这是作者编写的公开教学示例，不含教材扫描页、学校模板或学生资料。用于观察新版自定义课程如何工作，不代表任何国家数学考纲已核对。

## 教师任务

> 五年级数学，30 分钟。学生会读分数，尚未理解同分母相加。按这里的原创材料生成教案、四页大纲、讲稿与课末检查。自定义课程，不对照统考；本例只要大纲和讲稿，不生成或上传课件。

## 可查看的成果

- [原创材料](source-material.txt)：同一个整体、分母含义、例题与练习。
- [内容清单](source-inventory.md)：包含一张比较表，记录图像与公式的处理。
- [详细教案](detailed-lesson-plan.md)：目标—活动—评量—补教对应，合计 30 分钟。
- [四页大纲](slides-outline.md)。
- [逐页讲稿](teacher-notes.md)。
- [任务记录](task-state.json)：明确为 `custom`＋`outline-only`。
- [示例验收](qa-report.md)：区分文本结构检查与尚未生成的 PPT。

在仓库根目录检查：

```bash
python scripts/check_lesson_bundle.py examples/custom-fractions
```

本例没有 PPTX，也没有学校模板：它们不在教师任务范围内，不用空白文件冒充成品。想试 NotebookLM 可让 Agent 复用这四份材料，先取得上传选择，再执行 [NotebookLM 工作流](../../references/notebooklm-workflow.md)。

资料由本项目作者原创，依工作流内容的 CC BY-NC-SA 4.0 许可提供。
