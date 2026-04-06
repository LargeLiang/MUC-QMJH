import pandas as pd
import os
from collections import Counter
from typing import Dict, Set

def touch_model():
    """
    分析 model_a, model_b, winner字段
    统计每个模型的参与次数、胜率等，并生成报告。
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"
    print(f"正在分析文件: {file_path}")

    df = pd.read_parquet(file_path)
    print(f"  数据形状: {df.shape}")

    # 统计模型出现次数
    models = set()
    model_counts = Counter()

    for idx in range(len(df)):
        model_a, model_b = df.iloc[idx]['model_a'], df.iloc[idx]['model_b']
        models.add(model_a)
        models.add(model_b)
        model_counts[model_a] += 1
        model_counts[model_b] += 1

    model_wins = Counter()
    # 筛选 winner 为 'model_a' 或 'model_b' 的行（排除 tie / both_bad）
    winner_df = df[df['winner'].isin(['model_a', 'model_b'])]
    for _, row in winner_df.iterrows():
        model_wins[row[row['winner']]] += 1

    # 计算胜率（胜场 / 总出场次数）
    model_win_rates = {}
    for model in models:
        model_win_rates[model] = model_wins[model] / model_counts[model]
    
    print(f"  发现 {len(models)} 种 Model：")

    # 生成报告
    generate_model_report(
        file_path=file_path,
        total_rows=len(df),
        models=models,
        model_counts=model_counts,
        model_wins=model_wins,
        model_win_rates=model_win_rates
    )

def generate_model_report(file_path: str, total_rows: int, models: Set[str],
                          model_counts: Counter, model_wins: Counter,
                          model_win_rates: Dict[str, float], output_dir: str = os.getcwd() + r"\Reports"):
    """
    生成 Model 分析报告
    """
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "R04_model_report.txt")

    print("=" * 80)
    print("生成模型分析报告...")
    print("=" * 80)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Model 分析报告\n")
        f.write("=" * 80 + "\n\n")

        # 1. 基本信息
        f.write("1. 基本信息\n")
        f.write("-" * 100 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"出现的模型总数: {len(models)}\n\n")

        # 2. 模型出现次数
        f.write("2. 模型出现次数\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'排名':^10} {'出场次数':^10} {'模型名称':^80}\n")
        f.write("-" * 100 + "\n")
        sorted_model_counts = model_counts.most_common(len(models))
        for i, (model, count) in enumerate(sorted_model_counts, 1):
            f.write(f"{i:^10} {count:^10} {model:^80}\n")
        f.write("\n")

        # 3. 模型胜率
        f.write("3. 模型胜率排名\n")
        f.write("-" * 100 + "\n")
        # 按胜率降序排序
        sorted_models = sorted(models, key=lambda m: model_win_rates[m], reverse=True)
        f.write(f"{'排名':^10} {'总出场':^10} {'胜场':^10} {'胜率':^10} {'模型名称':^80}\n")
        f.write("-" * 100 + "\n")
        for i, model in enumerate(sorted_models, 1):
            f.write(f"{i:^10} {model_counts[model]:^10} {model_wins.get(model, 0):^10} {model_win_rates[model]:^8.2%} {model:^80}\n")
        f.write("\n")

        # 4. 结论
        f.write("4. 结论\n")
        f.write("-" * 40 + "\n")

        # 计算平均出现次数
        avg_count = sum(model_counts.values()) / len(models)
        f.write(f"平均模型出现次数: {avg_count}\n")

        most_model = max([(m, model_counts[m]) for m in models], key=lambda x: x[1])
        least_model = min([(m, model_counts[m]) for m in models], key=lambda x: x[1])
        f.write(f"出现最多的模型: {most_model[0]} ({most_model[1]}次)\n")
        f.write(f"出现最少的模型: {least_model[0]} ({least_model[1]}次)\n\n")

        # 计算平均胜率
        avg_win_rate = sum(model_win_rates.values()) / len(models)
        f.write(f"平均模型胜率: {avg_win_rate:.2%}\n")

        best_model = max([(m, model_win_rates[m]) for m in models], key=lambda x: x[1])
        worst_model = min([(m, model_win_rates[m]) for m in models], key=lambda x: x[1])
        f.write(f"胜率最高的模型: {best_model[0]} ({best_model[1]:.2%})\n")
        f.write(f"胜率最低的模型: {worst_model[0]} ({worst_model[1]:.2%})\n")


        f.write("数据可用于后续分析，注意不同模型的出场次数差异可能影响比较的可靠性。\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")

if __name__ == "__main__":
    print("=" * 80)
    print("分析 integrated_data 中的模型字段")
    touch_model()