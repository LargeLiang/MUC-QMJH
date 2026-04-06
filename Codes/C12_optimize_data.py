import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Tuple
from collections import Counter


def get_integrated_parquet_path(root: Path | str | None = None) -> Path:
    """返回整合数据 parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root = Path.cwd()
    root_path = Path(root)

    # 整合数据文件位于项目根目录下的 Data/integrated_data/integrated_data.parquet
    return root_path / "Data" / "integrated_data" / "integrated_data.parquet"


def check_qualification(row) -> Tuple[bool, str]:
    """
    检查单行数据是否符合优化条件。

    检查标准：
    1. evaluation_order == 1（仅保留第一轮评价，避免Session历史影响）
    2. conversation_a和conversation_b的content都非空（不接受缺失内容）
    3. category_tag中creative_writing和if的评分都不为None（需要有效标签）
    4. language不是错误标记'<err>'（排除语言识别失败的行）

    返回值：(是否合格, 不合格原因描述)
    """
    
    # 1. 检查 evaluation_order：只保留第一轮评价
    if row.get("evaluation_order", -1) > 1:
        return False, "evaluation_order > 1（非首轮评价，包含Session历史）"

    # 2. 检查 conversation_a 的 content 是否为空
    conv_a = row.get("conversation_a")
    if isinstance(conv_a, (list, tuple, np.ndarray)):
        for segment in conv_a:
            if isinstance(segment, dict):
                content = segment.get("content")
                if isinstance(content, (list, tuple)) and len(content) == 0:
                    return False, "conversation_a 中存在空 content"

    # 3. 检查 conversation_b 的 content 是否为空
    conv_b = row.get("conversation_b")
    if isinstance(conv_b, (list, tuple, np.ndarray)):
        for segment in conv_b:
            if isinstance(segment, dict):
                content = segment.get("content")
                if isinstance(content, (list, tuple)) and len(content) == 0:
                    return False, "conversation_b 中存在空 content"

    # 4. 检查 category_tag 的关键评分字段是否为 None
    category_tag = row.get("category_tag")
    if isinstance(category_tag, dict):
        cw : dict | None = category_tag.get("creative_writing_v0.1")
        if isinstance(cw, dict) and cw.get("score") is None:
            return False, "creative_writing_v0.1 评分为 None"
        
        if_mod : dict | None = category_tag.get("if_v0.1")
        if isinstance(if_mod, dict) and if_mod.get("score") is None:
            return False, "if_v0.1 评分为 None"

    # 5. 检查 language 是否为错误标记
    if row.get("language") == "<err>":
        return False, "language 标记为 <err>（语言识别失败）"

    return True, ""


def optimize_conversation(conv_a: np.ndarray | list | tuple, 
                          conv_b: np.ndarray | list | tuple) -> Dict:
    """
    优化和扁平化对话结构。

    将嵌套的对话结构（按turn分组的user/assistant消息）转换为扁平结构，
    按turn分别提取用户提问、模型A回复、模型B回复的文本内容。

    参数说明：
    - conv_a：模型A侧对话，结构为[{role, content: [{text, ...}]}, ...]
    - conv_b：模型B侧对话，结构相同

    返回：
    {
        'turns': 总轮数,
        'a_conv': {f'turn_{i}_a_text': 文本, ...},
        'b_conv': {f'turn_{i}_b_text': 文本, ...},
        'user_conv': {f'turn_{i}_user_text': 文本, ...}
    }
    """
    
    # 初始化优化后的对话字典
    turns_count = 0
    if isinstance(conv_a, (list, tuple, np.ndarray)):
        # turns = 总消息数 / 2（user和assistant各一个为一个turn）
        turns_count = len(conv_a) // 2
    
    optimized_conv = {
        "turns": turns_count,
        "a_conv": {},
        "b_conv": {},
        "user_conv": {}
    }

    # 处理 conversation_a：提取user和assistant A的文本
    if isinstance(conv_a, (list, tuple, np.ndarray)):
        for i, segment in enumerate(conv_a):
            if not isinstance(segment, dict):
                continue
            
            role = segment.get("role")
            content = segment.get("content")
            
            # 从第一个content item提取文本（通常只有一个item）
            text = ""
            if isinstance(content, (list, tuple)) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict):
                    text = first_item.get("text", "")
            
            # 根据角色分配到对应的turn
            turn_num = i // 2 + 1
            if role == "user":
                optimized_conv["user_conv"][f"turn_{turn_num}_user_text"] = text
            elif role == "assistant":
                optimized_conv["a_conv"][f"turn_{turn_num}_a_text"] = text

    # 处理 conversation_b：提取assistant B的文本
    if isinstance(conv_b, (list, tuple, np.ndarray)):
        for i, segment in enumerate(conv_b):
            if not isinstance(segment, dict):
                continue
            
            role = segment.get("role")
            if role != "assistant":
                continue
            
            content = segment.get("content")
            text = ""
            if isinstance(content, (list, tuple)) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict):
                    text = first_item.get("text", "")
            
            turn_num = i // 2 + 1
            optimized_conv["b_conv"][f"turn_{turn_num}_b_text"] = text

    return optimized_conv


def optimize_conv_metadata(metadata: Dict) -> Dict:
    """
    优化 conv_metadata 字段。

    从原始的冗余元数据（包含多种token计数和格式计数）中提取关键字段，
    避免数据膨胀，同时保留对分析必需的信息：
    - 模型A/B的token数和格式特征（标题、列表、粗体数量）
    - 用户端的token数
    """
    
    optimized_metadata = {
        # 模型A相关字段
        "a_tokens": metadata.get("sum_assistant_a_tokens", 0),
        "a_header_count": metadata.get("header_count_a", 0),
        "a_list_count": metadata.get("list_count_a", 0),
        "a_bold_count": metadata.get("bold_count_a", 0),
        
        # 模型B相关字段
        "b_tokens": metadata.get("sum_assistant_b_tokens", 0),
        "b_header_count": metadata.get("header_count_b", 0),
        "b_list_count": metadata.get("list_count_b", 0),
        "b_bold_count": metadata.get("bold_count_b", 0),
        
        # 用户信息
        "user_tokens": metadata.get("sum_user_tokens", 0)
    }

    return optimized_metadata


def optimize_category_tag(category_tag: Dict) -> Dict:
    """
    优化 category_tag 字段。

    从category_tag的多层次嵌套结构中提取三个关键维度模块的核心信息：
    - creative_writing：创意写作分类和评分
    - if（instruction following）：指令遵循能力的分类和评分
    - math：数学相关任务分类（仅分类，无评分）
    """
    
    optimized_category_tag = {}

    # 1. 提取 creative_writing（创意写作）的分类和评分
    cw = category_tag.get("creative_writing_v0.1", {})
    if isinstance(cw, dict):
        optimized_category_tag["creative_writing_bool"] = cw.get("creative_writing", False)
        optimized_category_tag["creative_writing_score"] = cw.get("score")

    # 2. 提取 if（指令遵循）的分类和评分
    if_mod = category_tag.get("if_v0.1", {})
    if isinstance(if_mod, dict):
        optimized_category_tag["if_bool"] = if_mod.get("if", False)
        optimized_category_tag["if_score"] = if_mod.get("score")

    # 3. 提取 math（数学）的分类
    math_mod = category_tag.get("math_v0.1", {})
    if isinstance(math_mod, dict):
        optimized_category_tag["math_bool"] = math_mod.get("math", False)

    return optimized_category_tag


def optimize_criteria(category_tag: Dict) -> Dict:
    """
    优化 criteria 字段。

    从 criteria_v0.1 中提取所有七个评估维度的值：
    - complexity（复杂度）
    - creativity（创意）
    - domain_knowledge（领域知识）
    - problem_solving（问题求解）
    - real_world（实际应用）
    - specificity（具体性）
    - technical_accuracy（技术准确性）

    这些维度通常为二值（True/False）或多值分类。
    """
    
    optimized_criteria = {}
    
    criteria = category_tag.get("criteria_v0.1", {})
    if isinstance(criteria, dict):
        # 提取七个评估维度
        optimized_criteria = {
            "complexity": criteria.get("complexity"),
            "creativity": criteria.get("creativity"),
            "domain_knowledge": criteria.get("domain_knowledge"),
            "problem_solving": criteria.get("problem_solving"),
            "real_world": criteria.get("real_world"),
            "specificity": criteria.get("specificity"),
            "technical_accuracy": criteria.get("technical_accuracy")
        }

    return optimized_criteria


def optimize_data(file_path: Path | str | None = None,
                  data_dir: Path | str | None = None,
                  report_dir: Path | str | None = None) -> None:
    """
    优化原始整合数据的结构。

    本函数的目标是：
    1. 过滤不符合条件的行（evaluation_order > 1、缺失content、缺失评分等）
    2. 扁平化嵌套结构（对话、元数据、分类标签）
    3. 保留关键字段，去除冗余信息，减少数据膨胀
    4. 输出经过清洗和结构化的数据集

    参数说明：
    - file_path：输入的原始整合数据文件路径
    - data_dir：优化后数据文件的保存目录（默认为 Data/optimized_data）
    - report_dir：清洗报告的保存目录（默认为 Reports）

    最终输出包括：
    - 优化后的完整数据集（parquet格式）
    - 清洗统计报告（txt格式）
    """

    # 支持传入自定义文件路径和输出目录，便于测试或在不同目录下运行脚本
    if file_path is None:
        file_path = get_integrated_parquet_path()
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

    # 检查输入文件是否存在
    print(f"正在读取原始数据: {file_path}")
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

    # 统计变量：记录过滤和优化的详细信息
    optimization_stats : Dict[str, int | Counter] = {
        "total_rows": len(df),
        "qualified_rows": 0,
        "filtered_rows": 0,
        "filter_reasons": Counter(),
        "processing_errors": 0,
        "error_ids": []
    }

    optimized_rows : list[Dict] = []

    # 逐行处理数据
    for row in tqdm(df.itertuples(index=False), total=len(df), desc="优化行数据"):
        # 构建字典形式的row以支持.get()方法
        row_dict : Dict[str, any] = row._asdict() if hasattr(row, "_asdict") else dict(zip(df.columns, row))
        row_id : str | None = row_dict.get("id")

        # 检查该行是否符合优化条件
        is_qualified, reason = check_qualification(row_dict)
        
        if not is_qualified:
            optimization_stats["filtered_rows"] += 1
            optimization_stats["filter_reasons"][reason] += 1
            continue

        try:
            # 开始优化该行数据
            optimized_row : Dict[str, any] = {}

            # 1. 直接迁移的字段（无需优化）
            direct_cols : list[str] = ["id", "model_a", "model_b", "winner", "language", "is_code"]
            for col in direct_cols:
                optimized_row[col] = row_dict.get(col)

            # 2. 优化对话结构：扁平化并提取文本
            optimized_conv : Dict[str, any] = optimize_conversation(
                row_dict.get("conversation_a"),
                row_dict.get("conversation_b")
            )
            optimized_row.update(optimized_conv)

            # 3. 优化顺序数据：简化格式特征统计
            optimized_meta : Dict[str, any] = optimize_conv_metadata(row_dict.get("conv_metadata", {}))
            optimized_row.update(optimized_meta)

            # 4. 优化分类标签：提取关键标签和评分
            optimized_tags : Dict[str, any] = optimize_category_tag(row_dict.get("category_tag", {}))
            optimized_row.update(optimized_tags)

            # 5. 优化评估维度：提取七个评分维度
            optimized_crit : Dict[str, any] = optimize_criteria(row_dict.get("category_tag", {}))
            optimized_row.update(optimized_crit)

            optimized_rows.append(optimized_row)
            optimization_stats["qualified_rows"] += 1

        except Exception as exc:
            optimization_stats["processing_errors"] += 1
            optimization_stats["error_ids"].append((row_id, str(exc)))
            continue

    # 将优化后的行转换为 DataFrame
    if optimized_rows:
        optimized_df : pd.DataFrame = pd.DataFrame(optimized_rows)
        output_file : Path = data_dir / "optimized_data.parquet"
        try:
            optimized_df.to_parquet(output_file, index=False)
            print(f"已保存优化数据至: {output_file}")
        except Exception as exc:
            print(f"  ERROR: 保存文件失败: {exc}")
            return
    else:
        print("  WARNING: 没有符合条件的行，未生成优化数据")
        optimized_df : pd.DataFrame | None = None

    # 生成清洗统计报告
    generate_optimization_report(
        file_path=file_path,
        stats=optimization_stats,
        optimized_df_shape=optimized_df.shape if optimized_df is not None else (0, 0),
        report_dir=report_dir
    )


def generate_optimization_report(file_path: Path, stats: Dict, 
                                 optimized_df_shape: Tuple[int, int],
                                 report_dir: Path) -> None:
    """
    生成数据优化清洗报告。

    参数说明：
    - file_path：源数据文件路径
    - stats：优化过程的统计信息
    - optimized_df_shape：优化后数据的形状
    - report_dir：报告的保存目录
    """

    report_path = report_dir / "R09_optimization_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("数据优化清洗报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 基本信息\n")
        f.write("-" * 80 + "\n")
        f.write(f"源文件: {file_path}\n")
        f.write(f"原始行数: {stats['total_rows']}\n")
        f.write(f"符合条件行数: {stats['qualified_rows']}\n")
        f.write(f"过滤行数: {stats['filtered_rows']}\n")
        f.write(f"处理错误行数: {stats['processing_errors']}\n")
        f.write(f"清洗后数据形状: {optimized_df_shape[0]} 行 × {optimized_df_shape[1]} 列\n")
        f.write(f"保留率: {stats['qualified_rows'] / stats['total_rows'] * 100:.2f}%\n\n")

        f.write("2. 过滤原因分布\n")
        f.write("-" * 80 + "\n")
        if stats["filter_reasons"]:
            for reason, count in stats["filter_reasons"].most_common():
                f.write(f"  {reason}: {count} 行\n")
        else:
            f.write("  无过滤（所有行都符合条件）\n")
        f.write("\n")

        f.write("3. 数据优化说明\n")
        f.write("-" * 80 + "\n")
        f.write("已执行的优化操作：\n")
        f.write("  - 对话扁平化：按turn提取user/assistant文本\n")
        f.write("  - 元数据简化：保留token数和格式特征，去除冗余字段\n")
        f.write("  - 标签降维：提取creative_writing、if、math三个维度\n")
        f.write("  - 维度保留：保留criterion_v0.1的七个评估维度\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"已保存清洗报告至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("优化和清洗原始整合数据")
    print("=" * 80)

    # 执行数据优化
    optimize_data()
