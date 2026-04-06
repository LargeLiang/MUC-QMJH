import pandas as pd
from pathlib import Path
from typing import Dict


def get_optimized_parquet_path(root: Path | str | None = None) -> Path:
    """返回优化数据 parquet 文件的默认路径。"""

    if root is None:
        root = Path.cwd()
    root_path = Path(root)

    # 优化数据文件位于项目根目录下的 Data/optimized_data/optimized_data.parquet
    return root_path / "Data" / "optimized_data" / "optimized_data.parquet"


def create_single_category_subsets(df: pd.DataFrame, output_dir: Path) -> Dict[str, int]:
    """
    创建单一分类子集。

    对于每个分类维度（creative_writing、if、math），将数据分为True和False两个子集。
    原因：某些分析可能只关注属于或不属于某类别的样本。

    返回：{'subset_name': row_count, ...}
    """
    
    subset_stats = {}

    # 1. 创意写作子集：分离属于和不属于创意写作类别的样本
    cw_true = df[df["creative_writing_bool"] == True].copy()
    cw_false = df[df["creative_writing_bool"] == False].copy()
    
    cw_true.to_parquet(output_dir / "creative_writing_true_data.parquet", index=False)
    cw_false.to_parquet(output_dir / "creative_writing_false_data.parquet", index=False)
    
    subset_stats["creative_writing_true"] = len(cw_true)
    subset_stats["creative_writing_false"] = len(cw_false)
    print(f"  创意写作子集：True {len(cw_true)} 行，False {len(cw_false)} 行")

    # 2. 指令遵循子集：分离属于和不属于指令遵循类别的样本
    if_true = df[df["if_bool"] == True].copy()
    if_false = df[df["if_bool"] == False].copy()
    
    if_true.to_parquet(output_dir / "if_true_data.parquet", index=False)
    if_false.to_parquet(output_dir / "if_false_data.parquet", index=False)
    
    subset_stats["if_true"] = len(if_true)
    subset_stats["if_false"] = len(if_false)
    print(f"  指令遵循子集：True {len(if_true)} 行，False {len(if_false)} 行")

    # 3. 数学子集：分离属于和不属于数学类别的样本
    math_true = df[df["math_bool"] == True].copy()
    math_false = df[df["math_bool"] == False].copy()
    
    math_true.to_parquet(output_dir / "math_true_data.parquet", index=False)
    math_false.to_parquet(output_dir / "math_false_data.parquet", index=False)
    
    subset_stats["math_true"] = len(math_true)
    subset_stats["math_false"] = len(math_false)
    print(f"  数学子集：True {len(math_true)} 行，False {len(math_false)} 行")

    return subset_stats


def create_pure_subsets(df: pd.DataFrame, output_dir: Path) -> Dict[str, int]:
    """
    创建纯净子集（仅属于一个分类）。

    这些子集用于分离只属于单一类别的样本，用于分类特异性分析。
    例如 only_creative_writing 包含创意写作为True，但if和math都为False的样本。

    返回：{'subset_name': row_count, ...}
    """
    
    subset_stats = {}

    # 1. 仅创意写作：只含creative_writing，不含if和math
    only_cw_mask = (df["creative_writing_bool"] == True) & \
                   (df["if_bool"] == False) & \
                   (df["math_bool"] == False)
    only_cw = df[only_cw_mask].copy()
    only_cw.to_parquet(output_dir / "only_creative_writing_data.parquet", index=False)
    subset_stats["only_creative_writing"] = len(only_cw)
    print(f"  仅创意写作：{len(only_cw)} 行")

    # 2. 仅指令遵循：只含if，不含creative_writing和math
    only_if_mask = (df["creative_writing_bool"] == False) & \
                   (df["if_bool"] == True) & \
                   (df["math_bool"] == False)
    only_if = df[only_if_mask].copy()
    only_if.to_parquet(output_dir / "only_if_data.parquet", index=False)
    subset_stats["only_if"] = len(only_if)
    print(f"  仅指令遵循：{len(only_if)} 行")

    # 3. 仅数学：只含math，不含creative_writing和if
    only_math_mask = (df["creative_writing_bool"] == False) & \
                     (df["if_bool"] == False) & \
                     (df["math_bool"] == True)
    only_math = df[only_math_mask].copy()
    only_math.to_parquet(output_dir / "only_math_data.parquet", index=False)
    subset_stats["only_math"] = len(only_math)
    print(f"  仅数学：{len(only_math)} 行")

    return subset_stats


def create_two_category_subsets(df: pd.DataFrame, output_dir: Path) -> Dict[str, int]:
    """
    创建二分类交叉子集（同时属于两个分类但不属于第三个）。

    这些子集用于分析两个维度之间的联合特征。
    
    返回：{'subset_name': row_count, ...}
    """
    
    subset_stats = {}

    # 1. 创意写作 ∩ 指令遵循：同时为True，math为False
    cw_if_mask = (df["creative_writing_bool"] == True) & \
                 (df["if_bool"] == True)
    cw_if = df[cw_if_mask].copy()
    cw_if.to_parquet(output_dir / "creative_writing_if_data.parquet", index=False)
    subset_stats["creative_writing_if"] = len(cw_if)
    print(f"  创意写作 & 指令遵循：{len(cw_if)} 行")

    # 2. 创意写作 ∩ 数学：同时为True，if为False
    cw_math_mask = (df["creative_writing_bool"] == True) & \
                   (df["math_bool"] == True)
    cw_math = df[cw_math_mask].copy()
    cw_math.to_parquet(output_dir / "creative_writing_math_data.parquet", index=False)
    subset_stats["creative_writing_math"] = len(cw_math)
    print(f"  创意写作 & 数学：{len(cw_math)} 行")

    # 3. 指令遵循 ∩ 数学：同时为True，creative_writing为False
    if_math_mask = (df["if_bool"] == True) & \
                   (df["math_bool"] == True)
    if_math = df[if_math_mask].copy()
    if_math.to_parquet(output_dir / "if_math_data.parquet", index=False)
    subset_stats["if_math"] = len(if_math)
    print(f"  指令遵循 & 数学：{len(if_math)} 行")

    return subset_stats


def create_special_subsets(df: pd.DataFrame, output_dir: Path) -> Dict[str, int]:
    """
    创建特殊子集（全部分类或无分类）。

    - all_categories：三个分类都为True的样本（完全多分类）
    - no_category：三个分类都为False的样本（无分类标签）
    
    返回：{'subset_name': row_count, ...}
    """
    
    subset_stats = {}

    # 1. 全分类子集：creative_writing、if、math都为True
    all_three_mask = (df["creative_writing_bool"] == True) & \
                     (df["if_bool"] == True) & \
                     (df["math_bool"] == True)
    all_three = df[all_three_mask].copy()
    all_three.to_parquet(output_dir / "all_categories_data.parquet", index=False)
    subset_stats["all_categories"] = len(all_three)
    print(f"  全分类（三维都为True）：{len(all_three)} 行")

    # 2. 无分类子集：creative_writing、if、math都为False
    no_category_mask = (df["creative_writing_bool"] == False) & \
                       (df["if_bool"] == False) & \
                       (df["math_bool"] == False)
    no_category = df[no_category_mask].copy()
    no_category.to_parquet(output_dir / "no_category_data.parquet", index=False)
    subset_stats["no_category"] = len(no_category)
    print(f"  无分类（三维都为False）：{len(no_category)} 行")

    return subset_stats


def divide_data_by_category(file_path: Path | str | None = None,
                            data_dir: Path | str | None = None,
                            report_dir: Path | str | None = None) -> None:
    """
    根据category_tag的三个分类维度（creative_writing、if、math）完整划分数据集。

    本函数将优化后的数据集按照多个维度的不同组合进行划分，生成多个子集：
      1. 单一分类子集：按True/False分离各分类（6个）
      2. 纯净子集：仅属于单个维度为True的样本（3个）
      3. 二分类交叉：两个维度同时为True的样本（3个）
      4. 特殊子集：全分类或无分类的样本（2个）

    这样的划分设计用于：
    - 分析各类别的独立特征
    - 研究跨类别的关联特征
    - 验证分类的排他性或重叠性

    注意：数据来自C12_optimize_data.py的输出，已进行清洗，无需重复验证。

    参数说明：
    - file_path：优化数据文件路径（默认为 Data/optimized_data/optimized_data.parquet）
    - data_dir：子集数据保存目录（默认为 Data/optimized_data）
    - report_dir：报告保存目录（默认为 Reports）
    """

    if file_path is None:
        file_path = get_optimized_parquet_path()
    else:
        file_path = Path(file_path)

    # 默认数据输出目录为当前工作目录下的 Data/optimized_data
    if data_dir is None:
        data_dir = Path.cwd() / "Data" / "optimized_data"
    else:
        data_dir = Path(data_dir)

    # 默认报告输出目录为当前工作目录下的 Reports
    if report_dir is None:
        report_dir = Path.cwd() / "Reports"
    else:
        report_dir = Path(report_dir)

    # 提前创建输出目录，避免后续保存时因目录不存在而失败
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在读取优化数据: {file_path}")

    # 直接读取优化数据（C12已进行数据清洗，无需重复验证）
    try:
        df = pd.read_parquet(file_path)
    except Exception as exc:
        print(f"  ERROR: 读取失败 - {exc}")
        return

    print(f"  数据加载成功，形状：{df.shape}")
    print(f"  总行数：{len(df)}\n")

    # 统计所有子集的信息
    all_stats = {
        "original_rows": len(df),
        "subsets": {}
    }

    # 创建各类子集
    print("=" * 80)
    print("正在创建单一分类子集...")
    print("-" * 80)
    stats_single = create_single_category_subsets(df, data_dir)
    all_stats["subsets"].update(stats_single)

    print("\n" + "=" * 80)
    print("正在创建纯净子集（仅一个维度）...")
    print("-" * 80)
    stats_pure = create_pure_subsets(df, data_dir)
    all_stats["subsets"].update(stats_pure)

    print("\n" + "=" * 80)
    print("正在创建二分类交叉子集...")
    print("-" * 80)
    stats_two = create_two_category_subsets(df, data_dir)
    all_stats["subsets"].update(stats_two)

    print("\n" + "=" * 80)
    print("正在创建特殊子集...")
    print("-" * 80)
    stats_special = create_special_subsets(df, data_dir)
    all_stats["subsets"].update(stats_special)

    # 生成报告
    generate_division_report(
        original_file=file_path,
        stats=all_stats,
        report_dir=report_dir
    )


def generate_division_report(original_file: Path, stats: Dict, report_dir: Path) -> None:
    """
    生成数据集划分的统计报告。

    参数说明：
    - original_file：源数据文件路径
    - stats：划分过程的统计信息
    - report_dir：报告的保存目录
    """

    report_path = report_dir / "R10_division_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("数据集按任务分类划分报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 80 + "\n")
        f.write(f"源文件: {original_file}\n")
        f.write(f"原始行数: {stats['original_rows']}\n\n")

        f.write("2. 单一分类子集（按True/False分类）\n")
        f.write("-" * 80 + "\n")
        f.write(f"  creative_writing_true:  {stats['subsets'].get('creative_writing_true', 0):6d} 行\n")
        f.write(f"  creative_writing_false: {stats['subsets'].get('creative_writing_false', 0):6d} 行\n")
        f.write(f"  if_true:                {stats['subsets'].get('if_true', 0):6d} 行\n")
        f.write(f"  if_false:               {stats['subsets'].get('if_false', 0):6d} 行\n")
        f.write(f"  math_true:              {stats['subsets'].get('math_true', 0):6d} 行\n")
        f.write(f"  math_false:             {stats['subsets'].get('math_false', 0):6d} 行\n\n")

        f.write("3. 纯净子集（仅一个维度为True）\n")
        f.write("-" * 80 + "\n")
        f.write(f"  only_creative_writing: {stats['subsets'].get('only_creative_writing', 0):6d} 行\n")
        f.write(f"  only_if:               {stats['subsets'].get('only_if', 0):6d} 行\n")
        f.write(f"  only_math:             {stats['subsets'].get('only_math', 0):6d} 行\n\n")

        f.write("4. 二分类交叉子集（两个维度同时为True）\n")
        f.write("-" * 80 + "\n")
        f.write(f"  creative_writing_if:   {stats['subsets'].get('creative_writing_if', 0):6d} 行\n")
        f.write(f"  creative_writing_math: {stats['subsets'].get('creative_writing_math', 0):6d} 行\n")
        f.write(f"  if_math:               {stats['subsets'].get('if_math', 0):6d} 行\n\n")

        f.write("5. 特殊子集\n")
        f.write("-" * 80 + "\n")
        f.write(f"  all_categories: {stats['subsets'].get('all_categories', 0):6d} 行（三维都为True）\n")
        f.write(f"  no_category:    {stats['subsets'].get('no_category', 0):6d} 行（三维都为False）\n\n")

        f.write("6. 子集覆盖总结\n")
        f.write("-" * 80 + "\n")
        total_unique = sum(v for k, v in stats['subsets'].items() if k.startswith('only_'))
        total_unique += stats['subsets'].get('all_categories', 0)
        total_unique += stats['subsets'].get('no_category', 0)
        f.write(f"互不重叠的子集总行数（纯净+特殊）: {total_unique}\n")
        f.write(f"注意：单一分类、二分类交叉等子集间存在重叠\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"\n划分报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("按任务分类维度划分优化后的数据集")
    print("=" * 80)
    print()

    divide_data_by_category()

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)
