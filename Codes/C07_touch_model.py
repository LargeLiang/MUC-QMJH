"""
C07_touch_model

分析整合数据中模型（model_a/model_b）的出场次数与胜率分布。

功能：
- 统计每个模型出现在 A/B/任意位置的次数
- 计算各模型的胜率（winner_model_a/b/tie 三类）
- 输出模型出场数排行榜及胜率汇总表

数据流向：
  integrated_data.parquet → 模型出场与胜率统计 → Reports/R04_model_report.txt
"""

import pandas as pd
from pathlib import Path
from typing import Dict

from accessor import get_path, get_dir, load_parquet_or_none


def touch_model(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 model_a, model_b, winner 字段。

    统计每个模型的参与次数、胜场次数和胜率，并生成详细报告。
    胜率定义为胜场次数除以总出场次数。

    参数说明：
    - file_path：待分析的整合数据 parquet 文件路径（默认值为 integrated_data.parquet）
    - output_dir：报告输出目录（默认值为当前工作目录下的 Reports）

    返回值：
    - 无返回值，直接输出报告文件并在控制台打印摘要
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path : Path = get_path("integrated")
    else:
        file_path : Path = Path(file_path)

    # 默认输出目录为当前工作目录下的 Reports
    if output_dir is None:
        output_dir : Path = get_dir("report")
    else:
        output_dir : Path = Path(output_dir)

    # 提前创建输出目录，避免后续保存时因目录不存在而失败
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，则输出警告并返回
    print(f"正在分析文件: {file_path}")
    df : pd.DataFrame | None = load_parquet_or_none(file_path)
    if df is None:
        return

    print(f"  读取成功，数据形状: {df.shape}")

    model_counts : pd.Series = pd.concat(
        [df["model_a"], df["model_b"]],
        ignore_index=True,
    ).value_counts()

    winner_df : pd.DataFrame = df[df["winner"].isin(["model_a", "model_b"])]
    winner_models : pd.Series = pd.concat(
        [
            winner_df.loc[winner_df["winner"] == "model_a", "model_a"],
            winner_df.loc[winner_df["winner"] == "model_b", "model_b"],
        ],
        ignore_index=True,
    )
    model_wins : pd.Series = winner_models.value_counts()

    # 计算胜率：胜场次数 / 总出场次数
    model_win_rates : Dict[str, float] = {}
    for model, count in model_counts.items():
        model_win_rates[model] = float(model_wins.get(model, 0)) / float(count)

    print(f"  发现 {len(model_counts)} 种不同的模型")

    # 生成报告
    generate_model_report(
        file_path=file_path,
        total_rows=len(df),
        model_counts=model_counts,
        model_wins=model_wins,
        model_win_rates=model_win_rates,
        output_dir=output_dir
    )


def generate_model_report(file_path: Path, total_rows: int,
                          model_counts: pd.Series, model_wins: pd.Series,
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
        f.write(f"出现的模型总数: {len(model_counts)}\n\n")

        # 2. 模型出现次数排名
        f.write("2. 模型出现次数排名\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'排名':^10} {'出场次数':^10} {'模型名称':^80}\n")
        f.write("-" * 100 + "\n")
        sorted_model_counts = list(model_counts.items())
        for i, (model, count) in enumerate(sorted_model_counts, 1):
            f.write(f"{i:^10} {count:^10} {model:^80}\n")
        f.write("\n")

        # 3. 模型胜率排名
        f.write("3. 模型胜率排名\n")
        f.write("-" * 100 + "\n")
        # 按胜率降序排序
        sorted_models = sorted(model_win_rates.keys(), key=lambda m: model_win_rates[m], reverse=True)
        f.write(f"{'排名':^10} {'总出场':^10} {'胜场':^10} {'胜率':^10} {'模型名称':^80}\n")
        f.write("-" * 100 + "\n")
        for i, model in enumerate(sorted_models, 1):
            f.write(f"{i:^10} {model_counts[model]:^10} {model_wins.get(model, 0):^10} {model_win_rates[model]:^8.2%} {model:^80}\n")
        f.write("\n")

        # 4. 结论
        f.write("4. 结论\n")
        f.write("-" * 40 + "\n")

        # 计算平均出现次数
        avg_count = float(model_counts.sum()) / len(model_counts) if not model_counts.empty else 0
        f.write(f"平均模型出现次数: {avg_count:.2f}\n")

        # 找出出现次数最多和最少的模型
        if not model_counts.empty:
            most_model = (model_counts.idxmax(), int(model_counts.max()))
            least_model = (model_counts.idxmin(), int(model_counts.min()))
            f.write(f"出现最多的模型: {most_model[0]} ({most_model[1]}次)\n")
            f.write(f"出现最少的模型: {least_model[0]} ({least_model[1]}次)\n\n")

            # 计算平均胜率
            avg_win_rate = sum(model_win_rates.values()) / len(model_win_rates)
            f.write(f"平均模型胜率: {avg_win_rate:.2%}\n")

            # 找出胜率最高和最低的模型
            best_model = max(model_win_rates.items(), key=lambda x: x[1])
            worst_model = min(model_win_rates.items(), key=lambda x: x[1])
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
