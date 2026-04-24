"""
C05_touch_order

分析整合数据中 evaluation_order 字段的分布情况。

功能：
- 统计 evaluation_order 的唯一值及各值的出现次数
- 生成按 order 值排序的出现次数分布表

数据流向：
  integrated_data.parquet → order 值频率统计 → Reports/R02_order_report.txt
"""

import pandas as pd
from pathlib import Path


def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据 parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # 整合数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def touch_order(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 evaluation_order 字段，统计唯一值和出现频率。

    通过计数每个 order 值的出现次数，了解数据分布并生成详细报告。
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

    # 提前创建输出目录，避免后续保存时因目录不存在失败
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，则输出警告并返回
    print(f"正在分析文件: {file_path}")
    if not file_path.exists():
        print(f"  ERROR: 文件不存在: {file_path}")
        return

    # 读取 parquet 文件，并对读取异常进行捕获
    try:
        df : pd.DataFrame = pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取 parquet 文件失败: {exc}")
        return

    print(f"  读取成功，数据形状: {df.shape}")

    # 对 order 计数
    order_counts : pd.Series = df["evaluation_order"].value_counts()

    print(f"  发现 {len(order_counts)} 种不同的 evaluation_order 字段值")
    print(f"  分别为 {sorted(order_counts.index.tolist())}")

    # 调用报告生成函数，传入统计结果
    generate_order_report(
        file_path=file_path,
        total_rows=len(df),
        order_counts=order_counts,
        output_dir=output_dir
    )


def generate_order_report(file_path: Path, total_rows: int,
                          order_counts: pd.Series,
                          output_dir: Path) -> None:
    """
    生成 evaluation_order 分析报告。

    报告包括基本信息和出现次数分布，便于了解数据特征。
    """

    report_path : Path = output_dir / "R02_order_report.txt"

    print("=" * 80)
    print("生成分析报告...")
    print("=" * 80)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("evaluation_order 分析报告\n")
        f.write("=" * 80 + "\n\n")

        # 1. 基本信息：文件路径、总行数、唯一值数量等
        f.write("1. 基本信息\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"evaluation_order 唯一值数量: {len(order_counts)}\n\n")

        # 2. 出现次数分布：按 order 值排序显示每个值的出现次数
        f.write("2. 出现次数分布\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'Order':>5} {'出现次数':>10}\n")
        f.write("-" * 40 + "\n")
        for order, count in order_counts.sort_index().items():
            f.write(f"{order:>5}{count:>10}\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析原数据的 evaluation_order 字段")
    print("=" * 80)

    touch_order()
