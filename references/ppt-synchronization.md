# PPT 与教案、大纲、讲稿同步关卡

两条 PPT 路线都必须执行。同步指内容和实际页码一致，不是把四个文件放在同一目录。

## 生成前

为大纲每页设稳定 id（P01等），教案教学过程引用这些 id，讲稿按相同 id 写作。各页记录对应目标、活动、答案与预计用时。先按计划检查内容闭环，再开始制作。

## 生成后：以实际课件核对

1. 打开／渲染实际PPTX，按真实页序列出每页标题、核心内容、提问或任务。NotebookLM 图片页需实际看图，不能只从XML提取标题。
2. 保存 page-sync.json：pages 中每项记录 id、slide_number、actual_title、outline_ref、notes_ref、lesson_plan_ref 和 status（matched或needs_review）。一个最终页对应一个最终id，页码从1连续排列。
3. 对照原计划：有少页、多页、合并或换序时，先检查是否影响目标、活动和课时。生成错误就修PPT；合理变化则保留原版本，更新大纲和讲稿的实际页序及教案引用，不为迁就错误课件删掉教学目标。
4. 每页讲稿必须能用于讲授该实际页面，提问、答案及过渡也须相符。板书／教具／作业相关变化同时核对。
5. qa-report.md 写逐页检查证据和修正结果；所有页面核对后才置 matched。待核页面不能算通过。

## 绑定已验收版本

page-sync.json 中 files 记录 lesson_plan、outline、teacher_notes、slides 四个角色的实际 path 和 sha256。task-state.json 的 outputs.page_sync 指向该文件。最终完整性检查验证每页映射和四份文件摘要；文件修改后旧同步证明立即失效，须重新核对、更新摘要与QA，不能只更新hash而不检查内容。

```json
{
  "pages": [{"id":"P01","slide_number":1,"actual_title":"本课标题","outline_ref":"P01","notes_ref":"P01","lesson_plan_ref":"教学过程导入行","status":"matched"}],
  "files": {
    "lesson_plan":{"path":"detailed-lesson-plan.md","sha256":"实际摘要"},
    "outline":{"path":"slides-outline.md","sha256":"实际摘要"},
    "teacher_notes":{"path":"teacher-notes.md","sha256":"实际摘要"},
    "slides":{"path":"teaching-slides.pptx","sha256":"实际摘要"}
  }
}
```

结构检查只能证明映射齐全、编号一致和文件未变，不能证明页面含义一致；实际逐页查看不可省略。

## 后续修改

教师要求改PPT或讲稿时先定位受影响id，修改相关文件；NotebookLM 来源变动记录新摘要，远程重新生成须沿用授权并查旧任务状态。保存旧成品，最终再跑同步及完整验收。任何一步未完成都明确待核，不宣称自动实时同步。
