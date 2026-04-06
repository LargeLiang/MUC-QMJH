import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def prepare_length_data(df: pd.DataFrame) -> pd.DataFrame:
    """准备长度特征数据"""
    print("准备长度特征数据...")
    
    win_df = df[~df['winner'].isin(['tie', 'both_bad'])].copy()
    print(f"过滤平局（'tie' 或 'both_bad'）后数据量: {len(win_df)}")

    print("计算长度比率（'length_ratio' = 'model_tokens' / 'user_tokens'）")
    
    win_df['a_length_ratio'] = win_df['a_tokens'] / win_df['user_tokens']
    win_df['b_length_ratio'] = win_df['b_tokens'] / win_df['user_tokens']
    
    print("计算长度差值（'length_diff' = 'a_tokens' - 'b_tokens'）")
    
    win_df['length_diff'] = win_df['a_tokens'] - win_df['b_tokens']

    a_data = win_df[['a_length_ratio']].copy()
    a_data['length_diff'] = win_df['length_diff']
    a_data['is_winner'] = (win_df['winner'] == 'model_a').astype(bool)
    a_data = a_data.rename(columns={'a_length_ratio': 'length_ratio'})
    a_data['model'] = win_df['model_a']
    
    b_data = win_df[['b_length_ratio']].copy()
    b_data['length_diff'] = - win_df['length_diff']
    b_data['is_winner'] = (win_df['winner'] == 'model_b').astype(bool)
    b_data = b_data.rename(columns={'b_length_ratio': 'length_ratio'})
    b_data['model'] = win_df['model_b']
    
    length_data = pd.concat([a_data, b_data], ignore_index=True)
    print(f"合并后数据量: {len(length_data)} 个回答")

    print("=" * 80)

    return length_data

def create_length_ratio_bins(length_data: pd.DataFrame, n_bins) -> pd.DataFrame:
    """创建长度比率分箱"""
    print(f"创建长度比率分箱 (n_bins={n_bins})...")
    
    max_ratio = length_data['length_ratio'].quantile(0.99)
    print(f"长度比率最大值 (99%分位数): {max_ratio:.2f}")
    
    bins = np.linspace(0, max_ratio, n_bins + 1)
    length_data['ratio_bin'] = pd.cut(length_data['length_ratio'], bins=bins, include_lowest=True)

    ratio_bin_stats = length_data.groupby('ratio_bin').agg({
        'is_winner': ['mean', 'count'],
        'length_ratio': 'mean'
    }).reset_index()

    ratio_bin_stats.columns = ['ratio_bin', 'win_rate', 'sample_count', 'avg_ratio']

    total_samples = ratio_bin_stats['sample_count'].sum()
    ratio_bin_stats['sample_proportion'] = ratio_bin_stats['sample_count'] / total_samples
    
    print(f"分箱数量: {len(ratio_bin_stats)}")
    print(f"总样本量: {total_samples}")

    print("=" * 80)
    
    return ratio_bin_stats

def create_length_diff_bins(length_data: pd.DataFrame, n_bins=20) -> pd.DataFrame:
    """创建长度差值分箱"""
    print(f"创建长度差值分箱 (n_bins={n_bins})...")
    
    diff_min = length_data['length_diff'].min()
    diff_max = length_data['length_diff'].max()
    diff_std = length_data['length_diff'].std()
    
    print(f"差值范围: [{diff_min:.0f}, {diff_max:.0f}]")
    print(f"差值标准差: {diff_std:.0f}")
    
    lower_bound = length_data['length_diff'].quantile(0.01)
    upper_bound = length_data['length_diff'].quantile(0.99)
    print(f"使用1%-99%分位数范围: [{lower_bound:.0f}, {upper_bound:.0f}]")
    
    bins = np.linspace(lower_bound, upper_bound, n_bins + 1)
    length_data['diff_bin'] = pd.cut(length_data['length_diff'], bins=bins, include_lowest=True)

    diff_bin_stats = length_data.groupby('diff_bin').agg({
        'is_winner': ['mean', 'count'],
        'length_diff': 'mean'
    }).reset_index()

    diff_bin_stats.columns = ['diff_bin', 'win_rate', 'sample_count', 'avg_diff']

    total_samples = diff_bin_stats['sample_count'].sum()
    diff_bin_stats['sample_proportion'] = diff_bin_stats['sample_count'] / total_samples
    
    print(f"差值分箱数量: {len(diff_bin_stats)}")
    print(f"差值分析总样本量: {total_samples}")
    
    print("=" * 80)
    
    return diff_bin_stats

def find_optimal_interval_ratio(ratio_bin_stats: pd.DataFrame) -> tuple:
    """找到最优比率区间"""
    best_idx = ratio_bin_stats['win_rate'].idxmax()
    ratio_best_bin = ratio_bin_stats.loc[best_idx, 'ratio_bin']
    ratio_best_win_rate = ratio_bin_stats.loc[best_idx, 'win_rate']
    best_avg_ratio = ratio_bin_stats.loc[best_idx, 'avg_ratio']
    
    return ratio_best_bin, ratio_best_win_rate, best_avg_ratio

def find_optimal_interval_diff(diff_bin_stats: pd.DataFrame) -> tuple:
    """找到最优差值区间"""
    best_idx = diff_bin_stats['win_rate'].idxmax()
    diff_best_bin = diff_bin_stats.loc[best_idx, 'diff_bin']
    diff_best_win_rate = diff_bin_stats.loc[best_idx, 'win_rate']
    best_avg_diff = diff_bin_stats.loc[best_idx, 'avg_diff']
    
    return diff_best_bin, diff_best_win_rate, best_avg_diff

def plot_length_ratio_preference_chart(ratio_bin_stats: pd.DataFrame, chart_path: str):
    """绘制长度比率双轴折线图"""
    print("绘制长度比率双轴折线图...")

    fig, ax1 = plt.subplots(figsize=(14, 8))

    color1 = '#FF6B6B'
    
    ax1.set_xlabel('length_ratio', fontsize=14, fontweight='bold')
    ax1.set_xlim(ratio_bin_stats['avg_ratio'].min() * 0.97, ratio_bin_stats['avg_ratio'].max() * 1.03)

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
    
    line1 = ax1.plot(ratio_bin_stats['avg_ratio'], ratio_bin_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8, 
                     label='win_rate', markerfacecolor='white', markeredgewidth=2)
    
    color2 = '#4ECDC4'

    ax2 = ax1.twinx()

    ax2.set_ylabel('sample_proportion', color=color2, fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, ratio_bin_stats['sample_proportion'].max() * 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line2 = ax2.plot(ratio_bin_stats['avg_ratio'], ratio_bin_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8,
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    
    ratio_best_bin, ratio_best_win_rate, best_avg_ratio = find_optimal_interval_ratio(ratio_bin_stats)
    
    ax1.axvline(x=best_avg_ratio, color='#FFD166', linestyle='-', linewidth=3, alpha=0.6)
    ax1.fill_betweenx([0, 1], ratio_best_bin.left, ratio_best_bin.right,
                    color='#FFD166', alpha=0.3, label='optimal_interval')
        
    annotation_text = f"optimal_interval\nlength_ratio: {best_avg_ratio:.2f}\nwin_rate: {ratio_best_win_rate:.2%}"
    
    ax1.annotate(annotation_text, 
                xy=(best_avg_ratio, ratio_best_win_rate), 
                xytext=(best_avg_ratio * 1.15, ratio_best_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=14, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))
    
    z = np.polyfit(ratio_bin_stats['avg_ratio'], ratio_bin_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(ratio_bin_stats['avg_ratio'].min(), ratio_bin_stats['avg_ratio'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)
    
    plt.title('Length Preference Analysis - Length Ratio vs Win Rate & Sample Proportion', 
              fontsize=18, fontweight='bold', pad=20)
    
    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color = "#FF8888")
    
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color = "#AED1FF")

    plt.tight_layout()
    
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"长度比率双轴折线图保存到: {chart_path}")
    
    print("=" * 80)

    return ratio_best_bin, ratio_best_win_rate, best_avg_ratio

def plot_length_diff_preference_chart(diff_bin_stats: pd.DataFrame, chart_path: str):
    """绘制长度差值双轴折线图"""
    print("绘制长度差值双轴折线图...")

    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    color1 = '#FF6B6B'

    ax1.set_xlabel('length_diff', fontsize=14, fontweight='bold')
    ax1.set_xlim(diff_bin_stats['avg_diff'].min() * 0.95, diff_bin_stats['avg_diff'].max() * 1.05)

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.2, 0.8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line1 = ax1.plot(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8, 
                     label='win_rate', markerfacecolor='white', markeredgewidth=2)
    
    ax1.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='zero_line')

    color2 = '#4ECDC4'

    ax2 = ax1.twinx()

    ax2.set_ylabel('sample_proportion', color=color2, fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, diff_bin_stats['sample_proportion'].max() * 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line2 = ax2.plot(diff_bin_stats['avg_diff'], diff_bin_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8, 
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    
    diff_best_bin, diff_best_win_rate, best_avg_diff = find_optimal_interval_diff(diff_bin_stats)

    ax1.axvline(x=best_avg_diff, color='#FFD166', linestyle='-', linewidth=3, alpha=0.6)
    ax1.fill_betweenx([0, 1], diff_best_bin.left, diff_best_bin.right,
                      color='#FFD166', alpha=0.3, label='optimal_interval')

    annotation_text = f'optimal_interval\nlength_diff: {best_avg_diff:.0f} tokens\nwin_rate: {diff_best_win_rate:.2%}'
    
    ax1.annotate(annotation_text, 
                xy=(best_avg_diff, diff_best_win_rate), 
                xytext=(best_avg_diff * 0.65, diff_best_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=12, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    z = np.polyfit(diff_bin_stats['avg_diff'], diff_bin_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(diff_bin_stats['avg_diff'].min(), diff_bin_stats['avg_diff'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    plt.title('Length Preference Analysis - Length Diff vs Win Rate & Sample Proportion', 
              fontsize=18, fontweight='bold', pad=20)

    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color = "#FF8888")
    
    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.6, color = "#AED1FF")

    plt.tight_layout()

    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"长度差值双轴折线图保存到: {chart_path}")

    print("=" * 80)
    
    return diff_best_bin, diff_best_win_rate, best_avg_diff

def create_statistical_table(ratio_bin_stats: pd.DataFrame, diff_bin_stats: pd.DataFrame, 
                           output_dir: str = "length_preference_visualization"):
    """创建统计表格"""
    print("创建统计表格...")

    ratio_stats_table = ratio_bin_stats.copy()
    ratio_stats_table['bin_left'] = ratio_stats_table['ratio_bin'].apply(lambda x: x.left)
    ratio_stats_table['bin_right'] = ratio_stats_table['ratio_bin'].apply(lambda x: x.right)
    ratio_stats_table['bin_center'] = ratio_stats_table['avg_ratio']

    ratio_stats_table = ratio_stats_table.rename(columns={
        'win_rate': '胜率',
        'sample_count': '样本数量',
        'sample_proportion': '样本占比',
        'bin_left': '分箱左边界',
        'bin_right': '分箱右边界',
        'bin_center': '分箱中心值'
    })

    output_cols = ['分箱左边界', '分箱右边界', '分箱中心值', '胜率', '样本数量', '样本占比']
    ratio_stats_table = ratio_stats_table[output_cols]

    ratio_stats_path = os.path.join(output_dir, "T01_length_ratio_analysis_stats.csv")
    ratio_stats_table.to_csv(ratio_stats_path, index=False, encoding='utf-8-sig')
    print(f"长度比率统计表格保存到: {ratio_stats_path}")

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

    diff_stats_table = diff_stats_table[output_cols]

    diff_stats_path = os.path.join(output_dir, "T02_length_diff_analysis_stats.csv")
    diff_stats_table.to_csv(diff_stats_path, index=False, encoding='utf-8-sig')
    print(f"长度差值统计表格保存到: {diff_stats_path}")
    
    return ratio_stats_table, diff_stats_table

def generate_analysis_report(ratio_bin_stats: pd.DataFrame, diff_bin_stats: pd.DataFrame,
                           ratio_best_bin, ratio_best_win_rate, best_avg_ratio,
                           diff_best_bin, diff_best_win_rate, best_avg_diff,
                           output_path: str = "length_preference_report.txt"):
    """生成分析报告"""
    print("生成分析报告...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("长度偏好分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 分析概况\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"长度比率分箱数量: {len(ratio_bin_stats)}\n")
        f.write(f"长度差值分箱数量: {len(diff_bin_stats)}\n")
        f.write(f"总样本量: {ratio_bin_stats['sample_count'].sum()}\n")
        f.write(f"长度比率范围: [{ratio_bin_stats['avg_ratio'].min():.2f}, {ratio_bin_stats['avg_ratio'].max():.2f}]\n")
        f.write(f"长度差值范围: [{diff_bin_stats['avg_diff'].min():.0f}, {diff_bin_stats['avg_diff'].max():.0f}]\n\n")

        f.write("2. 最优长度比率区间\n")
        f.write("-" * 40 + "\n")
        f.write(f"optimal_interval: {ratio_best_bin}\n")
        f.write(f"中心值: {best_avg_ratio:.2f} 倍\n")
        f.write(f"win_rate: {ratio_best_win_rate:.2%}\n")
        f.write(f"样本数量: {ratio_bin_stats.loc[ratio_bin_stats['avg_ratio'] == best_avg_ratio, 'sample_count'].values[0]}\n")
        f.write(f"sample_proportion: {ratio_bin_stats.loc[ratio_bin_stats['avg_ratio'] == best_avg_ratio, 'sample_proportion'].values[0]:.2%}\n\n")


        f.write("3. 最优长度差值区间\n")
        f.write("-" * 40 + "\n")
        f.write(f"optimal_interval: {diff_best_bin}\n")
        f.write(f"中心值: {best_avg_diff:.0f} tokens\n")
        f.write(f"win_rate: {diff_best_win_rate:.2%}\n")
        f.write(f"样本数量: {diff_bin_stats.loc[diff_bin_stats['avg_diff'] == best_avg_diff, 'sample_count'].values[0]}\n")
        f.write(f"sample_proportion: {diff_bin_stats.loc[diff_bin_stats['avg_diff'] == best_avg_diff, 'sample_proportion'].values[0]:.2%}\n\n")

        f.write("4. 关键统计量\n")
        f.write("-" * 40 + "\n")

        f.write("长度比率分析:\n")
        f.write(f"  平均win_rate: {ratio_bin_stats['win_rate'].mean():.3f}\n")
        f.write(f"  win_rate标准差: {ratio_bin_stats['win_rate'].std():.3f}\n")
        f.write(f"  win_rate中位数: {ratio_bin_stats['win_rate'].median():.3f}\n")
        f.write(f"  win_rate范围: [{ratio_bin_stats['win_rate'].min():.3f}, {ratio_bin_stats['win_rate'].max():.3f}]\n")

        f.write(f"  平均长度比率: {ratio_bin_stats['avg_ratio'].mean():.3f}\n")
        f.write(f"  长度比率中位数: {ratio_bin_stats['avg_ratio'].median():.3f}\n\n")
        
        f.write("长度差值分析:\n")
        f.write(f"  平均win_rate: {diff_bin_stats['win_rate'].mean():.3f}\n")
        f.write(f"  win_rate标准差: {diff_bin_stats['win_rate'].std():.3f}\n")
        f.write(f"  win_rate中位数: {diff_bin_stats['win_rate'].median():.3f}\n")
        f.write(f"  win_rate范围: [{diff_bin_stats['win_rate'].min():.3f}, {diff_bin_stats['win_rate'].max():.3f}]\n")
        
        f.write(f"  平均长度差值: {diff_bin_stats['avg_diff'].mean():.0f}\n")
        f.write(f"  长度差值中位数: {diff_bin_stats['avg_diff'].median():.0f}\n\n")

        f.write("5. 趋势分析\n")
        f.write("-" * 40 + "\n")
        
        ratio_correlation = ratio_bin_stats['avg_ratio'].corr(ratio_bin_stats['win_rate'])
        f.write(f"长度比率与win_rate的相关系数: {ratio_correlation:.3f}\n")
        
        if ratio_correlation > 0.3:
            f.write("趋势: 正相关 - 长度比率增加，win_rate倾向于增加\n")
        elif ratio_correlation < -0.3:
            f.write("趋势: 负相关 - 长度比率增加，win_rate倾向于降低\n")
        else:
            f.write("趋势: 弱相关或无显著相关\n")
        
        diff_correlation = diff_bin_stats['avg_diff'].corr(diff_bin_stats['win_rate'])
        f.write(f"\n长度差值与win_rate的相关系数: {diff_correlation:.3f}\n")
        
        if diff_correlation > 0.3:
            f.write("趋势: 正相关 - 长度差值增加，win_rate倾向于增加\n")
        elif diff_correlation < -0.3:
            f.write("趋势: 负相关 - 长度差值增加，win_rate倾向于降低\n")
        else:
            f.write("趋势: 弱相关或无显著相关\n")

        f.write("\n长度比率win_rate最高的3个分箱:\n")
        top_3 = ratio_bin_stats.nlargest(3, 'win_rate')
        for idx, row in top_3.iterrows():
            f.write(f"  分箱: {row['ratio_bin']}, win_rate: {row['win_rate']:.3f}, "
                   f"长度比率: {row['avg_ratio']:.2f}\n")

        f.write("\n长度差值win_rate最高的3个分箱:\n")
        top_3_diff = diff_bin_stats.nlargest(3, 'win_rate')
        for idx, row in top_3_diff.iterrows():
            f.write(f"  分箱: {row['diff_bin']}, win_rate: {row['win_rate']:.3f}, "
                   f"长度差值: {row['avg_diff']:.0f}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")
    
    print(f"分析报告保存到: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 80)
    print("长度偏好可视化")
    print("=" * 80)
    
    file_path = os.getcwd() + r"\Data\optimized_data\optimized_data.parquet"
    print(f"加载数据: {file_path}")
    df = pd.read_parquet(file_path)
    print(f"数据加载成功! 形状: {df.shape}")

    chart_dir = "Pictures"
    report_dir = "Reports"
    table_dir = "Tables"
    n_bins = 20
    
    os.makedirs(chart_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(table_dir, exist_ok=True)
    
    length_data = prepare_length_data(df)
    length_data_output = os.getcwd() + r"\Data\length_data\length_data.parquet"
    length_data.to_parquet(length_data_output, index=False)

    ratio_bin_stats = create_length_ratio_bins(length_data, n_bins)
    
    ratio_preference_path = os.path.join(chart_dir, "P04_length_ratio_line_chart.png")
    ratio_best_bin, ratio_best_win_rate, best_avg_ratio = plot_length_ratio_preference_chart(ratio_bin_stats, ratio_preference_path)

    diff_bin_stats = create_length_diff_bins(length_data, n_bins)
    
    diff_preference_path = os.path.join(chart_dir, "P05_length_diff_line_chart.png")
    diff_best_bin, diff_best_win_rate, best_avg_diff = plot_length_diff_preference_chart(diff_bin_stats, diff_preference_path)

    stats_table_ratio, stats_table_diff = create_statistical_table(ratio_bin_stats, diff_bin_stats, table_dir)

    report_path = os.path.join(report_dir, "R05_length_analysis_report.txt")
    generate_analysis_report(ratio_bin_stats, diff_bin_stats, 
                           ratio_best_bin, ratio_best_win_rate, best_avg_ratio,
                           diff_best_bin, diff_best_win_rate, best_avg_diff, report_path)

    print("\n" + "=" * 80)
    print("任务完成!")
    print("=" * 80)
    
    print(f"\n输出文件:")
    print(f"  1. 长度比率双轴折线图: {ratio_preference_path}")
    print(f"  2. 长度差值双轴折线图: {diff_preference_path}")
    print(f"  3. 长度比率统计表格: {os.path.join(chart_dir, 'length_ratio_analysis_stats.csv')}")
    print(f"  4. 长度差值统计表格: {os.path.join(chart_dir, 'length_diff_analysis_stats.csv')}")
    print(f"  5. 分析报告: {report_path}/R05_length_analysis_report.txt")
