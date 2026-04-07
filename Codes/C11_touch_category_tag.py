"""
C11_touch_category_tag

分析整合数据中 category_tag 字段各子模块的分布情况。

功能：
- 解析 category_tag 字典中的多个子字段（类别、任务类型、语言、难度等）
- 统计每个子字段的唯一值分布及出现频率
- 识别缺失值、异常值及跨子字段的组合分布

数据流向：
  integrated_data.parquet → category_tag 字段解析 → 各子模块频率统计 → Reports/R08_category_tag_report.txt
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from typing import Dict


def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据 parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # 整合数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def touch_category_tag(file_path: Path | str | None = None,
                       output_dir: Path | str | None = None) -> None:
    """
    分析整合数据中的 category_tag 和相关分类标签字段。

    category_tag 是一个多层次的嵌套字典，包含以下子模块：
    - creative_writing_v0.1：创意写作相关标签及评分
    - criteria_v0.1：多维度准则评分（复杂度、创意、领域知识等7项）
    - if_v0.1：信息流相关标签及评分
    - math_v0.1：数学相关标签

    同时分析顶级字段 language（语言）和 is_code（是否代码）。
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

    # 初始化统计变量
    # creative_writing 模块：包含创意写作分类和评分
    creative_writing_count: Counter = Counter()
    creative_writing_score_count: Counter = Counter()

    # criteria 模块：包含7个评估维度，分别统计每个维度的值分布
    complexity_count: Counter = Counter()
    creativity_count: Counter = Counter()
    domain_knowledge_count: Counter = Counter()
    problem_solving_count: Counter = Counter()
    real_world_count: Counter = Counter()
    specificity_count: Counter = Counter()
    technical_accuracy_count: Counter = Counter()

    # if 模块：包含信息流分类和评分
    if_count: Counter = Counter()
    if_score_count: Counter = Counter()

    # math 模块：包含数学相关分类
    math_count: Counter = Counter()

    # 顶级字段：语言和代码标记
    language_count: Counter = Counter()
    is_code_count: Counter = Counter()

    # 缺失数据统计
    invalid_category_tag_rows: int = 0
    missing_submodule_rows: Dict[str, int] = {}

    for row in df.itertuples(index=False):
        row_id : object = getattr(row, "id", None)
        category_tag : dict | None = getattr(row, "category_tag", None)
        language : object = getattr(row, "language", None)
        is_code : object = getattr(row, "is_code", None)

        # 检查category_tag是否为有效的字典结构
        if not isinstance(category_tag, dict):
            invalid_category_tag_rows += 1
            continue

        # 1. 提取creative_writing_v0.1模块的数据
        cw : dict | None = category_tag.get("creative_writing_v0.1")
        if isinstance(cw, dict):
            cw_val : bool | None = cw.get("creative_writing")
            cw_score : float | None = cw.get("score")
            if cw_val is not None:
                creative_writing_count[cw_val] += 1
            if cw_score is not None:
                creative_writing_score_count[cw_score] += 1
        else:
            missing_submodule_rows["creative_writing_v0.1"] = missing_submodule_rows.get("creative_writing_v0.1", 0) + 1

        # 2. 提取criteria_v0.1模块的数据
        crit : dict | None = category_tag.get("criteria_v0.1")
        if isinstance(crit, dict):
            # criteria包含7个评估维度，分别统计各维度值的分布
            complexity_count[crit.get("complexity")] += 1
            creativity_count[crit.get("creativity")] += 1
            domain_knowledge_count[crit.get("domain_knowledge")] += 1
            problem_solving_count[crit.get("problem_solving")] += 1
            real_world_count[crit.get("real_world")] += 1
            specificity_count[crit.get("specificity")] += 1
            technical_accuracy_count[crit.get("technical_accuracy")] += 1
        else:
            missing_submodule_rows["criteria_v0.1"] = missing_submodule_rows.get("criteria_v0.1", 0) + 1

        # 3. 提取if_v0.1模块的数据
        if_mod : dict | None = category_tag.get("if_v0.1")
        if isinstance(if_mod, dict):
            if_val : bool | None = if_mod.get("if")
            if_score : float | None = if_mod.get("score")
            if if_val is not None:
                if_count[if_val] += 1
            if if_score is not None:
                if_score_count[if_score] += 1
        else:
            missing_submodule_rows["if_v0.1"] = missing_submodule_rows.get("if_v0.1", 0) + 1

        # 4. 提取math_v0.1模块的数据
        math_mod : dict | None = category_tag.get("math_v0.1")
        if isinstance(math_mod, dict):
            math_val : bool | None = math_mod.get("math")
            if math_val is not None:
                math_count[math_val] += 1
        else:
            missing_submodule_rows["math_v0.1"] = missing_submodule_rows.get("math_v0.1", 0) + 1

        # 5. 统计顶级字段
        if language is not None:
            language_count[language] += 1
        if is_code is not None:
            is_code_count[is_code] += 1

    print(f"  发现 {len(creative_writing_count)} 种 creative_writing 值")
    print(f"  发现 {len(creativity_count)} 种 creativity 值")
    print(f"  发现 {len(complexity_count)} 种 complexity 值")
    print(f"  发现 {len(language_count)} 种 language 值")
    print(f"  发现 {len(is_code_count)} 种 is_code 值")
    print(f"  invalid category_tag 行数: {invalid_category_tag_rows}")

    generate_category_tag_report(
        file_path=file_path,
        total_rows=len(df),
        creative_writing_count=creative_writing_count,
        creative_writing_score_count=creative_writing_score_count,
        complexity_count=complexity_count,
        creativity_count=creativity_count,
        domain_knowledge_count=domain_knowledge_count,
        problem_solving_count=problem_solving_count,
        real_world_count=real_world_count,
        specificity_count=specificity_count,
        technical_accuracy_count=technical_accuracy_count,
        if_count=if_count,
        if_score_count=if_score_count,
        math_count=math_count,
        language_count=language_count,
        is_code_count=is_code_count,
        invalid_category_tag_rows=invalid_category_tag_rows,
        missing_submodule_rows=missing_submodule_rows,
        output_dir=output_dir,
    )


def generate_category_tag_report(file_path: Path, total_rows: int,
                                 creative_writing_count: Counter,
                                 creative_writing_score_count: Counter,
                                 complexity_count: Counter,
                                 creativity_count: Counter,
                                 domain_knowledge_count: Counter,
                                 problem_solving_count: Counter,
                                 real_world_count: Counter,
                                 specificity_count: Counter,
                                 technical_accuracy_count: Counter,
                                 if_count: Counter,
                                 if_score_count: Counter,
                                 math_count: Counter,
                                 language_count: Counter,
                                 is_code_count: Counter,
                                 invalid_category_tag_rows: int,
                                 missing_submodule_rows: Dict[str, int],
                                 output_dir: Path) -> None:
    """生成 category_tag 分析报告。"""

    report_path = output_dir / "R08_category_tag_report.txt"

    print("=" * 80)
    print("生成 category_tag 分析报告...")
    print("=" * 80)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("category_tag 分析报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 100 + "\n")
        f.write(f"分析文件: {file_path}\n")
        f.write(f"数据总行数: {total_rows}\n")
        f.write(f"无效 category_tag（非字典）行数: {invalid_category_tag_rows}\n")
        if missing_submodule_rows:
            f.write(f"缺失子模块的行数:\n")
            for mod_name, count in sorted(missing_submodule_rows.items()):
                f.write(f"  {mod_name}: {count}\n")
        f.write("\n")

        f.write("2. creative_writing_v0.1 分析\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, creative_writing_count, "creative_writing")
        write_counter_section(f, creative_writing_score_count, "creative_writing_score")

        f.write("3. criteria_v0.1 分析（7个评估维度）\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, complexity_count, "复杂度 (complexity)")
        write_counter_section(f, creativity_count, "创意 (creativity)")
        write_counter_section(f, domain_knowledge_count, "领域知识 (domain_knowledge)")
        write_counter_section(f, problem_solving_count, "问题求解 (problem_solving)")
        write_counter_section(f, real_world_count, "实际应用 (real_world)")
        write_counter_section(f, specificity_count, "具体性 (specificity)")
        write_counter_section(f, technical_accuracy_count, "技术准确性 (technical_accuracy)")

        f.write("4. if_v0.1 分析\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, if_count, "if")
        write_counter_section(f, if_score_count, "if_score")

        f.write("5. math_v0.1 分析\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, math_count, "math")

        f.write("6. 顶级字段分析\n")
        f.write("-" * 100 + "\n")
        write_counter_section(f, language_count, "language")
        write_counter_section(f, is_code_count, "is_code")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"分析报告已保存至: {report_path}")


def write_counter_section(f, counter: Counter, label: str, top_n: int = 10) -> None:
    """
    将 Counter 统计结果写入报告。

    将指定标签的Counter数据格式化输出，显示唯一值数量和高频项分布。
    默认显示top_n项，避免报告过大。
    """
    f.write(f"{label} 唯一值数量: {len(counter)}\n")
    if counter:
        f.write(f"{label} 值列表（前{top_n}）: {[item for item, _ in counter.most_common(top_n)]}\n")
        f.write(f"{label} 值分布（前{top_n}）:\n")
        f.write(f"  {'值':>30} {'出现次数':>15}\n")
        f.write(f"  {'-' * 45}\n")
        for value, count in counter.most_common(top_n):
            f.write(f"  {str(value):>30} {count:>15}\n")
    else:
        f.write(f"{label} 无有效数据\n")
    f.write("\n")


if __name__ == "__main__":
    print("=" * 80)
    print("分析 category_tag 字段")
    print("=" * 80)

    touch_category_tag()