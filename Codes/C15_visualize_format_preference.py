"""
格式偏好可视化分析脚本

本脚本对AI模型的输出格式偏好进行全面的可视化分析，包括：
- 格式特征提取：从嵌套的format_counts字典中提取标题、列表、粗体等
- 格式存在分析：有/无特定格式对胜率的影响
- 计数分析：标题数、列表数、粗体数与胜率的关系
- 组合分析：不同格式组合与胜率的关系
- 统计报告：生成详细的统计表格和分析报告

数据流向：
  optimized_data.parquet → 格式特征计算 → 分类分析 → 可视化 → 报告生成
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# 全局配置：忽略所有警告（可选）
warnings.filterwarnings('ignore')

# matplotlib和seaborn配置：用于支持中文显示和美观的图表样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 用于正确显示负号
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ========================================================================
# 路径管理函数：集中管理项目中的文件和目录路径
# ========================================================================

def get_optimized_parquet_path(root: Path | str | None = None) -> Path:
    """返回优化数据 parquet 文件的默认路径。"""
    
    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path = Path.cwd()
    else:
        root_path = Path(root)
    
    # 优化数据文件位于项目根目录下的 Data/optimized_data/optimized_data.parquet
    return root_path / "Data" / "optimized_data" / "optimized_data.parquet"


def get_format_data_path(root: Path | str | None = None) -> Path:
    """
    返回格式数据 parquet 文件的默认路径。
    
    此路径用于存储预处理后的格式特征数据，可用于后续快速分析。
    """
    if root is None:
        root_path = Path.cwd()
    else:
        root_path = Path(root)
    
    return root_path / "Data" / "format_data" / "format_data.parquet"



# ========================================================================
# 格式特征提取函数：从嵌套字典中提取原始特征值
# ========================================================================

def extract_header_count(header_dict: dict | None) -> int:
    """
    从header_counts字典中提取标题总数。
    
    参数说明：
    - header_dict：格式为 {'h1': count, 'h2': count, ..., 'h6': count} 的字典，
                   或为None（表示无标题数据）
    
    返回值：所有等级的标题总数（h1到h6）
    
    说明：
    - 当header_dict为None或不是dict时，返回0
    - 统计h1到h6所有等级标题的数量
    """
    if isinstance(header_dict, dict):
        # 遍历h1到h6，求和所有等级的标题数量
        return sum(header_dict.get(f'h{i}', 0) for i in range(1, 7))
    return 0


def extract_list_count(list_dict: dict | None) -> int:
    """
    从list_counts字典中提取列表总数。
    
    参数说明：
    - list_dict：格式为 {'ordered': count, 'unordered': count} 的字典，
                 或为None（表示无列表数据）
    
    返回值：有序列表和无序列表的总和
    
    说明：
    - 当list_dict为None或不是dict时，返回0
    - 统计ordered（有序）和unordered（无序）两种列表的数量
    """
    if isinstance(list_dict, dict):
        # 有序列表(如1.2.3)和无序列表(如·项目符号)的总数
        return list_dict.get('ordered', 0) + list_dict.get('unordered', 0)
    return 0


def extract_bold_count(bold_dict: dict | None) -> int:
    """
    从bold_counts字典中提取粗体总数。
    
    参数说明：
    - bold_dict：格式为 {'**': count, '__': count} 的字典，
                 或为None（表示无粗体数据）
    
    返回值：所有粗体标记的总数
    
    说明：
    - 当bold_dict为None或不是dict时，返回0
    - Markdown中粗体可用 ** 或 __ 表示，统计两种标记的总数
    """
    if isinstance(bold_dict, dict):
        # ** 和 __ 都是粗体标记方式，统计两种的总数
        return bold_dict.get('**', 0) + bold_dict.get('__', 0)
    return 0



def prepare_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    从优化数据中提取格式特征并执行解缠化处理，同时计算格式密度列。

    格式密度 = 格式计数 / (输出 tokens + 1)，用于控制长度对格式计数的混淆影响。
    +1 避免除零，且不影响非零情况下的数量级。

    注：样本已解缠化，每对评价拆分为两条记录，配对数约为样本数的 1/2。

    参数说明：
    - df：优化后的数据框，需包含以下列：
        - winner: 评价结果
        - a_header_count, b_header_count: 标题数（dict 格式）
        - a_list_count, b_list_count: 列表数（dict 格式）
        - a_bold_count, b_bold_count: 粗体数（dict 格式）
        - a_tokens, b_tokens: 两模型输出 token 数
        - model_a, model_b: 两个模型的名称

    返回值：扩展后的数据框，包含格式特征、密度特征和胜负标签

    异常处理：
    - 若数据为空，返回空的 DataFrame
    - 若缺少必要列，会在运行时抛出 KeyError
    """
    print("准备格式特征数据...")

    # 1. 过滤掉"平局"评价，保留有明确胜负的评价
    win_df = df[~df['winner'].isin(['tie', 'both_bad'])].copy()
    original_rows = len(df)
    valid_rows = len(win_df)
    print(f"  原始行数: {original_rows} 条评价")
    print(f"  过滤平局后: {valid_rows} 条有效评价 (过滤率: {(1 - valid_rows/original_rows):.1%})")

    # 2. 提取格式计数（向量化，避免逐行 .iloc 循环）
    print("  提取格式特征...")
    a_header = win_df['a_header_count'].apply(extract_header_count)
    a_list   = win_df['a_list_count'].apply(extract_list_count)
    a_bold   = win_df['a_bold_count'].apply(extract_bold_count)

    b_header = win_df['b_header_count'].apply(extract_header_count)
    b_list   = win_df['b_list_count'].apply(extract_list_count)
    b_bold   = win_df['b_bold_count'].apply(extract_bold_count)

    # 3. 计算格式密度：count / (tokens + 1)，控制长度混淆
    a_tokens = win_df['a_tokens'].values
    b_tokens = win_df['b_tokens'].values

    a_header_density = a_header.values / (a_tokens + 1)
    a_list_density   = a_list.values   / (a_tokens + 1)
    a_bold_density   = a_bold.values   / (a_tokens + 1)

    b_header_density = b_header.values / (b_tokens + 1)
    b_list_density   = b_list.values   / (b_tokens + 1)
    b_bold_density   = b_bold.values   / (b_tokens + 1)

    # 4. 解缠化：构建模型 A 样本
    a_has_header = (a_header > 0)
    a_has_list   = (a_list   > 0)
    a_has_bold   = (a_bold   > 0)

    a_df = pd.DataFrame({
        'header_count': a_header.values,
        'list_count':   a_list.values,
        'bold_count':   a_bold.values,
        'has_header': a_has_header.values,
        'has_list':   a_has_list.values,
        'has_bold':   a_has_bold.values,
        'has_format': (a_has_header | a_has_list | a_has_bold).values,
        'total_format': (a_header + a_list + a_bold).values,
        'header_density': a_header_density,
        'list_density':   a_list_density,
        'bold_density':   a_bold_density,
        'is_winner': (win_df['winner'].values == 'model_a'),
        'model': win_df['model_a'].values
    })

    # 5. 解缠化：构建模型 B 样本（逻辑与 A 完全对称）
    b_has_header = (b_header > 0)
    b_has_list   = (b_list   > 0)
    b_has_bold   = (b_bold   > 0)

    b_df = pd.DataFrame({
        'header_count': b_header.values,
        'list_count':   b_list.values,
        'bold_count':   b_bold.values,
        'has_header': b_has_header.values,
        'has_list':   b_has_list.values,
        'has_bold':   b_has_bold.values,
        'has_format': (b_has_header | b_has_list | b_has_bold).values,
        'total_format': (b_header + b_list + b_bold).values,
        'header_density': b_header_density,
        'list_density':   b_list_density,
        'bold_density':   b_bold_density,
        'is_winner': (win_df['winner'].values == 'model_b'),
        'model': win_df['model_b'].values
    })

    # 6. 合并两个子集，完成解缠化
    format_data = pd.concat([a_df, b_df], ignore_index=True)
    print(f"  解缠化后总样本数: {len(format_data)} 个模型回答")

    return format_data



def analyze_format_density(format_data: pd.DataFrame,
                           n_bins: int = 20) -> Dict[str, pd.DataFrame]:
    """
    对三种格式密度特征分别进行分箱分析，输出密度–胜率关系。

    格式密度已在 prepare_format_data 中计算：density = count / (tokens + 1)。
    本函数将各密度列分成 n_bins 个等宽区间（1%–99% 范围），计算各箱胜率。

    参数说明：
    - format_data：包含 header_density / list_density / bold_density / is_winner 列的数据框
    - n_bins：分箱数量（默认 20）

    返回值：字典 {'header': df, 'list': df, 'bold': df}，每个 df 包含
      - bin_center, win_rate, sample_count, sample_proportion
    """
    print("分析格式密度特征...")
    density_stats: Dict[str, pd.DataFrame] = {}

    for feat in ['header', 'list', 'bold']:
        col = f'{feat}_density'
        series = format_data[col]

        lower = series.quantile(0.01)
        upper = series.quantile(0.99)

        # 若上下界几乎相等（特征基本为零），跳过该特征
        if upper - lower < 1e-9:
            print(f"  {col}: 范围过小，跳过分箱")
            density_stats[feat] = pd.DataFrame(
                columns=['bin_center', 'win_rate', 'sample_count', 'sample_proportion'])
            continue

        bins = np.linspace(lower, upper, n_bins + 1)
        fd = format_data.copy()
        fd['_bin'] = pd.cut(fd[col], bins=bins, include_lowest=True)

        stats = fd.groupby('_bin').agg(
            win_rate=('is_winner', 'mean'),
            sample_count=('is_winner', 'count'),
            bin_center=(col, 'mean')
        ).reset_index(drop=True)

        total = stats['sample_count'].sum()
        stats['sample_proportion'] = stats['sample_count'] / total
        density_stats[feat] = stats

        best_idx = stats['win_rate'].idxmax()
        print(f"  {col}: 最优密度中心值={stats.loc[best_idx, 'bin_center']:.4f}  "
              f"胜率={stats.loc[best_idx, 'win_rate']:.3f}")

    return density_stats


def analyze_format_presence(format_data: pd.DataFrame) -> pd.DataFrame:
    """
    分析格式存在性对胜率的影响。
    
    本函数计算有/无特定格式时的平均胜率，用于判断该格式是否对模型表现有帮助。
    
    分析维度：
    - has_format: 是否包含任何格式（标题、列表或粗体中的任意一种）
    - has_header: 是否包含标题
    - has_list: 是否包含列表
    - has_bold: 是否包含粗体
    
    对于每个维度，计算：
    - with_format_win_rate: 有该格式时的胜率
    - without_format_win_rate: 无该格式时的胜率
    - win_rate_diff: 两者之差（正值表示有该格式时表现更好）
    
    参数说明：
    - format_data：包含格式特征和is_winner列的数据框
    
    返回值：统计数据框，包含上述指标
    """
    print("分析 format_presence...")
    
    # 要分析的四种格式特征
    format_types = ['has_format', 'has_header', 'has_list', 'has_bold']
    
    results = []
    for format_type in format_types:
        # 【二分类分析逻辑】
        # 将样本按是否具有该格式分为两组，计算各组的平均胜率
        win_rate_with = format_data.loc[format_data[format_type], 'is_winner'].mean()
        win_rate_without = format_data.loc[~format_data[format_type], 'is_winner'].mean()
        
        # 计算样本数量（用于后续评估统计可信度）
        sum_with = format_data[format_type].sum()
        sum_without = len(format_data) - sum_with
        
        results.append({
            'format_type': format_type,
            'with_format_win_rate': win_rate_with,
            'without_format_win_rate': win_rate_without,
            'with_format_count': sum_with,
            'without_format_count': sum_without,
            'win_rate_diff': win_rate_with - win_rate_without
        })
    
    presence_df = pd.DataFrame(results)
    
    print("\n  格式存在性分析结果:")
    for _, row in presence_df.iterrows():
        print(f"    {row['format_type']}: "
              f"有格式={row['with_format_win_rate']:.3f} "
              f"无格式={row['without_format_win_rate']:.3f} "
              f"差异={row['win_rate_diff']:+.3f}")
    
    print("=" * 80)
    return presence_df



def analyze_count_feature(format_data: pd.DataFrame, 
                         feature_name: str,
                         min_sample_count: int = 200) -> Tuple[pd.DataFrame, float, float]:
    """
    通用的计数特征分析函数。
    
    本函数是对header_count、list_count、bold_count分析的统一实现，
    避免了三个函数的代码重复，提高了代码维护性。
    
    分析逻辑：
    1. 按feature_name的值进行分组
    2. 计算每组的胜率（is_winner均值）和样本数量
    3. 过滤掉样本量过少的分组（通常由异常值引起）
    4. 找到胜率最高的分组作为"最优值"
    
    参数说明：
    - format_data：包含格式特征列的数据框
    - feature_name：要分析的列名（如'header_count'、'list_count'、'bold_count'）
    - min_sample_count：样本数量阈值，低于此值的分组会被过滤（默认200）
                        这是为了避免样本不足造成的统计偏差
    
    返回值：(count_stats, best_count, best_win_rate)
      - count_stats：按feature_name分组的统计数据框
      - best_count：胜率最高的feature值
      - best_win_rate：该值对应的胜率
    
    使用场景：
    - analyze_header_count() 可改写为 analyze_count_feature('header_count')
    - analyze_list_count() 可改写为 analyze_count_feature('list_count')
    - analyze_bold_count() 可改写为 analyze_count_feature('bold_count')
    """
    print(f"分析 {feature_name}...")
    
    # ========================================================================
    # 第一步：按feature值分组，计算每组的胜率和样本统计
    # ========================================================================
    # groupby的agg方法一次性计算多个聚合统计（比循环append更高效）
    count_stats = format_data.groupby(feature_name).agg({
        'is_winner': ['mean', 'count'],  # mean用于计算胜率，count用于样本数
    }).reset_index()
    
    # 扁平化多级列名为单级（由groupby的agg产生）
    count_stats.columns = [feature_name, 'win_rate', 'sample_count']
    
    # ========================================================================
    # 第二步：计算样本占比，用于评估统计可信度
    # ========================================================================
    # 样本占比 = 该分组样本数 / 总样本数
    total_samples = count_stats['sample_count'].sum()
    count_stats['sample_proportion'] = count_stats['sample_count'] / total_samples
    
    # ========================================================================
    # 第三步：过滤掉样本量过少的分组
    # ========================================================================
    # 【为什么需要过滤】：
    # 样本少的分组胜率波动大，可能不代表真实趋势，而是随机波动
    # 例如：5个样本中恰好4个胜出，胜率80%，但这个结果不可靠
    original_groups = len(count_stats)
    count_stats = count_stats[count_stats['sample_count'] >= min_sample_count].copy()
    filtered_groups = len(count_stats)
    
    if filtered_groups < original_groups:
        print(f"  按样本数过滤: {original_groups}组 → {filtered_groups}组 (阈值: {min_sample_count})")
    
    # ========================================================================
    # 第四步：找到最优的feature值（胜率最高的分组）
    # ========================================================================
    if len(count_stats) == 0:
        # 若全部被过滤，返回None值以示错误
        print(f"  WARNING: 所有分组都因样本不足被过滤，无法进行分析")
        return count_stats, None, None
    
    best_idx = count_stats['win_rate'].idxmax()
    best_count = count_stats.loc[best_idx, feature_name]
    best_win_rate = count_stats.loc[best_idx, 'win_rate']
    
    # ========================================================================
    # 第五步：输出分析结果
    # ========================================================================
    print(f"  分析分组数: {len(count_stats)}")
    print(f"  总样本量: {total_samples:,}")
    print(f"  最优{feature_name}: {best_count}, win_rate: {best_win_rate:.3f}")
    print("=" * 80)
    
    # 返回三元组：统计数据框、最优特征值、对应胜率
    # 调用方通过解包 header_stats, best_count, best_win_rate = analyze_header_count(...) 使用
    return count_stats, best_count, best_win_rate


def analyze_header_count(format_data: pd.DataFrame, min_sample_count: int = 200) -> Tuple[pd.DataFrame, float, float]:
    """
    分析标题数（header_count）对胜率的影响。
    
    这是analyze_count_feature的特化版本，用于向后兼容。
    """
    return analyze_count_feature(format_data, 'header_count', min_sample_count)


def analyze_list_count(format_data: pd.DataFrame, min_sample_count: int = 1000) -> Tuple[pd.DataFrame, float, float]:
    """
    分析列表数（list_count）对胜率的影响。
    
    注意：list_sample的阈值调整为1000，因为列表分组比较稀疏。
    """
    return analyze_count_feature(format_data, 'list_count', min_sample_count)


def analyze_bold_count(format_data: pd.DataFrame, min_sample_count: int = 1000) -> Tuple[pd.DataFrame, float, float]:
    """
    分析粗体数（bold_count）对胜率的影响。
    
    注意：bold_count的阈值调整为1000，因为粗体分组比较稀疏。
    """
    return analyze_count_feature(format_data, 'bold_count', min_sample_count)



def analyze_format_combinations(format_data: pd.DataFrame) -> pd.DataFrame:
    """
    分析格式组合（多种格式的并集）对胜率的影响。
    
    格式组合分析的目标是找到最有效的格式搭配方式。
    
    分析逻辑：
    1. 定义8种互斥的格式组合（通过布尔组合）
    2. 为每个样本分配格式组合标签
    3. 按格式组合分组计算胜率
    4. 排序输出，以便识别最优组合
    
    8种互斥的格式组合：
    1. 仅有列表 (list & ~header & ~bold)
    2. 仅有标题 (~list & header & ~bold)
    3. 仅有粗体 (~list & ~header & bold)
    4. 列表+标题 (list & header & ~bold)
    5. 列表+粗体 (list & ~header & bold)
    6. 标题+粗体 (~list & header & bold)
    7. 三种都有 (list & header & bold)
    8. 无任何格式 (~list & ~header & ~bold)
    
    这8种组合涵盖了所有可能的情况（2^3 = 8），且彼此互不重叠。
    
    参数说明：
    - format_data：包含has_header、has_list、has_bold列的数据框
    
    返回值：统计数据框，按胜率从高到低排序
      - format_combination: 组合标签
      - win_rate: 该组合的平均胜率
      - sample_count: 样本数量
      - sample_proportion: 占比
    """
    print("分析 format_combination...")
    
    # ========================================================================
    # 第一步：定义8种互斥的格式组合条件
    # ========================================================================
    # 使用列表存储(条件, 标签)对，便于后续迭代处理
    conditions = [
        (format_data['has_list'] & ~format_data['has_header'] & ~format_data['has_bold'], 
         'with_list_only'),
        (~format_data['has_list'] & format_data['has_header'] & ~format_data['has_bold'], 
         'with_header_only'),
        (~format_data['has_list'] & ~format_data['has_header'] & format_data['has_bold'], 
         'with_bold_only'),
        (format_data['has_list'] & format_data['has_header'] & ~format_data['has_bold'], 
         'with_list_and_header'),
        (format_data['has_list'] & ~format_data['has_header'] & format_data['has_bold'], 
         'with_list_and_bold'),
        (~format_data['has_list'] & format_data['has_header'] & format_data['has_bold'], 
         'with_header_and_bold'),
        (format_data['has_list'] & format_data['has_header'] & format_data['has_bold'], 
         'with_all_three'),
        (~format_data['has_list'] & ~format_data['has_header'] & ~format_data['has_bold'], 
         'without_any_format')
    ]
    
    # ========================================================================
    # 第二步：为每个样本分配格式组合标签（使用 np.select 高效实现）
    # ========================================================================
    # 【为什么用 np.select 而非逐行 .loc[condition]】：
    # - 逐行 .loc 对大 DataFrame 需要多次全量扫描，会产生 SettingWithCopyWarning
    # - np.select 一次性向量化处理，速度更快，语义更清晰
    # - 注意：np.select 按列表顺序优先匹配第一个满足的条件
    conditions_list = [cond for cond, _ in conditions]
    labels_list     = [label for _, label in conditions]
    # default='unknown' 理论上不应触发（8 种互斥组合已覆盖全集）
    format_data_copy = format_data.copy()
    format_data_copy['format_combination'] = np.select(
        conditions_list, labels_list, default='unknown'
    )
    
    # ========================================================================
    # 第三步：按格式组合分组统计
    # ========================================================================
    combination_stats = format_data_copy.groupby('format_combination').agg({
        'is_winner': ['mean', 'count'],
    }).reset_index()
    
    # 扁平化列名
    combination_stats.columns = ['format_combination', 'win_rate', 'sample_count']
    
    # ========================================================================
    # 第四步：计算样本占比，用于评估数据代表性
    # ========================================================================
    total_samples = combination_stats['sample_count'].sum()
    combination_stats['sample_proportion'] = combination_stats['sample_count'] / total_samples
    
    # ========================================================================
    # 第五步：按胜率从高到低排序
    # ========================================================================
    # 这样便于识别最优的格式组合
    combination_stats = combination_stats.sort_values('win_rate', ascending=False)
    
    # ========================================================================
    # 第六步：输出分析结果
    # ========================================================================
    print(f"  分析分组数: {len(combination_stats)}")
    print("\n  格式组合 vs 胜率 排名:")
    for idx, row in combination_stats.iterrows():
        print(f"    {row['format_combination']:30s}: {row['win_rate']:.3f} "
              f"(n={row['sample_count']}, {row['sample_proportion']:.1%})")
    
    print("=" * 80)
    return combination_stats



# ========================================================================
# 绘图函数：生成格式偏好分析的可视化图表
# ========================================================================

def plot_presence_bar_chart(presence_df: pd.DataFrame, 
                           output_dir: Path | str | None = None) -> Path:
    """
    绘制格式存在性条形图。
    
    图表结构说明：
    - X轴：四种格式特征 (has_format, has_header, has_list, has_bold)
    - 左Y轴（红色）：有该格式时的胜率
    - 右Y轴（蓝色，已删除）：无该格式时的胜率
    - 使用并列条形比较，便于识别格式的有利程度
    
    图表元素说明：
    - 青色条形：有格式时的胜率（with_format_win_rate）
    - 红色条形：无格式时的胜率（without_format_win_rate）
    - X轴标签：四种格式类型
    - 网格线：便于读取精确数值
    
    设计理念：
    - 并列条形设计：直观对比两种情况的胜率差异
    - 颜色编码：便于区分（与C14保持一致）
    
    参数说明：
    - presence_df：格式存在性分析的统计数据框
    - output_dir：输出目录（默认为Pictures）
    
    返回值：保存的图表文件路径
    """
    print("绘制格式存在性条形图...")
    
    # 参数标准化：支持Path或str，默认使用Pictures目录
    if output_dir is None:
        output_dir = Path.cwd() / "Pictures"
    else:
        output_dir = Path(output_dir)
    
    # 前置检查：确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # 第一步：创建图表和轴对象
    # ========================================================================
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    
    # ========================================================================
    # 第二步：配置数据和位置
    # ========================================================================
    x = np.arange(len(presence_df))  # 标签的位置
    width = 0.35  # 条形宽度
    
    # ========================================================================
    # 第三步：绘制两组并列条形
    # ========================================================================
    # 有格式时的胜率（青色）
    bars_with = ax.bar(x - width/2, presence_df['with_format_win_rate'], width, 
                       label='with_format', color='#4ECDC4', alpha=0.9)
    # 无格式时的胜率（红色）
    bars_without = ax.bar(x + width/2, presence_df['without_format_win_rate'], width, 
                          label='without_format', color='#FF6B6B', alpha=0.9)
    
    # ========================================================================
    # 第三步（补充）：在每个条形顶部标注精确的胜率数值
    # ========================================================================
    # 标注可以帮助读者直接读数，无需对照Y轴刻度
    for bar in bars_with:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.003,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10,
                color='#007A73', fontweight='bold')
    
    for bar in bars_without:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.003,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10,
                color='#CC2200', fontweight='bold')
    
    # ========================================================================
    # 第四步：配置轴标签和标题
    # ========================================================================
    ax.set_xlabel('format_type', fontsize=14, fontweight='bold')
    ax.set_ylabel('win_rate', fontsize=14, fontweight='bold')
    ax.set_title("Format Preference Analysis - Format Presence vs Win Rate", 
                 fontsize=18, fontweight='bold')
    
    # ========================================================================
    # 第五步：配置X轴刻度和标签
    # ========================================================================
    ax.set_xticks(x)
    ax.set_xticklabels(presence_df['format_type'], fontsize=12)
    
    # ========================================================================
    # 第六步：配置网格和图例
    # ========================================================================
    ax.grid(True, linestyle='--', linewidth=1, alpha=0.6, color="#FF8888", axis='y')
    ax.legend(fontsize=12, loc='upper right')
    
    # ========================================================================
    # 第七步：保存和关闭
    # ========================================================================
    plt.tight_layout()
    
    chart_path = output_dir / "P06_format_presence_bar_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  已保存至: {chart_path}")
    print("=" * 80)
    
    return chart_path



def plot_count_feature_line_chart(count_stats: pd.DataFrame, 
                                 feature_name: str,
                                 best_count: float,
                                 best_win_rate: float,
                                 output_dir: Path | str | None = None,
                                 output_filename: str | None = None) -> Path:
    """
    通用的计数特征折线图绘制函数。
    
    本函数是对plot_header_count_line_chart、plot_list_count_line_chart、
    plot_bold_count_line_chart的统一实现，避免了大量代码重复。
    
    图表结构说明：
    - 左轴（Y1，红色）：模型的胜率 win_rate，范围[0.3, 0.7]
    - 右轴（Y2，青色）：样本占比 sample_proportion，范围[0, max*1.1]
    - X轴：计数特征的值（如标题数、列表数、粗体数）
    
    图表元素说明：
    - 红色折线 + 圆点：胜率曲线
    - 青色虚线 + 方点：样本占比曲线
    - 黄色竖线：最优值位置
    - 黄色星形标记：最优点
    - 红色曲线：二次多项式拟合的趋势线
    - 注释文本框：标注最优点的具体数值
    
    设计理念：
    - 双轴设计：同时展示胜率趋势和样本分布
    - 样本占比帮助判断结果的统计可信度
      * 样本多的位置: 统计结果更稳定
      * 样本少的位置: 结果可能由于样本不足而波动
    - 趋势线：反映整体的二阶非线性关系
    
    参数说明：
    - count_stats：计数特征分组后的统计数据框
    - feature_name：特征名称（如'header_count'、'list_count'、'bold_count'）
    - best_count：最优的特征值
    - best_win_rate：最优值对应的胜率
    - output_dir：输出目录（默认为Pictures）
    - output_filename：输出文件名（默认根据feature_name自动生成）
    
    返回值：保存的图表文件路径
    """
    print(f"绘制 {feature_name} 折线图...")
    
    # ========================================================================
    # 第一步：参数标准化、目录准备和边界条件检查
    # ========================================================================
    if output_dir is None:
        output_dir = Path.cwd() / "Pictures"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 若未指定输出文件名，按约定自动生成
    if output_filename is None:
        # 映射关系：header_count -> P07, list_count -> P08, bold_count -> P09
        name_map = {
            'header_count': 'P07_header_count_line_chart.png',
            'list_count': 'P08_list_count_line_chart.png',
            'bold_count': 'P09_bold_count_line_chart.png'
        }
        output_filename = name_map.get(feature_name, f'P__{feature_name}_line_chart.png')
    
    # 【防护：数据不足时提前退出】
    # 若所有分组均被样本过滤掉（count_stats 为空），无法绘图，直接返回 None
    if len(count_stats) == 0:
        print(f"  WARNING: {feature_name} 数据为空，跳过绘图")
        return None
    
    # 【防护：最优值为 None 时降级处理】
    # 当 analyze_count_feature 因全部过滤而无法找到最优值时，
    # 传入的 best_count/best_win_rate 会是 None，此时只绘制折线，跳过最优点标注
    has_best = (best_count is not None) and (best_win_rate is not None)
    
    # ========================================================================
    # 第二步：创建图表和双轴对象
    # ========================================================================
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # ========================================================================
    # 第三步：配置左轴（Y1，红色，胜率）
    # ========================================================================
    color1 = '#FF6B6B'  # 红色，代表胜率
    
    # 设置X轴标签和范围
    ax1.set_xlabel(feature_name, fontsize=14, fontweight='bold')
    
    # 设置左Y轴：胜率
    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    # 使用百分比格式化Y轴标签
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
    
    # 绘制胜率折线：红色折线，白色圆点标记
    ax1.plot(count_stats[feature_name], count_stats['win_rate'], 
             color=color1, marker='o', linewidth=3, markersize=8,
             label='win_rate', markerfacecolor='white', markeredgewidth=2)
    
    # ========================================================================
    # 第四步：配置右轴（Y2，青色，样本占比）
    # ========================================================================
    color2 = '#4ECDC4'  # 青色，代表样本分布
    
    ax2 = ax1.twinx()  # 创建共享x轴的右轴
    
    # 设置右Y轴：样本占比
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
    
    # 绘制样本占比曲线：虚线，方点标记
    ax2.plot(count_stats[feature_name], count_stats['sample_proportion'], 
             color=color2, marker='s', linestyle='--', linewidth=3, markersize=8,
             label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    
    # ========================================================================
    # 第五步：标注最优点（仅在 best_count/best_win_rate 有效时执行）
    # ========================================================================
    if has_best:
        # 在最优点处绘制星形标记（黄色）
        ax1.plot(best_count, best_win_rate, 'r*', color='#FFD166', markersize=18, 
                 label='best_spot')
        
        # ——根据最优点的位置动态决定注释文本框的位置——
        # 若最优值在 X 轴左 60% 范围内，注释偏右；否则偏左，以避免遮挡折线
        x_min = count_stats[feature_name].min()
        x_max = count_stats[feature_name].max()
        x_range = x_max - x_min if x_max > x_min else 1
        rel_pos = (best_count - x_min) / x_range  # 相对位置 [0, 1]
        
        if rel_pos < 0.6:
            # 最优点在左侧，文字标注放右边
            text_x = best_count + x_range * 0.2
        else:
            # 最优点在右侧，文字标注放左边
            text_x = best_count - x_range * 0.3
        text_y = best_win_rate * 0.72  # 稍低于最优点
        
        annotation_text = f"best_spot\n{feature_name}: {best_count}\nwin_rate: {best_win_rate:.2%}"
        
        ax1.annotate(annotation_text, 
                     xy=(best_count, best_win_rate), 
                     xytext=(text_x, text_y),
                     arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                     fontsize=12, ha='center', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))
    
    # ========================================================================
    # 第六步：添加趋势线（二次多项式拟合）
    # ========================================================================
    # 二次多项式能捕捉非线性的倒U形或U形关系
    # 【防护】：polyfit 至少需要 3 个数据点才能拟合二次多项式，否则跳过
    if len(count_stats) >= 3:
        z = np.polyfit(count_stats[feature_name], count_stats['win_rate'], 2)
        p = np.poly1d(z)
        x_smooth = np.linspace(count_stats[feature_name].min(), 
                              count_stats[feature_name].max(), 100)
        ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')
    
    # ========================================================================
    # 第七步：配置图例和标题
    # ========================================================================
    # 左轴的图例
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=12)
    
    # 右轴的图例
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=12)
    
    # 图表标题
    title = f"Format Preference Analysis - {feature_name} vs Win Rate & Sample Proportion"
    ax1.set_title(title, fontsize=16, fontweight='bold')
    
    # ========================================================================
    # 第八步：配置网格线
    # ========================================================================
    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color="#FF8888")
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color="#AED1FF")
    
    # ========================================================================
    # 第九步：保存和关闭
    # ========================================================================
    plt.tight_layout()
    
    chart_path = output_dir / output_filename
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  已保存至: {chart_path}")
    print("=" * 80)
    
    return chart_path


def plot_header_count_line_chart(header_stats: pd.DataFrame, 
                                best_header_count: float,
                                best_header_win_rate: float, 
                                output_dir: Path | str | None = None) -> Path:
    """
    绘制标题数（header_count）折线图。
    
    这是plot_count_feature_line_chart的特化版本，用于向后兼容。
    """
    return plot_count_feature_line_chart(header_stats, 'header_count',
                                        best_header_count, best_header_win_rate,
                                        output_dir, 'P07_header_count_line_chart.png')


def plot_list_count_line_chart(list_stats: pd.DataFrame, 
                              best_list_count: float,
                              best_list_win_rate: float, 
                              output_dir: Path | str | None = None) -> Path:
    """
    绘制列表数（list_count）折线图。
    
    这是plot_count_feature_line_chart的特化版本，用于向后兼容。
    """
    return plot_count_feature_line_chart(list_stats, 'list_count',
                                        best_list_count, best_list_win_rate,
                                        output_dir, 'P08_list_count_line_chart.png')


def plot_bold_count_line_chart(bold_stats: pd.DataFrame, 
                              best_bold_count: float,
                              best_bold_win_rate: float, 
                              output_dir: Path | str | None = None) -> Path:
    """
    绘制粗体数（bold_count）折线图。
    
    这是plot_count_feature_line_chart的特化版本，用于向后兼容。
    """
    return plot_count_feature_line_chart(bold_stats, 'bold_count',
                                        best_bold_count, best_bold_win_rate,
                                        output_dir, 'P09_bold_count_line_chart.png')



def plot_combination_bar_chart(combination_stats: pd.DataFrame, 
                              output_dir: Path | str | None = None) -> Path:
    """
    绘制格式组合条形图。
    
    图表结构说明：
    - X轴：8种格式组合（按胜率从高到低排序）
    - Y轴：该组合的平均胜率
    - 条形颜色：使用color bar，从黄到红渐变，反映胜率的高低
    - 条形标签：在顶部显示精确胜率和样本数
    
    图表元素说明：
    - 条形颜色：黄->橙->红渐变，黄色表示高胜率，红色表示低胜率
    - X轴标签：各种格式组合（字体旋转45度便于阅读）
    - 条形顶部标注：显示精确的胜率和样本数量
    - 网格线：仅Y轴方向，便于读取数值
    
    设计理念：
    - 颜色编码：直观反映胜率的相对大小
    - 样本数标注：提醒用户某些组合可能样本不足
    - 排序设计：从高到低排序，便于识别"最佳实践"
    
    参数说明：
    - combination_stats：格式组合分析的统计数据框
    - output_dir：输出目录（默认为Pictures）
    
    返回值：保存的图表文件路径
    """
    print("绘制格式组合条形图...")
    
    # 参数标准化：支持Path或str，默认使用Pictures目录
    if output_dir is None:
        output_dir = Path.cwd() / "Pictures"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # 第一步：选择前8个组合（如果有）
    # ========================================================================
    # 通常有8种互斥的组合，全部显示；若数据不足，显示可用的
    display_stats = combination_stats.head(8).copy()
    
    # ========================================================================
    # 第二步：创建图表对象
    # ========================================================================
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # ========================================================================
    # 第三步：绘制条形图，使用color bar进行胜率编码
    # ========================================================================
    # YlOrRd色盘：Yellow -> Orange -> Red，黄色表示高胜率，红色表示低胜率
    bars = ax.bar(range(len(display_stats)), display_stats['win_rate'], 
                  color=plt.cm.YlOrRd(display_stats['win_rate'] / display_stats['win_rate'].max()))
    
    # ========================================================================
    # 第四步：配置坐标轴标签和标题
    # ========================================================================
    ax.set_xlabel('format_combination', fontsize=12, fontweight='bold')
    ax.set_ylabel('win_rate', fontsize=12, fontweight='bold')
    ax.set_title("Format Preference Analysis - Format Combination vs Win Rate", 
                 fontsize=14, fontweight='bold')
    
    # ========================================================================
    # 第五步：配置X轴刻度和标签
    # ========================================================================
    ax.set_xticks(range(len(display_stats)))
    # 旋转45度，向右对齐，便于长标签的阅读
    ax.set_xticklabels(display_stats['format_combination'], rotation=45, ha='right', fontsize=10)
    
    # ========================================================================
    # 第六步：配置网格线
    # ========================================================================
    ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    
    # ========================================================================
    # 第七步：在条形顶部添加数值标注
    # ========================================================================
    # 标注包含：胜率（百分比）和样本数量，帮助用户理解数据
    for i, (bar, row) in enumerate(zip(bars, display_stats.itertuples())):
        height = bar.get_height()  # 条形高度（胜率）
        # 在条形顶部上方显示标注
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                f'{height:.3f}\n(n={int(row.sample_count)})',
                ha='center', va='bottom', fontsize=9)
    
    # ========================================================================
    # 第八步：保存和关闭
    # ========================================================================
    plt.tight_layout()
    
    chart_path = output_dir / "P10_format_combination_bar_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  已保存至: {chart_path}")
    print("=" * 80)
    
    return chart_path



def create_summary_tables(format_data: pd.DataFrame, 
                         presence_df: pd.DataFrame,
                         header_stats: pd.DataFrame,
                         list_stats: pd.DataFrame,
                         bold_stats: pd.DataFrame,
                         combination_stats: pd.DataFrame,
                         output_dir: Path | str | None = None) -> Path:
    """
    创建并保存格式分析的统计表格为CSV文件。
    
    本函数将各个分析阶段的结果导出为格式化的CSV表格，便于后续的报告生成和数据分析。
    
    生成的CSV文件说明：
    - T03_basic_statistics.csv：基本统计信息
      * 各格式特征的描述性统计（均值、标准差、最小值等）
    - T04_format_presence_analysis.csv：格式存在性分析
      * 有/无各种格式时的胜率对比
    - T05_header_count_analysis.csv：标题数分析
      * 不同标题数范围内的胜率分布
    - T06_list_count_analysis.csv：列表数分析
      * 不同列表数范围内的胜率分布
    - T07_bold_count_analysis.csv：粗体数分析
      * 不同粗体数范围内的胜率分布
    - T08_format_combination_analysis.csv：格式组合分析
      * 各种格式组合的胜率排名
    
    参数说明：
    - format_data：基础格式数据（用于计算基本统计）
    - presence_df：格式存在性分析结果
    - header_stats：标题数分析结果
    - list_stats：列表数分析结果
    - bold_stats：粗体数分析结果
    - combination_stats：格式组合分析结果
    - output_dir：输出目录（默认为Tables）
    
    返回值：基本统计表格的保存路径
    
    异常处理：
    - 若output_dir不存在，自动创建
    - 对于空的DataFrames，会输出空的CSV
    """
    print("创建统计表格...")
    
    # 参数标准化：支持Path或str，默认使用Tables目录
    if output_dir is None:
        output_dir = Path.cwd() / "Tables"
    else:
        output_dir = Path(output_dir)
    
    # 前置检查：确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # 第一步：生成基本统计表（描述性统计）
    # ========================================================================
    # 对关键的数值列进行描述性统计（均值、标准差、分位数等）
    basic_stats = format_data[['list_count', 'header_count', 'bold_count', 'total_format']].describe()
    basic_stats_path = output_dir / "T03_basic_statistics.csv"
    basic_stats.to_csv(basic_stats_path, encoding='utf-8-sig')
    print(f"  已保存: T03_basic_statistics.csv")
    
    # ========================================================================
    # 第二步：保存格式存在性分析表
    # ========================================================================
    # 包含：有/无格式时的胜率、样本数、占比等
    presence_path = output_dir / "T04_format_presence_analysis.csv"
    presence_df.to_csv(presence_path, index=False, encoding='utf-8-sig')
    print(f"  已保存: T04_format_presence_analysis.csv")
    
    # ========================================================================
    # 第三步：保存标题数分析表（如果非空）
    # ========================================================================
    if len(header_stats) > 0:
        header_path = output_dir / "T05_header_count_analysis.csv"
        header_stats.to_csv(header_path, index=False, encoding='utf-8-sig')
        print(f"  已保存: T05_header_count_analysis.csv")
    
    # ========================================================================
    # 第四步：保存列表数分析表（如果非空）
    # ========================================================================
    if len(list_stats) > 0:
        list_path = output_dir / "T06_list_count_analysis.csv"
        list_stats.to_csv(list_path, index=False, encoding='utf-8-sig')
        print(f"  已保存: T06_list_count_analysis.csv")
    
    # ========================================================================
    # 第五步：保存粗体数分析表（如果非空）
    # ========================================================================
    if len(bold_stats) > 0:
        bold_path = output_dir / "T07_bold_count_analysis.csv"
        bold_stats.to_csv(bold_path, index=False, encoding='utf-8-sig')
        print(f"  已保存: T07_bold_count_analysis.csv")
    
    # ========================================================================
    # 第六步：保存格式组合分析表（如果非空）
    # ========================================================================
    if len(combination_stats) > 0:
        combo_path = output_dir / "T08_format_combination_analysis.csv"
        combination_stats.to_csv(combo_path, index=False, encoding='utf-8-sig')
        print(f"  已保存: T08_format_combination_analysis.csv")
    
    print(f"所有统计表格已保存到: {output_dir}")
    print("=" * 80)
    
    return basic_stats_path



def generate_analysis_report(format_data: pd.DataFrame,
                             presence_df: pd.DataFrame,
                             header_stats: pd.DataFrame,
                             list_stats: pd.DataFrame,
                             bold_stats: pd.DataFrame,
                             combination_stats: pd.DataFrame,
                             best_header_count: float,
                             best_header_win_rate: float,
                             best_list_count: float,
                             best_list_win_rate: float,
                             best_bold_count: float,
                             best_bold_win_rate: float,
                             density_stats: Dict[str, pd.DataFrame] | None = None,
                             output_dir: Path | str | None = None,
                             mode: str = "w",
                             section_tag: str = "全量数据") -> Path:
    """
    生成格式偏好分析的完整报告，支持以追加模式写入子集结论。

    参数说明：
    - format_data：基础格式数据（用于计算总样本数）
    - presence_df：格式存在性分析结果
    - header_stats / list_stats / bold_stats：各计数特征分析结果
    - combination_stats：格式组合分析结果
    - best_*_count / best_*_win_rate：各维度的最优值和胜率
    - density_stats：格式密度分箱统计（dict，key 为 'header'/'list'/'bold'；可为 None）
    - output_dir：输出目录（默认为 Reports）
    - mode：文件写入模式，'w' 为覆写，'a' 为追加（默认 'w'）
    - section_tag：当前分析集名称，用于报告标题区分（默认"全量数据"）

    返回值：保存的报告文件路径
    """
    print(f"生成分析报告（{section_tag}）...")

    if output_dir is None:
        output_dir = Path.cwd() / "Reports"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "R12_format_preference_report.txt"

    with open(report_path, mode, encoding='utf-8') as f:

        # 1. 分析概况
        f.write("=" * 80 + "\n")
        f.write(f"格式偏好分析报告 — {section_tag}\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 分析概况\n")
        f.write(f"   分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"   总样本数（解缠化后）: {len(format_data):,}\n")
        f.write(f"   对应原始配对数（约）: {len(format_data) // 2:,}\n")
        f.write("   注：样本已解缠化，每对评价拆分为两条记录，配对数约为样本数的 1/2。\n")
        f.write(f"   有任何格式的样本占比: {format_data['has_format'].mean():.2%}\n")
        f.write(f"   有标题: {format_data['has_header'].mean():.2%}  "
                f"有列表: {format_data['has_list'].mean():.2%}  "
                f"有粗体: {format_data['has_bold'].mean():.2%}\n\n")

        # 2. 格式存在性分析
        f.write("2. 格式存在性分析\n")
        for _, row in presence_df.iterrows():
            diff_label = ("有该格式时显著更优" if row['win_rate_diff'] > 0.01
                          else "无该格式时显著更优" if row['win_rate_diff'] < -0.01
                          else "影响不显著")
            f.write(f"   {row['format_type']}: "
                    f"有={row['with_format_win_rate']:.3f} (n={int(row['with_format_count'])})  "
                    f"无={row['without_format_win_rate']:.3f} (n={int(row['without_format_count'])})  "
                    f"差={row['win_rate_diff']:+.3f}  [{diff_label}]\n")
        f.write("\n")

        # 3. 计数特征分析
        f.write("3. 计数特征最优值\n")
        for name, best_c, best_wr in [
            ("header_count", best_header_count, best_header_win_rate),
            ("list_count",   best_list_count,   best_list_win_rate),
            ("bold_count",   best_bold_count,   best_bold_win_rate),
        ]:
            if best_c is not None:
                f.write(f"   最优 {name}: {int(best_c)}  胜率: {best_wr:.3f}\n")
            else:
                f.write(f"   {name}: 数据不足\n")
        f.write("\n")

        # 4. 格式密度分析
        f.write("4. 格式密度分析\n")
        f.write("   注：格式计数效应可能含长度混淆，详见 R14 格式密度辅助检验。\n")
        if density_stats:
            for feat in ['header', 'list', 'bold']:
                stats = density_stats.get(feat, pd.DataFrame())
                if stats.empty:
                    f.write(f"   {feat}_density: 数据不足\n")
                    continue
                best_idx = stats['win_rate'].idxmax()
                f.write(f"   {feat}_density 最优中心值: "
                        f"{stats.loc[best_idx, 'bin_center']:.4f}  "
                        f"胜率: {stats.loc[best_idx, 'win_rate']:.3f}  "
                        f"(n={int(stats.loc[best_idx, 'sample_count'])})\n")
        else:
            f.write("   （本次未计算密度统计）\n")
        f.write("\n")

        # 5. 格式组合分析
        f.write("5. 格式组合排名（Top-5）\n")
        top5 = combination_stats.head(5)
        for rank, (_, row) in enumerate(top5.iterrows(), 1):
            f.write(f"   {rank}. {row['format_combination']:30s}  "
                    f"胜率: {row['win_rate']:.3f}  "
                    f"n={int(row['sample_count'])} ({row['sample_proportion']:.1%})\n")
        f.write("\n")

    print(f"  分析报告写入: {report_path}")
    return report_path



if __name__ == "__main__":
    print("=" * 80)
    print("格式偏好可视化分析")
    print("=" * 80)

    # 1. 初始化路径
    data_file_path = get_optimized_parquet_path()
    charts_dir  = Path.cwd() / "Pictures"
    reports_dir = Path.cwd() / "Reports"
    tables_dir  = Path.cwd() / "Tables"
    for d in (charts_dir, reports_dir, tables_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 2. 加载数据
    # 检查输入文件是否存在
    if not data_file_path.exists():
        print(f"ERROR: 输入文件不存在 - {data_file_path}")
        print("请确保已运行 C12_optimize_data.py 生成优化数据")
        exit(1)

    try:
        df = pd.read_parquet(data_file_path)
        print(f"  数据加载成功，形状: {df.shape[0]:,} × {df.shape[1]}")
    except Exception as exc:
        print(f"ERROR: 数据加载失败 - {exc}")
        exit(1)

    # 1. 全量分析
    print("\n" + "-" * 40)
    print("1. 全量数据分析")
    print("-" * 40)

    format_data = prepare_format_data(df)

    # 1.1 缓存解缠化结果
    format_data_path = get_format_data_path()
    format_data_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        format_data.to_parquet(format_data_path, index=False)
        print(f"  格式数据缓存已保存: {format_data_path}")
    except Exception as e:
        print(f"  WARNING: 缓存保存失败 - {e}")

    # 1.2 存在性分析
    presence_df = analyze_format_presence(format_data)

    # 1.3 计数特征分析
    header_stats, best_header_count, best_header_win_rate = analyze_header_count(format_data)
    list_stats, best_list_count, best_list_win_rate = analyze_list_count(format_data)
    bold_stats, best_bold_count, best_bold_win_rate = analyze_bold_count(format_data)

    # 1.4 组合分析
    combination_stats = analyze_format_combinations(format_data)

    # 1.5 密度分析
    density_stats = analyze_format_density(format_data)

    # 1.6 可视化
    plot_presence_bar_chart(presence_df, charts_dir)
    plot_header_count_line_chart(header_stats, best_header_count, best_header_win_rate, charts_dir)
    plot_list_count_line_chart(list_stats, best_list_count, best_list_win_rate, charts_dir)
    plot_bold_count_line_chart(bold_stats, best_bold_count, best_bold_win_rate, charts_dir)
    plot_combination_bar_chart(combination_stats, charts_dir)

    # 1.7 统计表格
    create_summary_tables(format_data, presence_df, header_stats,
                          list_stats, bold_stats, combination_stats, tables_dir)

    # 1.8 报告（首次写入，覆写模式）
    generate_analysis_report(
        format_data, presence_df, header_stats, list_stats, bold_stats,
        combination_stats, best_header_count, best_header_win_rate,
        best_list_count, best_list_win_rate, best_bold_count, best_bold_win_rate,
        density_stats=density_stats, output_dir=reports_dir,
        mode="w", section_tag="全量数据"
    )

    # 2. 分层子集分析（仅存在性 + 密度，计数特征因样本量有限仅供参考）
    subset_configs = [
        ("creative_writing_true_data.parquet", "CW（创意写作）"),
        ("if_true_data.parquet",              "IF（指令跟随）"),
        ("math_true_data.parquet",            "MATH（数学）"),
        ("code_true_data.parquet",            "CODE（代码）"),
    ]
    subset_dir = Path.cwd() / "Data" / "optimized_data"

    for filename, tag in subset_configs:
        subset_path = subset_dir / filename
        if not subset_path.exists():
            print(f"\n  WARNING: 子集文件不存在，跳过 {filename}")
            continue

        print(f"\n{'-' * 40}")
        print(f"2. 分层分析 — {tag}")
        print(f"{'-' * 40}")

        df_sub = pd.read_parquet(subset_path)
        print(f"  子集形状: {df_sub.shape}")

        format_data_sub = prepare_format_data(df_sub)
        presence_sub = analyze_format_presence(format_data_sub)
        header_sub, best_h_sub, best_h_wr_sub = analyze_header_count(format_data_sub)
        list_sub,   best_l_sub, best_l_wr_sub = analyze_list_count(format_data_sub)
        bold_sub,   best_b_sub, best_b_wr_sub = analyze_bold_count(format_data_sub)
        combo_sub = analyze_format_combinations(format_data_sub)
        density_sub = analyze_format_density(format_data_sub)

        # 追加写入同一报告
        generate_analysis_report(
            format_data_sub, presence_sub, header_sub, list_sub, bold_sub,
            combo_sub, best_h_sub, best_h_wr_sub,
            best_l_sub, best_l_wr_sub, best_b_sub, best_b_wr_sub,
            density_stats=density_sub, output_dir=reports_dir,
            mode="a", section_tag=tag
        )

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)