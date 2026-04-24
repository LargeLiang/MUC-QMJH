"""
C09_touch_cont

分析整合数据中 conversation 字段内各消息的 content 结构特征。

功能：
- 检测 content 字段的数据类型（str / list / None）
- 统计多模态内容（content 为列表时）的结构分布
- 识别空内容、超长内容等异常情况

数据流向：
  integrated_data.parquet → conversation 解析 → content 类型统计 → Reports/R06_cont_report.txt
"""

import numpy as np
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


def touch_cont(file_path: Path | str | None = None, output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中 conversation_a 和 conversation_b 的 content 结构。

    统计 content 长度分布，以及 type、text、image、mimeType 的分布情况。
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
        df: pd.DataFrame = pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取 parquet 文件失败: {exc}")
        return

    print(f"  读取成功，数据形状: {df.shape}")

    # 初始化统计变量，包括 content 列表长度分布、次级字段分布，以及缺失 content 的行级计数
    a_cont_item_counts: Counter = Counter()
    b_cont_item_counts: Counter = Counter()
    a_missing_cont_count: int = 0
    b_missing_cont_count: int = 0

    # 由于 content 字段是一个列表，我们需要统计每条记录中 content 列表的长度分布，以及其中各项的 type、text、image、mimeType 分布。
    a_type_counts: Counter = Counter()
    a_text_counts: Counter = Counter()
    a_image_counts: Counter = Counter()
    a_mimeType_counts: Counter = Counter()

    b_type_counts: Counter = Counter()
    b_text_counts: Counter = Counter()
    b_image_counts: Counter = Counter()
    b_mimeType_counts: Counter = Counter()

    # 定义一个辅助函数，用于安全地将 content 字段转换为列表，避免因数据格式问题导致的异常
    def normalize_content_list(content) -> list:
        if isinstance(content, (list, tuple, np.ndarray)):
            return list(content)
        return []

    def update_content_stats(
        conversation,
        cont_item_counts: Counter,
        type_counts: Counter,
        text_counts: Counter,
        image_counts: Counter,
        mime_type_counts: Counter,
    ) -> bool:
        """遍历单侧对话并累计 content 相关统计，返回该行是否出现空 content。"""

        has_missing_content = False
        for side in normalize_content_list(conversation):
            if not isinstance(side, dict):
                continue

            content : list = normalize_content_list(side.get("content"))
            cont_item_counts[len(content)] += 1

            if len(content) == 0:
                has_missing_content = True
                continue

            for item in content:
                if not isinstance(item, dict):
                    continue
                type_counts[item.get("type") or "<missing>"] += 1
                text_counts[item.get("text") or "<missing>"] += 1
                image_counts[item.get("image") or "<missing>"] += 1
                mime_type_counts[item.get("mimeType") or "<missing>"] += 1

        return has_missing_content

    for row in df.itertuples(index=False):
        conversation_a : list = getattr(row, "conversation_a")
        conversation_b : list = getattr(row, "conversation_b")

        # 方法：空 content 仅用于计数时，不再维护整套 id 集合；逐行布尔返回即可保留原语义。
        a_missing_cont_count += int(update_content_stats(
            conversation_a,
            a_cont_item_counts,
            a_type_counts,
            a_text_counts,
            a_image_counts,
            a_mimeType_counts,
        ))
        b_missing_cont_count += int(update_content_stats(
            conversation_b,
            b_cont_item_counts,
            b_type_counts,
            b_text_counts,
            b_image_counts,
            b_mimeType_counts,
        ))

    print(f"在 conversation_a 中发现 {len(a_cont_item_counts)} 种 len(content) 值")
    print(f"在 conversation_b 中发现 {len(b_cont_item_counts)} 种 len(content) 值")
    print(f"conversation_a 缺失 content 的行数: {a_missing_cont_count}")
    print(f"conversation_b 缺失 content 的行数: {b_missing_cont_count}")

    generate_cont_report(
        file_path=file_path,
        total_rows=len(df),
        a_cont_item_counts=a_cont_item_counts,
        b_cont_item_counts=b_cont_item_counts,
        a_type_counts=a_type_counts,
        b_type_counts=b_type_counts,
        a_text_counts=a_text_counts,
        b_text_counts=b_text_counts,
        a_image_counts=a_image_counts,
        b_image_counts=b_image_counts,
        a_mimeType_counts=a_mimeType_counts,
        b_mimeType_counts=b_mimeType_counts,
        a_missing_cont_count=a_missing_cont_count,
        b_missing_cont_count=b_missing_cont_count,
        output_dir=output_dir,
    )


def generate_cont_report(file_path: Path, total_rows: int,
                         a_cont_item_counts: Counter,
                         b_cont_item_counts: Counter,
                         a_type_counts: Counter,
                         b_type_counts: Counter,
                         a_text_counts: Counter,
                         b_text_counts: Counter,
                         a_image_counts: Counter,
                         b_image_counts: Counter,
                         a_mimeType_counts: Counter,
                         b_mimeType_counts: Counter,
                         a_missing_cont_count: int,
                         b_missing_cont_count: int,
                         output_dir: Path) -> None:
    """生成 content 字段分析报告。"""

    report_path = output_dir / "R06_cont_report.txt"
    print("=" * 80)
    print("生成 content 分析报告...")
    print("=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("content 字段分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 100 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"conversation_a 缺失 content 行数: {a_missing_cont_count}\n")
        f.write(f"conversation_b 缺失 content 行数: {b_missing_cont_count}\n\n")

        f.write("2. conversation_a content 长度分布\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'len(content)':>12} {'数量':>10}\n")
        f.write("-" * 100 + "\n")
        for length in sorted(a_cont_item_counts.keys()):
            f.write(f"{length:>12} {a_cont_item_counts[length]:>10}\n")
        f.write("\n")

        f.write("3. conversation_b content 长度分布\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'len(content)':>12} {'数量':>10}\n")
        f.write("-" * 100 + "\n")
        for length in sorted(b_cont_item_counts.keys()):
            f.write(f"{length:>12} {b_cont_item_counts[length]:>10}\n")
        f.write("\n")

        f.write("4. conversation_a content 次级字段分布\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, a_type_counts, "type")
        write_counter_section(f, a_text_counts, "text", top_n=10)
        write_counter_section(f, a_image_counts, "image")
        write_counter_section(f, a_mimeType_counts, "mimeType")

        f.write("5. conversation_b content 次级字段分布\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, b_type_counts, "type")
        write_counter_section(f, b_text_counts, "text", top_n=10)
        write_counter_section(f, b_image_counts, "image")
        write_counter_section(f, b_mimeType_counts, "mimeType")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


def write_counter_section(f, counter: Counter, label: str, top_n: int = 5) -> None:
    """将 Counter 统计结果写入报告，默认只显示 top_n 项。"""
    f.write(f"{label} 值种类: {len(counter)}\n")
    f.write(f"{label} 值列表（前 {top_n}）：{[item for item, _ in counter.most_common(top_n)]}\n")
    f.write(f"{label} 分布（前 {top_n}）：\n")
    for value, count in counter.most_common(top_n):
        f.write(f"  {value!r}: {count}\n")
    f.write("\n")


if __name__ == "__main__":
    print("=" * 80)
    print("分析 content 字段")
    print("=" * 80)

    touch_cont()