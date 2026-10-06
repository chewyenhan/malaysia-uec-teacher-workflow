# NotebookLM 可选配套与完整教学流程

本文件只在教师选用 NotebookLM 时读取。教学工作流负责内容、页序与验收；NotebookLM 配套工具负责操作服务。

## 配套工具的来源

- 项目与 Agent Skill：[teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py)。
- 安装依据：[作者安装文档](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)。
- 操作依据：[作者 Skill](https://github.com/teng-lin/notebooklm-py/blob/main/SKILL.md)。
- 命令参考：[CLI 文档](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md)。

它是非 Google 官方的社区工具，依赖的内部接口可能变动。本项目只链接和调用，不复制第三方 Skill，也不要求安装旧 NotebookLM MCP。检查能力时不要把安装成功、凭据文件存在或 Python import 成功当成能连接服务。

## 执行约束与成品边界

本路线顺序固定：连接验证 → 四份本地来源齐全 → 上传授权 → 上传并确认就绪 → 指定四份 source ID 生成 → 保存任务 ID → 查询同一任务 → 下载真实 PPTX → 逐页与大纲、讲稿核对。不得省掉教案或讲稿。教师指定 MCP 时必须使用实际 MCP；CLI、SDK 和浏览器不称为 MCP，也不能静默替代指定接口。

完整备课任务要求 PPTX。只有 PDF 时保留为中间文件并标记 PPTX 尚未完成，不能当作四项完整交付。按实际输出修订或修正，使教案页码、大纲、讲稿和课件一致；生成服务偏离结构时不得只接受结果而不检查。

## 1. 检查现有能力

先看当前环境是否有可用的 NotebookLM 浏览器操作、CLI 或接口。已有可用工具就复用；不安装重复版本、不动其他 Agent 的配置。使用 CLI 时确认 `notebooklm --version`，再按当前版本的 `--help` 读取命令。

老师选择自动化路线但缺工具时，说明上述仓库、实际安装项目和 Google 登录需求。获得对应安装授权后，按当前平台与作者文档执行；使用既有 Python 环境或 CLI 工具安装方式，不默认下载完整源码、开发依赖或常驻 MCP。

常规 Python 安装入口：

```bash
python -m pip install "notebooklm-py[browser]"
notebooklm skill install --help
```

安装前核对现有环境；指定 Agent Skill 的目标目录以当前安装帮助和目标 Agent 的文档为准，检查路径再写入，避免覆写已有同名 Skill。Python 程序与 Agent Skill 都要可用；只复制 SKILL.md 不能完成程序安装。不要为解决系统包管理限制关闭保护设置，CLI 隔离安装可参考作者文档。

本项目不执行安装时，也应给老师一个可复制请求：

> 请检查我的环境是否已有 notebooklm-py。若没有，请依据 https://github.com/teng-lin/notebooklm-py 的发布版安装说明配置程序和适用于当前 AI Agent 的 Skill。保留已有配置，说明所需安装；登录由我完成。连接验证成功后，按教学工作流上传我已同意的四份资料、生成课件并做验收。

## 2. Google 登录与连接验证

登录由教师在自己的浏览器完成，Agent 不要求把密码或凭证贴到对话。选择账号有歧义时先确认，以免把学校材料放进错误账号。

按已安装版本检查 `notebooklm auth check --help`，使用其支持的实时连接测试（例如 `notebooklm auth check --test --json`）；认证失效时让教师完成 `notebooklm login` 后重测。只展示账号确认结果与成功／失败状态，不输出 cookies、token 或 storage_state 内容。

## 3. 四份来源先备齐

| 角色 | 内容 | 常见文件名 |
|---|---|---|
| 教材 | 教师实际提供的完整相关课文／认可转录，含表格与必要图注 | `source-material.txt`，或实际 PDF／DOCX |
| 教案 | 同一课题的目标、活动、评量和课时 | `detailed-lesson-plan.md` |
| 大纲 | 稳定页面编号、每页内容与视觉要求 | `slides-outline.md` |
| 讲稿 | 与大纲逐页对应的讲解、提问及过渡 | `teacher-notes.md` |

内容清单不是教材原文的替代品。原格式含地图、公式或插图而转录无法保留时，准备教师同意的相应原文件／图片，说明额外来源。不要为了凑四项用同一文件冒充四个角色。

列明拟上传文件，移除无关学生资料，沿用教师明确授权。四份不齐或缺上传授权时先完成本地材料，不开始上传／生成。可按 [quality-and-resume.md](quality-and-resume.md) 写任务记录，再运行：

```bash
python scripts/check_lesson_bundle.py path/to/lesson-folder --json
```

## 4. 建笔记本、上传与等待就绪

- 新课题建一个笔记本，或使用教师指定笔记本。续做先查任务记录中的笔记本 ID，确认实际存在及对应账号，不重复创建。
- CLI 使用显式 notebook ID 和来源 ID；不依赖可能被其他任务改变的“当前笔记本”。
- 按四个角色上传实际文件，记录各角色的来源 ID、文件摘要指纹及处理状态。
- 检查服务端四份来源均就绪后才生成。上传返回 ID 不等于来源解析完成。
- 来源内容更新时对照摘要与现有 ID，仅处理变化项。旧来源的删除另行取得授权，不为清理而自动删除。
- 可保留诊断所需 ID 与状态，不在日志中写教材全文或凭据。

## 5. 生成并记录任务

使用当前版本 `notebooklm generate slide-deck --help` 的参数，将语言、风格、课时、页序和每页内容要求传入；长提示词用该版本支持的文件参数，避免 shell 转义损坏中文。

同时参考四份已就绪来源，以大纲为页面结构蓝本、教材为事实依据、教案为课堂节奏、讲稿为讲解依据。固定页数／风格是请求，仍需检查实际结果。

记录生成任务／artifact ID、状态及选用来源。生成中按正常间隔查询同一任务，达到本次等待上限时保存进度、报告仍在生成，续做查询原任务；不因等待超时重新发起。确定失败后诊断原因；只在已排除问题且教师授权覆盖新的生成／费用时再试。

## 6. 下载、逐页 QA 与修正

先检查 `notebooklm download slide-deck --help` 的实际格式选项。支持 PPTX 时下载并验证；只支持 PDF 时明确交付 PDF 或使用已验证的其他下载方式，不把扩展名改成 PPTX。

打开／渲染，核对实际页面和大纲、讲稿；重点检查中文专名、事实、年代、数字、公式、地图与措辞。记录通过、待核、已修正页。错误页可用当前可用的修订功能或本地课件工具修正，再验收对应文件；保留原生成版本，不覆盖溯源文件。

PPTX 是文件格式，不保证文字可编辑。标明实际为图片式、可编辑或尚未检查。检查工具不可用则把该项列为待核，不宣称全部通过。

## 7. 失败时仍能交付

保留教案、大纲、教材、讲稿和任务记录；把具体问题归入未安装、未登录、来源未就绪、服务额度／接口错误、生成中、下载或 QA。提示下一步，允许教师手动在网站完成，或选择已有可编辑课件工具。未经选择不替换路线，不为了完成课件改变教材事实。

生成后和后续修改时必须执行 [PPT同步关卡](ppt-synchronization.md)，保存逐页映射及四份成品摘要；最终验收不得跳过。

选择风格和制作前必须读取 [完整PPT风格库](slide-style-library.md)；将所选风格落实到每页构图、配色和文字布局，并以样张检查全片一致性。
