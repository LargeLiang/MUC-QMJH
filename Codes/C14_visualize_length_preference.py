"""
C14_visualize_length_preference

对解缠化后的长度特征进行描述性可视化分析，输出 diff 分箱折线图与文本报告。

功能：
- 解缠化处理：将配对评价拆分为单模型回复样本
- 长度差值分箱分析：diff 分箱胜率 + 样本占比双轴折线图
- 分层描述：对 4 个任务类别子集（CW / IF / MATH / CODE）分别重复上述分析
- 统计表格：输出差值分箱的 CSV 汇总
- 文本报告：全量 + 各子集的描述性结论

数据流向：
  optimized_data.parquet → 解缠化计算 → diff 分箱分析 → 可视化图像输出 →
  + *_true_data.parquet（4 类子集）→ 分层可视化 → Reports/R11_length_preference_report.txt
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
        root_path = Path.cwd()
    else:
        root_path = Path(root)
    
    # 优化数据文件位于项目根目录下的 Data/optimized_data/optimized_data.parquet
    return root_path / "Data" / "optimized_data" / "optimized_data.parquet"


def get_length_data_path(root: Path | str | None = None) -> Path:
    """
    返回长度数据 parquet 文件的默认路径。
    
    此路径用于存储预处理后的长度特征数据，可用于后续快速分析。
    """
    if root is None:
        root_path = Path.cwd()
    else:
        root_path = Path(root)
    
    return root_path / "Data" / "length_data" / "length_data.parquet"


def prepare_length_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    从优化数据中提取长度特征并执行解缠化处理。

    将每条配对评价记录拆分为两条单模型样本（模型 A 和模型 B），
    记录各自的输出长度差值与胜负标签。

    注：样本已解缠化，每对评价拆分为两条记录，配对数约为样本数的 1/2。

    参数说明：
    - df：优化后的数据框，需包含以下列：
        - winner: 评价结果
        - a_tokens, b_tokens: 两个模型的输出 token 数
        - model_a, model_b: 两个模型的名称

    返回值：包含 length_diff、is_winner、model 列的解缠化数据框

    异常处理：
    - 若数据为空，返回空的 DataFrame
    - 若缺少必要列，会在运行时抛出 KeyError
    """
    print("准备长度特征数据...")

    # 1. 过滤掉"平局"评价，保留有明确胜负的评价
    win_df = df[~df['winner'].isin(['tie', 'both_bad'])].copy()
    original_rows = len(df)
    valid_rows = len(win_df)
    print(f"  原始行数: {original_rows} 条评价")
    print(f"  过滤平局后: {valid_rows} 条有效评价 (过滤率: {(1 - valid_rows/original_rows):.1%})")

    # 2. 计算长度差值（绝对长度）
    # 正值表示模型 A 更冗长，负值表示模型 B 更冗长
    print("  计算长度差值 = a_tokens - b_tokens（正值表示 A 更长）")
    win_df['length_diff'] = win_df['a_tokens'] - win_df['b_tokens']

    # 3. 解缠化处理：从配对评价转换为单模型样本

    # 3.1 模型 A 样本
    a_data = win_df[['length_diff', 'model_a']].copy()
    a_data['is_winner'] = (win_df['winner'] == 'model_a').values
    a_data = a_data.rename(columns={'model_a': 'model'})

    # 3.2 模型 B 样本（差值符号反转，表示从 B 视角的相对长度）
    b_data = win_df[['model_b']].copy()
    b_data['length_diff'] = -win_df['length_diff'].values
    b_data['is_winner'] = (win_df['winner'] == 'model_b').values
    b_data = b_data.rename(columns={'model_b': 'model'})

    # 3.3 合并两个子集
    length_data = pd.concat([a_data, b_data], ignore_index=True)
    print(f"  解缠化后总样本数: {len(length_data)} 个模型回答")

    return length_data


def create_length_diff_bins(length_data: pd.DataFrame, n_bins: int = 20) -> pd.DataFrame:
    """
    按长度差值进行分箱分析，使用 1%–99% 分位数区间以过滤极端值。

    参数说明：
    - length_data：包含 length_diff 和 is_winner 列的数据框
    - n_bins：分箱数量（默认 20）

    返回值：统计数据框，包含 diff_bin、win_rate、sample_count、avg_diff、sample_proportion
    """
    print(f"创建长度差值分箱 (n_bins={n_bins})...")

    # 1. 输出基本分布统计，便于诊断
    diff_min = length_data['length_diff'].min()
    diff_max = length_data['length_diff'].max()
    diff_std = length_data['length_diff'].std()
    print(f"  长度差值分布统计:")
    print(f"    最小值: {diff_min:.0f} tokens")
    print(f"    最大值: {diff_max:.0f} tokens")
    print(f"    标准差: {diff_std:.0f} tokens")

    # 2. 取 1%–99% 分位数范围作为分箱边界，自动过滤极端异常值
    lower_bound = length_data['length_diff'].quantile(0.01)
    upper_bound = length_data['length_diff'].quantile(0.99)
    print(f"    分箱范围 (1%–99% 分位数): [{lower_bound:.0f}, {upper_bound:.0f}] tokens")

    # 3. 在范围内均匀分箱
    bins = np.linspace(lower_bound, upper_bound, n_bins + 1)
    length_data = length_data.copy()
    length_data['diff_bin'] = pd.cut(length_data['length_diff'], bins=bins, include_lowest=True)

    # 4. 按分箱聚合：均值胜率、样本数、平均差值
    diff_bin_stats = length_data.groupby('diff_bin').agg({
        'is_winner': ['mean', 'count'],
        'length_diff': 'mean'
    }).reset_index()
    diff_bin_stats.columns = ['diff_bin', 'win_rate', 'sample_count', 'avg_diff']

    total_samples = diff_bin_stats['sample_count'].sum()
    diff_bin_stats['sample_proportion'] = diff_bin_stats['sample_count'] / total_samples

    print(f"  分箱数量: {len(diff_bin_stats)} 个")
    print(f"  总样本量: {total_samples:,} 个")

    return diff_bin_stats


def find_optimal_interval_diff(diff_bin_stats: pd.DataFrame) -> Tuple[object, float, float]:
    """
    从分箱统计中找出胜率最高的分箱。

    参数说明：
    - diff_bin_stats：create_length_diff_bins 返回的统计数据框

    返回值：(diff_best_bin, diff_best_win_rate, best_avg_diff)
    - diff_best_bin：胜率最高的 Interval 对象
    - diff_best_win_rate：对应胜率
    - best_avg_diff：该分箱内平均长度差值
    """
    # 筛选有效分箱（过滤掉样本量过小的分箱，避免偶然性干扰）
    valid_bins = diff_bin_stats[diff_bin_stats['sample_count'] >= 30]
    if valid_bins.empty:
        valid_bins = diff_bin_stats

    best_idx = valid_bins['win_rate'].idxmax()
    best_row = diff_bin_stats.loc[best_idx]
    return best_row['diff_bin'], float(best_row['win_rate']), float(best_row['avg_diff'])


def plot_length_diff_preference_chart(diff_bin_stats: pd.DataFrame,
                                      chart_path: Path | str,
                                      title_suffix: str = "") -> Tuple[object, float, float]:
    """
    绘制长度差值与胜率的双轴折线图。

    左轴（红色）为胜率 win_rate，右轴（青色）为样本占比 sample_proportion。
    X 轴为长度差值（该模型输出 tokens 减去对比模型输出 tokens）。

    参数说明：
    - diff_bin_stats：长度差值分箱统计数据
    - chart_path：输出图表的文件路径
    - title_suffix：附加到图表标题的后缀字符串（用于区分子集，默认为空）

    返回值：(diff_best_bin, diff_best_win_rate, best_avg_diff)
    """
    print("绘制长度差值双轴折线图...")

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # 1. 配置左轴（胜率）
    color1 = '#FF6B6B'
    ax1.set_xlabel('length_diff', fontsize=14, fontweight='bold')
    ax1.set_xlim(diff_bin_stats['avg_diff'].min() * 0.95,
                 diff_bin_stats['avg_diff'].max() * 1.05)

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.2, 0.8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    # 1.2 绘制胜率曲线
    ax1.plot(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'],
             color=color1, marker='o', linewidth=3, markersize=8,
             label='win_rate', markerfacecolor='white', markeredgewidth=2)

    # 1.3 零差值参考线
    ax1.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='zero_line')

    # 2. 配置右轴（样本占比）
    color2 = '#4ECDC4'
    ax2 = ax1.twinx()
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, diff_bin_stats['sample_proportion'].max() * 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
    ax2.plot(diff_bin_stats['avg_diff'], diff_bin_stats['sample_proportion'],
             color=color2, marker='s', linestyle='--', linewidth=3, markersize=8,
             label='sample_proportion', markerfacecolor='white', markeredgewidth=2)

    # 3. 标注最优区间
    diff_best_bin, diff_best_win_rate, best_avg_diff = find_optimal_interval_diff(diff_bin_stats)

    # 3.1 在最优长度差值处绘制竖线
    ax1.axvline(x=best_avg_diff, color='#FFD166', linestyle='-', linewidth=3, alpha=0.6)
    
    # 3.2 最优分箱背景填充
    ax1.fill_betweenx([0, 1], diff_best_bin.left, diff_best_bin.right,
                      color='#FFD166', alpha=0.3, label='optimal_interval')

    # 3.3 最优点注释文本框
    annotation_text = f'optimal_interval\nlength_diff: {best_avg_diff:.0f} tokens\nwin_rate: {diff_best_win_rate:.2%}'
    ax1.annotate(annotation_text,
                 xy=(best_avg_diff, diff_best_win_rate),
                 xytext=(best_avg_diff * 0.65, diff_best_win_rate * 0.7),
                 arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                 fontsize=12, ha='center', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    # 4. 二次多项式趋势线
    z = np.polyfit(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(diff_bin_stats['avg_diff'].min(),
                           diff_bin_stats['avg_diff'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    # 5. 图例与标题
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    base_title = 'Length Preference Analysis - Length Diff vs Win Rate & Sample Proportion'
    plt.title(f'{base_title}{title_suffix}', fontsize=18, fontweight='bold', pad=20)

    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#FF8888")
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color="#AED1FF")

    plt.tight_layout()
    chart_path = Path(chart_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"  长度差值双轴折线图保存到: {chart_path}")

    return diff_best_bin, diff_best_win_rate, best_avg_diff


def create_statistical_table(diff_bin_stats: pd.DataFrame,
                             output_dir: Path | str | None = None) -> pd.DataFrame:
    """
    将差值分箱统计数据保存为 CSV 表格。

    参数说明：
    - diff_bin_stats：长度差值分箱统计数据
    - output_dir：输出目录（默认为 Tables）

    返回值：处理后的表格数据框
    """
    print("创建统计表格...")

    if output_dir is None:
        output_dir = Path.cwd() / "Tables"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 从 Interval 对象中提取左右边界，便于 CSV 中展示数值范围
    diff_stats_table = diff_bin_stats.copy()
    diff_stats_table['bin_left'] = diff_stats_table['diff_bin'].apply(lambda x: x.left)
    diff_stats_table['bin_right'] = diff_stats_table['diff_bin'].apply(lambda x: x.right)
    diff_stats_table['bin_center'] = diff_stats_table['avg_diff']

    diff_stats_table = diff_stats_table.rename(columns={
        'win_rate': '胜率',
        'sample_count': '样本数量',
        'sample_proportion': '样本占比',
        'bin_left': '分箱左边界',
        'bin_right': '分箱右边界',
        'bin_center': '分箱中心值'
    })
    output_cols = ['分箱左边界', '分箱右边界', '分箱中心值', '胜率', '样本数量', '样本占比']
    diff_stats_table = diff_stats_table[output_cols]

    diff_stats_path = output_dir / "T01_length_diff_analysis_stats.csv"
    diff_stats_table.to_csv(diff_stats_path, index=False, encoding='utf-8-sig')
    print(f"  长度差值统计表格保存到: {diff_stats_path}")

    return diff_stats_table


def generate_analysis_report(diff_bin_stats: pd.DataFrame,
                             diff_best_bin: object,
                             diff_best_win_rate: float,
                             best_avg_diff: float,
                             output_path: Path | str | None = None,
                             mode: str = "w",
                             section_tag: str = "全量数据") -> Path:
    """
    生成长度偏好分析报告并写入文件。

    以追加模式（mode='a'）写入时可将多个子集结果合并到同一报告中。

    参数说明：
    - diff_bin_stats：长度差值分箱统计数据
    - diff_best_bin：最优分箱的 Interval 对象
    - diff_best_win_rate：最优分箱的胜率
    - best_avg_diff：最优分箱的平均差值（tokens）
    - output_path：输出文件路径（默认为 Reports/R11_length_preference_report.txt）
    - mode：文件写入模式，'w' 为覆写，'a' 为追加（默认 'w'）
    - section_tag：当前分析集名称，用于报告标题区分（默认"全量数据"）

    返回值：输出文件的 Path 对象
    """
    print(f"生成分析报告（{section_tag}）...")

    if output_path is None:
        output_path = Path.cwd() / "Reports" / "R11_length_preference_report.txt"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_samples = diff_bin_stats['sample_count'].sum()

    with open(output_path, mode, encoding='utf-8') as f:

        # 1. 分析概况
        f.write("=" * 80 + "\n")
        f.write(f"长度偏好分析报告 — {section_tag}\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 分析概况\n")
        f.write(f"   分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"   分箱数量: {len(diff_bin_stats)}\n")
        f.write(f"   总样本量（解缠化后）: {total_samples:,}\n")
        f.write(f"   对应原始配对数（约）: {total_samples // 2:,}\n")
        f.write("   注：样本已解缠化，每对评价拆分为两条记录，配对数约为样本数的 1/2。\n\n")

        # 2. 最优长度差值区间
        f.write("2. 最优长度差值区间\n")
        diff_best_idx = diff_bin_stats['avg_diff'].sub(best_avg_diff).abs().idxmin()
        diff_best_count = diff_bin_stats.loc[diff_best_idx, 'sample_count']
        diff_best_prop = diff_bin_stats.loc[diff_best_idx, 'sample_proportion']
        f.write(f"   分箱区间: {diff_best_bin}\n")
        f.write(f"   中心值: {best_avg_diff:.0f} tokens\n")
        f.write(f"   胜率: {diff_best_win_rate:.2%}\n")
        f.write(f"   样本数量: {diff_best_count:,}   样本占比: {diff_best_prop:.2%}\n\n")

        # 3. 关键统计量
        f.write("3. 关键统计量\n")
        f.write(f"   胜率均值: {diff_bin_stats['win_rate'].mean():.3f}\n")
        f.write(f"   胜率标准差: {diff_bin_stats['win_rate'].std():.3f}\n")
        f.write(f"   胜率范围: [{diff_bin_stats['win_rate'].min():.3f}, {diff_bin_stats['win_rate'].max():.3f}]\n")
        diff_corr = diff_bin_stats['avg_diff'].corr(diff_bin_stats['win_rate'])
        f.write(f"   diff–胜率相关系数: {diff_corr:.3f}\n\n")

        # 4. Top-3 最优分箱
        f.write("4. 最优分箱 Top-3\n")
        top3 = diff_bin_stats.nlargest(3, 'win_rate')
        for rank, (_, row) in enumerate(top3.iterrows(), 1):
            f.write(f"   {rank}. 区间: {row['diff_bin']}  "
                    f"中心值: {row['avg_diff']:.0f}t  "
                    f"胜率: {row['win_rate']:.3f}  "
                    f"样本: {row['sample_count']:,} ({row['sample_proportion']:.2%})\n")

        f.write("\n")

    print(f"  分析报告写入: {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 80)
    print("长度偏好可视化分析")
    print("=" * 80)

    # 路径初始化
    input_file_path = get_optimized_parquet_path()
    chart_dir = Path.cwd() / "Pictures"
    report_dir = Path.cwd() / "Reports"
    table_dir = Path.cwd() / "Tables"
    for d in [chart_dir, report_dir, table_dir]:
        d.mkdir(parents=True, exist_ok=True)

    n_bins = 20

    print(f"\n加载数据: {input_file_path}")
    if not input_file_path.exists():
        print(f"  ERROR: 输入文件不存在，请先运行 C12_optimize_data.py")
        exit(1)
    df = pd.read_parquet(input_file_path)
    print(f"  数据已加载，形状: {df.shape}")

    # 1. 全量分析
    print("\n" + "-" * 40)
    print("1. 全量数据分析")
    print("-" * 40)
    length_data = prepare_length_data(df)

    # 1.1 保存解缠化缓存
    length_data_path = get_length_data_path()
    length_data_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        length_data.to_parquet(length_data_path, index=False)
        print(f"  长度数据缓存已保存: {length_data_path}")
    except Exception as e:
        print(f"  WARNING: 缓存保存失败 - {e}")

    # 1.2 分箱 + 可视化
    diff_bin_stats = create_length_diff_bins(length_data, n_bins)
    diff_best_bin, diff_best_win_rate, best_avg_diff = plot_length_diff_preference_chart(
        diff_bin_stats, chart_dir / "P05_length_diff_line_chart.png"
    )

    # 1.3 统计表格
    create_statistical_table(diff_bin_stats, table_dir)

    # 1.4 报告（首次写入，覆写模式）
    report_path = report_dir / "R11_length_preference_report.txt"
    generate_analysis_report(
        diff_bin_stats, diff_best_bin, diff_best_win_rate, best_avg_diff,
        report_path, mode="w", section_tag="全量数据"
    )

    # 2. 分层子集分析
    subset_configs = [
        ("creative_writing_true_data.parquet", "CW（创意写作）"),
        ("if_true_data.parquet", "IF（指令跟随）"),
        ("math_true_data.parquet", "MATH（数学）"),
        ("code_true_data.parquet", "CODE（代码）"),
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

        length_data_sub = prepare_length_data(df_sub)

        # 子集若样本量不足以 n_bins 分箱则降为 10 箱
        bins_sub = n_bins if len(length_data_sub) >= n_bins * 30 else 10
        diff_bin_stats_sub = create_length_diff_bins(length_data_sub, bins_sub)

        chart_name = f"P05_{filename.replace('_data.parquet', '')}_length_diff.png"
        diff_best_bin_sub, diff_best_win_rate_sub, best_avg_diff_sub = (
            plot_length_diff_preference_chart(
                diff_bin_stats_sub,
                chart_dir / chart_name,
                title_suffix=f" [{tag}]"
            )
        )

        # 以追加模式写入同一报告
        generate_analysis_report(
            diff_bin_stats_sub, diff_best_bin_sub, diff_best_win_rate_sub, best_avg_diff_sub,
            report_path, mode="a", section_tag=tag
        )

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)
