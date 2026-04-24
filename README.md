# MUC-QMJH 数据分析研究仓库

**项目版本**: v1.5  
**更新时间**: 2026-04-15  
**状态**: 主分析链完成（C18–C22：净效应、双稳健性链、匹配诊断、SEM 全部完成）

本 README 现在同时承担两项职责：

- 作为 GitHub 公开仓库首页，说明项目定位、安装方式、许可边界和引用方式
- 作为项目技术总览，汇总数据流、脚本结构、核心产物和当前结论

---

## GitHub 仓库定位

本仓库是一个研究型 GitHub Repo，围绕 LLM 人类偏好数据中的长度偏好和格式偏好开展可复现分析。仓库当前主要包含：

- 自研分析脚本与 Notebook
- 自撰写方法说明和教学材料
- 研究报告、表格和图片产物
- 数据处理流程说明与复现入口

本仓库不以“直接再分发第三方原始数据”为目标。若你要复现结果，应先确认上游数据许可，并按说明自行放置数据文件。

## 快速开始

### 1. 环境准备

推荐 Python 3.10 及以上版本，并在仓库根目录安装依赖：

```bash
pip install -r requirements.txt
```

若需要运行全集成 Notebook，还建议保留 Jupyter 环境。

### 2. 数据准备

本仓库默认不承诺对第三方数据作统一再分发。请根据上游数据来源自行准备原始 parquet 分片，并放置到 README 与脚本约定的目录结构中。

### 3. 运行方式

所有脚本默认在仓库根目录执行，例如：

```bash
python Codes/C12_optimize_data.py
python Codes/C13_divide_subset.py
python Codes/C16_length_test.py
```

整体流程大体为：

1. C01-C02 验证与整合原始数据
2. C03-C11 检查字段结构与异常
3. C12 清洗和优化数据
4. C13 划分 20 个研究子集
5. C14-C22 完成描述统计、显著性检验、净效应、稳健性和 SEM

## 许可、数据与引用

### 代码许可

除另有说明外，自研代码采用 [Apache-2.0](./LICENSE) 发布。

### 文档许可

除另有说明外，自研文档和教学材料采用 [CC BY 4.0](./LICENSE-docs.md) 共享。

### 数据边界

Data/ 下的原始数据、缓存数据和可能受上游条款约束的派生数据，不受根目录代码许可证统一授权。使用前请先阅读 [LICENSE_POLICY.md](./LICENSE_POLICY.md)。

### 引用方式

若你在论文、课程、讲义或派生软件中使用本仓库，请优先引用 [CITATION.cff](./CITATION.cff)。在正式公开到 GitHub 前，请维护者补充实际仓库 URL 和维护者信息。

## 治理文件

公开仓库的协作、引用和合规说明已拆分到以下文件：

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)
- [LICENSE_POLICY.md](./LICENSE_POLICY.md)

---

## 目录

1. [GitHub 仓库定位](#github-仓库定位)
2. [快速开始](#快速开始)
3. [许可、数据与引用](#许可数据与引用)
4. [治理文件](#治理文件)
5. [项目概述](#项目概述)
6. [现有成果](#现有成果)
7. [数据流向](#数据流向)
8. [代码架构](#代码架构)
9. [代码风格规范](#代码风格规范)
10. [脚本详解](#脚本详解)
11. [关键设计模式](#关键设计模式)

---

## 项目概述

本项目对大规模AI模型人类偏好数据集（LMarena）进行全面的数据分析、清洗和优化。

**核心目标**：
- 验证原始数据完整性和一致性
- 清洗并优化数据集结构
- 按任务类型进行数据划分
- 量化长度/格式偏好、控制混淆，并通过 SEM 描述因果路径

**数据规模**：
- 原始行数：135,634 条记录
- 清洗后：108,171 条记录（保留率 79.75%）
- 涉及模型数：53 种
- 语言种类：126 种

---

## 现有成果

### 已完成的脚本

| 代码 | 名称 | 功能 | 输出 |
|------|------|------|------|
| C01 | verify_session_integrity | 验证Session完整性 | - |
| C02 | integrate_data | 整合parquet分片 | integrated_data.parquet |
| C03 | verify_order_consistency | 验证评价轮次一致性 | - |
| C04 | touch_session | 分析Session ID分布 | R01_session_report.txt |
| C05 | touch_order | 分析评价轮次分布 | R02_order_report.txt |
| C06 | touch_turn | 分析对话轮数 | R03_turn_report.txt |
| C07 | touch_model | 分析模型参与情况 | R04_model_report.txt |
| C08 | touch_role | 分析角色标签 | R05_role_report.txt |
| C09 | touch_cont | 分析对话内容结构 | R06_cont_report.txt |
| C10 | verify_token_correction | 验证Token数一致性 | R07_token_report.txt |
| C11 | touch_category_tag | 分析分类标签 | R08_category_tag_report.txt |
| C12 | optimize_data | 数据清洗和优化 | R09_optimization_report.txt + optimized_data.parquet |
| C13 | divide_subset | 按分类划分数据集 | R10_division_report.txt + 20个子集文件 |
| C14 | visualize_length_preference | 长度偏好可视化（差值分析）| R11 + T01 + P05 |
| C15 | visualize_format_preference | 格式偏好可视化（新增格式密度）| R12 + T03-T08 + P06-P10 |
| C16 | length_test | Wilcoxon 长度偏好检验 + Bonferroni + Bootstrap CI + Cohen's d | R13 ✅ |
| C17 | format_test | 格式偏好检验（Wilcoxon + 密度辅助 + 卡方）| R14 ✅ |
| C18 | pure_effect | 净效应嵌套逻辑回归（长度 M0→M3；格式 F0→F3；C13 子集）| R16 ✅ |
| C19 | length_effect_robust | 调整 Logit + 稳定化 IPW + bootstrap CI | R17 + T14 ✅ |
| C20 | format_effect_robust | 格式效应稳健性分析（调整 Logit + 稳定化 IPW + bootstrap CI） | R18 + T15 ✅ |
| C21 | enhanced_matching_diagnostics | PSM 匹配诊断 + SMD 平衡性 + 配对 Wilcoxon | R19 + T16-T17 ✅ |
| C22 | sem_analysis | 结构方程模型（主模型/扩展模型 + bootstrap CI + 路径图）| R20 + T09-T13 + P11 ✅ |

### 最新核心结论

- **长度偏好在控制混淆后仍然稳健存在**：C18 全量净效应 OR=1.355；C19 全量调整 OR=1.910，IPW ATE=0.149，95% CI [0.135, 0.161]。
- **标题/粗体格式偏好在稳健性分析中仍成立，列表仅保留为敏感性变量**：C20 全量标题密度调整 OR=1.132，IPW ATE=0.028；粗体密度调整 OR=1.106，IPW ATE=0.025；列表密度全量 IPW CI 跨 0，不写入主结论。
- **匹配后长度结论仍成立**：C21 全量样本 mean|SMD| 从 0.250 降至 0.060，匹配后 ATE=0.160，配对 Wilcoxon 极显著。
- **SEM 支持“长度 + 标题密度 + 粗体密度”并列作用于偏好**：C22 主模型拟合优度极高（CFI=0.9998，RMSEA=0.0030），三条直接路径 bootstrap CI 均不跨 0。

### 生成的数据文件

**数据目录结构**：
```
Data/
├── integrated_data/
│   └── integrated_data.parquet          (135,634行 × 14列)
├── optimized_data/
│   ├── optimized_data.parquet           (108,171行 × 32列)
│   ├── creative_writing_*.parquet       (按分类)
│   ├── if_*.parquet                     (按分类)
│   ├── math_*.parquet                   (按分类)
│   └── ...                              (20个子集)
├── length_data/
│   └── length_data.parquet              (长度分析专用)
└── format_data/
    └── format_data.parquet              (格式分析专用)
```

### 生成的报告文件

```
Reports/
├── R01_session_report.txt               (Session ID分析)
├── R02_order_report.txt                 (评价轮次分析)
├── R03_turn_report.txt                  (对话轮数分析)
├── R04_model_report.txt                 (模型参与分析)
├── R05_role_report.txt                  (角色标签分析)
├── R06_cont_report.txt                  (内容结构分析)
├── R07_token_report.txt                 (Token一致性)
├── R08_category_tag_report.txt          (分类标签分析)
├── R09_optimization_report.txt          (清洗统计)
├── R10_division_report.txt              (划分统计)
├── R11-R14_*.txt                        (描述统计 + 显著性检验)
├── R16_pure_effect_report.txt           (净效应分析)
├── R17_length_effect_robust_report.txt  (长度稳健性)
├── R18_format_effect_robust_report.txt  (格式稳健性)
├── R19_enhanced_diagnostics_report.txt  (匹配诊断)
└── R20_sem_analysis_report.txt          (SEM 报告)
```

---

## 数据流向

```
┌─────────────────────────────────────────────────────────────┐
│ 原始数据：7个parquet分片 (train-00000 ~ train-00006)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                    C02 integrate_data
                         │
        ┌────────────────▼────────────────┐
        │ integrated_data.parquet         │
        │ 135,634行 × 14列                │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
    C03-C11: 数据验证与分析            
        │                                 │
        └────────────────┬────────────────┘
                         │
                    C12 optimize_data
                    (清洗+扁平化+降维)
                         │
        ┌────────────────▼────────────────┐
        │ optimized_data.parquet          │
        │ 108,171行 × 32列                │
        │ (过滤27,463行，保留率79.75%)   │
        └────────────────┬────────────────┘
                         │
                   C13 divide_subset
                  (按分类维度划分)
                         │
    ┌────────┬─────┬──────┴───────┬──────┬──────┐
    │        │     │              │      │      │
creative_  if_  math_  only_*  两分类  全分类 无分类
writing  orders orders   subsets intersect data  data
(6个)    (6个)  (6个)    (3个)    (3个)   (1个) (1个)
    
    ↓
总计20个子集文件
```

---

## 代码架构

### 逻辑分层

```
第一层：数据采集 (C01-C02)
  ├─ C01: 原始数据验证
  └─ C02: 多文件整合

第二层：数据验证 (C03-C11)
  ├─ C03: Order字段一致性
  ├─ C04-C09: 字段分布分析
  └─ C10-C11: 嵌套字段验证

第三层：数据清洗 (C12)
  ├─ 行级过滤 (check_qualification)
  ├─ 对话扁平化 (optimize_conversation)
  ├─ 元数据简化 (optimize_conv_metadata)
  ├─ 标签降维 (optimize_category_tag)
  └─ 维度提取 (optimize_criteria)

第四层：数据划分 (C13)
  ├─ 单一分类子集 (6个)
  ├─ 纯净子集 (3个)
  ├─ 二分类交叉 (3个)
  ├─ 全分类子集 (1个)
  └─ 无分类子集 (1个)

第五层：描述性分析 (C14-C15)
  ├─ C14: 长度偏好可视化 (双轴折线图 + 分箱统计)
  └─ C15: 格式偏好可视化 (存在性/数量/组合三维分析)

第六层：统计检验 (C16-C17，已完成)
  ├─ C16: Wilcoxon 符号秩检验（长度，13 子集，12/13 显著）
  └─ C17: 格式偏好混合检验（Wilcoxon + 密度辅助 + 卡方）

第六.五层：净效应分析 (C18，已完成)
  └─ C18: 嵌套逻辑回归（长度 M0→M3；格式 F0→F3；混淆比例；C13 子集）

第七层：稳健性检验与匹配诊断 (C19-C21，已完成)
    ├─ C19: 长度效应稳健性（调整 Logit + 稳定化 IPW + bootstrap CI）
    ├─ C20: 格式效应稳健性（标题/粗体主分析，列表敏感性分析）
    └─ C21: 匹配质量诊断 + SMD 平衡性 + Within-pair Wilcoxon

第八层：机制解释 (C22，已完成)
    └─ C22: SEM 路径分析（主模型/扩展模型 + bootstrap CI + 路径图）
```

### 模块化设计

每个脚本遵循统一的结构：

```python
1. 工具函数
   ├─ get_*_path()        # 路径管理
   └─ validate_*()        # 数据验证（可选）

2. 分析函数
   └─ touch_*() / optimize_*() / divide_*()

3. 辅助函数
   ├─ create_*_subsets()  # 子集创建
   └─ generate_*_report() # 报告生成

4. 主函数
   └─ if __name__ == "__main__"
```

---

## 代码风格规范

### 1. 路径管理

**统一使用 `pathlib.Path` 对象**：

```python
from pathlib import Path

def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据文件的默认路径。"""
    if root is None:
        root = Path.cwd()
    root_path = Path(root)
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"
```

**优势**：
- 跨平台兼容（自动处理 / 和 \）
- 链式调用清晰
- 内置 `exists()`, `mkdir()` 等方法

### 2. 参数设计

**统一的可选参数模式**：

```python
def optimize_data(file_path: Path | str | None = None,
                  data_dir: Path | str | None = None,
                  report_dir: Path | str | None = None) -> None:
    """
    参数说明。
    
    参数：
    - file_path：输入文件（默认使用内置路径）
    - data_dir：数据输出目录（默认为Data/optimized_data）
    - report_dir：报告输出目录（默认为Reports）
    """
    
    # 参数标准化
    if file_path is None:
        file_path = get_integrated_parquet_path()
    else:
        file_path = Path(file_path)
    
    if data_dir is None:
        data_dir = Path.cwd() / "Data" / "optimized_data"
    else:
        data_dir = Path(data_dir)
    
    # 提前创建目录
    data_dir.mkdir(parents=True, exist_ok=True)
```

**优势**：
- 支持自定义输入输出路径，便于测试
- 默认参数提供合理的默认值
- 统一的参数验证逻辑

### 3. 类型提示

**完整的类型标注**：

```python
from typing import Dict, Counter, Set, Tuple

def touch_model(file_path: Path | str | None = None, 
                output_dir: Path | str | None = None) -> None:
    """..."""

def check_qualification(row: dict) -> Tuple[bool, str]:
    """检查单行数据。返回(是否合格, 原因)"""

def create_single_category_subsets(df: pd.DataFrame, 
                                   output_dir: Path) -> Dict[str, int]:
    """创建子集。返回统计字典"""
```

**优势**：
- IDE自动补全
- 类型检查工具支持
- 代码可读性高

### 4. 错误处理

**统一的异常捕获模式**：

```python
# 文件存在性检查
if not file_path.exists():
    print(f"  ERROR: 文件不存在: {file_path}")
    return

# 读取异常处理
try:
    df = pd.read_parquet(file_path)
except Exception as exc:
    print(f"  ERROR: 读取失败 - {exc}")
    return

# 写入异常处理
try:
    df.to_parquet(output_file, index=False)
    print(f"已保存至: {output_file}")
except Exception as exc:
    print(f"  ERROR: 保存失败 - {exc}")
    return
```

**原则**：
- 捕获具体异常类型（如有可能）
- 输出清晰的错误消息
- 优雅地处理失败（返回或记录日志）

### 5. 输出规范

**统一的进度提示**：

```python
print("=" * 80)
print(f"处理文件 {file_idx}/{len(file_paths)}: {file_path}")
print("-" * 80)

print(f"  读取成功，数据形状: {df.shape}")
print(f"  发现 {len(models)} 种不同的模型")

print("=" * 80)
print("任务完成！")
print("=" * 80)
```

**规范**：
- 使用分隔符区分不同阶段
- 包含进度信息（如 n/total）
- 两个空行分隔主要段落

---

## 脚本详解

### C12: optimize_data（关键脚本）

**核心功能**：数据清洗和结构优化

**过滤标准**：
```python
1. evaluation_order == 1           # 仅保留首轮评价
2. conversation_a/b content非空    # 排除缺失内容
3. category_tag评分非None         # 需要有效标签
4. language != '<err>'             # 排除语言识别失败
```

**优化步骤**：
```python
原始数据形状: (135634, 14)
            ↓
按qualification过滤: 108171行 (保留79.75%)
            ↓
对话扁平化: 提取turn_X_a_text, turn_X_b_text
            ↓
元数据简化: 保留a_tokens, a_header_count等关键字段
            ↓
标签降维: creative_writing_bool, if_bool, math_bool, code_bool
            ↓
维度提取: 7个标准评估维度
            ↓
最终形状: (108171, 32)
```

**两个独立输出路径**：
- `data_dir`: 优化数据文件 → `Data/optimized_data/`
- `report_dir`: 清洗报告 → `Reports/R09_optimization_report.txt`

### C13: divide_subset（数据分割脚本）

**划分维度**：4个分类布尔值
```python
creative_writing_bool  | if_bool | math_bool | code_bool
────────────────────────────────────────────────────────
        T/F              |  T/F    |   T/F     |   T/F
```

**20个子集的组织**：
```
1. 单一分类（4个，含该类，允许重叠）
    - creative_writing_true
    - if_true
    - math_true
    - code_true

2. 纯净子集（4个）
    - only_cw
    - only_if
    - only_math
    - only_code

3. 二分类交叉（6个）
    - cw_if, cw_math, cw_code
    - if_math, if_code, math_code

4. 三分类交叉（4个）
    - cw_if_math, cw_if_code
    - cw_math_code, if_math_code

5. 特殊子集（2个）
   - all_categories
   - no_category

5. 共覆盖互不重叠: 104,192行
```

**简化点**：
- 去除了 `validate_optimized_data()` 验证函数
- 原因：C12已进行清洗，无需重复验证

---

## 关键设计模式

### 模式1：路径工厂函数

```python
def get_integrated_parquet_path(root=None) -> Path:
    """单一职责：返回标准路径"""
    if root is None:
        root = Path.cwd()
    return Path(root) / "Data" / "integrated_data" / "integrated_data.parquet"

# 使用
file_path = get_integrated_parquet_path()  # 使用默认
file_path = get_integrated_parquet_path("/custom/root")  # 自定义
```

**优势**：
- 集中管理路径逻辑
- 便于维护路径规范
- 支持路径的动态构造

### 模式2：统计字典收集

```python
optimization_stats = {
    "total_rows": len(df),
    "qualified_rows": 0,
    "filtered_rows": 0,
    "filter_reasons": Counter(),
    "processing_errors": 0,
    "error_ids": []
}

# 在循环中累积统计
for row in df.itertuples():
    is_qualified, reason = check_qualification(row_dict)
    if not is_qualified:
        optimization_stats["filtered_rows"] += 1
        optimization_stats["filter_reasons"][reason] += 1

# 使用统计生成报告
generate_optimization_report(..., stats=optimization_stats, ...)
```

**优势**：
- 统计信息集中管理
- 易于传递给报告函数
- 支持后续扩展

### 模式3：分阶段子集创建

```python
def divide_data_by_category(...):
    """分阶段创建子集，分别处理逻辑"""
    
    # 第一阶段：单一分类
    stats_single = create_single_category_subsets(df, data_dir)
    
    # 第二阶段：纯净子集
    stats_pure = create_pure_subsets(df, data_dir)
    
    # 第三阶段：二分类
    stats_two = create_two_category_subsets(df, data_dir)
    
    # 第四阶段：特殊子集
    stats_special = create_special_subsets(df, data_dir)
    
    # 汇总生成报告
    all_stats["subsets"].update(stats_single)
    all_stats["subsets"].update(stats_pure)
    # ...
```

**优势**：
- 逻辑清晰，易于调试
- 模块化程度高
- 便于扩展新的划分维度

---

## 注释规范

### docstring格式

```python
def optimize_data(file_path: Path | str | None = None,
                  data_dir: Path | str | None = None,
                  report_dir: Path | str | None = None) -> None:
    """
    简短一句描述。

    详细描述（可选），说明函数做什么，为什么这样做，使用场景等。

    参数说明：
    - file_path：输入文件路径（默认使用内置路径）
    - data_dir：输出数据目录（默认为Data/optimized_data）
    - report_dir：输出报告目录（默认为Reports）

    返回值：无（直接保存文件和生成报告）
    
    异常处理：
    - 文件不存在时输出ERROR并返回
    - 读取/保存失败时捕获Exception并返回
    """
```

### 段落注释

```python
# 检查该行是否符合优化条件
# evaluation_order > 1表示非首轮评价，应被过滤
is_qualified, reason = check_qualification(row_dict)

if not is_qualified:
    # 记录过滤原因分布，用于后续统计报告
    optimization_stats["filtered_rows"] += 1
    optimization_stats["filter_reasons"][reason] += 1
    continue
```

### 行内注释（谨慎使用）

```python
# 仅当必要时添加，解释"为什么"而非"做什么"

# 计算长度比率: 模型输出长度 / 用户输入长度
a_length_ratio = a_tokens / user_tokens

# 按turn分配: turn_num = 消息索引 / 2 + 1
# 原因：每个turn包含user和assistant各一条消息
turn_num = i // 2 + 1
```

---

## 质量指标

| 指标 | 值 | 说明 |
|------|-----|------|
| 代码规范性 | ⭐⭐⭐⭐⭐ | 统一的风格、命名、类型提示 |
| 可维护性 | ⭐⭐⭐⭐⭐ | 模块化设计，低耦合 |
| 可扩展性 | ⭐⭐⭐⭐⭐ | 灵活的参数化，支持自定义路径 |
| 错误处理 | ⭐⭐⭐⭐☆ | 完整的异常捕获，清晰的错误消息 |
| 文档完整性 | ⭐⭐⭐⭐⭐ | 详尽的docstring和段落注释 |

---

## 后续开发建议

### 当前优先

- [ ] 为 C13 增加 `lang_en` 英语子集，检验多语言污染对主结论的影响
- [ ] 将 `no_category` 进一步细分为 `no_category_code` / `no_category_natural`

### 近期扩展

- [ ] 在 C21 中加入新的回复级中介：步骤数、代码块数、引用数、段落数
- [ ] 对 C19/C20/C21 增加英语子集附录结果，评估结论跨语言稳定性

### 论文整合

- [ ] 将 R13–R19 收束为论文“结果”主表和附录表
- [ ] 依据 R19 路径结果，重写“长度与格式偏好机制”章节

---

## 参考资料

**项目文件**：
- [C12_optimize_data.py](./Codes/C12_optimize_data.py) - 数据清洗脚本
- [C13_divide_subset.py](./Codes/C13_divide_subset.py) - 数据划分脚本
- [R09_optimization_report.txt](./Reports/R09_optimization_report.txt) - 清洗统计

**相关数据**：
- 整合数据：`Data/integrated_data/integrated_data.parquet` (135,634行)
- 优化数据：`Data/optimized_data/optimized_data.parquet` (108,171行)
- 子集数据：`Data/optimized_data/*.parquet` (20个文件)

---

**README 最近整理时间**: 2026-04-15  
**仓库维护方**: MUC-QMJH Team  
**机构归属**: Minzu University of China（公开发布前建议核对正式英文署名）
