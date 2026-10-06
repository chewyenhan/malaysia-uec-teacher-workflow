# 教学 PPT 风格库与执行模板

改编自 junior-history-lesson 的六种风格、年级密度、提示词结构与样张锚定。保留视觉设计，更新过时的中文生图做法：AI Agent 路线采用无文字视觉素材＋真实字体文本框；NotebookLM 在生成后实际检查中文。风格不是自动生成图片的授权，费用及上传范围沿用本次授权。

## 开始时同轮选择

| 风格 | 历史科推荐（不是强制） | 视觉特征 |
|---|---|---|
| Q版 chibi | J1／低年龄 | 圆润大眼、明亮配色、轻松、干净留白 |
| 故事绘本 storybook | J2／叙事教学 | 柔和大地色、细腻质感、人物置于场景 |
| 写实 realistic | J3／史料与复习 | 可信服饰建筑、低饱和、庄重光影 |
| 手绘解说 hand-drawn | 示范、推导、边讲边画 | 白底、线稿、箭头、逐步关系 |
| 水墨国风 ink-wash | 古代史、诗词、文化 | 宣纸、笔触、留白、少量点色 |
| 科技霓虹 neon | 科技、近现代或复习 | 深底、青紫点缀、数字图形、高对比 |

也允许教师指定其他风格。年级推荐不代替教师确认；跨科按内容和学生程度推荐。必要时在同一轮确认路线、风格及样张要求。

## Q版

- 关键词：`cute chibi cartoon illustration, round-headed characters, big sparkling eyes, rounded shapes, thick clean outlines, vibrant cheerful flat colors, simple background, school-friendly`。
- 色调：淡黄、天蓝、粉红、草绿，避免混用过多强调色。
- 构图：主体居中或偏左，右侧／下方留正文区；概念可用卡通意象，但拟人化不能造成知识误解。
- 文字：圆角字块／云朵卡片，清晰无衬线字体；J1建议标题≤8字、≤3条要点、每条≤12字，专名与必要解释不为凑字数截断。
- 禁忌：写实人物、血腥黑暗、密集文字、复杂背景。

## 故事绘本

- 关键词：`warm storybook illustration, soft flat colors, subtle texture, gentle painterly feel, cinematic composition, expressive light, narrative scene, matte gouache texture`。
- 色调：柔和大地色，暖褐／橄榄绿／青绿点缀。
- 构图：人物在真实教学情境中，场景有叙事关系；正文放干净的浅色半透明卡片。
- 文字：深色字；J2建议标题≤10字、≤4条要点、每条≤16字。
- 禁忌：过度Q版、血腥写实、整页堆字。

## 写实

- 关键词：`semi-realistic historical illustration, cinematic lighting, atmospheric scene, high detail textures, muted serious color grading, historically accurate costumes and architecture, dignified mood`。
- 色调：做旧棕、墨绿、藏蓝，低饱和且正文区足够明亮。
- 构图：大场景／局部特写＋稳重排版，画面必须与史实或学科对象一致；示意图不可冒充真实史料。
- 文字：清晰衬线或无衬线文字、简洁卡片；J3建议标题≤12字、≤5条要点、每条≤20字。
- 禁忌：Q版角色、糖果色、emoji式装饰、牺牲阅读性的暗底。

## 手绘解说

- 关键词：`hand-drawn whiteboard sketch style, pencil outlines, marker-style arrows, educational doodle, clean white background`。
- 色调：白／米白底，深色线条，2—3种强调色。
- 构图：主体结构配箭头、编号与留白；数学科学的关系、坐标、实验顺序须准确。
- 文字：真实文本框模拟手写感但保持清晰；标签、箭头文字不得由图片模型生成。
- 禁忌：装饰线与有效数据混淆、无逻辑箭头、过密涂鸦。

## 水墨国风

- 关键词：`traditional Chinese ink wash painting, brush strokes, rice paper texture, minimalist, elegant, muted monochrome ink, subtle color accents`。
- 色调：墨黑、宣纸白、淡灰，少量朱红或青绿。
- 构图：远近层次与大面积留白，文字区干净；地图与史料要清楚，不能仅作朦胧装饰。
- 文字：清晰中文衬线字体；书法仅用于可读标题，正文不用难辨草书。
- 禁忌：浓墨盖住文字、背景花纹过密、用意境代替事实。

## 科技霓虹

- 关键词：`glowing cyan and magenta accents, dark background, futuristic holographic elements, digital screen aesthetic, high contrast`。
- 色调：深蓝／黑底，青与紫红作少量强调。
- 构图：数字卡片、流程／时间关系，画面层次简单；古代历史中科技元素是展示语言，不能混入不符时代的事实物件。
- 文字：清晰浅色真文字，发光只作点缀，正文不加模糊光晕。
- 禁忌：过量光效、低对比细字、赛博装饰盖住教学对象。

## 每页风格规格（两条路线必用）

大纲的每页视觉栏必须写：选定风格＋内容主体＋配色／氛围＋构图与文字留白＋实际视觉用途。不能仅重复“Q版／写实”或“美观”。整体记录字体、颜色、角色造型、卡片形状及素材来源，在 slide-specs.json（Agent）或生成指令（NotebookLM）中落实。

### AI Agent 无文字素材提示词

按内容主体 → 风格关键词 → 色调 → 构图留白 → 16:9课堂用途 → 无文字要求组织：

```text
{本页准确场景或概念}；{选定风格关键词}；{颜色与氛围}；
{主体位置，给真实文字层保留干净区域}；16:9 classroom projection；
NO text, letters, characters, numbers, labels or writing.
```

标题、要点、地图标签、公式与数字在PPT中使用真实文字／图形层。背景不应留下假文字；中文字体必须在实际环境可用，检查字体替换。

### NotebookLM 生成指令模板

```text
按已选{风格}制作课堂幻灯片。以大纲为结构，教材为事实依据，
教案为节奏，逐页讲稿为讲授依据。页面按P01等顺序，逐页视觉设计见大纲。
全片使用{配色}、{人物造型／插画质感}、{文字卡片形状及字体要求}。
每页一个主题，中文准确、正文投影可读。保持目标、活动和检查任务。
不要添加缺乏来源的年代、地图标注、公式或事实。
```

参数语言代码按实际工具帮助选择，不凭模板猜接口参数。生成结果必须逐页检查，不能宣称提示词保证风格或中文字正确。

## 样张锚定与逐页QA

样张确定后，在后续每页视觉规格／素材提示词明确延续相同造型、配色、质感与卡片样式；只改变本页场景。可用表达：`Same visual style as the approved sample; new scene: ...`，但必须附具体已确认风格，不只写“同上”。

逐页检查：风格与样张一致、正文可读、内容与教材一致、中文无错字、图形／地图／公式准确、实际16:9（教师另指定比例除外）。失败页修复后再查看。文字问题优先修真实文字层，不能反复要求生图模型画正确中文字；NotebookLM图片文字不能直接改时，采用已验证修订能力或经教师选择的本地修正方案，不静默换路线。
