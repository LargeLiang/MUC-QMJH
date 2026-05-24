"""
C10_verify_token_correction

审计整合数据中 token 字段的层级、覆盖范围与可校验性。

功能：
- 校验 conversation_b 中逐消息 num_tokens 与汇总字段的对应关系
- 统计 conv_metadata 中各 token 字段的存在情况
- 明确哪些字段可直接校验，哪些字段当前只能确认存在

数据流向：
    integrated_data.parquet → token 字段审计 → Reports/R07_token_report.txt
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
from collections import Counter

from accessor import get_path, get_dir, load_parquet_or_none


TOKEN_METADATA_FIELDS = [
        "sum_assistant_a_tokens",
        "sum_assistant_b_tokens",
        "sum_user_tokens",
        "context_a_tokens",
        "context_b_tokens",
]

def verify_token_correction(file_path: Path | str | None = None,
                            output_dir: Path | str | None = None) -> None:
    """
    审计 token 字段的层级结构与一致性。

    本函数将 token 审计拆为三部分：
    1. 对 conversation_b 中逐消息 num_tokens 与 sum_user_tokens / sum_assistant_b_tokens 做一致性校验
    2. 统计 conv_metadata 中五个 token 相关字段的存在情况
    3. 明确 conversation_a 是否存在对等的逐消息 num_tokens，从而判断 sum_assistant_a_tokens 是否可直接校验

    参数说明：
    - file_path：待分析的整合数据 parquet 文件路径（默认值为 integrated_data.parquet）
    - output_dir：报告输出目录（默认值为当前工作目录下的 Reports）

    返回值：
    - 无返回值，直接输出报告文件并在控制台打印摘要
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path = get_path("integrated")
    else:
        file_path = Path(file_path)

    # 默认输出目录为当前工作目录下的 Reports
    if output_dir is None:
        output_dir = get_dir("report")
    else:
        output_dir = Path(output_dir)

    # 提前创建输出目录，避免后续保存时因目录不存在而失败
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，则输出警告并返回
    print(f"正在分析文件: {file_path}")
    df: pd.DataFrame | None = load_parquet_or_none(file_path)
    if df is None:
        return

    print(f"  读取成功，数据形状: {df.shape}")

    # 统计信息分三类：
    # 1. 汇总一致性
    # 2. 字段存在性
    # 3. 逐消息 num_tokens 覆盖范围
    token_stats: Dict[str, int | Counter | list[tuple[object, int, int, int, int]]] = {
        "total_rows": len(df),
        "mismatch_user_sum_count": 0,
        "mismatch_assistant_sum_count": 0,
        "user_exceeds_expected_count": 0,
        "missing_metadata_count": 0,
        "missing_sum_assistant_a_tokens_count": 0,
        "missing_sum_assistant_b_tokens_count": 0,
        "missing_sum_user_tokens_count": 0,
        "missing_context_a_tokens_count": 0,
        "missing_context_b_tokens_count": 0,
        "invalid_conversation_a_count": 0,
        "invalid_conversation_b_count": 0,
        "invalid_segment_count": 0,
        "conversation_a_segment_count": 0,
        "conversation_b_segment_count": 0,
        "conversation_a_rows_with_num_tokens_count": 0,
        "conversation_b_rows_with_num_tokens_count": 0,
        "conversation_a_segments_with_num_tokens_count": 0,
        "conversation_b_segments_with_num_tokens_count": 0,
        "conversation_a_assistant_segments_count": 0,
        "conversation_a_assistant_segments_with_num_tokens_count": 0,
        "conversation_b_user_segments_with_num_tokens_count": 0,
        "conversation_b_assistant_segments_with_num_tokens_count": 0,
        "metadata_token_key_presence": Counter(),
        "conversation_a_role_counts": Counter(),
        "conversation_b_role_counts": Counter(),
        "sample_mismatches": [],
    }

    for row in df.itertuples(index=False):
        row_id = getattr(row, "id", None)
        conv_meta = getattr(row, "conv_metadata", None)
        conv_a = getattr(row, "conversation_a", None)
        conv_b = getattr(row, "conversation_b", None)

        if not isinstance(conv_meta, dict):
            token_stats["missing_metadata_count"] += 1
            continue

        for field_name in TOKEN_METADATA_FIELDS:
            if field_name in conv_meta:
                token_stats["metadata_token_key_presence"][field_name] += 1

        sum_assistant_a_tokens = conv_meta.get("sum_assistant_a_tokens")
        sum_user_tokens = conv_meta.get("sum_user_tokens")
        sum_assistant_b_tokens = conv_meta.get("sum_assistant_b_tokens")
        context_a_tokens = conv_meta.get("context_a_tokens")
        context_b_tokens = conv_meta.get("context_b_tokens")

        if sum_assistant_a_tokens is None:
            token_stats["missing_sum_assistant_a_tokens_count"] += 1
        if sum_assistant_b_tokens is None:
            token_stats["missing_sum_assistant_b_tokens_count"] += 1
        if sum_user_tokens is None:
            token_stats["missing_sum_user_tokens_count"] += 1
        if context_a_tokens is None:
            token_stats["missing_context_a_tokens_count"] += 1
        if context_b_tokens is None:
            token_stats["missing_context_b_tokens_count"] += 1

        user_token_total: int = 0
        assistant_token_total: int = 0
        conv_a_has_num_tokens = False
        conv_b_has_num_tokens = False

        # 审计 conversation_a：当前重点不是求和，而是确认是否存在可与 sum_assistant_a_tokens 对照的逐消息 num_tokens。
        if isinstance(conv_a, (list, tuple, np.ndarray)):
            for segment in conv_a:
                if not isinstance(segment, dict):
                    token_stats["invalid_segment_count"] += 1
                    continue

                token_stats["conversation_a_segment_count"] += 1
                role = segment.get("role")
                num_tokens = segment.get("num_tokens")

                if role is not None:
                    token_stats["conversation_a_role_counts"][role] += 1

                if role == "assistant":
                    token_stats["conversation_a_assistant_segments_count"] += 1

                if isinstance(num_tokens, (int, float)):
                    token_stats["conversation_a_segments_with_num_tokens_count"] += 1
                    conv_a_has_num_tokens = True
                    if role == "assistant":
                        token_stats["conversation_a_assistant_segments_with_num_tokens_count"] += 1
        else:
            token_stats["invalid_conversation_a_count"] += 1

        if conv_a_has_num_tokens:
            token_stats["conversation_a_rows_with_num_tokens_count"] += 1

        # 审计 conversation_b：这里既要统计逐消息 num_tokens 的存在范围，也要做汇总一致性校验。
        if isinstance(conv_b, (list, tuple, np.ndarray)):
            for segment in conv_b:
                if not isinstance(segment, dict):
                    token_stats["invalid_segment_count"] += 1
                    continue

                token_stats["conversation_b_segment_count"] += 1
                role = segment.get("role")
                num_tokens = segment.get("num_tokens")

                if role is not None:
                    token_stats["conversation_b_role_counts"][role] += 1

                if isinstance(num_tokens, (int, float)):
                    token_stats["conversation_b_segments_with_num_tokens_count"] += 1
                    conv_b_has_num_tokens = True

                    if role == "assistant":
                        assistant_token_total += int(num_tokens)
                        token_stats["conversation_b_assistant_segments_with_num_tokens_count"] += 1
                    elif role == "user":
                        user_token_total += int(num_tokens)
                        token_stats["conversation_b_user_segments_with_num_tokens_count"] += 1
                else:
                    token_stats["invalid_segment_count"] += 1
        else:
            token_stats["invalid_conversation_b_count"] += 1

        if conv_b_has_num_tokens:
            token_stats["conversation_b_rows_with_num_tokens_count"] += 1

        # 验证 token 汇总字段与实际统计值是否一致，并记录不一致的行数和示例
        if isinstance(sum_user_tokens, (int, float)):
            if user_token_total != int(sum_user_tokens):
                token_stats["mismatch_user_sum_count"] += 1

            if user_token_total > int(sum_user_tokens):
                token_stats["user_exceeds_expected_count"] += 1

        # 验证 assistant token 汇总字段与实际统计值是否一致，并记录不一致的行数和示例
        if isinstance(sum_assistant_b_tokens, (int, float)):
            if assistant_token_total != int(sum_assistant_b_tokens):
                token_stats["mismatch_assistant_sum_count"] += 1

        # 记录部分不一致示例，限制示例数量以保持报告简洁
        if (len(token_stats["sample_mismatches"]) < 10
                and isinstance(sum_user_tokens, (int, float))
                and user_token_total != int(sum_user_tokens)):
            token_stats["sample_mismatches"].append(
                (row_id, int(sum_user_tokens), user_token_total,
                 int(sum_assistant_b_tokens) if isinstance(sum_assistant_b_tokens, (int, float)) else -1,
                 assistant_token_total)
            )

    print(f"conversation_b 中 role='user' 的 num_tokens 总和与 sum_user_tokens 是否全部一致：{token_stats['mismatch_user_sum_count'] == 0}")
    if token_stats["mismatch_user_sum_count"]:
        print(f"  反例数量: {token_stats['mismatch_user_sum_count']}")

    print(f"conversation_b 中 role='assistant' 的 num_tokens 总和与 sum_assistant_b_tokens 是否全部一致：{token_stats['mismatch_assistant_sum_count'] == 0}")
    if token_stats["mismatch_assistant_sum_count"]:
        print(f"  反例数量: {token_stats['mismatch_assistant_sum_count']}")

    print(f"conversation_b 中 role='user' 的 num_tokens 总和是否始终不大于 sum_user_tokens：{token_stats['user_exceeds_expected_count'] == 0}")
    if token_stats["user_exceeds_expected_count"]:
        print(f"  反例数量: {token_stats['user_exceeds_expected_count']}")

    print(f"conversation_a 中检测到逐消息 num_tokens 的行数: {token_stats['conversation_a_rows_with_num_tokens_count']}")
    print(f"conversation_b 中检测到逐消息 num_tokens 的行数: {token_stats['conversation_b_rows_with_num_tokens_count']}")
    print(f"缺失 sum_assistant_a_tokens 行数: {token_stats['missing_sum_assistant_a_tokens_count']}")
    print(f"缺失 context_a_tokens 行数: {token_stats['missing_context_a_tokens_count']}")
    print(f"缺失 context_b_tokens 行数: {token_stats['missing_context_b_tokens_count']}")
    print(f"缺失 conv_metadata 行数: {token_stats['missing_metadata_count']}")
    print(f"conversation_a 非列表结构或缺失行数: {token_stats['invalid_conversation_a_count']}")
    print(f"conversation_b 非列表结构或缺失行数: {token_stats['invalid_conversation_b_count']}")
    print(f"无效 segment 记录数: {token_stats['invalid_segment_count']}")

    generate_token_report(
        file_path=file_path,
        stats=token_stats,
        output_dir=output_dir,
    )


def generate_token_report(file_path: Path,
                          stats: Dict[str, int | Counter | list[tuple[object, int, int, int, int]]],
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
        f.write(f"数据总行数: {stats['total_rows']}\n")
        f.write(f"缺失 conv_metadata 的行数: {stats['missing_metadata_count']}\n")
        f.write(f"conversation_a 非列表结构或缺失的行数: {stats['invalid_conversation_a_count']}\n")
        f.write(f"conversation_b 非列表结构或缺失的行数: {stats['invalid_conversation_b_count']}\n")
        f.write(f"无效 segment 记录总数: {stats['invalid_segment_count']}\n\n")

        f.write("2. conv_metadata token 字段存在性\n")
        f.write("-" * 100 + "\n")
        for field_name in TOKEN_METADATA_FIELDS:
            present_count = stats["metadata_token_key_presence"].get(field_name, 0)
            missing_key_count = stats["total_rows"] - stats["missing_metadata_count"] - present_count
            missing_value_key = f"missing_{field_name}_count"
            missing_value_count = stats.get(missing_value_key, 0)
            f.write(f"{field_name:<24s}: key存在 {present_count:7,} 行 | key缺失 {missing_key_count:7,} 行 | value为None {missing_value_count:7,} 行\n")
        f.write("\n")

        f.write("3. conversation 逐消息 token 结构\n")
        f.write("-" * 100 + "\n")
        f.write(f"conversation_a segment 总数: {stats['conversation_a_segment_count']}\n")
        f.write(f"conversation_a 含 num_tokens 的 segment 数: {stats['conversation_a_segments_with_num_tokens_count']}\n")
        f.write(f"conversation_a 含 num_tokens 的行数: {stats['conversation_a_rows_with_num_tokens_count']}\n")
        f.write(f"conversation_a assistant segment 总数: {stats['conversation_a_assistant_segments_count']}\n")
        f.write(f"conversation_a assistant 且含 num_tokens 的 segment 数: {stats['conversation_a_assistant_segments_with_num_tokens_count']}\n")
        f.write(f"conversation_b segment 总数: {stats['conversation_b_segment_count']}\n")
        f.write(f"conversation_b 含 num_tokens 的 segment 数: {stats['conversation_b_segments_with_num_tokens_count']}\n")
        f.write(f"conversation_b 含 num_tokens 的行数: {stats['conversation_b_rows_with_num_tokens_count']}\n")
        f.write(f"conversation_b user 且含 num_tokens 的 segment 数: {stats['conversation_b_user_segments_with_num_tokens_count']}\n")
        f.write(f"conversation_b assistant 且含 num_tokens 的 segment 数: {stats['conversation_b_assistant_segments_with_num_tokens_count']}\n\n")

        f.write("conversation_a role 分布\n")
        for role, count in stats["conversation_a_role_counts"].most_common():
            f.write(f"  {role}: {count}\n")
        f.write("conversation_b role 分布\n")
        for role, count in stats["conversation_b_role_counts"].most_common():
            f.write(f"  {role}: {count}\n")
        f.write("\n")

        f.write("4. 汇总一致性校验\n")
        f.write("-" * 100 + "\n")
        f.write(f"conversation_b role='user' 的 num_tokens 与 sum_user_tokens 不一致行数: {stats['mismatch_user_sum_count']}\n")
        f.write(f"conversation_b role='assistant' 的 num_tokens 与 sum_assistant_b_tokens 不一致行数: {stats['mismatch_assistant_sum_count']}\n")
        f.write(f"conversation_b role='user' 的 num_tokens 超过 sum_user_tokens 行数: {stats['user_exceeds_expected_count']}\n\n")

        f.write("5. 审计结论\n")
        f.write("-" * 100 + "\n")
        if stats["conversation_b_segments_with_num_tokens_count"] > 0:
            f.write("- conversation_b 提供逐消息 num_tokens，可直接对照 sum_user_tokens 与 sum_assistant_b_tokens。\n")
        else:
            f.write("- conversation_b 未提供可用的逐消息 num_tokens，当前无法做汇总一致性校验。\n")

        if stats["conversation_a_assistant_segments_with_num_tokens_count"] == 0:
            f.write("- conversation_a 的 assistant 段未检测到对等的逐消息 num_tokens，因此 sum_assistant_a_tokens 当前只能确认存在，不能像 B 侧那样直接求和复核。\n")
        else:
            f.write("- conversation_a 检测到了 assistant 侧逐消息 num_tokens，可考虑后续补做 sum_assistant_a_tokens 的对等复核。\n")

        if stats["metadata_token_key_presence"].get("context_a_tokens", 0) > 0 or stats["metadata_token_key_presence"].get("context_b_tokens", 0) > 0:
            f.write("- conv_metadata 中存在 context_a_tokens 与 context_b_tokens，但本脚本当前只完成字段存在性审计，尚未确认其严格语义与下游用途。\n")

        f.write("- 原始数据未发现显式的 per-turn token 字段；当前可见的是 conv_metadata 的 Order 级汇总，以及 conversation_b 的逐消息 num_tokens。\n\n")

        f.write("6. 部分不一致示例\n")
        f.write("-" * 100 + "\n")
        if stats["sample_mismatches"]:
            f.write(f"{'id':>40} {'sum_user_tokens':>15} {'user_total':>15} {'sum_assistant_b_tokens':>25} {'assistant_total':>15}\n")
            f.write("-" * 100 + "\n")
            for row_id, expect_user, actual_user, expect_assistant, actual_assistant in stats["sample_mismatches"]:
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
