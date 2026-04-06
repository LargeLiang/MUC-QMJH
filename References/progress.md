# 阶段报告：基于大语言模型输出文本的选择偏好研究
**项目**：中央民族大学本科生创新训练计划（青苗计划）
**主题**：LMArena人类偏好数据深度探索与描述性统计分析

---

## 一、原数据初步探索
### 1. 数据整体认知
- 数据集：`lmarena-aiarena-human-preference-140k`
- 格式：`parquet`，共7个`train-`分片文件
- 规模：**135634条**数据，下载大小约**1.5GB**
- 结构：多特征、高度嵌套、双模型对比（model_a / model_b）

### 2. 数据特征结构（三层维度）
#### （1）主体层
- 核心标识：`model_a`、`model_b`、`winner`
- 会话上下文：`id`、`evaluation_session_id`、`evaluation_order`、`timestamp`

#### （2）内容层
- 对话内容：`conversation_a`、`conversation_b`、`full_conversation`
- 辅助属性：`language`、`is_code`

#### （3）特征层
- 格式统计（`conv_metadata`）：Token数、标题/列表/粗体计数
- 分类标签（`category_tag`）：任务类型、人工标注质量维度

### 3. 会话层级逻辑
`Chat/Session` → `Order`（一次用户评价） → `Turn`（一轮问答）
- 1个Session可包含多个Order
- 1个Order可包含多个Turn
- 1行数据 = 1次Order

---

## 二、代码探查与数据校验
### 1. 会话完整性验证
- 跨parquet分片存在相同`evaluation_session_id`
- 结论：**必须合并全部数据**，恢复会话完整性

### 2. 会话连续性验证
- 同一Session内Order存在缺失
- 但`full_conversation`保留完整对话历史

### 3. 核心字段统计
- Session：共115372个唯一会话，多数仅含1个Order
- Order：`evaluation_order`共28种，以1为主（108315条）
- Turn：共35种取值，集中在1–3轮
- Model：共53个模型，分布极不均衡，胜率差异显著

### 4. 内容层探查
- `conversation_a/b`仅含`user/assistant`两类角色
- `content`存在少量缺失，`type/image/mimeType`无有效信息
- 结论：可剔除冗余字段，仅保留`role`与`text`

### 5. 特征层关键发现
- `sum_assistant_a/b_tokens`与当前Order一致
- `sum_user_tokens`是**整个Session**统计，非当前Order
- 反例数：27319条，恰好等于`evaluation_order>1`的样本量
- 结论：**剔除evaluation_order>1的数据**，避免上下文污染

---

## 三、数据结构优化
### 优化逻辑
1. 提取关键字段，剔除冗余（`timestamp`/`type`/`image`/`mimeType`）
2. 清理缺失值与异常数据
3. 扁平化嵌套结构，生成标准化数据集

### 优化后核心字段
- 标识：`id`/`model_a`/`model_b`/`winner`
- 长度：`a_tokens`/`b_tokens`
- 格式：`header_count`/`list_count`/`bold_count`
- 对话：`user_conv`/`a_conv`/`b_conv`
- 标签：`is_code`/`math`/`creative_writing`及质量标注

---

## 四、描述性统计与可视化
### 1. 长度特征编码
- 基础指标：Token数
- 比率指标：`length_ratio = model_tokens / user_tokens`
- 差值指标：`length_diff = a_tokens - b_tokens`

### 2. 长度偏好可视化
- 双轴折线图：长度比率/差值 → 胜率 + 样本占比
- 二次曲线拟合，定位**最优长度区间**
- 输出：分析表`csv`+统计报告`txt`

### 3. 格式特征编码与可视化
- 格式类型：标题（h1–h6）、有序/无序列表、粗体
- 可视化：
  - 单格式数量→胜率折线图
  - 格式存在性柱状图
  - 格式组合胜率对比图
- 关键指标：**优势比OR**、胜率、样本量

### 4. 格式偏好结论
- 格式对偏好存在明显影响
- 组合格式（标题+列表+粗体）胜率更高
- 单一格式样本量少时波动大

---

## 五、现阶段成果总结
### 已完成工作
1. 数据深度探索与结构解析
2. 数据整合、清洗、去重、去异常
3. 长度/格式特征量化编码
4. 多维度可视化与描述统计
5. 形成可检验的研究假设

### 产出物清单
- 数据集：4套重构后数据集
- 代码：14份Python脚本
- 图表：10张可视化图
- 表格：8张分析表
- 报告：6份统计报告

### 主要困难与解决
1. **数据嵌套复杂**
   - 方案：分步`touch_`脚本探查，最终统一优化脚本
2. **统计方法不足**
   - 方案：后续强化检验方法与结果解读

---

## 六、下一阶段计划
1. **偏好存在性检验**
   - 长度：t检验/ANOVA/Kruskal-Wallis
   - 格式：卡方检验/Fisher精确检验
   - 效应量：Cramér’s V、OR、Cohen’s d、η²
2. **伪相关与混淆变量控制**
   - 模型能力等级差
   - 任务类型哑变量
   - 分层逻辑回归，计算净效应
3. **分任务子集分析**
   - 数学、写作、代码等场景分层验证

---

要不要我把这份阶段报告也整理成**可直接提交的正式版md**，统一格式、标题层级与排版？