import pandas as pd
from pathlib import Path
from collections import Counter
from typing import Dict, Set


def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据 parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # 整合数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def touch_model(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 model_a, model_b, winner 字段。

    统计每个模型的参与次数、胜场次数和胜率，并生成详细报告。
    胜率定义为胜场次数除以总出场次数。
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path : Path = get_integrated_parquet_path()
    else:
        file_path : Path = Path(file_path)

    # 默认输出目录为当前工作目录下的 Reports
    if output_dir is None:
        output_dir : Path = Path.cwd() / "Reports"
    else:
        output_dir : Path = Path(output_dir)

    # 提前创建输出目录，避免后续保存时因目录不存在而失败
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，则输出警告并返回
    print(f"正在分析文件: {file_path}")
    if not file_path.exists():
        print(f"  ERROR: 文件不存在: {file_path}")
        return

    # 读取 parquet 文件，并对读取异常进行捕获
    try:
        df : pd.DataFrame= pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取 parquet 文件失败: {exc}")
        return

    print(f"  读取成功，数据形状: {df.shape}")

    # 初始化统计变量
    models : Set[str] = set()  # 存储所有唯一模型名称
    model_counts : Counter = Counter()  # 统计每个模型的总出场次数
    model_wins : Counter = Counter()  # 统计每个模型的胜场次数

    # 第一遍遍历：统计模型出现次数
    # 每个模型在 model_a 或 model_b 中出现一次算一次出场
    for idx in range(len(df)):
        model_a : str = df.iloc[idx]['model_a']
        model_b : str = df.iloc[idx]['model_b']
        models.add(model_a)
        models.add(model_b)
        model_counts[model_a] += 1
        model_counts[model_b] += 1

    # 第二遍遍历：统计胜场次数
    # 只考虑 winner 为 'model_a' 或 'model_b' 的行，排除 'tie' 或 'both_bad'
    winner_df = df[df['winner'].isin(['model_a', 'model_b'])]
    for _, row in winner_df.iterrows():
        # 根据 winner 字段确定胜者模型
        # row['winner'] 是 'model_a' 或 'model_b'，row[row['winner']] 是对应的模型名
        winner_model : str = row[row['winner']]
        model_wins[winner_model] += 1

    # 计算胜率：胜场次数 / 总出场次数
    model_win_rates : Dict[str, float] = {}
    for model in models:
        # 避免除零错误，虽然理论上每个模型至少出现一次
        if model_counts[model] > 0:
            model_win_rates[model] = model_wins[model] / model_counts[model]
        else:
            model_win_rates[model] = 0.0

    print(f"  发现 {len(models)} 种不同的模型")

    # 生成报告
    generate_model_report(
        file_path=file_path,
        total_rows=len(df),
        models=models,
        model_counts=model_counts,
        model_wins=model_wins,
        model_win_rates=model_win_rates,
        output_dir=output_dir
    )


def generate_model_report(file_path: Path, total_rows: int, models: Set[str],
                          model_counts: Counter, model_wins: Counter,
                          model_win_rates: Dict[str, float], output_dir: Path) -> None:
    """
    生成模型分析报告。

    报告包括基本信息、模型出现次数排名、胜率排名以及结论，便于数据质量评估和后续分析。
    """

    report_path = output_dir / "R04_model_report.txt"

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

        # 2. 模型出现次数排名
        f.write("2. 模型出现次数排名\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'排名':^10} {'出场次数':^10} {'模型名称':^80}\n")
        f.write("-" * 100 + "\n")
        # 按出场次数降序排序
        sorted_model_counts = model_counts.most_common(len(models))
        for i, (model, count) in enumerate(sorted_model_counts, 1):
            f.write(f"{i:^10} {count:^10} {model:^80}\n")
        f.write("\n")

        # 3. 模型胜率排名
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
        avg_count = sum(model_counts.values()) / len(models) if models else 0
        f.write(f"平均模型出现次数: {avg_count:.2f}\n")

        # 找出出现次数最多和最少的模型
        if models:
            most_model = max([(m, model_counts[m]) for m in models], key=lambda x: x[1])
            least_model = min([(m, model_counts[m]) for m in models], key=lambda x: x[1])
            f.write(f"出现最多的模型: {most_model[0]} ({most_model[1]}次)\n")
            f.write(f"出现最少的模型: {least_model[0]} ({least_model[1]}次)\n\n")

            # 计算平均胜率
            avg_win_rate = sum(model_win_rates.values()) / len(models)
            f.write(f"平均模型胜率: {avg_win_rate:.2%}\n")

            # 找出胜率最高和最低的模型
            best_model = max([(m, model_win_rates[m]) for m in models], key=lambda x: x[1])
            worst_model = min([(m, model_win_rates[m]) for m in models], key=lambda x: x[1])
            f.write(f"胜率最高的模型: {best_model[0]} ({best_model[1]:.2%})\n")
            f.write(f"胜率最低的模型: {worst_model[0]} ({worst_model[1]:.2%})\n")

        f.write("\n数据可用于后续分析，注意不同模型的出场次数差异可能影响比较的可靠性。\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析 integrated_data 中的模型字段")
    print("=" * 80)

    touch_model()