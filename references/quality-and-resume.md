# 任务记录、逐页验收与继续执行

只为需要多个产物、远程生成或中断恢复的任务建立记录；单份短教案可用简短验收说明。

## 任务记录

把 `task-state.json` 放在本课输出目录。它记录状态与可回查位置，不记录教材全文、学生个人资料或登录凭证。文件名可映射教师既有命名。

```json
{
  "schema_version": 1,
  "curriculum_route": "custom",
  "slide_route": "notebooklm",
  "sources": {
    "material": "source-material.txt",
    "lesson_plan": "detailed-lesson-plan.md",
    "outline": "slides-outline.md",
    "teacher_notes": "teacher-notes.md"
  },
  "page_ids": ["P01", "P02"],
  "steps": {
    "materials": "complete",
    "lesson_plan": "complete",
    "outline": "complete",
    "teacher_notes": "complete",
    "slides": "awaiting_auth",
    "qa": "pending"
  },
  "notebooklm": {
    "upload_approved": false,
    "notebook_id": null,
    "source_ids": {},
    "source_hashes": {},
    "artifact_id": null
  },
  "outputs": {},
  "next_action": "教师完成 Google 登录并确认四份来源后继续"
}
```

`page_ids` 必须是本课实际大纲页序，不复制示例页数。四份资料角色由来源映射确定。任务步骤状态使用 `pending`、`complete`、`awaiting_auth`、`awaiting_approval`、`in_progress`、`needs_review`、`failed`；没有执行的步骤不能记 complete。

完成课件后在 `outputs.slides` 写实际相对路径，并记录实际图片式／可编辑情况。文件变化后更新相应状态、来源指纹与 QA，不沿用旧“通过”。

## 离线资料包检查

```bash
python scripts/check_lesson_bundle.py path/to/lesson-folder
python scripts/check_lesson_bundle.py path/to/lesson-folder --json
```

该脚本只读本课记录和文件，不登录、不上传、不安装工具、不写入或删除材料。检查课程／课件路线、来源是否齐全且非空、页面编号对应及已有 PPTX 的实际结构。退出码 0 为结构检查通过、1 为存在结构错误。

它不能判断事实、中文错字、教学适切性或视觉质量；机器结构通过不等于整课验收通过。正式交付仍需要下面的实际检查。

## 实际验收记录

`qa-report.md` 按本次适用项记录，不把不适用项算通过：

| 检查 | 标准 | 证据 |
|---|---|---|
| 材料 | 正文、表格、图注、公式、练习无遗漏 | 内容清单及原材料位置 |
| 课程依据 | 真实版本／编号；无外部考纲明确说明 | 核证表 |
| 教学设计 | 目标、活动、证据、标准及补教对应 | 教案具体位置 |
| 课时 | 时间合计符合教师指定的本课长度 | 分钟数 |
| 模板 | 指定位置正确，其他内容保留 | 打开／渲染后的检查 |
| 页面对应 | 实际课件、大纲、讲稿页序及内容一致 | 页面编号与实际标题 |
| 中文与学科内容 | 专名、事实、公式和因果不越出依据 | 逐页检查与修正记录 |
| 画面与格式 | 投影可读、无截断错位、文件真实可打开 | 实际查看结果 |
| 教师语言 | 具体自然，可直接讲授 | 润色后段落或讲稿 |
| 交付 | 正确文件与状态，不宣称尚未完成的步骤 | 路径与待核清单 |

对问题记录页面／位置、原问题、来源依据、处理和复查结果。不能用“自评高分”替代指出具体检查。已有润色工具可辅助，但不更改事实和术语来追求语气。

## 继续执行

1. 先读记录和现有文件，确认课程路线、工具路线及输入有无变化。
2. 远程步骤只读核对实际笔记本、来源、任务状态与记录是否一致。
3. 对已完成且仍有效的产物复用；缺失／改变的项目标回待处理。
4. 只继续缺失步骤，避免重复上传、重复生成或全套重装。
5. 认证／额度／接口问题阻塞课件时，先交付已完成材料，并说明下一步；不把失败写成完成。

一课目录只保留有用途的成品、工作资料和记录；原始材料与溯源版本不得自动删除。

## 最终交付关卡

完整四项任务交付前必须运行 `python scripts/check_lesson_bundle.py 本课目录 --require-complete --json`。普通模式用于准备阶段，允许尚未生成课件，不能用普通模式的通过宣称完整交付。

最终模式要求教案、大纲、讲稿、实际PPTX、相关步骤 complete 及 outputs.qa_report 指向非空验收记录。它仍只检查结构，不能自动证明教案内容、画面或QA报告真实正确；Agent 必须另做上述实际检查。明确限定范围的任务按其约定验收，不伪造四项来通过此模式。

生成后和后续修改时必须执行 [PPT同步关卡](ppt-synchronization.md)，保存逐页映射及四份成品摘要；最终验收不得跳过。
