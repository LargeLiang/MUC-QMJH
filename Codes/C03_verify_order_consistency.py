"""
C03_verify_order_consistency

验证整合数据中 evaluation_session_id 与 evaluation_order 的一致性。

功能：
- 按 session_id 分组，统计记录数、最大 order 值和唯一 order 数
- 检查是否存在 order 缺失（记录数 < max_order）
- 检查是否存在 order 重复（记录数 > unique_order_count）

数据流向：
  integrated_data.parquet → groupby 分组统计 → 控制台一致性结论
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

    # 原始数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def verify_order_consistency(file_path: Path | str | None = None) -> None:
    """
    验证整合数据中 evaluation_session_id 与 evaluation_order 的一致性。

    通过统计每个 session 的记录数和全局最大 evaluation_order，帮助判断是否存在缺失或重复的 order。
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path : Path = get_integrated_parquet_path()
    else:        
        file_path : Path = Path(file_path)

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

    # 先压缩到 session 分组，再基于聚合结果判断一致性
    session_summary : pd.DataFrame = (
        df.groupby("evaluation_session_id")["evaluation_order"]
        .agg(count="count", max_order="max", unique_order_count="nunique")
    )

    # 计算全局最大 session 大小和最高 evaluation_order，识别可能存在 order 问题的 session
    max_session_size : int = int(session_summary["count"].max())
    max_evaluation_order : int = int(df["evaluation_order"].max())

    # 这里使用 count 与 max_order 的关系判断是否存在缺失 order （如果 count < max_order，说明 session 中的记录数不足以覆盖从 1 到 max_order 的所有 order）
    inconsistent_order_sessions : pd.DataFrame = session_summary[
        session_summary["count"] < session_summary["max_order"]
    ]

    # 这里使用 count 与 unique_order_count 的关系判断是否存在重复 order （如果 count > unique_order_count，说明 session 中存在重复的 order 值）
    duplicate_order_sessions : pd.DataFrame = session_summary[
        session_summary["count"] > session_summary["unique_order_count"]
    ]

    inconsistent_order_count : int = len(inconsistent_order_sessions)
    duplicate_order_count : int = len(duplicate_order_sessions)

    print("=" * 80)
    print("验证结果")
    print("=" * 80)
    print(f"evaluation_session_id 总数: {len(session_summary)}")
    print(f"单个 session 最大记录数: {max_session_size}")
    print(f"全局 evaluation_order 最大值: {max_evaluation_order}")
    print(f"可能存在缺失 order 的 session 数量: {inconsistent_order_count}")
    print(f"可能存在重复 order 的 session 数量: {duplicate_order_count}")

    if inconsistent_order_count > 0 or duplicate_order_count > 0:
        print("  结论: 存在 session 的记录数、最大 order 或唯一 order 数不一致，可能存在 order 缺失或重复。")
    else:
        print("  结论: 未发现明显的 order 缺失或重复，session 记录数与 order 关系一致。")

if __name__ == "__main__":
    print("=" * 80)
    print("验证原数据的会话顺序完整性")
    print("=" * 80)

    verify_order_consistency()