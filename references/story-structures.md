# 先定新闻的问题，再定镜头的顺序

先写一句观众看完能回答的问题。用下表选一个主结构；旧素材的池子不变，换选题时才换开头、信息顺序和收尾。报道初起、事实不足时用快讯；资料已经补齐再做溯源、解释或数据稿。新闻片保持移动剪辑，和固定A4论文页分开。

| 结构 ID | 适用问题与证据门槛 | 脚本骨架（按播放顺序） | 剪辑与视觉 |
|---|---|---|---|
| `brief` 快讯／倒金字塔 | 最新变化是什么？先核实硬事实 | `news → support → context`，有已公布的下一步可加 `next` | 现场或原始声明开门见山；数字卡提供一个必要数据，背景可删，导语不可删 |
| `event_intro` 事件介绍 | 观众第一次看到这件事；需要知道为何值得关注 | `news → why_now → significance → reaction → watch` | 日期＋可证实现场；项目原理或测试目标图；结果意味着什么；带职衔的原话/转述卡；下一步观察卡 |
| `chronology` 顺叙 | 关键节点如何一步步发生？原始记录覆盖起点、中点和结果 | `origin → development → outcome` | 日期从早向晚，时间轴或地图；每个中间节点交代独立的新信息，不用同一天的补景凑顺序 |
| `reverse_chronology` 真正倒叙 | 最新结果之前最近的关键节点是什么？能核实至少三个不同时间的节点 | `outcome → prior → origin` | 日期从晚向早逐段后退；每次切换显示日期；同一时刻的机位切换不算一次倒推；全片末尾停在起点 |
| `hourglass` 沙漏／结果先行后回放 | 结果紧急，同时值得讲清来路 | `news → turn → origin → development → return` | 到手的结果先说；用字幕或口播明确拨回哪个日期；回放从早到晚，最后回到今天/结果。开头与收尾用不同信息，不重复一遍导语 |
| `explainer` 机制解读 | “为什么／怎么做到？”有可验证的机制或规则 | `question → mechanism → mechanism → takeaway` | 问题作钩子，用两处原理图/剖面/流程分别解释；配画用标签注明是示意。证据只支持相关时，用“同时发生”或明确归属，箭头不得暗示已证实的因果 |
| `case_feature` 个案带出全局 | 谁受影响？有一个可核验个案及独立背景/总体资料 | `case → nut_graf → context → return` | 从现场可确认的一幕切入，尽快交代它关联的更大议题，再回到个案；一个故事不作总体证据 |
| `data_check` 用数据核对一个说法 | 单一说法和可核对基线；单位、样本、时间窗确认后才选 | `claim → baseline → comparison → finding` | 引用卡区分“说法”和“已核实事实”；比较用同口径条形/点图；变化用折线；有口径限制就放在图与口播最近的位置 |

## 从脚本到剪辑

- 先做事发时间表，再做播放顺序。每个事实记录发生日期（按可核实精度）、来源、必要时引语上下文；新闻日期、素材拍摄日期、文件发布时间和成片时间不能混用。引用当时消息要标注“截至某日”；历史示例不可借用日后才出现的结论。
- `why_now`解释新闻性或事件的重要条件（例：第一次把飞船、火箭、地面系统放进同一次实飞）；`significance`写具体结果或下一阶段的用途（例：回收后分析隔热盾，为载人任务做准备）；`reaction` 是谁、什么身份、何时、原话还是转述。找不到关键人物的可靠公开评价，改用快讯或机制稿，不配假声和引号。`watch` 写可观察的下一步（数据、试验、申报、下次公告），提计划要标出时间口径和归属，别套用过期排期。
- 在一个短镜头里安排一个新事实。画面提供证据，字幕提供定位，旁白负责衔接，音乐给段落分隔。快讯用干净切点、低强度底乐；回溯在时间跳转处标日期、换一层音色即可，不做“倒放实况”；机制稿在原理图处降音乐、留足读图时间；个案优先留环境声，不能用音效补造现场。工具默认静音素材；实际需要同期声时单独编排，复核全文和出入点。
- 按事实搜索素材：`事件/机构 + 日期 + 地点 + 镜头用途`。直接现场、档案背景、示意图及人物/机构表态在表中分列；维持双证据链：画面归属不能替代主张出处。应保留原始转载或官方源、源文件In/Out和画面时间标签。速率、变焦、调色、声画拼接都不能改写画面含义；缺少直证镜头就用明确标示的图形或文件卡。
- 先跑 `python scripts/story_preflight.py <manifest>`，再跑 `broadcast.py`。这是结构、归属和日期前置校验，不能代替来源核实、最终试听或视觉核验。为了避免硬套，结构只约束语义组顺序；一个功能可跨多个镜头（相邻保持同一 `role`），一个镜头不承担多个主角色。非语义的片尾署名可放在最后，不新增一个无证据的结论。
- 对24秒预览，5个叙事功能可以分约4/5/5/5/5秒，实际按句子可读性调整；假如要完整口播，按真实朗读时间及停顿排，读不清就删字或延长，别硬塞。按叙事决定配乐的起伏，别由鼓点替你改事实顺序。

## 数据：日期、角色、引语

新稿在现有渲染清单加 `editorial` 对象：`structure`、`question`、`as_of`（YYYY-MM-DD）、`facts`（ID → `text`、`source`、`locator`、`kind`、`available_on`，日期按已核实来源或当时已公开的可用日期；`kind` 为 `fact`、`statement`、`plan`、`inference` 之一；statement 和 plan 加 `attribution`）。每个 `beat` 加 `role`、`fact_ids`、`visual_role`（`direct`、`archive`、`illustration`、`document`）；有素材加 `visual_date`（可为 YYYY、YYYY-MM 或 YYYY-MM-DD，阶段精度可用明确范围），现场/档案日期或范围必须出现在 `detail` 或素材 `credit`。日期排序结构的关键 beat 必须加 `event_date`（YYYY-MM-DD），不同节点需要不同日期；一天内同日事件只在有明确时间戳时采用单独的时刻粒度方案，不硬塞日级模板。跳时的 `turn` 和真正倒叙的每一节点应在字幕、标题、细节或来源标识出现其日期（倒叙示例使用 ISO 日期）。`reaction` 加 `quote_mode`（`paraphrase` 或 `direct`），主体明确写出；`direct` 额外在事实表保存 `original_quote`，有原声音轨可核对才作为同期声。

工作示例（同一素材池）见 [NASA事件介绍](../examples/artemis-event-intro.json) 和 [NASA真正倒叙](../examples/artemis-reverse.json)；旧 [样片](../examples/artemis-broadcast.json) 的开头先溅落、倒回发射、回到海面，接近沙漏，不是从头到尾持续倒推。示例按2022-12-11发布当晚编辑视角，`watch` 是当时的检查与分析计划。展现今天的进展应该单独更新来源和日期。素材的角色标记与故事叙述分开，发射远景不是人物讲话的证据。需要给无旁白样片使用原始语音之外的来源卡时，首选用字幕转述并清楚标名。

### 同一题材可以怎么讲：Artemis I

- **事件介绍（2022年当晚视角）**：0–4秒，2022-12-11美东12:40，猎户座溅落太平洋 → 4–9秒，这是SLS、猎户座、地面系统首次一同参加实飞测试 → 9–14秒，月球返程再入提供隔热盾在实飞中的表现数据，为载人任务做准备 → 14–19秒，时任NASA局长比尔·纳尔逊称溅落是本次任务最突出的成就（发布稿转述） → 19–24秒，当晚的下一步：送回检查并分析机载记录。[NASA当日任务日志](https://www.nasa.gov/blogs/artemis/2022/12/11/artemis-i-flight-day-26-orion-splashes-down-concluding-historic-artemis-i-mission/)｜[当日发布稿](https://www.nasa.gov/centers-and-facilities/hq/splashdown-nasas-orion-returns-to-earth-after-historic-moon-mission/)｜[任务目标](https://www.nasa.gov/artemis-i-press-kit/)
- **真正倒叙（同一素材池）**：0–7秒，2022-12-11溅落 → 7–16秒，2022-12-05返程飞越时点火 → 16–24秒，2022-11-16发射，停在旅程起点。中段用任务日志卡，不拿其他日期的实况填空。[NASA 12月5日任务日志](https://www.nasa.gov/blogs/missions/2022/12/05/artemis-i-flight-day-20-orion-conducts-return-powered-flyby/)
- **2026年机制/数据回顾（独立线路，未渲染）**：从“NASA检查发现，隔热盾炭化层脱落点从Artemis I的103处降至Artemis II的9处”开场（处数，非面积），回溯2024年NASA报告的气体排出受阻、压力积聚，再讲II修改再入轨迹；后续关注II材料取样分析、III改进后的Avcoat材料均匀性与透气性。[NASA 2024年原因调查](https://www.nasa.gov/missions/artemis/nasa-identifies-cause-of-artemis-i-orion-heat-shield-char-loss/)｜[NASA 2026年后续分析](https://www.nasa.gov/missions/artemis/artemis-2/rigorous-analysis-confirms-nasas-artemis-ii-heat-shield-performance/)

## 参考依据和取舍

- [Horst Pöttker，News and its Communicative Quality: the Inverted Pyramid (2003)](https://doi.org/10.1080/1461670032000136596)：把重要信息提前，当成读者辨认核心事件的工具。具体24秒分配是本Skill的制作建议，不是论文结论。
- [Chip Scanlan，Poynter：The hourglass](https://www.poynter.org/reporting-editing/2003/the-hourglass-serving-the-news-serving-the-reader/) 与 [Poynter：Organize](https://www.poynter.org/wp-content/uploads/2019/01/PoynterNewsU_EffectiveWriter_Organize_Week1.pdf)：借鉴新闻摘要、过渡、按正序重讲三部分；个案式把较大议题提前点出来。
- [David Bordwell，Narration in the Fiction Film](https://www.routledge.com/Narration-in-the-Fiction-Film/Bordwell/p/book/9781315002163)：借鉴区分“发生顺序”和“展示顺序”；新闻不用电影虚构去填证据缺口。
- [Kovach、Rosenstiel，The Elements of Journalism（第4版）](https://penguinrandomhousehighereducation.com/book/?isbn=9780593239353) 和 [BBC《Accuracy》编辑规范](https://downloads.bbc.co.uk/guidelines/editorialguidelines/pdfs/Section_03_Accuracy.pdf)：取核验、交代来源、准确呈现剪接和档案性质的原则。机构自评以身份归属出现。
- [Segel & Heer，Narrative Visualization (2010)](https://vis.stanford.edu/files/2010-Narrative-InfoVis.pdf)：借鉴作者设定的阅读路径与视觉引导；15–60秒视频改用可读的定点标注与逐步揭示，不把交互分类当成剪辑定律。
- GitHub：[Knight Lab TimelineJS3](https://github.com/NUKnightLab/TimelineJS3) 参考时间与素材对象分离，[Knight Lab Storyline](https://github.com/NUKnightLab/storyline) 参考把说明绑定到真实数据点，[OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) 参考源片裁剪区间与成片时码分离。对照 [Serena 的同类Skill](https://github.com/SerenaMugua/news-documentary-video-skill) 的分层制作思路，保留成片QA。以上未搬用第三方代码或模板，也不是本工具的运行依赖。
