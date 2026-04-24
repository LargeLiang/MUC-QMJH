"""
C04_touch_session

分析整合数据中 evaluation_session_id 字段的分布情况。

功能：
- 统计唯一 session_id 数量及各 session 的出现次数
- 识别多次出现的 session（跨 evaluation_order 的会话）
- 生成出现次数分布表和多次出现 session 的前10详情

数据流向：
  integrated_data.parquet → session_id 频率统计 → Reports/R01_session_report.txt
"""

import pandas as pd
from pathlib import Path
from collections import Counter


def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据 parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # 整合数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def touch_session(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 evaluation_session_id 字段，统计唯一值和出现频率。

    通过计数每个 session_id 的出现次数，识别多次出现的 session，并生成详细报告。
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
        df : pd.DataFrame = pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取 parquet 文件失败: {exc}")
        return

    print(f"  读取成功，数据形状: {df.shape}")

    # 借助 Counter 统计 evaluation_session_id 的出现次数，识别多次出现的 session
    session_counts : pd.Series = df["evaluation_session_id"].value_counts()

    frequent_session_counts : pd.Series = session_counts[session_counts > 1]

    print(f"  发现 {len(session_counts)} 种不同的 evaluation_session_id 字段值")
    print(f"  发现 {len(frequent_session_counts)} 种多次出现的 evaluation_session_id 字段值")

    # 调用报告生成函数，传入统计结果
    generate_session_report(
        file_path=file_path,
        total_rows=len(df),
        session_counts=session_counts,
        frequent_session_counts=frequent_session_counts,
        output_dir=output_dir
    )


def generate_session_report(file_path: Path, total_rows: int,
                            session_counts: pd.Series,
                            frequent_session_counts: pd.Series,
                            output_dir: Path) -> None:
    """
    生成 evaluation_session_id 分析报告。

    报告包括基本信息、出现次数分布和多次出现 session 的详情，便于数据质量评估。
    """

    report_path = output_dir / "R01_session_report.txt"

    print("=" * 80)
    print("生成分析报告...")
    print("=" * 80)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("evaluation_session_id 分析报告\n")
        f.write("=" * 80 + "\n\n")

        # 1. 基本信息：文件路径、总行数、唯一值数量等
        f.write("1. 基本信息\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"evaluation_session_id 唯一值数量: {len(session_counts)}\n")
        f.write(f"多次出现的 evaluation_session_id 数量: {len(frequent_session_counts)}\n\n")

        # 2. 出现次数分布：统计每种出现次数对应的 session 数量
        f.write("2. 出现次数分布\n")
        f.write("-" * 40 + "\n")
        occurrence_distribution = Counter(session_counts.tolist())
        f.write(f"{'出现次数':>5} {'evaluation_session_id 数量':>30}\n")
        f.write("-" * 40 + "\n")
        for occ in sorted(occurrence_distribution.keys()):
            f.write(f"{occ:>5}{occurrence_distribution[occ]:>30}\n")
        f.write("\n")

        # 3. 多次出现 session 详情（前10个，按出现次数降序）
        f.write("3. 多次出现 evaluation_session_id 详情（前10个）\n")
        f.write("-" * 40 + "\n")
        sorted_frequent = list(frequent_session_counts.items())
        f.write(f"{'排名':>5} {'出现次数':>5} {'evaluation_session_id':>40}\n")
        f.write("-" * 40 + "\n")
        for i, (sid, cnt) in enumerate(sorted_frequent[:10], 1):
            f.write(f"{i:>5} {cnt:>5} {sid:>40}\n")
        f.write("\n")

        # 计算多次出现的 session 占总行数的比例
        frequent_entries = int(frequent_session_counts.sum())
        ratio = frequent_entries / total_rows if total_rows > 0 else 0
        f.write(f"多次出现的 evaluation_session_id 共包含 {frequent_entries} 行，占总行数的 {ratio:.2%}\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析原数据的 evaluation_session_id 字段")
    print("=" * 80)

    touch_session()
