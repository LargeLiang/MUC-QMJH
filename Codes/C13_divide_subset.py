"""
C13_divide_subset

按嵌套任务类别字段将优化数据集划分为分析子集。

功能：
- 依据 category_tag 内的 cw、if、math、code 四个布尔字段划分子集
- 生成四类单一类别子集（含该类别的全部行，4 个）
- 生成互不重叠的纯净分区（4^2 完全枚举）：
    · 独立类（exactly one True）：   4 个
    · 二交集（exactly two True）：   C(4,2)=6 个
    · 三交集（exactly three True）： C(4,3)=4 个
    · 四交集（all four True）：      1 个
    · 无类别（all False）：          1 个
  共 16 个互不重叠的纯净子集，覆盖全部 108k 行
- 将各子集保存为独立 parquet 文件

数据流向：
    optimized_data.parquet（108,171 行）→ 布尔掩码分组 → Data/subsets/*.parquet
  + Reports/R10_division_report.txt
"""

import pandas as pd
from pathlib import Path
from typing import Dict

from accessor import get_data_dir, get_data_path, get_output_dir

# 四个分类字段的简写，便于后续枚举引用
_SHORT = ["cw", "if", "math", "code"]


def _extract_category_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    从 category_tag 嵌套字段中提取四个分类布尔值。

    参数说明：
    - df：完整 DataFrame，要求包含 category_tag 列

    返回值：
    - 含 cw / if / math / code 四列的布尔 DataFrame
    """

    default_flags = {key: False for key in _SHORT}

    extracted = df["category_tag"].apply(
        lambda value: {key: bool(value.get(key, False)) for key in _SHORT}
        if isinstance(value, dict)
        else default_flags.copy()
    )

    return pd.DataFrame(list(extracted), index=df.index).astype(bool)


def _exact_mask(category_flags: pd.DataFrame, true_keys: list[str]) -> "pd.Series[bool]":
    """
    生成精确掩码：true_keys 中的列为 True，其余三列为 False。

    参数说明：
    - category_flags：由 _extract_category_flags 生成的布尔 DataFrame
    - true_keys：需要为 True 的字段名列表（从 _SHORT 中选取）

    返回值：
    - 布尔 Series
    """
    mask = pd.Series([True] * len(category_flags), index=category_flags.index)
    for key in _SHORT:
        if key in true_keys:
            mask &= category_flags[key] == True
        else:
            mask &= category_flags[key] == False
    return mask


def create_single_category_subsets(df: pd.DataFrame,
                                   category_flags: pd.DataFrame,
                                   output_dir: Path) -> Dict[str, int]:
    """
    创建单一分类子集（含该类别的全部行，不排除与其他类别的重叠）。

    四类：creative_writing / if / math / code，各取 bool=True 的行。
    用于"某类任务中的偏好分析"，允许与其他类别重叠。

    返回值：
    - {'subset_name': row_count, ...}
    """
    subset_stats = {}

    pairs = [
        ("cw",   "creative_writing_true"),
        ("if",   "if_true"),
        ("math", "math_true"),
        ("code", "code_true"),
    ]

    for key, name in pairs:
        sub = df[category_flags[key] == True].copy()
        sub.to_parquet(output_dir / f"{name}_data.parquet", index=False)
        subset_stats[name] = len(sub)
        print(f"  {name}: {len(sub):,} 行")

    return subset_stats


def create_exclusive_subsets(df: pd.DataFrame,
                             category_flags: pd.DataFrame,
                             output_dir: Path) -> Dict[str, int]:
    """
    创建互不重叠的纯净分区（完全枚举 2^4 = 16 个非空组合）。

    分区逻辑：精确匹配指定组合的 True/False 模式，确保 16 个子集不重叠、完全覆盖。

    子集命名规则：
    - 独立类：only_{a}
    - 二交集：{a}_{b}（字母顺序：cw < if < math < code）
    - 三交集：{a}_{b}_{c}
    - 四交集：all_categories
    - 无类别：no_category

    返回值：
    - {'subset_name': row_count, ...}
    """
    subset_stats = {}

    # 从 _BOOLS / _SHORT 构建所有 2^4=16 种组合（含空集=no_category）
    # combinations 格式：(true_index_list, file_name)
    from itertools import combinations

    combos = []

    # 无类别（空集）
    combos.append(([], "no_category"))

    # 独立类（恰好 1 个 True）
    for i in range(4):
        combos.append(([i], f"only_{_SHORT[i]}"))

    # 二交集（恰好 2 个 True），按 _SHORT 字典序
    for pair in combinations(range(4), 2):
        name = "_".join(_SHORT[j] for j in pair)
        combos.append((list(pair), name))

    # 三交集（恰好 3 个 True）
    for triple in combinations(range(4), 3):
        name = "_".join(_SHORT[j] for j in triple)
        combos.append((list(triple), name))

    # 四交集（全部 True）
    combos.append(([0, 1, 2, 3], "all_categories"))

    for true_indices, name in combos:
        true_keys = [_SHORT[i] for i in true_indices]
        mask = _exact_mask(category_flags, true_keys)
        sub = df[mask].copy()
        sub.to_parquet(output_dir / f"{name}_data.parquet", index=False)
        subset_stats[name] = len(sub)
        print(f"  {name}: {len(sub):,} 行")

    return subset_stats


def divide_data_by_category(file_path: Path | str | None = None,
                            data_dir: Path | str | None = None,
                            report_dir: Path | str | None = None) -> None:
    """
    根据 category_tag 的四个分类维度（creative_writing、if、math、code）完整划分数据集。

    子集体系：
      1. 单一分类子集：含该类别的全部行（4 个，允许重叠）
      2. 纯净分区：完全枚举 2^4=16 个精确组合（互不重叠，完全覆盖）

    参数说明：
    - file_path：优化数据文件路径（默认为 Data/optimized_data/optimized_data.parquet）
    - data_dir：子集数据保存目录（默认为 Data/subsets）
    - report_dir：报告保存目录（默认为 Reports）

    返回值：
    - 无返回值，直接输出子集 parquet 文件和划分报告
    """

    # 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path = get_data_path("optimized")
    else:
        file_path = Path(file_path)

    # 默认数据输出目录为当前工作目录下的 Data/subsets
    if data_dir is None:
        data_dir = get_data_dir("subsets")
    else:
        data_dir = Path(data_dir)

    # 默认报告输出目录为当前工作目录下的 Reports
    if report_dir is None:
        report_dir = get_output_dir("report")
    else:
        report_dir = Path(report_dir)

    # 提前创建输出目录，避免后续保存时因目录不存在而失败
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在读取优化数据: {file_path}")
    try:
        df = pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取失败 - {exc}")
        return

    print(f"  数据加载成功，形状：{df.shape}")

    if "category_tag" not in df.columns:
        print("  ERROR: 列 'category_tag' 不存在，请先运行新的 C12。")
        return

    category_flags = _extract_category_flags(df)

    all_stats: Dict = {"original_rows": len(df), "single": {}, "exclusive": {}}

    print("\n" + "=" * 80)
    print("1. 单一分类子集（含该类别，允许重叠）")
    print("-" * 80)
    all_stats["single"] = create_single_category_subsets(df, category_flags, data_dir)

    print("\n" + "=" * 80)
    print("2. 纯净分区（互不重叠，完全枚举 2^4=16 个组合）")
    print("-" * 80)
    all_stats["exclusive"] = create_exclusive_subsets(df, category_flags, data_dir)

    generate_division_report(file_path, all_stats, report_dir)


def generate_division_report(original_file: Path, stats: Dict, report_dir: Path) -> None:
    """
    生成数据集划分的统计报告。

    参数说明：
    - original_file：源优化数据文件路径
    - stats：子集划分统计信息
    - report_dir：报告输出目录

    返回值：
    - 无返回值，直接写出 R10_division_report.txt
    """

    from itertools import combinations

    report_path = report_dir / "R10_division_report.txt"
    exc = stats["exclusive"]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("数据集按任务分类划分报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 80 + "\n")
        f.write(f"源文件: {original_file}\n")
        f.write(f"原始行数: {stats['original_rows']}\n\n")

        f.write("2. 单一分类子集（含该类别，允许与其他类别重叠）\n")
        f.write("-" * 80 + "\n")
        for name, cnt in stats["single"].items():
            f.write(f"  {name:<30s}: {cnt:7,} 行\n")

        f.write("\n3. 纯净分区（互不重叠，共 16 个精确组合）\n")
        f.write("-" * 80 + "\n")

        # 无类别
        f.write(f"\n  [无类别]\n")
        f.write(f"  {'no_category':<36s}: {exc.get('no_category', 0):7,} 行\n")

        # 独立类（1个True）
        f.write(f"\n  [独立类，恰好 1 个 True]\n")
        for s in _SHORT:
            name = f"only_{s}"
            f.write(f"  {name:<36s}: {exc.get(name, 0):7,} 行\n")

        # 二交集（2个True）
        f.write(f"\n  [二交集，恰好 2 个 True，C(4,2)=6 个]\n")
        for pair in combinations(range(4), 2):
            name = "_".join(_SHORT[j] for j in pair)
            f.write(f"  {name:<36s}: {exc.get(name, 0):7,} 行\n")

        # 三交集（3个True）
        f.write(f"\n  [三交集，恰好 3 个 True，C(4,3)=4 个]\n")
        for triple in combinations(range(4), 3):
            name = "_".join(_SHORT[j] for j in triple)
            f.write(f"  {name:<36s}: {exc.get(name, 0):7,} 行\n")

        # 四交集
        f.write(f"\n  [四交集，全部 True]\n")
        f.write(f"  {'all_categories':<36s}: {exc.get('all_categories', 0):7,} 行\n")

        total_exclusive = sum(exc.values())
        f.write(f"\n  纯净分区行数合计（应等于原始行数）: {total_exclusive:,}\n")
        orig = stats["original_rows"]
        if total_exclusive == orig:
            check_str = "✓ 吻合"
        else:
            check_str = f"✗ 差异 {total_exclusive - orig}"
        f.write(f"  校验：{check_str}\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"\n划分报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("按任务分类维度划分优化后的数据集（四类：CW / IF / MATH / CODE）")
    print("=" * 80)
    print()

    divide_data_by_category()

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)

