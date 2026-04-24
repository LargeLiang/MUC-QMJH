"""
C10_verify_token_correction

校验整合数据中汇总 token 字段与各明细 token 字段之间的一致性。

功能：
- 对 sum_assistant_a_tokens 等汇总字段与明细字段求和进行比对
- 识别汇总值与明细之和不一致的记录数和比例
- 输出各字段的校验通过率

数据流向：
  integrated_data.parquet → token 字段求和比对 → Reports/R07_token_correction_report.txt
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


def verify_token_correction(file_path: Path | str | None = None,
                            output_dir: Path | str | None = None) -> None:
    """
    验证 conversation_b 内 num_tokens 之和是否与 conv_metadata 中的汇总字段一致。

    主要检查点：
    1. conversation_b 中 role='user' 的 num_tokens 总和是否等于 sum_user_tokens。
    2. conversation_b 中 role='assistant' 的 num_tokens 总和是否等于 sum_assistant_b_tokens。
    3. conversation_b 中 role='user' 的 num_tokens 总和是否总是小于等于 sum_user_tokens。
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path = get_integrated_parquet_path()
    else:
        file_path = Path(file_path)

    # 默认输出目录为当前工作目录下的 Reports
    if output_dir is None:
        output_dir = Path.cwd() / "Reports"
    else:
        output_dir = Path(output_dir)

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

    # 方法：仅对需要追溯示例的异常保留样本列表，其余异常只维护计数即可。
    mismatch_user_sum_count: int = 0
    mismatch_assistant_sum_count: int = 0
    user_exceeds_expected_count: int = 0
    missing_metadata_count: int = 0
    missing_token_columns_count: int = 0
    invalid_conversation_b_count: int = 0
    invalid_segment_count: int = 0
    role_counts: Counter = Counter()
    sample_mismatches: list[tuple[object, int, int, int, int]] = []

    for row in df.itertuples(index=False):
        row_id = getattr(row, "id", None)
        conv_meta = getattr(row, "conv_metadata", None)
        conv_b = getattr(row, "conversation_b", None)

        if not isinstance(conv_meta, dict):
            missing_metadata_count += 1
            continue

        sum_user_tokens = conv_meta.get("sum_user_tokens")
        sum_assistant_b_tokens = conv_meta.get("sum_assistant_b_tokens")

        if sum_user_tokens is None or sum_assistant_b_tokens is None:
            missing_token_columns_count += 1

        user_token_total: int = 0
        assistant_token_total: int = 0

        # 验证 conversation_b 结构是否为列表，并统计 role 分布及 num_tokens 汇总
        if isinstance(conv_b, (list, tuple, np.ndarray)):
            for segment in conv_b:
                if not isinstance(segment, dict):
                    invalid_segment_count += 1
                    continue

                role = segment.get("role")
                num_tokens = segment.get("num_tokens")

                if role is None or not isinstance(num_tokens, (int, float)):
                    invalid_segment_count += 1
                    continue

                role_counts[role] += 1
                if role == "assistant":
                    assistant_token_total += int(num_tokens)
                else:
                    user_token_total += int(num_tokens)
        else:
            invalid_conversation_b_count += 1

        # 验证 token 汇总字段与实际统计值是否一致，并记录不一致的行数和示例
        if isinstance(sum_user_tokens, (int, float)):
            if user_token_total != int(sum_user_tokens):
                mismatch_user_sum_count += 1

            if user_token_total > int(sum_user_tokens):
                user_exceeds_expected_count += 1

        # 验证 assistant token 汇总字段与实际统计值是否一致，并记录不一致的行数和示例
        if isinstance(sum_assistant_b_tokens, (int, float)):
            if assistant_token_total != int(sum_assistant_b_tokens):
                mismatch_assistant_sum_count += 1

        # 记录部分不一致示例，限制示例数量以保持报告简洁
        if len(sample_mismatches) < 10 and isinstance(sum_user_tokens, (int, float)) and user_token_total != int(sum_user_tokens):
            sample_mismatches.append(
                (row_id, int(sum_user_tokens), user_token_total,
                 int(sum_assistant_b_tokens) if isinstance(sum_assistant_b_tokens, (int, float)) else -1,
                 assistant_token_total)
            )

    print(f"conversation_b 中 role='user' 的 num_tokens 总和与 sum_user_tokens 是否全部一致：{mismatch_user_sum_count == 0}")
    if mismatch_user_sum_count:
        print(f"  反例数量: {mismatch_user_sum_count}")

    print(f"conversation_b 中 role='assistant' 的 num_tokens 总和与 sum_assistant_b_tokens 是否全部一致：{mismatch_assistant_sum_count == 0}")
    if mismatch_assistant_sum_count:
        print(f"  反例数量: {mismatch_assistant_sum_count}")

    print(f"conversation_b 中 role='user' 的 num_tokens 总和是否始终不大于 sum_user_tokens：{user_exceeds_expected_count == 0}")
    if user_exceeds_expected_count:
        print(f"  反例数量: {user_exceeds_expected_count}")

    print(f"缺失 conv_metadata 行数: {missing_metadata_count}")
    print(f"缺失 token 汇总字段行数: {missing_token_columns_count}")
    print(f"conversation_b 非列表结构或缺失行数: {invalid_conversation_b_count}")
    print(f"无效 segment 记录数: {invalid_segment_count}")

    generate_token_report(
        file_path=file_path,
        total_rows=len(df),
        mismatch_user_sum_count=mismatch_user_sum_count,
        mismatch_assistant_sum_count=mismatch_assistant_sum_count,
        user_exceeds_expected_count=user_exceeds_expected_count,
        missing_metadata_count=missing_metadata_count,
        missing_token_columns_count=missing_token_columns_count,
        invalid_conversation_b_count=invalid_conversation_b_count,
        invalid_segment_count=invalid_segment_count,
        role_counts=role_counts,
        sample_mismatches=sample_mismatches,
        output_dir=output_dir,
    )


def generate_token_report(file_path: Path, total_rows: int,
                          mismatch_user_sum_count: int,
                          mismatch_assistant_sum_count: int,
                          user_exceeds_expected_count: int,
                          missing_metadata_count: int,
                          missing_token_columns_count: int,
                          invalid_conversation_b_count: int,
                          invalid_segment_count: int,
                          role_counts: Counter,
                          sample_mismatches: list[tuple[object, int, int, int, int]],
                          output_dir: Path) -> None:
    """生成 token 校验分析报告。"""

    report_path = output_dir / "R07_token_report.txt"

    print("=" * 80)
    print("生成 token 校验分析报告...")
    print("=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("token 校验分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 100 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"conversation_b role='user' 的 num_tokens 与 sum_user_tokens 不一致行数: {mismatch_user_sum_count}\n")
        f.write(f"conversation_b role='assistant' 的 num_tokens 与 sum_assistant_b_tokens 不一致行数: {mismatch_assistant_sum_count}\n")
        f.write(f"conversation_b role='user' 的 num_tokens 超过 sum_user_tokens 行数: {user_exceeds_expected_count}\n")
        f.write(f"缺失 conv_metadata 的行数: {missing_metadata_count}\n")
        f.write(f"缺失 token 汇总字段的行数: {missing_token_columns_count}\n")
        f.write(f"conversation_b 非列表结构或缺失的行数: {invalid_conversation_b_count}\n")
        f.write(f"无效 segment 记录总数: {invalid_segment_count}\n\n")

        f.write("2. conversation_b role 分布\n")
        f.write("-" * 100 + "\n")
        f.write(f"role 类型数量: {len(role_counts)}\n")
        for role, count in role_counts.most_common():
            f.write(f"{role}: {count}\n")
        f.write("\n")

        f.write("3. 部分不一致示例\n")
        f.write("-" * 100 + "\n")
        if sample_mismatches:
            f.write(f"{'id':>40} {'sum_user_tokens':>15} {'user_total':>15} {'sum_assistant_b_tokens':>25} {'assistant_total':>15}\n")
            f.write("-" * 100 + "\n")
            for row_id, expect_user, actual_user, expect_assistant, actual_assistant in sample_mismatches:
                f.write(f"{str(row_id):>40} {expect_user:>15} {actual_user:>15} {expect_assistant:>25} {actual_assistant:>15}\n")
        else:
            f.write("无不一致示例。\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("分析 token 相关字段")
    print("=" * 80)

    verify_token_correction()