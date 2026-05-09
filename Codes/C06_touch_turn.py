"""
C06_touch_turn

分析整合数据中 turns 字段的分布及其与 conversation 结构的一致性。

功能：
- 统计 turns 字段的唯一值及各值出现次数
- 与 conversation 字段中实际对话轮次数进行交叉核验
- 识别 turns 记录值与实际对话轮次不一致的记录

数据流向：
  integrated_data.parquet → turns 分布统计 + 一致性校验 → Reports/R03_turn_report.txt
"""

import pandas as pd
from pathlib import Path
from collections import Counter

from accessor import get_data_path, get_output_dir, load_parquet_or_none


def touch_turn(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 turns 值，并验证对话长度与 turns 字段的关系。

    该函数统计每个 turns 的出现频率，检查 conversation_a 和 conversation_b 的长度是否匹配，
    以及 conv_a 长度是否与 turns 关系一致。

    参数说明：
    - file_path：待分析的整合数据 parquet 文件路径（默认值为 integrated_data.parquet）
    - output_dir：报告输出目录（默认值为当前工作目录下的 Reports）

    返回值：
    - 无返回值，直接输出报告文件并在控制台打印摘要
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path : Path = get_data_path("integrated")
    else:
        file_path : Path = Path(file_path)

    # 默认输出目录为当前工作目录下的 Reports
    if output_dir is None:
        output_dir : Path = get_output_dir("report")
    else:
        output_dir : Path = Path(output_dir)

    # 提前创建输出目录，避免后续写入失败
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，则输出警告并返回
    print(f"正在分析文件: {file_path}")
    df : pd.DataFrame | None = load_parquet_or_none(file_path)
    if df is None:
        return

    print(f"  读取成功，数据形状: {df.shape}")

    required_columns : set[str] = {"id", "conversation_a", "conversation_b", "conv_metadata"}
    missing_columns : set[str] = required_columns.difference(df.columns)
    if missing_columns:
        print(f"  ERROR: 缺少必要字段: {sorted(missing_columns)}")
        return

    # 用于统计各 turns 值出现频率
    turn_counts : Counter = Counter()

    # 保留异常 id 集合，是因为需要给出反例示例，不能只保留计数
    mismatch_conv_length_ids : set[object] = set()
    mismatch_turn_ids : set[object] = set()

    for row in df.itertuples(index=False):
        row_id = getattr(row, "id")
        conv_a = getattr(row, "conversation_a")
        conv_b = getattr(row, "conversation_b")
        conv_meta = getattr(row, "conv_metadata")

        # conv_metadata 里应包含 turns 字段，否则视为异常
        turn = conv_meta.get("turns") if isinstance(conv_meta, dict) else None
        if turn is None:
            print(f"  WARNING: 行 {row_id} 的 conv_metadata 缺少 turns 字段，已跳过该行的 turns 统计")
            continue

        turn_counts[turn] += 1

        if len(conv_a) != len(conv_b):
            mismatch_conv_length_ids.add(row_id)

        expected_turn : int = len(conv_a) // 2
        if expected_turn != turn:
            mismatch_turn_ids.add(row_id)

    print(f"发现 {len(turn_counts)} 种不同的 turns 字段值")
    print(f"  len(conv_a) 是否总等于 len(conv_b)：{not mismatch_conv_length_ids}")
    if mismatch_conv_length_ids:
        print(f"  反例数量: {len(mismatch_conv_length_ids)}，示例 id: {list(mismatch_conv_length_ids)[:10]}")

    print(f"  len(conv_a) / 2 是否总等于 turn：{not mismatch_turn_ids}")
    if mismatch_turn_ids:
        print(f"  反例数量: {len(mismatch_turn_ids)}，示例 id: {list(mismatch_turn_ids)[:10]}")

    generate_turn_report(
        file_path=file_path,
        total_rows=len(df),
        turn_counts=turn_counts,
        mismatch_conv_length_count=len(mismatch_conv_length_ids),
        mismatch_turn_count=len(mismatch_turn_ids),
        output_dir=output_dir,
    )


def generate_turn_report(file_path: Path, total_rows: int,
                         turn_counts: Counter,
                         mismatch_conv_length_count: int,
                         mismatch_turn_count: int,
                         output_dir: Path) -> None:
    """
    生成 turns 字段分析报告。

    报告包含基本统计、turns 分布以及长度一致性检查结果。
    """

    report_path = output_dir / "R03_turn_report.txt"

    print("=" * 80)
    print("生成分析报告...")
    print("=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("turns 字段分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 40 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"turns 唯一值数量: {len(turn_counts)}\n")
        f.write(f"conv_a / conv_b 长度不一致记录数: {mismatch_conv_length_count}\n")
        f.write(f"len(conv_a)/2 与 turns 不匹配记录数: {mismatch_turn_count}\n\n")

        f.write("2. turns 数量分布\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'turns':>5} {'数量':>10}\n")
        f.write("-" * 80 + "\n")
        for turn in sorted(turn_counts.keys()):
            f.write(f"{turn:>5}{turn_counts[turn]:>10}\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析原数据的 turns 字段，并验证与 conversation 结构的一致性")
    print("=" * 80)

    touch_turn()