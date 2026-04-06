import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def extract_header_count(header_dict):
    """从header_counts字典中提取标题总数"""
    if isinstance(header_dict, dict):
        return sum(header_dict.get(f'h{i}', 0) for i in range(1, 7))
    return 0

def extract_list_count(list_dict):
    """从list_counts字典中提取列表总数"""
    if isinstance(list_dict, dict):
        return list_dict.get('ordered', 0) + list_dict.get('unordered', 0)
    return 0

def extract_bold_count(bold_dict):
    """从bold_counts字典中提取粗体总数"""
    if isinstance(bold_dict, dict):
        return bold_dict.get('**', 0) + bold_dict.get('__', 0)
    return 0

def prepare_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    准备格式特征数据
    """
    print("准备格式特征数据...")
    
    win_df = df[~df['winner'].isin(['tie', 'both_bad'])].copy()
    print(f"过滤平局后数据量: {len(win_df)}")

    print("提取模型A的格式特征...")

    a_header_counts = win_df['a_header_counts'].apply(extract_header_count)
    a_list_counts = win_df['a_list_counts'].apply(extract_list_count)
    a_bold_counts = win_df['a_bold_counts'].apply(extract_bold_count)
    
    print("提取模型B的格式特征...")

    b_header_counts = win_df['b_header_counts'].apply(extract_header_count)
    b_list_counts = win_df['b_list_counts'].apply(extract_list_count)
    b_bold_counts = win_df['b_bold_counts'].apply(extract_bold_count)
    
    a_data_list = []
    for idx in range(len(win_df)):
        a_data = {
            'header_count': a_header_counts.iloc[idx],
            'list_count': a_list_counts.iloc[idx],
            'bold_count': a_bold_counts.iloc[idx],
            'has_header': a_header_counts.iloc[idx] > 0,
            'has_list': a_list_counts.iloc[idx] > 0,
            'has_bold': a_bold_counts.iloc[idx] > 0,
            'has_format': (a_header_counts.iloc[idx] > 0) | (a_list_counts.iloc[idx] > 0) | (a_bold_counts.iloc[idx] > 0),
            'total_format': a_header_counts.iloc[idx] + a_list_counts.iloc[idx] + a_bold_counts.iloc[idx],
            'is_winner': (win_df.iloc[idx]['winner'] == 'model_a'),
            'model': win_df.iloc[idx]['model_a']
        }
        a_data_list.append(a_data)
    
    b_data_list = []
    for idx in range(len(win_df)):
        b_data = {
            'header_count': b_header_counts.iloc[idx],
            'list_count': b_list_counts.iloc[idx],
            'bold_count': b_bold_counts.iloc[idx],
            'has_header': b_header_counts.iloc[idx] > 0,
            'has_list': b_list_counts.iloc[idx] > 0,
            'has_bold': b_bold_counts.iloc[idx] > 0,
            'has_format': (b_header_counts.iloc[idx] > 0) | (b_list_counts.iloc[idx] > 0) | (b_bold_counts.iloc[idx] > 0),
            'total_format': b_header_counts.iloc[idx] + b_list_counts.iloc[idx] + b_bold_counts.iloc[idx],
            'is_winner': (win_df.iloc[idx]['winner'] == 'model_b'),
            'model': win_df.iloc[idx]['model_b'],
        }
        b_data_list.append(b_data)

    a_df = pd.DataFrame(a_data_list)
    b_df = pd.DataFrame(b_data_list)
    format_data = pd.concat([a_df, b_df], ignore_index=True)
    
    print(f"合并后数据量: {len(format_data)} 个回答")
    
    print("=" * 80)
    return format_data

def analyze_format_presence(format_data: pd.DataFrame) -> pd.DataFrame:
    print("分析format_presence...")
    
    format_types = ['has_format', 'has_header', 'has_list', 'has_bold']

    results = []
    for type in format_types:
        win_rate_with = format_data.loc[format_data[type], 'is_winner'].mean()
        win_rate_without = format_data.loc[~format_data[type], 'is_winner'].mean()
        
        sum_with = format_data[type].sum()
        sum_without = len(format_data) - sum_with
        
        results.append({
            'format_type': type,
            'with_format_win_rate': win_rate_with,
            'without_format_win_rate': win_rate_without,
            'with_format_count': sum_with,
            'without_format_count': sum_without,
            'win_rate_diff': win_rate_with - win_rate_without
        })
    
    presence_df = pd.DataFrame(results)

    print("\nformat_presence分析结果:")
    for _, row in presence_df.iterrows():
        print(f"{row['format_type']}: with_format_win_rate = {row['with_format_win_rate']:.3f}, "
              f"without_format_win_rate = {row['without_format_win_rate']:.3f}, ")
    
    print("=" * 80)
    return presence_df

def analyze_header_count(format_data: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
    """分析 header_count 对 win_rate 的影响"""
    print("分析 header_count...")
    
    header_stats = format_data.groupby('header_count').agg({
        'is_winner': ['mean', 'count'],
    }).reset_index()
    
    header_stats.columns = ['header_count', 'win_rate', 'sample_count']
    
    total_samples = header_stats['sample_count'].sum()
    header_stats['sample_proportion'] = header_stats['sample_count'] / total_samples
    
    # 筛选掉样本量过少（<200）
    header_stats = header_stats[header_stats['sample_count'] >= 200].copy()
    
    print(header_stats)

    best_idx = header_stats['win_rate'].idxmax()
    best_header_count = header_stats.loc[best_idx, 'header_count']
    best_header_win_rate = header_stats.loc[best_idx, 'win_rate']
    
    print(f"header_count分析分组数: {len(header_stats)}")
    print(f"最优header_count: {best_header_count}, win_rate: {best_header_win_rate:.3f}")
    print("=" * 80)
    
    return header_stats, best_header_count, best_header_win_rate

def analyze_list_count(format_data: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
    """分析list_count对win_rate的影响"""
    print("分析list_count...")

    list_stats = format_data.groupby('list_count').agg({
        'is_winner': ['mean', 'count'],
    }).reset_index()
    
    list_stats.columns = ['list_count', 'win_rate', 'sample_count']
    
    total_samples = list_stats['sample_count'].sum()
    list_stats['sample_proportion'] = list_stats['sample_count'] / total_samples
    
    # 筛选掉样本量过少（<1000）
    list_stats = list_stats[list_stats['sample_count'] >= 1000].copy()

    print(list_stats)

    best_idx = list_stats['win_rate'].idxmax()
    best_list_count = list_stats.loc[best_idx, 'list_count']
    best_list_win_rate = list_stats.loc[best_idx, 'win_rate']
    
    print(f"list_count分析分组数: {len(list_stats)}")
    print(f"最优list_count: {best_list_count}, win_rate: {best_list_win_rate:.3f}")
    print("=" * 80)
    
    return list_stats, best_list_count, best_list_win_rate

def analyze_bold_count(format_data: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
    """分析bold_count对win_rate的影响"""
    print("分析bold_count...")

    bold_stats = format_data.groupby('bold_count').agg({
        'is_winner': ['mean', 'count'],
    }).reset_index()
    
    bold_stats.columns = ['bold_count', 'win_rate', 'sample_count']
    
    total_samples = bold_stats['sample_count'].sum()
    bold_stats['sample_proportion'] = bold_stats['sample_count'] / total_samples
    
    # 筛选掉样本量过少（<1000）
    bold_stats = bold_stats[bold_stats['sample_count'] >= 1000].copy()

    print(bold_stats)

    best_idx = bold_stats['win_rate'].idxmax()
    best_bold_count = bold_stats.loc[best_idx, 'bold_count']
    best_bold_win_rate = bold_stats.loc[best_idx, 'win_rate']
    
    print(f"bold_count分析分组数: {len(bold_stats)}")
    print(f"最优bold_count: {best_bold_count}, win_rate: {best_bold_win_rate:.3f}")
    print("=" * 80)
    
    return bold_stats, best_bold_count, best_bold_win_rate

def analyze_format_combinations(format_data: pd.DataFrame) -> pd.DataFrame:
    """分析format_combination对win_rate的影响"""
    print("分析format_combination...")
    
    conditions = [
        (format_data['has_list'] & ~format_data['has_header'] & ~format_data['has_bold'], 'with_list'),
        (~format_data['has_list'] & format_data['has_header'] & ~format_data['has_bold'], 'with_header'),
        (~format_data['has_list'] & ~format_data['has_header'] & format_data['has_bold'], 'with_bold'),
        (format_data['has_list'] & format_data['has_header'] & ~format_data['has_bold'], 'with_list_&_header'),
        (format_data['has_list'] & ~format_data['has_header'] & format_data['has_bold'], 'with_list_&_bold'),
        (~format_data['has_list'] & format_data['has_header'] & format_data['has_bold'], 'with_header_&_bold'),
        (format_data['has_list'] & format_data['has_header'] & format_data['has_bold'], 'with_header_&_list_&_bold'),
        (~format_data['has_list'] & ~format_data['has_header'] & ~format_data['has_bold'], 'without_format')
    ]
    
    for condition, label in conditions:
        format_data.loc[condition, 'format_combination'] = label
    
    combination_stats = format_data.groupby('format_combination').agg({
        'is_winner': ['mean', 'count'],
    }).reset_index()
    
    combination_stats.columns = ['format_combination', 'win_rate', 'sample_count']
    
    total_samples = combination_stats['sample_count'].sum()
    combination_stats['sample_proportion'] = combination_stats['sample_count'] / total_samples
    
    combination_stats = combination_stats.sort_values('win_rate', ascending=False)
    
    print(f"format_combination分析分组数: {len(combination_stats)}")
    print("\nformat_combinationwin_rate排名:")
    print(combination_stats)
    
    print("=" * 80)
    return combination_stats

def plot_presence_bar_chart(presence_df: pd.DataFrame, output_dir: str):
    """绘制format_presence条形图（仅保留胜率对比部分）"""
    print("绘制format_presence条形图...")
    
    # 创建输出目录（若不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 仅创建1个子图（删除原来的2行1列布局）
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))  # 调整高度，因仅保留一个图
    
    x = np.arange(len(presence_df))
    width = 0.35
    
    # 绘制两组并列条形图（原来的ax1改为ax）
    ax.bar(x - width/2, presence_df['with_format_win_rate'], width, 
           label='with_format', color='#4ECDC4', alpha=0.9)
    ax.bar(x + width/2, presence_df['without_format_win_rate'], width, 
           label='without_format', color='#FF6B6B', alpha=0.9)
    
    # 设置坐标轴标签、标题、刻度
    ax.set_xlabel('format_type', fontsize=14, fontweight='bold')
    ax.set_ylabel('win_rate', fontsize=14, fontweight='bold')
    ax.set_title("Format Preference Analysis - Format Presence vs Win Rate", 
                 fontsize=18, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(presence_df['format_type'], fontsize=14)
    
    # 添加网格与图例
    ax.grid(True, linestyle='--', linewidth=1, alpha=0.6, color="#FF8888")
    ax.legend(fontsize=12)
    
    # 调整布局并保存
    plt.tight_layout()
    save_path = os.path.join(output_dir, "P06_format_presence_bar_chart.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"保存到: {save_path}")
    return save_path

def plot_header_count_line_chart(header_stats: pd.DataFrame, best_header_count: float,
                           best_header_win_rate: float, output_dir: str):
    """绘制header_count折线图"""
    print("绘制header_count折线图...")
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color1 = '#FF6B6B'

    ax1.set_xlabel('header_count', fontsize=14, fontweight='bold')

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line1 = ax1.plot(header_stats['header_count'], header_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8,
                     label='win_rate', markerfacecolor='white', markeredgewidth=2) 
    
    color2 = '#4ECDC4'

    ax2 = ax1.twinx()
    
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line2 = ax2.plot(header_stats['header_count'], header_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8, 
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    

    ax1.plot(best_header_count, best_header_win_rate, 'r*', color='#FFD166', markersize=18, 
             label='best_spot')
    annotation_text = f"best_spot\nheader_count: {best_header_count}\nwin_rate: {best_header_win_rate:.2%}"
    
    ax1.annotate(annotation_text, 
                xy=(best_header_count, best_header_win_rate), 
                xytext=(best_header_count * 1.05, best_header_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=14, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    z = np.polyfit(header_stats['header_count'], header_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(header_stats['header_count'].min(), header_stats['header_count'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    ax1.set_title("Format Preference Analysis - Header Count vs Win Rate & Sample Proportion", fontsize=18, fontweight='bold')

    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#FF8888")

    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#AED1FF")

    plt.tight_layout()

    save_path = os.path.join(output_dir, "P07_header_count_line_chart.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"保存到: {save_path}")
    return save_path

def plot_list_count_line_chart(list_stats: pd.DataFrame, best_list_count: float,
                           best_list_win_rate: float, output_dir: str):
    """绘制list_count折线图"""
    print("绘制list_count折线图...")
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color1 = '#FF6B6B'

    ax1.set_xlabel('list_count', fontsize=14, fontweight='bold')

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line1 = ax1.plot(list_stats['list_count'], list_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8,
                     label='win_rate', markerfacecolor='white', markeredgewidth=2) 
    
    color2 = '#4ECDC4'

    ax2 = ax1.twinx()
    
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line2 = ax2.plot(list_stats['list_count'], list_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8, 
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    

    ax1.plot(best_list_count, best_list_win_rate, 'r*', color='#FFD166', markersize=18, 
             label='best_spot')
    annotation_text = f"best_spot\nlist_count: {best_list_count}\nwin_rate: {best_list_win_rate:.2%}"
    
    ax1.annotate(annotation_text, 
                xy=(best_list_count, best_list_win_rate), 
                xytext=(best_list_count * 0.85, best_list_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=14, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    z = np.polyfit(list_stats['list_count'], list_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(list_stats['list_count'].min(), list_stats['list_count'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    ax1.set_title("Format Preference Analysis - list Count vs Win Rate & Sample Proportion", fontsize=18, fontweight='bold')

    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#FF8888")

    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#AED1FF")

    plt.tight_layout()

    save_path = os.path.join(output_dir, "P08_list_count_line_chart.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"保存到: {save_path}")
    return save_path

def plot_bold_count_line_chart(bold_stats: pd.DataFrame, best_bold_count: float,
                           best_bold_win_rate: float, output_dir: str):
    """绘制bold_count折线图"""
    print("绘制bold_count折线图...")
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color1 = '#FF6B6B'

    ax1.set_xlabel('bold_count', fontsize=14, fontweight='bold')

    ax1.set_ylabel('win_rate', color=color1, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.3, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line1 = ax1.plot(bold_stats['bold_count'], bold_stats['win_rate'], 
                     color=color1, marker='o', linewidth=3, markersize=8,
                     label='win_rate', markerfacecolor='white', markeredgewidth=2) 
    
    color2 = '#4ECDC4'

    ax2 = ax1.twinx()
    
    ax2.set_ylabel('sample_proportion', color=color2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

    line2 = ax2.plot(bold_stats['bold_count'], bold_stats['sample_proportion'], 
                     color=color2, marker='s', linestyle='--', linewidth=3, markersize=8, 
                     label='sample_proportion', markerfacecolor='white', markeredgewidth=2)
    

    ax1.plot(best_bold_count, best_bold_win_rate, 'r*', color='#FFD166', markersize=18, 
             label='best_spot')
    annotation_text = f"best_spot\nbold_count: {best_bold_count}\nwin_rate: {best_bold_win_rate:.2%}"
    
    ax1.annotate(annotation_text, 
                xy=(best_bold_count, best_bold_win_rate), 
                xytext=(best_bold_count * 0.85, best_bold_win_rate * 0.7),
                arrowprops=dict(arrowstyle='->', color="#000000", linewidth=1.5),
                fontsize=14, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4'))

    z = np.polyfit(bold_stats['bold_count'], bold_stats['win_rate'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(bold_stats['bold_count'].min(), bold_stats['bold_count'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), color="#FF5353", linewidth=3, alpha=0.6, label='trend_line')

    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(handles1, labels1, loc='upper left', fontsize=14)

    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles2, labels2, loc='upper right', fontsize=14)

    ax1.set_title("Format Preference Analysis - bold Count vs Win Rate & Sample Proportion", fontsize=18, fontweight='bold')

    ax1.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#FF8888")

    ax2.grid(True, which='major', linestyle='--', linewidth=1, alpha=0.3, color = "#AED1FF")

    plt.tight_layout()

    save_path = os.path.join(output_dir, "P09_bold_count_line_chart.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"保存到: {save_path}")
    return save_path

def plot_combination_bar_chart(combination_stats: pd.DataFrame, output_dir: str):
    """绘制format_combination条形图"""
    print("绘制format_combination条形图...")

    display_stats = combination_stats.head(8).copy()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    bars = ax.bar(range(len(display_stats)), display_stats['win_rate'], 
                  color=plt.cm.YlOrRd(display_stats['win_rate'] / display_stats['win_rate'].max()))
    
    ax.set_xlabel('format_combination', fontsize=12, fontweight='bold')
    ax.set_ylabel('win_rate', fontsize=12, fontweight='bold')
    ax.set_title("Format Preference Analysis - Format Combination vs Win Rate", fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(display_stats)))
    ax.set_xticklabels(display_stats['format_combination'], rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    for i, (bar, row) in enumerate(zip(bars, display_stats.itertuples())):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                f'{height:.3f}\n(n={row.sample_count})',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    save_path = os.path.join(output_dir, "P10_format_combination_bar_charts.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"保存到: {save_path}")
    return save_path

def create_summary_tables(format_data: pd.DataFrame, presence_df: pd.DataFrame,
                         list_stats: pd.DataFrame, header_stats: pd.DataFrame,
                         combination_stats: pd.DataFrame, output_dir: str):
    """创建汇总统计表格"""
    print("创建统计表格...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 基本统计表
    basic_stats = format_data[['list_count', 'header_count', 'bold_count', 'total_format']].describe()
    basic_stats_path = os.path.join(output_dir, "T03_basic_statistics.csv")
    basic_stats.to_csv(basic_stats_path, encoding='utf-8-sig')
    
    # 2. format_presence表
    presence_path = os.path.join(output_dir, "T04_format_presence_analysis.csv")
    presence_df.to_csv(presence_path, index=False, encoding='utf-8-sig')
    
    # 3. header_count数量表
    if len(header_stats) > 0:
        header_path = os.path.join(output_dir, "T05_header_count_analysis.csv")
        header_stats.to_csv(header_path, index=False, encoding='utf-8-sig')

    # 4. list_count表
    if len(list_stats) > 0:
        list_path = os.path.join(output_dir, "T06_list_count_analysis.csv")
        list_stats.to_csv(list_path, index=False, encoding='utf-8-sig')

    # 5. bold_count数量表
    if len(bold_stats) > 0:
        bold_path = os.path.join(output_dir, "T07_bold_count_analysis.csv")
        bold_stats.to_csv(bold_path, index=False, encoding='utf-8-sig')
    
    # 6. format_combination表
    if len(combination_stats) > 0:
        combo_path = os.path.join(output_dir, "T08_format_combination_analysis.csv")
        combination_stats.to_csv(combo_path, index=False, encoding='utf-8-sig')
    
    print(f"统计表格已保存到: {output_dir}")
    return basic_stats_path

def generate_report(format_data: pd.DataFrame, presence_df: pd.DataFrame,
                    header_stats: pd.DataFrame, list_stats: pd.DataFrame, bold_stats: pd.DataFrame,
                    combination_stats: pd.DataFrame, best_header_count: float,
                    best_header_win_rate: float, best_list_count: float,
                    best_list_win_rate: float, best_bold_count: float,
                    best_bold_win_rate: float, output_dir: str):
    """生成分析报告"""
    print("生成分析报告...")
    
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "R06_format_analysis_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("格式偏好分析报告\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("1. 分析概况\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总sample_count: {len(format_data)} 个回答\n")
        f.write(f"with_format的sample_proportion: {format_data['has_format'].mean():.2%}\n")
        f.write(f"avg_format_count: {format_data['total_format'].mean():.2f}\n")
        f.write(f"avg_list_count: {format_data['list_count'].mean():.2f}\n")
        f.write(f"avg_header_count: {format_data['header_count'].mean():.2f}\n")
        f.write(f"avg_bold_count: {format_data['bold_count'].mean():.2f}\n\n")
        
        f.write("2. format_presence分析\n")
        f.write("-" * 40 + "\n")
        for _, row in presence_df.iterrows():
            f.write(f"{row['format_type']}:\n")
            f.write(f"  with_formatwin_rate: {row['with_format_win_rate']:.3f} (n={row['with_format_count']})\n")
            f.write(f"  without_formatwin_rate: {row['without_format_win_rate']:.3f} (n={row['without_format_count']})\n")

        f.write("3. header_count分析\n")
        f.write("-" * 40 + "\n")
        f.write(f"最优header_count: {best_header_count}\n")
        f.write(f"最优win_rate: {best_header_win_rate:.3f}\n")
        f.write(f"分析分组数: {len(header_stats)}\n\n")
        f.write("header_count与win_rate关系:\n")
        for idx, row in header_stats.iterrows():
            f.write(f"  标题数 {row['header_count']}: win_rate={row['win_rate']:.3f}, "
                    f"sample_count={row['sample_count']}, 占比={row['sample_proportion']:.2%}\n")
        f.write("\n")

        f.write("4. list_count分析\n")
        f.write("-" * 40 + "\n")
        f.write(f"最优list_count: {best_list_count}\n")
        f.write(f"最优win_rate: {best_list_win_rate:.3f}\n")
        f.write(f"分析分组数: {len(list_stats)}\n\n")
        f.write("list_count与win_rate关系:\n")
        for idx, row in list_stats.iterrows():
            f.write(f"  list_count {row['list_count']}: win_rate={row['win_rate']:.3f}, "
                    f"sample_count={row['sample_count']}, 占比={row['sample_proportion']:.2%}\n")
        f.write("\n")
        
        f.write("5. bold_count分析\n")
        f.write("-" * 40 + "\n")
        f.write(f"最优bold_count: {best_bold_count}\n")
        f.write(f"最优win_rate: {best_bold_win_rate:.3f}\n")
        f.write(f"分析分组数: {len(bold_stats)}\n\n")
        f.write("bold_count与win_rate关系:\n")
        for idx, row in bold_stats.iterrows():
            f.write(f"  bold_count {row['bold_count']}: win_rate={row['win_rate']:.3f}, "
                    f"sample_count={row['sample_count']}, 占比={row['sample_proportion']:.2%}\n")
        f.write("\n")
        
        f.write("5. format_combination分析\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析分组数: {len(combination_stats)}\n\n")
        f.write("format_combinationwin_rate排名:\n")
        for idx, row in combination_stats.iterrows():
            f.write(f"  {idx+1}. {row['format_combination']}: {row['win_rate']:.3f} "
                    f"(n={row['sample_count']}, {row['sample_proportion']:.1%})\n")
        
        f.write("6. 主要发现\n")
        f.write("-" * 40 + "\n")

        if not presence_df.empty and 'advantage_ratio' in presence_df.columns:
            if not presence_df['advantage_ratio'].isna().all():
                best_idx = presence_df['advantage_ratio'].idxmax(skipna=True)
                best_format = presence_df.loc[best_idx]
                f.write(f"最有利的格式特征: {best_format['format_type']} (优势比: {best_format['advantage_ratio']:.2f})\n")
        
        best_combo = combination_stats.iloc[0]
        f.write(f"最佳format_combination: {best_combo['format_combination']} (win_rate: {best_combo['win_rate']:.3f})\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")
    
    print(f"分析报告保存到: {report_path}")
    return report_path

if __name__ == "__main__":
    print("=" * 80)
    print("格式偏好可视化分析")
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

    format_data = prepare_format_data(df)
    format_data_output = os.path.join("Data", "format_data", "format_data.parquet")
    format_data.to_parquet(format_data_output, index=False)

    presence_df = analyze_format_presence(format_data)
    
    header_stats, best_header_count, best_header_win_rate = analyze_header_count(format_data)

    list_stats, best_list_count, best_list_win_rate = analyze_list_count(format_data)
    
    bold_stats, best_bold_count, best_bold_win_rate = analyze_bold_count(format_data)

    combination_stats = analyze_format_combinations(format_data)
    
    print("\n开始绘制图表...")
    plot_presence_bar_chart(presence_df, chart_dir)

    plot_header_count_line_chart(header_stats, best_header_count, best_header_win_rate, chart_dir)
    plot_list_count_line_chart(list_stats, best_list_count, best_list_win_rate, chart_dir)
    plot_bold_count_line_chart(bold_stats, best_bold_count, best_bold_win_rate, chart_dir)

    plot_combination_bar_chart(combination_stats, chart_dir)
    
    create_summary_tables(format_data, presence_df, list_stats, header_stats, combination_stats, table_dir)
    
    generate_report(format_data, presence_df, header_stats, list_stats, bold_stats, combination_stats,
                    best_header_count, best_header_win_rate, best_list_count, best_list_win_rate,
                    best_bold_count, best_bold_win_rate, report_dir)
    
    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)
   
    print(f"\n输出文件:")
    print(f"1. format_presence条形图: {chart_dir}/P06_format_presence_bar_chart.png")
    print(f"2. header_count折线图: {chart_dir}/P07_header_count_line_chart.png")
    print(f"3. list_count折线图: {chart_dir}/P08_list_count_line_chart.png")
    print(f"4. bold_count折线图: {chart_dir}/P09_bold_count_line_chart.png")
    print(f"5. format_combination条形图: {chart_dir}/P10_format_combination_bar_chart.png")
    print(f"6. 基本统计表格：{table_dir}/T03_basic_statistics.csv")
    print(f"7. format_presence统计表格：{table_dir}/T04_format_presence_analysis.csv")
    print(f"8. header_count统计表格：{table_dir}/T05_header_count_analysis.csv")
    print(f"9. list_count统计表格：{table_dir}/T06_list_count_analysis.csv")
    print(f"10. bold_count统计表格：{table_dir}/T07_bold_count_analysis.csv")
    print(f"11. format_combination统计表格：{table_dir}/T08_format_combination_analysis.csv")
    print(f"12. 分析报告: {report_dir}/R06_format_analysis_report.txt")