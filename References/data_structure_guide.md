# 项目数据结构总览与运用说明

本文件面向整个 Codes 目录，对项目中实际参与读取、清洗、统计、建模与输出的数据结构进行系统梳理。目标不是只解释 Python 语法，而是回答三个更贴近统计研究的问题：

1. 这份代码到底把数据装在什么结构里。
2. 每一种结构为什么适合当前任务。
3. 在本项目里，这些结构如何彼此转换，最终支撑统计分析与论文结果。

## 一、阅读范围与说明

- 审阅范围：Codes 目录中的 C01-C22 脚本。
- 关注重点：运行时真正参与数据处理的结构，而不是仅用于类型标注的抽象名词。
- 说明方式：每种结构都给出“介绍”“运用说明”“项目实例”。
- 文档中的文件引用以典型脚本为主，不追求把每一处重复写法全部列尽，而是覆盖所有主要结构类型。

补充说明：像 Dict、Tuple、Iterable 这样的 typing 标注，在文档里会按其运行时对应结构来解释，例如 Dict 对应 dict，Tuple 对应 tuple，Iterable 在本项目里通常最终落成 list 或循环可迭代对象。

补充说明（2026-05 结构修订）：`optimized_data.parquet` 已从旧版 32 列 flat 主表改为 14 列 nested 主表；`Codes/accessor.py` 与 `Codes/C18_pure_effect.py` 负责在分析阶段临时派生兼容旧逻辑的分析列，其中 `accessor.py` 还统一承接常用路径工厂与防御式读取 helper。以下若提到 `a_tokens`、`creative_writing_bool`、`a_header_count` 一类字段，除特别说明外，均指“分析阶段临时列”，而不是持久化 parquet 的顶层列。

## 二、总体分类

本项目中的数据结构大致可以分成五层：

| 层级 | 代表结构 | 主要作用 |
| --- | --- | --- |
| 基础标量层 | str、int、float、bool、None | 表示单个字段值，例如 id、token 数、布尔标签、缺失值 |
| Python 容器层 | Path、list、tuple、dict、set、Counter | 组织路径、嵌套对话、分类标签、异常样本、频数统计 |
| pandas / numpy 层 | DataFrame、Series、布尔掩码、groupby 结果、ndarray | 表格计算、向量化分析、统计聚合 |
| 项目数据模式层 | integrated_data.parquet、optimized_data.parquet、子集 parquet | 原始研究数据与分析就绪数据 |
| 输出层 | txt、csv、png | 将统计结果序列化为报告、表格、图表 |

如果只记一句话，可以这样理解：

- DataFrame 是主战场。
- dict / list[dict] 是原始嵌套结构。
- Counter、set、Series 是辅助统计结构。
- ndarray 用于数值计算和重采样。
- Path 管理所有输入输出路径。

## 三、基础标量类型

### 1. str

**介绍**

字符串用于保存文本、标识符、模型名、类别名、错误说明等，是最基本的字段值类型。

**运用说明**

- 记录唯一标识，例如 id、evaluation_session_id。
- 表示类别名，例如 winner、role、language。
- 保存文本内容，例如每一轮对话文本。
- 作为 dict 的键，例如 category_tag 子模块名称。

**项目实例**

- [C04_touch_session.py](../Codes/C04_touch_session.py) 中的 evaluation_session_id。
- [C07_touch_model.py](../Codes/C07_touch_model.py) 中的 model_a、model_b。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中 `conv_user`、`conv_a`、`conv_b` 嵌套字典里的 turn 级文本键。

示例：

```python
winner = row_dict.get("winner")
row_id = row_dict.get("id")
optimized_conv["conv_user"][f"turn_{turn_num}_text_user"] = text
```

### 2. int

**介绍**

整数在本项目中主要表示计数、索引、轮次、token 数与布尔枚举的离散值。

**运用说明**

- 保存出现次数、行数、轮数。
- 保存 token 数和格式计数。
- 保存统计过程中的样本量与异常数量。

**项目实例**

- [C03_verify_order_consistency.py](../Codes/C03_verify_order_consistency.py) 中的 `max_evaluation_order`。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中的 `turns` 与 `metadata_a.token_a`、`metadata_b.token_b`、`metadata_user.token_user`。
- [accessor.py](../Codes/accessor.py) 中临时派生的 `a_tokens`、`b_tokens`、`user_tokens` 分析列。
- [C13_divide_subset.py](../Codes/C13_divide_subset.py) 中各子集的行数统计。

### 3. float

**介绍**

浮点数用于表示比例、胜率、标准化结果、效应量、模型系数、置信区间边界等连续量。

**运用说明**

- 在建模阶段表达估计值与统计量。
- 在可视化和表格输出中表示均值、标准差、OR、相关系数等。

**项目实例**

- [C07_touch_model.py](../Codes/C07_touch_model.py) 中的 `model_win_rates`。
- [C16_length_test.py](../Codes/C16_length_test.py) 中的 bootstrap 统计量。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中的 z-score、路径系数与拟合指标。

### 4. bool

**介绍**

布尔值在本项目中非常关键，因为研究任务类别划分就是建立在多个布尔字段之上的。

**运用说明**

- 表示某行是否满足筛选条件。
- 表示某任务是否属于创意写作、IF、数学、代码四类。
- 表示布尔掩码是否选中某些行。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中 nested `category_tag` 下的 `cw`、`if`、`math`、`code`。
- [accessor.py](../Codes/accessor.py) 中临时派生的 `creative_writing_bool`、`if_bool`、`math_bool`、`code_bool`。
- [C13_divide_subset.py](../Codes/C13_divide_subset.py) 中基于 nested `category_tag` 构造的精确掩码。

示例：

```python
mask &= df[col] == True
optimized_category_tag["category_tag"]["code"] = bool(is_code)
```

### 5. None

**介绍**

None 不是容器，但它是数据结构设计里的重要信号，用来表示“缺失值”或“当前字段不可用”。

**运用说明**

- 判断标签、评分、内容是否缺失。
- 作为输入校验和过滤逻辑的依据。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中检查 `creative_writing_v0.1` 和 `if_v0.1` 的 score 是否为 None。
- [C10_verify_token_correction.py](../Codes/C10_verify_token_correction.py) 中检查 `sum_user_tokens`、`sum_assistant_b_tokens` 是否存在。

## 四、Python 容器结构

### 1. pathlib.Path

**介绍**

Path 不是统计容器，但它是整个项目的数据入口与输出组织器。项目几乎所有脚本都采用路径工厂函数来构造数据文件、报告文件、图表文件的路径。

**运用说明**

- 统一管理输入输出目录。
- 保证脚本可以在不同根目录下运行。
- 避免字符串拼接路径带来的跨平台问题。

**项目实例**

- [C02_integrate_data.py](../Codes/C02_integrate_data.py) 中的 `get_parquet_file_paths()`。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中的输入输出目录构造。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中的报告、表格、图片路径函数。

示例：

```python
def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    if root is None:
        root_path = Path.cwd()
    else:
        root_path = Path(root)
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"
```

### 2. list

**介绍**

list 是项目中最常见的原生容器之一。它既可以保存多个文件路径，也可以保存对话段落、content 项、DataFrame 分片和模型变量名。

**运用说明**

- 当元素有顺序且允许重复时，使用 list 最合适。
- 原始对话按时间顺序出现，因此天然适合 list。
- 多文件合并时，DataFrame 分片先放在 list 中，再统一 `pd.concat`。

**项目实例**

- [C02_integrate_data.py](../Codes/C02_integrate_data.py) 中的 `list[Path]` 和 `list[pd.DataFrame]`。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中的 conversation 结构。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中的连续变量列表、二值变量列表、中介变量列表。

示例 1：文件列表

```python
return [data_dir / f"train-{i:05d}-of-00007.parquet" for i in range(7)]
```

示例 2：对话列表

```python
conversation_a = [
    {"role": "user", "content": [{"text": "请解释...", "type": "text"}]},
    {"role": "assistant", "content": [{"text": "好的，下面说明...", "type": "text"}]},
]
```

### 3. tuple

**介绍**

tuple 适合保存长度固定、语义位置明确的一组值。在本项目中，它常用于函数返回值、配对示例、固定字段组合。

**运用说明**

- 当返回值有固定顺序且不希望被修改时，tuple 比 list 更清晰。
- 在统计脚本里，布尔值和说明文字、两个 DataFrame、若干数值样例常被一起返回。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中 `check_qualification()` 返回 `Tuple[bool, str]`。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中 `prepare_sem_data()` 返回两个 DataFrame。
- [C10_verify_token_correction.py](../Codes/C10_verify_token_correction.py) 中样例不一致列表保存若干元组。

示例：

```python
def check_qualification(row) -> tuple[bool, str]:
    if row.get("evaluation_order", -1) > 1:
        return False, "evaluation_order > 1"
    return True, ""
```

### 4. dict

**介绍**

dict 是项目中第二重要的基础容器。原始标签、元数据、优化结果、统计结果、报告上下文几乎都依赖字典组织。

**运用说明**

- 用键名组织字段，比按位置存储更稳。
- 适合处理嵌套元数据，例如 `category_tag` 和 `conv_metadata`。
- 适合在处理中间阶段逐步构造“结果记录”。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中的 `conv_metadata`、`category_tag`、`optimized_conv`、`optimized_metadata`。
- [C11_touch_category_tag.py](../Codes/C11_touch_category_tag.py) 中的 `missing_submodule_rows` 和 `criteria_counters`。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中的 `EFFECT_LABELS_EN`、`get_table_paths()` 返回字典。

示例：

```python
optimized_metadata = {
    "metadata_a": {
        "token_a": metadata.get("sum_assistant_a_tokens", 0),
        "header_a": metadata.get("header_count_a", {}),
    },
    "metadata_b": {
        "token_b": metadata.get("sum_assistant_b_tokens", 0),
        "header_b": metadata.get("header_count_b", {}),
    },
    "metadata_user": {
        "token_user": metadata.get("sum_user_tokens", 0),
    },
}
```

### 5. 嵌套 dict：dict[str, dict]

**介绍**

这是项目原始标签结构中最重要的形式之一。外层 dict 先按模块分类，内层 dict 再保存具体字段。

**运用说明**

- 适合表示多层标签系统。
- 读取时通常先取模块，再取模块内部字段。
- 重组时通常会先收敛为更稳定的 nested 字段，再由分析脚本按需派生临时列。

**项目实例**

- [C11_touch_category_tag.py](../Codes/C11_touch_category_tag.py) 和 [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中的 `category_tag`。

示例：

```python
category_tag = {
    "creative_writing_v0.1": {"creative_writing": False, "score": 0.12},
    "if_v0.1": {"if": True, "score": 0.86},
    "math_v0.1": {"math": False},
    "criteria_v0.1": {
        "complexity": 1,
        "creativity": 0,
        "technical_accuracy": 1,
    },
}
```

### 6. list[dict]

**介绍**

list[dict] 是原始对话结构的核心形式。外层 list 保留消息顺序，内层 dict 保存每段消息的字段。

**运用说明**

- 适合表达聊天记录、事件流、按顺序排列的复杂对象。
- 统计前通常需要展开成更扁平的结构。

**项目实例**

- [C06_touch_turn.py](../Codes/C06_touch_turn.py) 中遍历 `conversation_a`、`conversation_b`。
- [C08_touch_role.py](../Codes/C08_touch_role.py) 中统计 role。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中将 conversation 重组为 `conv_user`、`conv_a`、`conv_b` 下的 `turn_X_text_*` 键。

示例：

```python
for segment in conv_a:
    if not isinstance(segment, dict):
        continue
    role = segment.get("role")
    content = segment.get("content")
```

### 7. set

**介绍**

set 用于保存唯一元素集合，最常见的用途是异常样本 id 去重、唯一值集合和交集运算。

**运用说明**

- 当只关心“有哪些”“是否重复”“能否求交集”时，set 很高效。
- 不适合保存频数，因为 set 不记录出现次数。

**项目实例**

- [C06_touch_turn.py](../Codes/C06_touch_turn.py) 中的 `mismatch_conv_length_ids`、`mismatch_turn_ids`。
- [C08_touch_role.py](../Codes/C08_touch_role.py) 中用计数器 key 派生 role 集合并求交集。

示例：

```python
mismatch_turn_ids: set[object] = set()
if expected_turn != turn:
    mismatch_turn_ids.add(row_id)
```

### 8. collections.Counter

**介绍**

Counter 是“带计数功能的字典”。它特别适合做频数统计，因此在探索性分析脚本里使用很多。

**运用说明**

- 统计类别出现次数。
- 统计错误原因出现次数。
- 统计“频数的频数”，例如“出现 2 次的 session 有多少个”。

**项目实例**

- [C04_touch_session.py](../Codes/C04_touch_session.py) 中统计“某个出现次数对应多少个 session”。
- [C09_touch_cont.py](../Codes/C09_touch_cont.py) 中统计 content 长度、type、text、image、mimeType。
- [C11_touch_category_tag.py](../Codes/C11_touch_category_tag.py) 中统计各模块与各维度值分布。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中 `optimization_stats["filter_reasons"]`。

示例：

```python
occurrence_distribution = Counter(session_counts.tolist())
filter_reasons = Counter()
filter_reasons[reason] += 1
```

## 五、pandas 与 numpy 结构

### 1. pandas.DataFrame

**介绍**

DataFrame 是本项目最核心的数据结构。它是一个二维表格，每列可以代表一个变量，每行可以代表一条观测记录。

**运用说明**

- 读取 parquet 后，绝大多数分析都在 DataFrame 中进行。
- 清洗、筛选、聚合、建模前准备、导出表格都依赖 DataFrame。
- 对统计研究而言，DataFrame 就是“样本 × 变量”的标准载体。

**项目实例**

- [C02_integrate_data.py](../Codes/C02_integrate_data.py) 中读取多个 parquet 分片并合并。
- [C03_verify_order_consistency.py](../Codes/C03_verify_order_consistency.py) 中 groupby 后生成 session 级汇总表。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中构造优化后的 nested 主表。
- [C14-C22](../Codes/C22_sem_analysis.py) 中几乎所有统计分析都以 DataFrame 为输入。

示例：

```python
df = pd.read_parquet(file_path)
integrated_df = pd.concat(df_list, ignore_index=True)
```

### 2. pandas.Series

**介绍**

Series 是单列数据，既可以看作 DataFrame 的一列，也可以看作带索引的一维向量。

**运用说明**

- 保存某个字段的频数统计结果。
- 保存 groupby / value_counts 的结果。
- 保存一个连续变量，供 z-score 或其他数值运算使用。

**项目实例**

- [C04_touch_session.py](../Codes/C04_touch_session.py) 中的 `session_counts`。
- [C05_touch_order.py](../Codes/C05_touch_order.py) 中的 `order_counts`。
- [C07_touch_model.py](../Codes/C07_touch_model.py) 中的 `model_counts`、`model_wins`。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中的 `_zscore(series)`。

示例：

```python
session_counts = df["evaluation_session_id"].value_counts()
order_counts = df["evaluation_order"].value_counts()
```

### 3. 布尔掩码 Series

**介绍**

布尔掩码本质上也是 Series，只不过其中的值是 True / False，用来选择满足条件的行。

**运用说明**

- 是 pandas 中最常见的筛选结构。
- 在子集划分、条件过滤、异常选择中非常高频。

**项目实例**

- [C13_divide_subset.py](../Codes/C13_divide_subset.py) 中 `_exact_mask()` 返回精确布尔掩码。
- [C03_verify_order_consistency.py](../Codes/C03_verify_order_consistency.py) 中基于条件筛选异常 session。

示例：

```python
mask = pd.Series([True] * len(df), index=df.index)
mask &= df[col] == True
sub = df[mask].copy()
```

### 4. groupby + agg 结果 DataFrame

**介绍**

当原始数据需要按 session、按分箱、按子集汇总时，最常见的结果结构就是 `groupby().agg()` 产生的聚合 DataFrame。

**运用说明**

- 把“行级数据”压缩成“组级统计表”。
- 非常适合一致性校验、描述统计和图表数据准备。

**项目实例**

- [C03_verify_order_consistency.py](../Codes/C03_verify_order_consistency.py) 中的 `session_summary`。
- [C14_visualize_length_preference.py](../Codes/C14_visualize_length_preference.py) 中长度分箱后的统计表。
- [C15_visualize_format_preference.py](../Codes/C15_visualize_format_preference.py) 中格式密度差值分箱后的统计表。

示例：

```python
session_summary = (
    df.groupby("evaluation_session_id")["evaluation_order"]
    .agg(count="count", max_order="max", unique_order_count="nunique")
)
```

### 5. MultiIndex 列

**介绍**

当一次聚合里对同一列计算多个统计量时，pandas 可能返回多层列名结构，也就是 MultiIndex 列。

**运用说明**

- 适合表达“同一变量的多个统计量”。
- 但在导出 csv 或画图之前，往往需要把它压平成普通列名。

**项目实例**

- [C15_visualize_format_preference.py](../Codes/C15_visualize_format_preference.py) 中聚合格式特征时会出现这一结构。

### 6. pandas.Index

**介绍**

Index 是 DataFrame 和 Series 的索引结构。虽然代码里不总是显式命名它，但很多筛选、对齐、拼接都依赖索引。

**运用说明**

- 帮助布尔掩码与原表对齐。
- 帮助 `reset_index()` 后形成新的整齐行号。

**项目实例**

- [C13_divide_subset.py](../Codes/C13_divide_subset.py) 中 `_exact_mask()` 使用 `index=df.index`。
- `pd.concat(..., ignore_index=True)` 在 [C02_integrate_data.py](../Codes/C02_integrate_data.py) 中用于重建统一索引。

### 7. numpy.ndarray

**介绍**

ndarray 是 numpy 的数组结构，适合做向量化数值计算。在本项目里它既出现于 parquet 反序列化后的 content 判断，也出现在 bootstrap、标准化、模型前处理里。

**运用说明**

- 比 list 更适合数值运算。
- 可用于 bootstrap 抽样、统计量计算、标准化与数组掩码。
- 在原始数据中，也可能被用作 conversation / content 的反序列化形式，因此代码需要兼容 `list | tuple | np.ndarray`。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中对 `np.ndarray` 的空 content 判断。
- [C16_length_test.py](../Codes/C16_length_test.py) 中 bootstrap 数组。
- [C22_sem_analysis.py](../Codes/C22_sem_analysis.py) 中 `_zscore()` 里使用 `np.zeros` 和 `np.isnan`。

示例：

```python
if isinstance(content, (list, tuple, np.ndarray)) and len(content) == 0:
    return False, "conversation_a 中存在空 content"

return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
```

### 8. itertuples() 返回的行对象

**介绍**

这是一个常被忽略但很实用的结构。`df.itertuples(index=False)` 返回的不是 dict，而是按列名组织的轻量行对象，通常接近 namedtuple。

**运用说明**

- 比 `iterrows()` 更快。
- 适合逐行读取复杂嵌套字段。
- 若需要 dict 风格访问，可以进一步 `_asdict()`。

**项目实例**

- [C06_touch_turn.py](../Codes/C06_touch_turn.py) 中逐行读取 conversation。
- [C08_touch_role.py](../Codes/C08_touch_role.py) 中逐行统计 role。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中将行对象转成 `row_dict`。

示例：

```python
for row in df.itertuples(index=False):
    conv_a = getattr(row, "conversation_a")
    conv_b = getattr(row, "conversation_b")
```

## 六、项目核心数据模式

这一部分不是解释编程容器，而是解释“研究数据本身长什么样”。统计研究能否成立，首先取决于这一层。

### 1. 原始分片结构：7 个 parquet 文件

**结构形式**

- 类型：`list[Path]`
- 作用：组织 7 个原始 parquet 分片的路径

**项目实例**

- [C02_integrate_data.py](../Codes/C02_integrate_data.py) 中 `get_parquet_file_paths()`。

### 2. integrated_data.parquet：整合但仍保留嵌套结构

**介绍**

这是 Layer 1 到 Layer 2 的核心结果。它已经把 7 个原始分片合并为一个总表，但 conversation、category_tag、conv_metadata 仍然是嵌套结构。

**代表字段结构**

```python
{
    "id": "...",
    "evaluation_session_id": "...",
    "evaluation_order": 1,
    "conversation_a": [
        {"role": "user", "content": [{"text": "问题", "type": "text"}]},
        {"role": "assistant", "content": [{"text": "回答A", "type": "text"}]},
    ],
    "conversation_b": [
        {"role": "user", "content": [{"text": "问题", "type": "text"}]},
        {"role": "assistant", "content": [{"text": "回答B", "type": "text"}]},
    ],
    "conv_metadata": {
        "sum_user_tokens": 123,
        "sum_assistant_a_tokens": 456,
        "header_count_a": 2,
    },
    "category_tag": {
        "creative_writing_v0.1": {"creative_writing": False, "score": 0.1},
        "if_v0.1": {"if": True, "score": 0.9},
        "math_v0.1": {"math": False},
        "criteria_v0.1": {"complexity": 1, "creativity": 0},
    },
}
```

**运用说明**

- 适合保留原始数据语义，但不适合直接做统计建模。
- 在 C03-C11 中，这种结构被用于字段审计和一致性检查。
- 在 C12 中，它被清洗并重组为层次更稳定的 nested optimized_data。

**项目实例**

- [C03-C11](../Codes/C11_touch_category_tag.py) 使用 integrated_data 进行 Phase 2 字段审阅。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 将其转换为优化后的 nested 主表。

### 3. conversation_a / conversation_b：嵌套对话结构

**结构形式**

- 类型：`list[dict]`
- 内层字段：`role`、`content`
- content 又是 `list[dict]`

**运用说明**

- 这是对话研究最重要的原始结构。
- 优点是完整保留了“谁在什么时候说了什么”。
- 缺点是统计分析前必须展开，否则很难直接按列操作。

**项目实例**

- [C06_touch_turn.py](../Codes/C06_touch_turn.py) 用它验证 turn 与对话长度是否一致。
- [C08_touch_role.py](../Codes/C08_touch_role.py) 用它统计 role。
- [C09_touch_cont.py](../Codes/C09_touch_cont.py) 用它统计 content 结构。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 用它重组 `conv_user`、`conv_a`、`conv_b` 内部的 turn 级文本键。

### 4. conv_metadata：原始元数据入口

**结构形式**

- 类型：`dict[str, int]` 为主
- 内容：token 数、标题数、列表数、粗体数等

**运用说明**

- 保存对话级别的辅助统计量。
- 原始字段较多，因此 C12 不再把它直接原样带入主表，而是重组为 `metadata_a`、`metadata_b`、`metadata_user`。

**项目实例**

- [C10_verify_token_correction.py](../Codes/C10_verify_token_correction.py) 用它校验 token 汇总值。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 中 `optimize_conv_metadata()` 将其整理为三块 nested metadata。

### 5. category_tag：多层标签结构

**结构形式**

- 类型：`dict[str, dict]`
- 子模块：creative_writing_v0.1、if_v0.1、math_v0.1、criteria_v0.1

**运用说明**

- 它是任务类别与质量维度的标签来源。
- 统计前既要检查其完整性，也要将其收敛为稳定的 nested `category_tag` 与 `criteria`。

**项目实例**

- [C11_touch_category_tag.py](../Codes/C11_touch_category_tag.py) 用它做模块级审阅。
- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 将其收敛为 `category_tag` 与 `criteria` 两块 nested 结构。

### 6. optimized_data.parquet：分析就绪的 nested 主表

**介绍**

这是项目从“保留原始结构”转向“稳定承载分析”的关键数据结构。它本质上仍是 DataFrame，但顶层只保留少量稳定字段，而把对话、元数据、任务标签和质量维度收进多个 nested 字典中。

**当前顶层字段**

- 标识类：id、model_a、model_b、winner、language
- 结构类：turns、conv_a、conv_b、conv_user
- 元数据类：metadata_a、metadata_b、metadata_user
- 标签类：category_tag、criteria

**nested 字段内部示例**

- `conv_user`：`turn_1_text_user`、`turn_2_text_user` 等
- `conv_a` / `conv_b`：`turn_1_text_a`、`turn_1_text_b` 等
- `metadata_a` / `metadata_b`：`token_a`、`header_a`、`list_a`、`bold_a` 等
- `metadata_user`：`token_user`
- `category_tag`：`cw`、`if`、`math`、`code`
- `criteria`：`complexity`、`creativity`、`domain_knowledge`、`problem_solving`、`real_world`、`specificity`、`technical_accuracy`

**分析阶段的临时兼容列**

- [accessor.py](../Codes/accessor.py) 会从 nested 主表临时派生 `a_tokens`、`a_header_count`、`creative_writing_bool` 等旧逻辑列。
- [C18_pure_effect.py](../Codes/C18_pure_effect.py) 的 `load_data_global()` / `load_subset()` 在此基础上继续构造 pair-level 建模字段。

**运用说明**

- 这是 C14-C22 的统一上游输入，但下游通常不会直接假设其顶层含有 flat 分析列。
- 优点是顶层 schema 更稳定，减少了每次变量扩展都要改主表列数的问题。
- 代价是很多分析列需要在运行时从 nested 字段临时解包，因此 `accessor.py` 与 C18 loader 变成关键兼容层；其中统计标准化和候选列筛选则进一步收敛到 `stats_utils.py`。

**项目实例**

- [C12_optimize_data.py](../Codes/C12_optimize_data.py) 写出该表。
- [C14-C17](../Codes/C17_format_test.py) 通过 `accessor.py` 解包该表进行长度/格式分析。
- [C18-C22](../Codes/C22_sem_analysis.py) 通过 C18 的共享 loader 在该表之上继续建模。

### 7. 子集 parquet：布尔掩码划分后的分析单元

**介绍**

当 optimized_data 构建完成后，项目继续将其按四个布尔列切分为多个分析子集，以支持不同类别组合下的比较与稳健性检验。

**结构形式**

- 类型：多个 parquet 文件
- 本质：多个“结构相同但行集合不同”的 DataFrame

**运用说明**

- 单一类别子集用于“某类任务整体分析”。
- 纯净分区用于“互不重叠的类别组合比较”。
- 当前子集划分来自 nested `category_tag`，而不是旧版顶层布尔列。

**项目实例**

- [C13_divide_subset.py](../Codes/C13_divide_subset.py) 中的 `create_single_category_subsets()` 与 `create_exclusive_subsets()`。

## 七、结构之间如何转换

这是全项目最重要的结构变化链路：

```text
list[Path]
  -> 多个 parquet 分片
  -> list[pd.DataFrame]
  -> pd.concat(...)
  -> integrated_data.parquet
  -> DataFrame（含 list[dict] / dict[str, dict] / dict[str, int]）
    -> 清洗与 nested 重组
  -> optimized_data.parquet
    -> DataFrame（14 列顶层 + 多个 nested dict）
    -> accessor / C18 loader / stats_utils
    -> DataFrame（临时分析列 + pair-level 特征）
  -> 布尔掩码 / groupby / 回归特征表 / 匹配表 / SEM 表
  -> Reports / Tables / Pictures
```

从统计研究角度看，这条链路对应三步：

1. 原始结构保真：先尽量保留原始语义。
2. 结构工程化：先把原始嵌套字段整理为稳定的 nested 主表，再按分析需要临时派生列。
3. 统计结构化：把分析结果再组织成表格、图形和报告。

## 八、最值得掌握的 8 种结构

如果只从项目学习角度出发，最值得优先掌握的是下面 8 种：

1. DataFrame：所有统计分析的主表。
2. Series：单变量统计、频数统计和数值变换的基础。
3. dict：元数据、标签、输出记录的基础结构。
4. list[dict]：原始 conversation 的核心结构。
5. Counter：探索性分析中的频数统计利器。
6. set：异常样本去重与集合判断的简洁工具。
7. 布尔掩码 Series：子集划分和条件过滤的关键。
8. ndarray：bootstrap、标准化和数值计算的基础数组。

## 九、学习建议

建议按下面顺序理解本项目的数据结构：

1. 先看 [C02_integrate_data.py](../Codes/C02_integrate_data.py)，理解 `list[Path] -> list[DataFrame] -> DataFrame`。
2. 再看 [C06_touch_turn.py](../Codes/C06_touch_turn.py)、[C08_touch_role.py](../Codes/C08_touch_role.py)、[C09_touch_cont.py](../Codes/C09_touch_cont.py)，理解原始 `list[dict]` 对话结构。
3. 然后看 [C11_touch_category_tag.py](../Codes/C11_touch_category_tag.py)，理解 `dict[str, dict]` 标签结构。
4. 接着看 [C12_optimize_data.py](../Codes/C12_optimize_data.py)，理解嵌套结构如何被重组为稳定的 nested 主表。
5. 然后看 [accessor.py](../Codes/accessor.py)、[stats_utils.py](../Codes/stats_utils.py) 与 [C18_pure_effect.py](../Codes/C18_pure_effect.py)，理解分析阶段如何临时派生兼容列并复用统计预处理 helper。
6. 最后看 [C13_divide_subset.py](../Codes/C13_divide_subset.py) 到 [C22_sem_analysis.py](../Codes/C22_sem_analysis.py)，理解 DataFrame、Series、布尔掩码、ndarray 如何支撑正式统计分析。

## 十、结论

统计研究的基础不是“代码跑通”，而是“数据结构设计正确”。本项目的结构设计具有非常清晰的层次：

- 用 Path 管理数据入口和输出位置。
- 用 list 和 dict 保留原始嵌套语义。
- 用 DataFrame 和 Series 承接绝大多数统计工作。
- 用 Counter、set、布尔掩码等轻量结构完成探索、审计与筛选。
- 用 C12 的 nested 重组稳定持久 schema，再通过共享 accessor 和 loader 把原始语义转化为可建模变量。

因此，如果要真正理解这套代码，最应该先掌握的不是某一个统计方法，而是“原始嵌套结构怎样先被整理成 nested 主表，再被派生成分析结构”。这正是本项目从数据工程走向统计研究的起点。