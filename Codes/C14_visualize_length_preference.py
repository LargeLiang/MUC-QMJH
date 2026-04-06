"""
长度偏好可视化分析脚本

本脚本对AI模型的输出长度偏好进行全面的可视化分析，包括：
- 长度比率分析：模型输出长度 / 用户输入长度的比率与胜率的关系
- 长度差值分析：两个模型输出长度差值与胜率的关系
- 趋势识别：通过多项式拟合识别最优长度区间
- 统计报告：生成详细的统计表格和分析报告

数据流向：
  optimized_data.parquet → 长度特征计算 → 分箱分析 → 可视化 → 报告生成
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

# 路径管理函数：集中管理项目中的文件和目录路径

def get_optimized_parquet_path(root: Path | str | None = None) -> Path:
    """返回优化数据 parquet 文件的默认路径。"""
    
    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root = Path.cwd()
    else:
        root = Path(root)
    
    # 优化数据文件位于项目根目录下的 Data/optimized_data/optimized_data.parquet
    return root / "Data" / "optimized_data" / "optimized_data.parquet"


def get_length_data_path(root: Path | str | None = None) -> Path:
    """
    返回长度数据 parquet 文件的默认路径。
    
    此路径用于存储预处理后的长度特征数据，可用于后续快速分析。
    """
    if root is None:
        root = Path.cwd()
    else:
        root = Path(root)
    
    return root / "Data" / "length_data" / "length_data.parquet"

def prepare_length_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    从优化数据中提取和计算长度特征。
    
    本函数执行以下关键步骤：
    1. 过滤掉平局评价（'tie' 或 'both_bad'）
    2. 计算长度比率 = 模型输出tokens / 用户输入tokens
    3. 计算长度差值 = 模型A输出 - 模型B输出
    4. 对数据进行"解缠化"处理：将模型对比转换为单模型样本
    
    解缠化逻辑说明：
    - 将每一行评价拆分为两个单模型样本（模型A和模型B）
    - 每个样本记录该模型是否胜出（is_winner）
    - 这样可以用单维度分析代替复杂的配对分析

    参数：
    - df：优化后的数据框，需包含以下列：
        - winner: 评价结果
        - a_tokens, b_tokens: 两个模型的输出token数
        - user_tokens: 用户输入token数
        - model_a, model_b: 两个模型的名称

    返回值：扩展后的数据框，包含长度特征和胜负标签
    
    异常处理：
    - 若数据为空，返回空的DataFrame
    - 若缺少必要列，会在运行时抛出KeyError
    """
    print("准备长度特征数据...")
    
    # 1. 过滤掉"平局"评价，保留有明确胜负的评价
    win_df = df[~df['winner'].isin(['tie', 'both_bad'])].copy()
    original_rows = len(df)
    valid_rows = len(win_df)
    print(f"  原始行数: {original_rows} 条评价")
    print(f"  过滤平局后: {valid_rows} 条有效评价 (过滤率: {(1 - valid_rows/original_rows):.1%})")

    # 2. 计算长度比率（相对长度）
    # 长度比率 = 模型输出长度 / 用户输入长度
    print("  计算长度比率 = 模型输出tokens / 用户输入tokens")
    win_df['a_length_ratio'] = win_df['a_tokens'] / win_df['user_tokens']
    win_df['b_length_ratio'] = win_df['b_tokens'] / win_df['user_tokens']
    
    # 3. 计算长度差值（绝对长度）
    # 长度差值 = 模型A长度 - 模型B长度
    # 正值表示模型A更冗长，负值表示模型B更冗长
    print("  计算长度差值 = a_tokens - b_tokens (正值表示A更长)")
    win_df['length_diff'] = win_df['a_tokens'] - win_df['b_tokens']

    # 4. 解缠化处理 - 从配对评价转换为单模型样本
    # 模型A的样本
    a_data = win_df[['a_length_ratio']].copy()
    a_data['length_diff'] = win_df['length_diff']
    a_data['is_winner'] = (win_df['winner'] == 'model_a').astype(bool)
    a_data = a_data.rename(columns={'a_length_ratio': 'length_ratio'})
    a_data['model'] = win_df['model_a']
    
    # 模型B的样本
    # 注意：长度差值符号反转（-length_diff），因为从B的视角，差异反向
    b_data = win_df[['b_length_ratio']].copy()
    b_data['length_diff'] = - win_df['length_diff']
    b_data['is_winner'] = (win_df['winner'] == 'model_b').astype(bool)
    b_data = b_data.rename(columns={'b_length_ratio': 'length_ratio'})
    b_data['model'] = win_df['model_b']
    
    # 合并两个数据集
    length_data = pd.concat([a_data, b_data], ignore_index=True)
    print(f"  解缠化后总样本数: {len(length_data)} 个模型回答")
    print("=" * 80)

    return length_data

def create_length_ratio_bins(length_data: pd.DataFrame, n_bins: int = 20) -> pd.DataFrame:
    """
    按长度比率进行分箱分析。
    
    本函数使用等宽分箱方法，将长度比率分成n_bins个区间，
    然后计算每个区间的胜率和样本比例。
    
    分箱策略说明：
    - 使用99%分位数作为上界（过滤异常值）
    - 从0到max_ratio之间均匀划分
    - 计算每个分箱内的平均胜率和样本占比
    
    这种分箱方法的优点：
    - 简单直观，便于解释
    - 避免异常值对分析的影响
    - 保留足够的样本量进行统计

    参数：
    - length_data：包含length_ratio和is_winner列的数据框
    - n_bins：分箱数量（默认20）

    返回值：统计数据框，包含：
      - ratio_bin: 分箱区间
      - win_rate: 该分箱内的模型胜率
      - sample_count: 样本数量
      - avg_ratio: 分箱内的平均长度比率
      - sample_proportion: 样本占比
    """
    print(f"创建长度比率分箱 (n_bins={n_bins})...")
    
    # 使用99%分位数作为边界，过滤极端异常的长度比率
    max_ratio = length_data['length_ratio'].quantile(0.99)
    print(f"  长度比率范围: [0.00, {max_ratio:.2f}] (99%分位数)")
    
    # 创建等宽分箱：从0到max_ratio均匀划分成n_bins个区间
    bins = np.linspace(0, max_ratio, n_bins + 1)
    length_data['ratio_bin'] = pd.cut(length_data['length_ratio'], bins=bins, include_lowest=True)

    # 按分箱统计：计算每个分箱的是_winner均值（即胜率）、样本数、平均长度比率
    ratio_bin_stats = length_data.groupby('ratio_bin').agg({
        'is_winner': ['mean', 'count'],
        'length_ratio': 'mean'
    }).reset_index()

    # 简化列名：['ratio_bin', 'win_rate', 'sample_count', 'avg_ratio']
    ratio_bin_stats.columns = ['ratio_bin', 'win_rate', 'sample_count', 'avg_ratio']

    # 计算样本占比：用于评估每个分箱的统计可信度
    total_samples = ratio_bin_stats['sample_count'].sum()
    ratio_bin_stats['sample_proportion'] = ratio_bin_stats['sample_count'] / total_samples
    
    print(f"  分箱数量: {len(ratio_bin_stats)} 个")
    print(f"  总样本量: {total_samples:,} 个")
    print(f"  平均每个分箱: {total_samples / len(ratio_bin_stats):.0f} 个样本")
    print("=" * 80)
    
    return ratio_bin_stats

def create_length_diff_bins(length_data: pd.DataFrame, n_bins: int = 20) -> pd.DataFrame:
    """
    按长度差值进行分箱分析。
    
    本函数使用稳健的分位数估计法进行分箱，避免极端值的影响。
    
    分箱策略说明：
    - 使用1%-99%分位数范围作为分箱区间
    - 使用1%-99%范围而非最小最大值，自动过滤极端异常值
    - 在该范围内分成n_bins个等宽区间
    - 超出范围的值被划入最近的分箱
    
    这种方法的好处：
    - 更能反映主要样本的特征
    - 自动过滤数据错误和极端异常
    - 分箱更加均衡，利于统计

    参数：
    - length_data：包含length_diff和is_winner列的数据框
    - n_bins：分箱数量（默认20）

    返回值：统计数据框，包含：
      - diff_bin: 分箱区间
      - win_rate: 该分箱内的模型胜率
      - sample_count: 样本数量
      - avg_diff: 分箱内的平均长度差值
      - sample_proportion: 样本占比
    """
    print(f"创建长度差值分箱 (n_bins={n_bins})...")
    
    # 计算长度差值的基本统计量，用于理解数据分布
    diff_min = length_data['length_diff'].min()
    diff_max = length_data['length_diff'].max()
    diff_std = length_data['length_diff'].std()
    
    print(f"  长度差值分布统计:")
    print(f"    最小值: {diff_min:.0f} tokens")
    print(f"    最大值: {diff_max:.0f} tokens")
    print(f"    标准差: {diff_std:.0f} tokens")
    
    # 使用1%-99%分位数范围作为分箱边界
    lower_bound = length_data['length_diff'].quantile(0.01)
    upper_bound = length_data['length_diff'].quantile(0.99)
    print(f"    分箱范围 (1%-99%分位数): [{lower_bound:.0f}, {upper_bound:.0f}] tokens")
    
    # 在[lower_bound, upper_bound]范围内均匀分箱
    bins = np.linspace(lower_bound, upper_bound, n_bins + 1)
    length_data['diff_bin'] = pd.cut(length_data['length_diff'], bins=bins, include_lowest=True)

    # 按分箱计算统计量
    diff_bin_stats = length_data.groupby('diff_bin').agg({
        'is_winner': ['mean', 'count'],
        'length_diff': 'mean'
    }).reset_index()

    diff_bin_stats.columns = ['diff_bin', 'win_rate', 'sample_count', 'avg_diff']

    total_samples = diff_bin_stats['sample_count'].sum()
    diff_bin_stats['sample_proportion'] = diff_bin_stats['sample_count'] / total_samples
    
    print(f"  分箱数量: {len(diff_bin_stats)} 个")
    print(f"  总样本量: {total_samples:,} 个")
    print(f"  平均每个分箱: {total_samples / len(diff_bin_stats):.0f} 个样本")
    print("=" * 80)
    
    return diff_bin_stats

def find_optimal_interval_ratio(ratio_bin_stats: pd.DataFrame) -> Tuple[object, float, float]:
    """
    找到长度比率中胜率最高的最优区间。
    
    策略说明：
    - 遍历所有分箱，找到胜率（win_rate）最大的分箱
    - 返回该分箱的区间范围、胜率和平均比率
    
    应用场景：
    - 识别最优的长度比率范围
    - 指导模型调优：维持这个比率可以最大化胜率

    参数：
    - ratio_bin_stats：长度比率分箱统计数据

    返回值：(ratio_best_bin, ratio_best_win_rate, best_avg_ratio)
      - ratio_best_bin：最优分箱的区间对象 Interval(left, right)
      - ratio_best_win_rate：该分箱的胜率 (0-1)
      - best_avg_ratio：该分箱的平均长度比率
    """
    best_idx = ratio_bin_stats['win_rate'].idxmax()
    ratio_best_bin = ratio_bin_stats.loc[best_idx, 'ratio_bin']
    ratio_best_win_rate = ratio_bin_stats.loc[best_idx, 'win_rate']
    best_avg_ratio = ratio_bin_stats.loc[best_idx, 'avg_ratio']
    
    return ratio_best_bin, ratio_best_win_rate, best_avg_ratio

def find_optimal_interval_diff(diff_bin_stats: pd.DataFrame) -> Tuple[object, float, float]:
    """
    找到长度差值中胜率最高的最优区间。
    
    策略说明：
    - 遍历所有分箱，找到胜率（win_rate）最大的分箱
    - 返回该分箱的区间范围、胜率和平均差值
    
    应用场景：
    - 识别最优的长度差值范围
    - 指导模型调优：保持这个差值范围可以最大化相对优势

    参数：
    - diff_bin_stats：长度差值分箱统计数据

    返回值：(diff_best_bin, diff_best_win_rate, best_avg_diff)
      - diff_best_bin：最优分箱的区间对象 Interval(left, right)
      - diff_best_win_rate：该分箱的胜率 (0-1)
      - best_avg_diff：该分箱的平均长度差值 (tokens)
    """
    best_idx = diff_bin_stats['win_rate'].idxmax()
    diff_best_bin = diff_bin_stats.loc[best_idx, 'diff_bin']
    diff_best_win_rate = diff_bin_stats.loc[best_idx, 'win_rate']
    best_avg_diff = diff_bin_stats.loc[best_idx, 'avg_diff']
    
    return diff_best_bin, diff_best_win_rate, best_avg_diff

def plot_length_ratio_preference_chart(ratio_bin_stats: pd.DataFrame, 
                                     chart_path: Path | str) -> Tuple[object, float, float]:
    """
    绘制长度比率与胜率的双轴折线图。
    
    图表结构说明：
    - 左轴（Y1，红色）：模型的胜率 win_rate，范围[0.3, 0.7]
    - 右轴（Y2，青色）：样本占比 sample_proportion，范围[0, max*1.1]
    - X轴：长度比率 (模型输出length / 用户输入length)
    
    图表元素说明：
    - 红色折线 + 圆点：胜率曲线
    - 青色虚线 + 方点：样本占比曲线
    - 黄色竖线：最优长度比率位置
    - 黄色背景区域：最优分箱范围
    - 红色曲线：二次多项式拟合的趋势线
    - 注释文本框：标注最优区间的具体数值
    
    设计理念：
    - 双轴设计：同时展示胜率趋势和样本分布
    - 样本占比帮助判断结果的统计可信度
      * 样本多的区间：统计结果更稳定
      * 样本少的区间：结果可能由于样本不足而波动
    - 趋势线：反映整体的二阶非线性关系

    参数：
    - ratio_bin_stats：长度比率分箱统计数据
    - chart_path：输出图表的文件路径

    返回值：(ratio_best_bin, ratio_best_win_rate, best_avg_ratio)
    """
    print("绘制长度比率双轴折线图...")

    # 创建fig和第一个y轴（左轴）
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # 1. 配置左轴（Y1） - 胜率曲线
    color1 = '#FF6B6B'  # 红色，代表胜率
    
    # 1.1 配置X轴
    ax1.set_xlabel('length_ratio', fontsize=14, fontweight='bold')
    ax1.set_xlim(ratio_bin_stats['avg_ratio'].min() * 0.97, 
                 ratio_bin_stats['avg_ratio'].max() * 1.03)

    # 1.2 配置左Y轴（胜率）
    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))  # 百分比格式
    
    # 1.3 绘制胜率曲线：红色折线，白色圆点标记
    line1 = ax1.plot(ratio_bin_stats['avg_ratio'], ratio_bin_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8, 
                     label='win_rate', markerfacecolor='white', markeredgewidth=2)
    
    # 2. 配置右轴（Y2） - 样本占比曲线
    color2 = '#4ECDC4'  # 青色，代表样本分布

    ax2 = ax1.twinx()  # 创建共享x轴的右轴

    # 2.1 配置右Y轴（样本占比）
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, ratio_bin_stats['sample_proportion'].max() * 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    # 2.2 绘制样本占比曲线：虚线，方点标记
    line2 = ax2.plot(ratio_bin_stats['avg_ratio'], ratio_bin_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8,
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    
    # 3. 标注最优区间
    ratio_best_bin, ratio_best_win_rate, best_avg_ratio = find_optimal_interval_ratio(ratio_bin_stats)
    
    # 3.1 在最优长度比率处绘制竖线
    ax1.axvline(x=best_avg_ratio, color='#FFD166', linestyle='-', linewidth=3, alpha=0.6)
    
    # 3.2 在最优分箱范围内填充背景
    ax1.fill_betweenx([0, 1], ratio_best_bin.left, ratio_best_bin.right,
                    color='#FFD166', alpha=0.3, label='optimal_interval')
        
    # 3.3 在最优点处添加注释文本框
    annotation_text = f"optimal_interval\nlength_ratio: {best_avg_ratio:.2f}\nwin_rate: {ratio_best_win_rate:.2%}"
    
    ax1.annotate(annotation_text, 
                xy=(best_avg_ratio, ratio_best_win_rate), 
                xytext=(best_avg_ratio * 1.15, ratio_best_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=14, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))
    
    # 4. 添加趋势线
    # 使用二次多项式（degree=2）拟合win_rate与avg_ratio的关系
    # 二次多项式能捕捉非线性的倒U形或U形关系
    z = np.polyfit(ratio_bin_stats['avg_ratio'], ratio_bin_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(ratio_bin_stats['avg_ratio'].min(), 
                          ratio_bin_stats['avg_ratio'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')
    
    # 5. 配置图例和标题

    # 5.1 左轴的图例
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    # 5.2 右轴的图例
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)
    
    # 5.3 图表标题
    plt.title('Length Preference Analysis - Length Ratio vs Win Rate & Sample Proportion', 
              fontsize=18, fontweight='bold', pad=20)
    
    # 5.4 网格线配置
    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#FF8888")
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#AED1FF")

    # 保存图表
    plt.tight_layout()
    
    chart_path = Path(chart_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  长度比率双轴折线图保存到: {chart_path}")
    print("=" * 80)

    return ratio_best_bin, ratio_best_win_rate, best_avg_ratio

def plot_length_diff_preference_chart(diff_bin_stats: pd.DataFrame, 
                                    chart_path: Path | str) -> Tuple[object, float, float]:
    """
    绘制长度差值与胜率的双轴折线图。
    
    图表结构说明：
    - 左轴（Y1，红色）：模型的胜率 win_rate，范围[0.2, 0.8]
    - 右轴（Y2，青色）：样本占比 sample_proportion，范围[0, max*1.1]
    - X轴：长度差值 (模型A输出tokens - 模型B输出tokens)
    
    图表元素说明：
    - 红色折线 + 圆点：胜率曲线，反映模型A相对于模型B的优势
    - 青色虚线 + 方点：样本占比曲线
    - 灰色虚线（X=0）：零差值线，代表两模型长度相同的分界线
    - 黄色竖线：最优长度差值位置
    - 黄色背景区域：最优分箱范围
    - 红色曲线：二次多项式拟合的趋势线
    
    解释说明：
    - X > 0：模型A比B更冗长
      * y > 0.5：说明更冗长时模型A胜率更高
      * y < 0.5：说明更冗长时模型A胜率更低（反而不利）
    - X < 0：模型B比A更冗长（即A更简洁）
      * y > 0.5：说明A更简洁时A胜率更高
    - X = 0：两模型长度相同
    
    应用：
    - 如果最优差值在正区间：应保持输出冗长
    - 如果最优差值在负区间：应保持输出简洁
    - 差值的绝对值指示最优的长度差异程度

    参数：
    - diff_bin_stats：长度差值分箱统计数据
    - chart_path：输出图表的文件路径

    返回值：(diff_best_bin, diff_best_win_rate, best_avg_diff)
    """
    print("绘制长度差值双轴折线图...")

    # 创建fig和第一个y轴（左轴）
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # 1. 配置左轴（Y1） - 胜率曲线
    color1 = '#FF6B6B'  # 红色，代表胜率

    # 1.1 配置X轴
    ax1.set_xlabel('length_diff', fontsize=14, fontweight='bold')
    ax1.set_xlim(diff_bin_stats['avg_diff'].min() * 0.95, 
                 diff_bin_stats['avg_diff'].max() * 1.05)

    # 1.2 配置左Y轴（胜率）
    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.2, 0.8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    # 1.3 绘制胜率曲线：红色折线，白色圆点标记
    line1 = ax1.plot(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8, 
                     label='win_rate', markerfacecolor='white', markeredgewidth=2)
    
    # 1.4 添加零差值线：用灰色虚线标记长度相同的位置
    ax1.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='zero_line')

    # 2. 配置右轴（Y2） - 样本占比曲线
    color2 = '#4ECDC4'  # 青色，代表样本分布

    ax2 = ax1.twinx()  # 创建共享x轴的右轴

    # 2.1 配置右Y轴（样本占比）
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, diff_bin_stats['sample_proportion'].max() * 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    # 2.2 绘制样本占比曲线：虚线，方点标记
    line2 = ax2.plot(diff_bin_stats['avg_diff'], diff_bin_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8, 
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    
    # 3. 标注最优区间
    diff_best_bin, diff_best_win_rate, best_avg_diff = find_optimal_interval_diff(diff_bin_stats)

    # 3.1 在最优长度差值处绘制竖线
    ax1.axvline(x=best_avg_diff, color='#FFD166', linestyle='-', linewidth=3, alpha=0.6)
    
    # 3.2 在最优分箱范围内填充背景
    ax1.fill_betweenx([0, 1], diff_best_bin.left, diff_best_bin.right,
                      color='#FFD166', alpha=0.3, label='optimal_interval')

    # 3.3 在最优点处添加注释文本框
    annotation_text = f'optimal_interval\nlength_diff: {best_avg_diff:.0f} tokens\nwin_rate: {diff_best_win_rate:.2%}'
    
    ax1.annotate(annotation_text, 
                xy=(best_avg_diff, diff_best_win_rate), 
                xytext=(best_avg_diff * 0.65, diff_best_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=12, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    # 4. 添加趋势线
    # 4.1 使用二次多项式拟合，捕捉非线性关系
    z = np.polyfit(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(diff_bin_stats['avg_diff'].min(), 
                          diff_bin_stats['avg_diff'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    # 5. 配置图例和标题
    # 5.1 左轴的图例
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    # 5.2 右轴的图例
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    # 5.3 图表标题
    plt.title('Length Preference Analysis - Length Diff vs Win Rate & Sample Proportion', 
              fontsize=18, fontweight='bold', pad=20)

    # 5.4 网格线配置
    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#FF8888")
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#AED1FF")

    # 保存图表
    plt.tight_layout()

    chart_path = Path(chart_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  长度差值双轴折线图保存到: {chart_path}")
    print("=" * 80)
    
    return diff_best_bin, diff_best_win_rate, best_avg_diff

def create_statistical_table(ratio_bin_stats: pd.DataFrame, 
                            diff_bin_stats: pd.DataFrame, 
                            output_dir: Path | str | None = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    创建并保存分箱统计表格为CSV文件。
    
    本函数将分箱统计数据转换为表格格式，包含区间边界和中心值，
    便于后续的报告生成和数据分析。
    
    生成的CSV文件说明：
    - T01_length_ratio_analysis_stats.csv：长度比率分箱统计
      * 分箱左边界、右边界、中心值
      * 胜率、样本数量、样本占比
    - T02_length_diff_analysis_stats.csv：长度差值分箱统计
      * 同样的列结构，针对长度差值维度

    参数：
    - ratio_bin_stats：长度比率分箱统计数据
    - diff_bin_stats：长度差值分箱统计数据
    - output_dir：输出目录（默认为 Tables）

    返回值：(ratio_stats_table, diff_stats_table) 处理后的表格数据框
    """
    print("创建统计表格...")
    
    # 设置默认输出目录
    if output_dir is None:
        output_dir = Path.cwd() / "Tables"
    else:
        output_dir = Path(output_dir)
    
    # 创建目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 处理长度比率统计表格
    ratio_stats_table = ratio_bin_stats.copy()
    
    # 1.1 从Interval对象中提取左右边界
    ratio_stats_table['bin_left'] = ratio_stats_table['ratio_bin'].apply(lambda x: x.left)
    ratio_stats_table['bin_right'] = ratio_stats_table['ratio_bin'].apply(lambda x: x.right)
    ratio_stats_table['bin_center'] = ratio_stats_table['avg_ratio']

    # 1.2 重命名列为中文，提高可读性
    ratio_stats_table = ratio_stats_table.rename(columns={
        'win_rate': '胜率',
        'sample_count': '样本数量',
        'sample_proportion': '样本占比',
        'bin_left': '分箱左边界',
        'bin_right': '分箱右边界',
        'bin_center': '分箱中心值'
    })

    # 1.3 选择输出列的顺序
    output_cols = ['分箱左边界', '分箱右边界', '分箱中心值', '胜率', '样本数量', '样本占比']
    ratio_stats_table = ratio_stats_table[output_cols]

    # 保存为CSV文件
    ratio_stats_path = output_dir / "T01_length_ratio_analysis_stats.csv"
    ratio_stats_table.to_csv(ratio_stats_path, index=False, encoding='utf-8-sig')
    print(f"  长度比率统计表格保存到: {ratio_stats_path}")

    # 2. 处理长度差值统计表格
    diff_stats_table = diff_bin_stats.copy()
    
    # 2.1 从Interval对象中提取左右边界
    diff_stats_table['bin_left'] = diff_stats_table['diff_bin'].apply(lambda x: x.left)
    diff_stats_table['bin_right'] = diff_stats_table['diff_bin'].apply(lambda x: x.right)
    diff_stats_table['bin_center'] = diff_stats_table['avg_diff']

    # 2.2 重命名列为中文，提高可读性
    diff_stats_table = diff_stats_table.rename(columns={
        'win_rate': '胜率',
        'sample_count': '样本数量',
        'sample_proportion': '样本占比',
        'bin_left': '分箱左边界',
        'bin_right': '分箱右边界',
        'bin_center': '分箱中心值'
    })

    # 2.3 选择输出列的顺序
    diff_stats_table = diff_stats_table[output_cols]

    # 保存为CSV文件
    diff_stats_path = output_dir / "T02_length_diff_analysis_stats.csv"
    diff_stats_table.to_csv(diff_stats_path, index=False, encoding='utf-8-sig')
    print(f"  长度差值统计表格保存到: {diff_stats_path}")
    
    print("=" * 80)
    
    return ratio_stats_table, diff_stats_table

def generate_analysis_report(ratio_bin_stats: pd.DataFrame, 
                            diff_bin_stats: pd.DataFrame,
                            ratio_best_bin: object, 
                            ratio_best_win_rate: float, 
                            best_avg_ratio: float,
                            diff_best_bin: object, 
                            diff_best_win_rate: float, 
                            best_avg_diff: float,
                            output_path: Path | str | None = None) -> Path:
    """
    生成详细的长度偏好分析报告。
    
    报告内容结构说明：
    1. 分析概况：数据基本统计（时间、样本量、数据范围）
    2. 最优长度比率区间：识别出的最优比率范围及其性能指标
    3. 最优长度差值区间：识别出的最优差值范围及其性能指标
    4. 关键统计量：分布特征（均值、标准差、中位数、范围）
    5. 趋势分析：相关系数解释，识别线性或非线性关系
    6. Top-3最优分箱：列出胜率最高的三个分箱，便于快速查阅
    
    报告用途：
    - 文档化分析结果，便于后续回顾
    - 作为报告部分，支持多人协作
    - 支持自动化处理（CSV格式的统计量便于编程解析）

    参数：
    - ratio_bin_stats/diff_bin_stats：分箱统计数据
    - ratio_best_bin/diff_best_bin：最优分箱的Interval对象
    - ratio_best_win_rate/diff_best_win_rate：最优分箱的胜率
    - best_avg_ratio/best_avg_diff：最优分箱的平均值
    - output_path：输出文件路径（默认为 Reports/R11_format_preference_report.txt）

    返回值：输出文件的Path对象
    """
    print("生成分析报告...")
    
    # 设置默认输出路径
    if output_path is None:
        output_path = Path.cwd() / "Reports" / "R11_length_preference_report.txt"
    else:
        output_path = Path(output_path)
    
    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 1. 分析概况
        f.write("=" * 80 + "\n")
        f.write("长度偏好分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 分析概况\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"长度比率分箱数量: {len(ratio_bin_stats)}\n")
        f.write(f"长度差值分箱数量: {len(diff_bin_stats)}\n")
        f.write(f"总样本量: {ratio_bin_stats['sample_count'].sum():,} 个样本\n")
        f.write(f"长度比率范围: [{ratio_bin_stats['avg_ratio'].min():.2f}, {ratio_bin_stats['avg_ratio'].max():.2f}]\n")
        f.write(f"长度差值范围: [{diff_bin_stats['avg_diff'].min():.0f}, {diff_bin_stats['avg_diff'].max():.0f}] tokens\n\n")

        # 2. 长度比率分析结果
        f.write("2. 最优长度比率区间\n")
        f.write("-" * 40 + "\n")
        f.write(f"分箱区间: {ratio_best_bin}\n")
        f.write(f"中心值: {best_avg_ratio:.2f} 倍\n")
        f.write(f"胜率: {ratio_best_win_rate:.2%}\n")
        
        # 查询该分箱的样本统计
        ratio_best_idx = ratio_bin_stats['avg_ratio'].sub(best_avg_ratio).abs().idxmin()
        ratio_best_count = ratio_bin_stats.loc[ratio_best_idx, 'sample_count']
        ratio_best_prop = ratio_bin_stats.loc[ratio_best_idx, 'sample_proportion']
        
        f.write(f"样本数量: {ratio_best_count:,} 个\n")
        f.write(f"样本占比: {ratio_best_prop:.2%}\n")
        f.write(f"\n解释: 当模型输出长度约为用户输入长度的 {best_avg_ratio:.2f} 倍时，\n")
        f.write(f"      模型获得胜率最高，达到 {ratio_best_win_rate:.2%}。\n\n")

        # 3. 最优长度差值区间
        f.write("3. 最优长度差值区间\n")
        f.write("-" * 40 + "\n")
        f.write(f"分箱区间: {diff_best_bin}\n")
        f.write(f"中心值: {best_avg_diff:.0f} tokens\n")
        f.write(f"胜率: {diff_best_win_rate:.2%}\n")
        
        # 查询该分箱的样本统计
        diff_best_idx = diff_bin_stats['avg_diff'].sub(best_avg_diff).abs().idxmin()
        diff_best_count = diff_bin_stats.loc[diff_best_idx, 'sample_count']
        diff_best_prop = diff_bin_stats.loc[diff_best_idx, 'sample_proportion']
        
        f.write(f"样本数量: {diff_best_count:,} 个\n")
        f.write(f"样本占比: {diff_best_prop:.2%}\n")
        
        if best_avg_diff > 0:
            f.write(f"\n解释: 当模型A比模型B多输出约 {best_avg_diff:.0f} 个tokens时，\n")
        elif best_avg_diff < 0:
            f.write(f"\n解释: 当模型A比模型B少输出约 {abs(best_avg_diff):.0f} 个tokens时，\n")
        else:
            f.write(f"\n解释: 当两模型输出长度相同时（差值≈0），\n")
        
        f.write(f"      模型A获得胜率最高，达到 {diff_best_win_rate:.2%}。\n\n")

        # 4. 关键统计量
        f.write("4. 关键统计量\n")
        f.write("-" * 40 + "\n")

        f.write("长度比率维度统计:\n")
        f.write(f"  胜率均值: {ratio_bin_stats['win_rate'].mean():.3f}\n")
        f.write(f"  胜率标准差: {ratio_bin_stats['win_rate'].std():.3f}\n")
        f.write(f"  胜率中位数: {ratio_bin_stats['win_rate'].median():.3f}\n")
        f.write(f"  胜率范围: [{ratio_bin_stats['win_rate'].min():.3f}, {ratio_bin_stats['win_rate'].max():.3f}]\n")

        f.write(f"\n  长度比率均值: {ratio_bin_stats['avg_ratio'].mean():.3f}\n")
        f.write(f"  长度比率中位数: {ratio_bin_stats['avg_ratio'].median():.3f}\n")
        f.write(f"  (注: 标准差较大表示胜率在不同比率下波动较大)\n\n")
        
        f.write("长度差值维度统计:\n")
        f.write(f"  胜率均值: {diff_bin_stats['win_rate'].mean():.3f}\n")
        f.write(f"  胜率标准差: {diff_bin_stats['win_rate'].std():.3f}\n")
        f.write(f"  胜率中位数: {diff_bin_stats['win_rate'].median():.3f}\n")
        f.write(f"  胜率范围: [{diff_bin_stats['win_rate'].min():.3f}, {diff_bin_stats['win_rate'].max():.3f}]\n")
        
        f.write(f"\n  长度差值均值: {diff_bin_stats['avg_diff'].mean():.0f} tokens\n")
        f.write(f"  长度差值中位数: {diff_bin_stats['avg_diff'].median():.0f} tokens\n\n")

        # 5. 趋势分析
        f.write("5. 趋势分析\n")
        f.write("-" * 40 + "\n")
        
        # 长度比率与胜率的相关性
        ratio_correlation = ratio_bin_stats['avg_ratio'].corr(ratio_bin_stats['win_rate'])
        f.write(f"长度比率与胜率的相关系数: {ratio_correlation:.3f}\n")
        
        if ratio_correlation > 0.3:
            f.write("  趋势判断: 正相关\n")
            f.write("  解释: 长度比率增加时，胜率倾向于增加\n")
            f.write("  建议: 倾向于增加输出长度\n")
        elif ratio_correlation < -0.3:
            f.write("  趋势判断: 负相关\n")
            f.write("  解释: 长度比率增加时，胜率倾向于降低\n")
            f.write("  建议: 倾向于减少输出长度\n")
        else:
            f.write("  趋势判断: 弱相关或无显著相关\n")
            f.write("  解释: 长度比率对胜率影响较弱\n")
            f.write("  建议: 长度比率不是关键因素\n")
        
        # 长度差值与胜率的相关性
        diff_correlation = diff_bin_stats['avg_diff'].corr(diff_bin_stats['win_rate'])
        f.write(f"\n长度差值与胜率的相关系数: {diff_correlation:.3f}\n")
        
        if diff_correlation > 0.3:
            f.write("  趋势判断: 正相关\n")
            f.write("  解释: 长度差值增加（A更长）时，A的胜率倾向于增加\n")
            f.write("  建议: A应该比B更冗长\n")
        elif diff_correlation < -0.3:
            f.write("  趋势判断: 负相关\n")
            f.write("  解释: 长度差值增加（A更长）时，A的胜率倾向于降低\n")
            f.write("  建议: A应该比B更简洁\n")
        else:
            f.write("  趋势判断: 弱相关或无显著相关\n")
            f.write("  解释: 长度差异对相对优势影响较弱\n")
            f.write("  建议: 长度差值不是关键竞争因素\n")

        # 6. Top-3最优分箱
        f.write("\n6. 最优分箱Top-3\n")
        f.write("-" * 40 + "\n")
        
        f.write("长度比率Top-3（胜率最高的3个分箱）:\n")
        top_3_ratio = ratio_bin_stats.nlargest(3, 'win_rate')
        for idx, (_, row) in enumerate(top_3_ratio.iterrows(), 1):
            f.write(f"  {idx}. 区间: {row['ratio_bin']}\n")
            f.write(f"     中心值: {row['avg_ratio']:.2f}, 胜率: {row['win_rate']:.3f}, ")
            f.write(f"样本: {row['sample_count']:,} ({row['sample_proportion']:.2%})\n")

        f.write("\n长度差值Top-3（胜率最高的3个分箱）:\n")
        top_3_diff = diff_bin_stats.nlargest(3, 'win_rate')
        for idx, (_, row) in enumerate(top_3_diff.iterrows(), 1):
            f.write(f"  {idx}. 区间: {row['diff_bin']}\n")
            f.write(f"     中心值: {row['avg_diff']:.0f}t, 胜率: {row['win_rate']:.3f}, ")
            f.write(f"样本: {row['sample_count']:,} ({row['sample_proportion']:.2%})\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")
    
    print(f"  分析报告保存到: {output_path}")
    print("=" * 80)
    
    return output_path

if __name__ == "__main__":
    """
    主函数：长度偏好可视化分析的主入口。
    
    执行流程：
    1. 加载优化后的数据集
    2. 准备长度特征（解缠化处理）
    3. 创建长度比率分箱统计
    4. 创建长度差值分箱统计
    5. 生成可视化图表（双轴折线图）
    6. 创建统计表格（CSV格式）
    7. 生成详细分析报告（文本格式）
    
    输出文件：
    - 两张图表：Pictures/P04_*, P05_*
    - 两个CSV表格：Tables/T01_*, T02_*
    - 一份分析报告：Reports/R11_*
    """
    print("=" * 80)
    print("长度偏好可视化分析模块")
    print("=" * 80)

    # 输入数据路径
    input_file_path = get_optimized_parquet_path()
    
    # 输出目录
    chart_dir = Path.cwd() / "Pictures"
    report_dir = Path.cwd() / "Reports"
    table_dir = Path.cwd() / "Tables"
    
    # 分箱数量（可调参数）：更多箱数=更细致的分析，但样本量要求更大
    n_bins = 20
    
    # 创建所有输出目录
    for directory in [chart_dir, report_dir, table_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"\n加载数据: {input_file_path}")
    
    if not input_file_path.exists():
        print(f"  ERROR: 输入文件不存在: {input_file_path}")
        print(f"  请确保已运行 C12_optimize_data.py 生成优化数据")
        exit(1)
    
    try:
        df = pd.read_parquet(input_file_path)
        print(f"  数据已加载，形状: {df.shape}")
    except Exception as e:
        print(f"  ERROR: 读取失败 - {e}")
        exit(1)
    
    print("=" * 80)

    length_data = prepare_length_data(df)
    
    # 保存长度数据缓存，便于后续快速接入
    length_data_path = get_length_data_path()
    length_data_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        length_data.to_parquet(length_data_path, index=False)
        print(f"  长度数据已保存: {length_data_path}\n")
    except Exception as e:
        print(f"  WARNING: 缓存保存失败 - {e}\n")
    

    ratio_bin_stats = create_length_ratio_bins(length_data, n_bins)

    ratio_preference_path = chart_dir / "P04_length_ratio_line_chart.png"
    ratio_best_bin, ratio_best_win_rate, best_avg_ratio = plot_length_ratio_preference_chart(
        ratio_bin_stats, ratio_preference_path
    )

    diff_bin_stats = create_length_diff_bins(length_data, n_bins)

    diff_preference_path = chart_dir / "P05_length_diff_line_chart.png"
    diff_best_bin, diff_best_win_rate, best_avg_diff = plot_length_diff_preference_chart(
        diff_bin_stats, diff_preference_path
    )
    
    stats_table_ratio, stats_table_diff = create_statistical_table(
        ratio_bin_stats, diff_bin_stats, table_dir
    )

    report_path = report_dir / "R11_length_preference_report.txt"
    generate_analysis_report(
        ratio_bin_stats, diff_bin_stats,
        ratio_best_bin, ratio_best_win_rate, best_avg_ratio,
        diff_best_bin, diff_best_win_rate, best_avg_diff,
        report_path
    )

    print("\n" + "=" * 80)
    print("任务完成!")
    print("=" * 80)
    
    print("\n生成的输出文件:")
    print(f"\n  【图表】")
    print(f"    1. {ratio_preference_path.name}")
    print(f"    2. {diff_preference_path.name}")
    
    print(f"\n  【统计表格】")
    print(f"    3. {(table_dir / 'T01_length_ratio_analysis_stats.csv').name}")
    print(f"    4. {(table_dir / 'T02_length_diff_analysis_stats.csv').name}")
    
    print(f"\n  【分析报告】")
    print(f"    5. {report_path.name}")
    
    print(f"\n输出目录:")
    print(f"    - 图表: {chart_dir}")
    print(f"    - 表格: {table_dir}")
    print(f"    - 报告: {report_dir}")
    
    print(f"\n关键发现:")
    print(f"    - 最优长度比率: {best_avg_ratio:.2f} (胜率: {ratio_best_win_rate:.2%})")
    print(f"    - 最优长度差值: {best_avg_diff:.0f} tokens (胜率: {diff_best_win_rate:.2%})")
    
    print("\n" + "=" * 80)
