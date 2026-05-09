过程报告：基于大语言模型输出文本的选择偏好研究

向您汇报本课题截至当前的研究推进过程、工程文件情况与个人成长 

过程报告主要以如下结构呈现：

1.课题定位与当前报告目的

2.当前仓库结构与工程文件



一、课题定位与报告摘要
1.1 核心研究问题

本课题围绕 LMArena 人类偏好数据展开，主要探讨两个递进的问题：

1.当人类在两个大语言模型输出之间做偏好选择时，是否会系统性地受到长度、标题、列表、粗体等形式特征影响；
2.如果会，这种影响究竟是表层相关、混淆放大，还是在控制其他因素后仍然成立的独立效应。

遵循上述研究问题方向，本课题的工作主要包括：数据清洗、描述性统计、显著性检验、结构方程建模。

1.2 研究流程规划

课题的研究流程大致有如下规划：

1.确认原始数据结构是否可靠。
2.把复杂嵌套数据整理成可分析对象。
3.通过图表和存在性检验识别偏好现象。
4.控制混淆变量并做稳健性验证。
5.尝试用机制模型解释偏好是如何形成的。

1.3 研究背景

除去先前挖掘的学术基础，令人惊喜的是课题的研究背景又在最近得到了更新：今年三月发表的论文《Brevity Constraints Reverse Performance Hierarchies in Language Models》明确指出：

“Constraining large models to produce brief responses improves accuracy by 26 percentage points and reduces performance gaps by up to two-thirds.”

“约束大模型生成简短回答，可使准确率提升 26 个百分点，并将性能差距缩小多达三分之二。”

这篇新发表的文章是对课题观点的力证：长回答确实并不意味着更准确或更高质量，本课题正是从统计学视角出发，前移研究焦点，试图剖析造成该类问题的因素。



二、当前仓库结构与工程文件

截至目前，仓库已经形成了 代码脚本 + 数据中间产物 + 图表表格 + 研究说明文档 的结构。并且以上工程文件均已通过 Git 控制版本，并在 Github 上开源展示。

工程文件的结构如下：

MUC-QMJH/
├─ Codes/         					数据处理、统计分析与建模脚本（C01-C22）
├─ Data/          					原始数据、中间数据、优化后数据、子集数据
├─ Reports/       					文本型分析报告
├─ Tables/        					结构化统计表格
├─ Pictures/      					图形化结果与结构示意图
├─ References/    					研究说明、教学导读、方法报告、规划与合规文档
├─ README.md      				仓库入口说明
└─ requirements.txt / LICENSE 等		仓库规范化文件

现在将分为三个层次介绍文件成果：Codes 层，研究过程中编撰的 Python 脚本；Data 层，研究依赖的 parquet 数据文件；Results 层，产出的正式结果；References层，总结个人在研究过程中的方向参考、思路整理与学习成长。

2.1  Codes 层

Codes 文件夹是整个研究的主干，当前共包含 C01 - C22 共 22 个脚本，可根据代码逻辑分为以下阶段：

脚本范围	阶段功能	关键产物
C01–C11	结构分析、字段探索	R01–R08
C12	数据清洗、过滤、嵌套重组与变量构造	`optimized_data.parquet`（14 列 nested schema）
C13	子集划分	`Data/subsets` 下 20 个子集 parquet，R10
C14–C15	描述性统计与可视化	R11–R12，T01–T08，P04–P10
C16–C17	正式统计检验	R13–R14
C18–C21	净效应、稳健性与匹配诊断	R16–R19，T14–T17
C22	结构方程模型与机制解释	R20，T09–T13，P11

需要额外说明的是：本轮结构修订后，Codes 中新增了 `accessor.py` 作为共享数据访问层。它不修改持久化 parquet 的 schema，但会统一提供常用路径工厂、nested 结构的防御式读取，以及 C14–C18 需要的 token、格式计数、类别布尔列和 criteria 等分析阶段临时列；C19–C22 则统一通过 C18 的 loader 继续复用这批临时分析列，并通过 `stats_utils.py` 复用标准化与列筛选 helper。

2.2  Data 层

Data 文件夹同时记录了原始数据与后续分析数据：

子目录	来源脚本	内容
`lmarena-aiarena-human-preference-140k/`	\	7 个原始 parquet 分片（135,634 行）
`integrated_data/`	C02	合并后的集成数据（135,634 × 14）
`optimized_data/`	C12	优化主表 `optimized_data.parquet`（108,171 × 14，nested schema）
`subsets/`	C13	4 个单类子集与 16 个纯净分区，共 20 个子集 parquet
`length_data/`	C14	解缠化后的长度特征中间缓存
`format_data/`	C15	格式特征解析中间缓存

其中，优化主表已经不再持久化旧版 `a_tokens`、`a_header_count`、`creative_writing_bool` 等 flat 顶层列；这些列只在分析阶段由 `accessor.py` 或 C18 的共享 loader 临时派生。

2.3  Results 层

目前研究产出的正式结果文件主要包括：

Reports：
R01 - R08：数据字段与结构探索报告
R09：数据清洗、重构报告
R10：数据子集划分报告
R11格式偏好初次探索报告
R11–R12：长度与格式偏好描述性探索报告
R13–R20：统计检验、净效应、稳健性、匹配诊断与 SEM 报告

Tables：
T01_01–T01_05：长度特征分箱图表
T02_01–T02_06：格式特征分箱图表

Pictures：
P01 - P03：数据结构与对话结构
P04_01 - P04_05：长度偏好可视化
P05_01 - P05_05：长度偏好可视化

同时，我将个人在研究过程中的思路整理与学习成果总结为笔记，记录于References中：

current_report.md
paper_framework.md
introduction_phase_1.md 至 introduction_phase_5.md
M01_C16_method_report.md
M02_C17_method_report.md
M03_confounding_analysis.md

2.4  References 层

References 主要由较零散的说明文档组成，主要分为四类：

1. 研究导读类：introduction_index 与 phase 1-5 教学导读。
2. 方法说明类：C16、C17、混淆控制等专题方法报告。
3. 研究规划类：project_plan、paper_framework、progress、current_report。
4. 工程治理类：github_public_release_compliance_audit、data_structure_guide 等。

三、研究推进逻辑：从数据审计到机制解释

为了便于从整体上把握课题，我将现有脚本和文档统一归纳为五个阶段，按照研究推进流程进行介绍。

阶段	脚本范围	核心任务	关键输出成果
一	C01–C03	数据审计	integrated_data.parquet
二	C04–C11	字段探查	R01–R08 探索报告
三	C12–C13	清洗、嵌套重构与子集划分	optimized_data.parquet（nested schema）、`Data/subsets` 下 20 个子集数据
四	C14–C17	描述统计与存在性检验	R11–R14、T01–T08、P04–P10
五	C18–C22	净效应、稳健性与机制建模	R16–R20、T09–T17、P11

以下第三部分内容均基于 2026 年 5 月 5 日对 C01–C22 脚本的逐一重新运行测试，并结合最新生成的 Reports、Tables、Pictures 与 Data 目录产物核对后整理。


3.1  第一阶段：认识数据与工程开端

对应脚本：`C01_verify_session_integrity`  `C02_integrate_data`  `C03_verify_order_consistency`

在正式进行统计分析前，必须先确认一个基础问题：数据结构本身是否可信？

首先，我结合原始数据集附的 README 说明文档梳理了对话层级与原始数据结构。梳理结果见 P01_original_structure.png 与 P02_chat_structure.png 。

现在简要介绍梳理结果：

对话主要分为三个层级结构：
`Session`：一次完整的评测会话，包含多次评测
`Order`：一次评测，包含多轮问答
`Turn`：一次评测内部的多轮问答

数据结构较复杂，字段较多且高度嵌套：

字段	类型	说明
id	string	记录唯一标识符
model_a / model_b	string	参与对比的两个模型名称
winner	string	人类偏好结果（model_a / model_b / tie / both_bad）
evaluation_session_id	string	所属会话 ID
evaluation_order	int32	同一 session 内的评价顺序（从 1 开始）
conversation_a	list[struct]	模型 A 侧的对话，格式：[[{role, content:[{type, text, image, mimeType}]}, ...]]
conversation_b	list[struct]	模型 B 侧的对话，结构与 A 相同，但
conv_metadata	struct	元数据，包含 token 计数、格式特征（header/list/bold 各级别计数）等
category_tag	struct	分类标签，嵌套 creative_writing_v0.1、if_v0.1、math_v0.1、criteria_v0.1
language	string	语言标识（如 en、zh；异常时为 <err>）
is_code	bool	是否为代码任务（顶级字段）
timestamp	timestamp[ns]	评价时间戳
full_conversation	list[struct]	包含 user/model_a/model_b 三方完整对话结构

注意到，原始数据被切分为7个 parquet 分片，结合对话结构与数据结构，可以确定以下的初步探索工作：

3.1.1  `C01_verify_session_integrity`

任务：校验原始 parquet 分片中的 `evaluation_session_id` 是否跨文件重复。

方法：逐一读取 `train-00000` 至 `train-00006` 共 7 个分片，对比全局去重数与各文件唯一数之和——若前者更小，则说明同一会话被拆散至不同分片。

输出：控制台结论

发现：7 个分片均成功读取；全局 `evaluation_session_id` 唯一值数量为 115372，而各文件唯一值数量之和为 129698。全局去重数显著小于分片唯一值之和，说明同一 Session 的多条记录确实分布在不同 parquet 分片中。因此不能以分片为单位独立分析，必须先合并。

3.1.2  `C02_integrate_data`

任务：将 7 个分片合并为单一整合文件

方法：使用 pd.concat 合并所有分片并重置索引

输出：保存整合文件至 `Data/integrated_data/integrated_data.parquet`（135,634 行 × 14 列）

发现：本次重新运行后，7 个分片均被成功拼接，整合文件仍稳定生成 135,634 行 × 14 列的数据主表，说明 C02 仍然是后续所有分析脚本的统一入口。

3.1.3  `C03_verify_order_consistency`

任务：验证合并后数据中 `evaluation_order` 的连续性

方法：按 `evaluation_session_id` 分组，统计记录数、最大 Order 值和唯一 Order 数。判断同一 Session 内是否存在 Order 缺失（记录数 < `max_order`）或重复（记录数 > `unique_order_count`）。

输出：控制台结论

发现：合并后的数据共有 115372 个 Session，单个 Session 最大记录数为 25，而全局 `evaluation_order` 最大值为 28；其中可能存在缺失 Order 的 Session 有 8912 个，存在重复 Order 的 Session 有 13 个。也就是说，Session 内部的 Order 并不天然连续，这一结果提醒我后续不能简单把高阶 Order 视为与首轮同质的独立样本。

3.2 第二阶段：把复杂原始数据加工成可分析数据

对应脚本：`C04_touch_session`  `C05_touch_order`  `C06_touch_turn `  `C07_touch_model`  `C08_touch_role`  `C09_touch_cont`  `C10_verify_token_correction`  `C11_touch_category_tag`

在数据完整性得到验证后，需要对每个核心字段逐一探索，理解其取值分布、内部逻辑与潜在异常，为 C12 的清洗决策与后续特征设计提供依据。

3.2.1  `C04_touch_session`

任务：分析整合数据中 evaluation_session_id 字段的分布情况。

方法：统计 session_id 的唯一值及各 session 的出现次数；识别多次出现的 session（具有多个 evaluation_order 的会话）；生成出现次数分布表和多次出现 session 的前10详情

输出：报告保存至Reports/R01_session_report.txt

发现：`evaluation_session_id` 唯一值数量为 115372，其中仅出现 1 次的 Session 有 102166 个，多次出现的 Session 有 13206 个，多次出现 Session 共覆盖 33468 行，占总行数的 24.68%。这说明约四分之一的数据天然位于多 Order 会话中，后续必须认真区分“首轮评价”和“会话延续评价”。

3.2.2  `C05_touch_order`

任务：分析整合数据中 `evaluation_order` 字段的分布情况。

方法：对 `evaluation_order` 做频数统计，并按 Order 值升序输出分布表。

输出：报告保存至 `Reports/R02_order_report.txt`

发现：`evaluation_order` 共出现 28 种取值，其中 Order = 1 的记录有 108315 行，占绝对多数；Order = 2 为 15972 行，之后快速长尾衰减，直到 Order = 28 仅剩 1 行。这个长尾分布说明高阶 Order 既稀少又更容易带入会话历史污染，因此在清洗阶段优先保留首轮评价是有数据基础的。

3.2.3  `C06_touch_turn`

任务：分析 `turns` 字段的分布，并验证其与 `conversation_a`、`conversation_b` 实际结构的一致性。

方法：逐行读取对话结构，比较 `len(conversation_a)` 与 `len(conversation_b)` 是否一致，并检查 `len(conversation_a) / 2` 是否等于 `conv_metadata['turns']`。

输出：报告保存至 `Reports/R03_turn_report.txt`

发现：`turns` 共出现 35 种取值，且 `conversation_a` 与 `conversation_b` 长度不一致的记录数为 0，`len(conv_a)/2` 与 `turns` 不匹配的记录数也为 0；其中单轮对话（turns = 1）达到 116433 行。这说明对话结构在轮次维度上是自洽的，后续可以放心按 Turn 扁平化提取文本。

3.2.4  `C07_touch_model`

任务：分析 `model_a`、`model_b` 与 `winner` 字段，统计模型出场次数与胜率分布。

方法：汇总模型在 A/B 两侧的总出场数，并将非 tie / both_bad 的获胜记录映射回真实获胜模型，计算各模型胜率。

输出：报告保存至 `Reports/R04_model_report.txt`

发现：整合数据共包含 53 个模型；出场次数最多的是 `claude-opus-4-20250514`（10092 次），胜率最高的是 `gemini-2.5-pro`（54.82%，出场 9219 次）。模型平均出场次数为 5118.26，但模型间出场量差异巨大，这意味着模型能力与模型暴露度本身就可能成为长度和格式分析中的重要混淆来源。

3.2.5  `C08_touch_role`

任务：分析 `conversation_a` 与 `conversation_b` 中消息的 `role` 标签分布。

方法：遍历双侧对话中的每个 segment，累计 `role` 频数，并比较两侧标签集合是否一致。

输出：报告保存至 `Reports/R05_role_report.txt`

发现：`conversation_a` 与 `conversation_b` 中均只出现 `user` 与 `assistant` 两种角色，且两侧各自的 `user` 与 `assistant` 计数都为 171054。这说明角色标签体系非常干净，后续可直接按 user / assistant 进行 token 汇总和文本抽取。

3.2.6  `C09_touch_cont`

任务：分析 `content` 字段的内部结构，检查是否存在多模态内容、空内容或异常值。

方法：统计每个消息 `content` 列表的长度分布，并进一步统计 `type`、`text`、`image`、`mimeType` 等子字段。

输出：报告保存至 `Reports/R06_cont_report.txt`

发现：`conversation_a` 中缺失 content 的行数为 93，`conversation_b` 为 82；绝大多数消息的 `len(content)` 都等于 1，`type` 只有 `text` 一种，`image` 与 `mimeType` 基本全部缺失。这说明当前研究对象实际上可以视为纯文本对话数据，而少量空内容记录则需要在清洗阶段剔除。

3.2.7  `C10_verify_token_correction`

任务：校验 `conversation_b` 内逐消息 token 数与 `conv_metadata` 中汇总 token 字段的一致性。

方法：分别汇总 `role='user'` 与 `role='assistant'` 的 `num_tokens`，再与 `sum_user_tokens`、`sum_assistant_b_tokens` 做逐行比对。

输出：报告保存至 `Reports/R07_token_report.txt`

发现：`sum_assistant_b_tokens` 与逐条 assistant 消息 token 总和完全一致，不一致记录为 0；但 `sum_user_tokens` 存在 27319 行不一致，且没有任何一行出现“实际 user token 总和超过汇总值”的情况。这表明污染来自历史累加而非字段错误，也就直接解释了为何 C12 必须过滤 `evaluation_order > 1` 的记录。

3.2.8  `C11_touch_category_tag`

任务：分析 `category_tag` 中各子模块及顶级分类字段的取值分布。

方法：分别解析 `creative_writing_v0.1`、`if_v0.1`、`math_v0.1`、`criteria_v0.1`、`language` 与 `is_code`，统计布尔或类别分布。

输出：报告保存至 `Reports/R08_category_tag_report.txt`

发现：`creative_writing=True` 的记录有 11587 行，`if=True` 有 24666 行，`math=True` 有 10892 行，`is_code=True` 有 39363 行；`language` 共出现 126 种标记，其中 `en` 最多（71175 行）。此外，七个 `criteria` 维度全部表现为布尔型字段，这为后续构造四类任务子集和七个质量控制变量提供了清晰的数据基础。

3.3 第三阶段：清洗、重构与子集划分

对应脚本：`C12_optimize_data`  `C13_divide_subset`

完成字段摸底后，研究才真正进入“把原始对象转化为可分析数据表”的阶段。这个阶段的目标不是再去认识字段，而是把前面识别出的结构事实、异常位置和统计口径，落实为稳定的数据工程规则。

3.3.1  `C12_optimize_data`

任务：对整合数据执行过滤、嵌套重组和变量工程，生成分析就绪的优化主表。

方法：逐行执行资格校验，仅保留 `evaluation_order = 1` 的记录；同时过滤空 content、`language = <err>` 与关键评分缺失的行；随后将原始双侧对话重组为 `conv_a`、`conv_b`、`conv_user` 三个嵌套字典，把 token 与格式统计重组为 `metadata_a`、`metadata_b`、`metadata_user`，再将任务标签和质量维度分别收敛为 `category_tag` 与 `criteria` 两个固定嵌套字段。

输出：生成 `Data/optimized_data/optimized_data.parquet`，并写出 `Reports/R09_optimization_report.txt`

发现：整合数据 135634 行中，最终保留 108171 行，过滤 27463 行，清洗后数据形状为 108171 行 × 14 列，保留率 79.75%。新的顶层字段固定为 `id`、`model_a`、`model_b`、`winner`、`language`、`turns`、`conv_a`、`conv_b`、`conv_user`、`metadata_a`、`metadata_b`、`metadata_user`、`category_tag`、`criteria`。过滤原因中，`evaluation_order > 1` 占 27319 行，是绝对主因；其余为 `conversation_a` 空 content 55 行、`conversation_b` 空 content 54 行、`language=<err>` 30 行、评分缺失 5 行。换句话说，C12 并不是随意缩减样本，而是在保留关键信息层级的前提下，把“复杂原始数据”收敛成了“结构稳定、可由下游统一解包的分析主表”。

3.3.2  `C13_divide_subset`

任务：依据 nested `category_tag` 中四个任务维度布尔值，将优化主表划分为可分层分析的子集体系。

方法：一方面根据 `category_tag` 内的 `cw / if / math / code` 生成允许重叠的四个单类子集，另一方面完整枚举 2^4 = 16 个互不重叠的纯净分区，确保所有记录都能被精确分配。

输出：在 `Data/subsets/` 下生成 20 个子集 parquet 文件，并写出 `Reports/R10_division_report.txt`

发现：单类子集中，`creative_writing_true` 有 9036 行，`if_true` 有 17235 行，`math_true` 有 8876 行，`code_true` 有 29613 行；16 个纯净分区合计 108171 行，与优化主表完全吻合。其中最大分区是 `no_category`（56357 行），在独立类中以 `only_code`（20788 行）最多，而 `all_categories` 仅 4 行。这说明迁移后的 C13 已经完全摆脱了对旧版顶层类别布尔列的依赖，后续分析可以直接建立在 nested `category_tag` 之上。

3.4 第四阶段：描述统计与存在性检验

对应脚本：`C14_visualize_length_preference`  `C15_visualize_format_preference`  `C16_length_test`  `C17_format_test`

前两个阶段解决的是“数据能不能用”和“数据该如何整理”，而这一阶段开始正面回答“偏好现象是否存在”。我先用描述性图表观察趋势，再用正式检验把“看起来明显”转化为“统计上可证”。

需要说明的是，从这一阶段开始，下游脚本已不再要求 `optimized_data.parquet` 持久化旧版 flat 列；长度链和格式链通过 `accessor.py` 从 nested `metadata_*`、`category_tag` 与 `criteria` 中临时解包出分析所需字段。

3.4.1  `C14_visualize_length_preference`

任务：对长度差值进行描述性分析，并在全量及四个任务大类子集中绘制胜率变化图。

方法：先排除 `tie` 与 `both_bad`，再将每条配对评价拆成两个单模型样本，构造 `length_diff`，按 1%–99% 分位数范围做 20 个分箱，并绘制“胜率 + 样本占比”双轴折线图。

输出：生成长度缓存 `Data/length_data/*.parquet`，报告 `Reports/R11_length_preference_report.txt`，统计表 `Tables/T01_01`–`T01_05`，以及图像 `Pictures/P04_01`–`P04_05`

发现：全量样本在解缠化后得到 154780 个模型回答，最优长度差值区间中心为 2792 tokens，对应胜率 74.30%，`diff–胜率` 相关系数达到 0.927；分层来看，创意写作子集最优中心为 2787 tokens、胜率 90.62%、相关系数 0.972，IF 子集为 3146 tokens、胜率 74.06%，MATH 子集为 2493 tokens、胜率 70.51%，CODE 子集为 2384 tokens、胜率 72.09%。这一阶段说明“更长更容易赢”并非个别区间波动，而是跨子集反复出现的趋势。

3.4.2  `C15_visualize_format_preference`

任务：对标题、列表、粗体等格式特征做描述性统计与可视化分析。

方法：在排除平局后同样做解缠化，提取格式存在性、计数、组合与密度特征，并分别绘制存在性条形图、计数折线图和组合条形图。

输出：生成格式缓存 `Data/format_data/format_data.parquet`，报告 `Reports/R12_format_preference_report.txt`，统计表 `Tables/T02_01`–`T02_06`，以及图像 `Pictures/P05_01`–`P05_05`

发现：全量格式样本共 157940 个，其中含任意格式的回答占 84.11%；有任意格式时的胜率为 0.515，无格式仅为 0.421，提升 9.4 个百分点。分项看，标题、列表、粗体分别带来约 8.7、8.0、11.1 个百分点的描述性提升；格式组合中“三种格式均含”胜率最高，为 0.557。值得注意的是，计数特征的“最优值”很可能夹带长度混淆，因此还需要 C17 的正式检验进一步区分“格式效应”和“长度代理效应”。

3.4.3  `C16_length_test`

任务：对全量及 16 个纯净分区执行长度偏好的正式存在性检验。

方法：构造 `δ = tokens(获胜模型) - tokens(落败模型)`，对 17 个配置子集做单侧 Wilcoxon 符号秩检验，并配合 Bonferroni 校正、Bootstrap 置信区间、rank-biserial r 与 Cohen's d 评估效应大小。

输出：生成 `Reports/R13_wilcoxon_length_test_report.txt`、`Tables/T18_length_wilcoxon_summary.csv` 与 `Pictures/P12_length_wilcoxon_overview.png`

发现：17 个子集中有 13 个达到最小样本量要求，其中 12 个在 Bonferroni 校正后仍显著。全量子集的有效配对数为 78970，胜者更长的比例为 62.21%，中位长度差为 +125 tokens，rank-biserial r = 0.3362，为中等效应；效应最强的是 `数学+代码`（r = 0.4101）。唯一未通过校正的是 `创意+指令+代码`，主要原因不是方向消失，而是样本量只有 113 对、功效不足。

3.4.4  `C17_format_test`

任务：对标题、列表、粗体三类格式特征执行正式检验，并额外判断其密度效应是否独立于长度。

方法：先对格式计数差做 Wilcoxon 检验，再对格式密度差做辅助 Wilcoxon 检验，同时加入存在性卡方检验，用以区分“格式更多是否赢”和“格式密度本身是否独立起作用”。

输出：生成 `Reports/R14_format_test_report.txt`、`Tables/T19_format_test_summary.csv` 与 `Pictures/P13_format_effect_heatmaps.png`

发现：在全量子集中，标题、列表、粗体三类格式的计数差均显著，效应量分别约为 `r = 0.3960`、`0.3833`、`0.3696`；但进一步看密度检验，`header_density` 的 p 值为 `6.9e-111`，`bold_density` 的 p 值为 `2.16e-277`，两者都显著，而 `list_density` 的 p 值为 `0.1196`，不再显著。也就是说，标题和粗体更像独立格式信号，而列表更可能是长度增长带来的伴生结构。

3.5 第五阶段：净效应、稳健性与机制建模

对应脚本：`C18_pure_effect`  `C19_length_effect_robust`  `C20_format_effect_robust`  `C21_enhanced_matching_diagnostics`  `C22_sem_analysis`

如果说第四阶段回答的是“偏好现象存不存在”，那么第五阶段回答的就是“这些现象到底有多少是真效应，有多少是模型能力、任务类型和样本不平衡共同抬高的表观相关”。

3.5.1  `C18_pure_effect`

任务：在控制任务属性、问题维度与模型代理变量后，估计长度与格式偏好的净效应。

方法：先用全量数据估计模型层面的胜率、平均长度和平均格式风格，再对各子集构造配对差异特征，分别拟合长度系列 M0→M3 与格式系列 F0→F3 的嵌套逻辑回归模型，观察核心系数在逐层控制后的衰减幅度。本轮重跑后，C18 同时承担了共享 loader 的角色：C19–C22 均通过其 `load_data_global` / `load_subset` / `add_pair_features` 从 nested schema 派生建模列。

输出：生成 `Reports/R16_pure_effect_report.txt`、`Tables/T20_pure_length_net_effect_summary.csv`、`Tables/T21_pure_format_net_effect_summary.csv`、`Pictures/P14_length_confounding_attenuation.png` 与 `Pictures/P15_format_net_effect_heatmaps.png`

发现：模型能力与平均长度的 Spearman 相关系数为 0.7171，与平均格式数的相关系数为 0.5318，说明不控制模型能力就谈长度或格式效应，结论会明显偏大。全量样本中，长度粗效应 OR 从 M0 的 1.9045 衰减到 M3 的 1.3551，混淆比例达到 60.74%，但净效应仍然存在；格式方面，F3 中标题密度净 OR 为 1.0606，粗体密度净 OR 为 1.0855，而列表密度仅 1.0249，且被标记为“主要混淆”。需要说明的是，极小交叉子集在高维控制下出现了 `Singular matrix` 或 `nan`，因此这些子集不应承担主结论。

3.5.2  `C19_length_effect_robust`

任务：用处理效应视角检验“更长”这一长度优势在控制混淆后是否仍稳健。

方法：构造 `longer_a` 处理变量，剔除长度平局行后，同时运行调整逻辑回归与稳定化 IPW，并用 Bootstrap 给出 ATE 置信区间。

输出：生成 `Reports/R17_length_effect_robust_report.txt`、`Tables/T14_length_robust_summary.csv` 与 `Pictures/P16_length_robust_forest.png`

发现：全量样本 n = 78783，更长一侧获胜比例为 0.6236；调整模型 OR 为 1.9103，IPW ATE 为 0.1489，95% CI 为 [0.1351, 0.1614]，且 bootstrap 30/30 全部成功。也就是说，即使换成处理效应框架，长度优势仍然稳定存在，而不只是某一种统计模型的产物。

3.5.3  `C20_format_effect_robust`

任务：在显式控制长度差和其他格式差的条件下，重新估计标题密度、粗体密度与列表密度的稳健处理效应。

方法：分别以 `header_density_diff`、`bold_density_diff`、`list_density_diff` 为处理变量，固定把 `token_diff_ab` 纳入控制项，并用调整 Logit + 稳定化 IPW 双重估计。

输出：生成 `Reports/R18_format_effect_robust_report.txt`、`Tables/T15_format_robust_summary.csv` 与 `Pictures/P17_format_robust_forest.png`

发现：全量样本中，标题密度的调整 OR 为 1.1317，IPW ATE 为 0.0277；粗体密度的调整 OR 为 1.1060，IPW ATE 为 0.0246；列表密度仅作为敏感性分析保留，不写入主结论。进一步看各纯净子集，很多小样本场景下置信区间会跨 0，这反而提醒我：格式效应比长度效应更依赖任务环境，不能用一条简单结论概括所有场景。

3.5.4  `C21_enhanced_matching_diagnostics`

任务：用倾向得分匹配进一步检查长度效应是否依赖原始样本失衡。

方法：复用 C19 的处理定义与混淆变量，按 `caliper = 0.2 × SD(logit_ps)` 做 1:1 最近邻匹配（有放回），比较匹配前后 SMD，并在匹配后的成对样本上再次进行 Wilcoxon 检验。

输出：生成 `Reports/R19_enhanced_diagnostics_report.txt`、`Tables/T16_matching_summary.csv`、`Tables/T17_matching_balance.csv` 与 `Pictures/P18_matching_diagnostics_overview.png`

发现：全量样本成功匹配 39237 对，treated 匹配率 100%；`mean|SMD|` 从 0.2502 降到 0.0597，`max|SMD|` 从 1.4732 降到 0.1765，匹配后 ATE 仍有 0.1601，且配对 Wilcoxon 的 p 值为 0。也就是说，长度优势并不依赖于原始样本分布的不平衡，在更可比的样本中仍然成立。

3.5.5  `C22_sem_analysis`

任务：将模型差异、长度差、格式密度差和最终偏好放入同一机制框架中，尝试解释偏好形成路径。

方法：以 `winner_a` 为结果变量，设置 `token_diff_ab`、`header_density_diff`、`bold_density_diff` 为主模型中介，再在扩展模型中加入 `list_density_diff` 做敏感性分析，并使用 50 次 Bootstrap 估计关键直接效应与间接效应置信区间。脚本内部并不直接依赖持久化 flat 主表，而是通过 C18 的共享 loader 在 nested schema 之上构造 SEM 所需的临时分析列。

输出：生成 `Reports/R20_sem_analysis_report.txt`、`Tables/T09`–`T13`、`Pictures/P11_sem_path_diagram.png` 与 `Pictures/P19_sem_bootstrap_effects_ci.png`

发现：主模型拟合指标非常好，`CFI = 0.9998`、`TLI = 0.9998`、`RMSEA = 0.0030`；在结果方程中，`winner_a ~ token_diff_ab` 的点估计为 0.6073，`winner_a ~ header_density_diff` 为 0.0173，`winner_a ~ bold_density_diff` 为 0.0215。进一步看 Bootstrap 置信区间，标题密度与粗体密度的直接效应都排除了 0，而长度直接效应的 CI 跨 0，这说明“更长”很可能仍夹带更复杂的代理意义，而标题与粗体则表现出更稳定的独立格式路径。运行时由于本地未安装 graphviz，脚本自动回退为内置路径图生成方案，但 `P11_sem_path_diagram.png` 仍成功落盘。

至此，第三部分所对应的五个阶段已经在当前环境中重新跑通，并且从原始分片验证、优化数据生成、描述统计、正式检验、净效应分析、稳健性验证到 SEM 机制解释，都形成了可对应到具体脚本与具体产物的完整研究链条。