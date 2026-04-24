"""
C08_touch_role

分析整合数据中 conversation 字段内各消息的 role 标签分布。

功能：
- 遍历每条记录的 conversation 列表，统计 role 字段的取值频率
- 识别非标准 role 值（user/assistant 以外的标签）
- 输出 role 分布统计及异常示例

数据流向：
  integrated_data.parquet → conversation 解析 → role 频率统计 → Reports/R05_role_report.txt
"""

import pandas as pd
import numpy as np
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


def touch_role(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 conversation_a 和 conversation_b 的 role 字段。

    统计各侧对话中 role 标签的出现次数和种类，并生成报告，便于检查对话角色标签分布。
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

    a_role_counts: Counter = Counter()
    b_role_counts: Counter = Counter()

    def collect_role_counts(conversation: list | tuple | np.ndarray, role_counts: Counter) -> None:
        """遍历单侧对话并累计 role 频数。"""

        if not isinstance(conversation, (list, tuple, np.ndarray)):
            return

        for segment in conversation:
            if not isinstance(segment, dict):
                continue
            role : str | None = segment.get("role")
            if role is None:
                continue
            role_counts[role] += 1

    for row in df.itertuples(index=False):
        conversation_a : list | tuple | np.ndarray = getattr(row, "conversation_a")
        conversation_b : list | tuple | np.ndarray = getattr(row, "conversation_b")

        collect_role_counts(conversation_a, a_role_counts)
        collect_role_counts(conversation_b, b_role_counts)

    print(f"在 conversation_a 中发现 {len(a_role_counts)} 种不同的 role 值")
    print(f"在 conversation_b 中发现 {len(b_role_counts)} 种不同的 role 值")

    generate_role_report(
        file_path=file_path,
        total_rows=len(df),
        a_role_counts=a_role_counts,
        b_role_counts=b_role_counts,
        output_dir=output_dir,
    )


def generate_role_report(file_path: Path, total_rows: int,
                         a_role_counts: Counter, b_role_counts: Counter,
                         output_dir: Path) -> None:
    """
    生成 role 字段分析报告。
    """

    report_path = output_dir / "R05_role_report.txt"
    a_roles = set(a_role_counts.keys())
    b_roles = set(b_role_counts.keys())

    print("=" * 80)
    print("生成 role 分析报告...")
    print("=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("role 字段分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 100 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"conversation_a 中 role 种类: {len(a_roles)}\n")
        f.write(f"conversation_b 中 role 种类: {len(b_roles)}\n\n")

        f.write("2. conversation_a role 分布\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'role':^20} {'出现次数':^10}\n")
        f.write("-" * 100 + "\n")
        for role in sorted(a_role_counts.keys()):
            f.write(f"{role:^20} {a_role_counts[role]:^10}\n")
        f.write("\n")

        f.write("3. conversation_b role 分布\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'role':^20} {'出现次数':^10}\n")
        f.write("-" * 100 + "\n")
        for role in sorted(b_role_counts.keys()):
            f.write(f"{role:^20} {b_role_counts[role]:^10}\n")
        f.write("\n")

        shared_roles = sorted(a_roles.intersection(b_roles))
        f.write("4. 交集 role 说明\n")
        f.write("-" * 100 + "\n")
        f.write(f"conversation_a 与 conversation_b 共有 role 数量: {len(shared_roles)}\n")
        f.write(f"共有 role 列表: {shared_roles}\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析 role 字段")
    print("=" * 80)

    touch_role()