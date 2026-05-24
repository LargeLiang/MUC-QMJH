"""
accessor

提供项目级的数据访问共享函数。

本模块统一承接三类职责：
- 项目数据与输出目录的路径工厂
- nested optimized_data schema 的安全读取、计数清洗与兼容列派生
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CRITERIA_KEYS = [
    "complexity",
    "creativity",
    "domain_knowledge",
    "problem_solving",
    "real_world",
    "specificity",
    "technical_accuracy",
]

# 数据目录与输出目录统一注册表（键名不重叠）
DIR_LAYOUTS: dict[str, tuple[str, ...]] = {
    # 数据目录
    "raw":        ("Data", "lmarena-aiarena-human-preference-140k", "Data"),
    "integrated": ("Data", "integrated_data"),
    "optimized":  ("Data", "optimized_data"),
    "subsets":    ("Data", "subsets"),
    "length":     ("Data", "length_data"),
    "format":     ("Data", "format_data"),
    # 输出目录
    "report":     ("Reports",),
    "table":      ("Tables",),
    "picture":    ("Pictures",),
}

# 省略 file_name 时的默认文件名（仅部分数据键有默认值）
_DEFAULT_FILES: dict[str, str] = {
    "integrated": "integrated_data.parquet",
    "optimized":  "optimized_data.parquet",
}

ANALYSIS_SUBSET_FILE_NAMES: dict[str, str] = {
    "无类别":         "no_category_data.parquet",
    "仅创意写作":     "only_cw_data.parquet",
    "仅指令遵循":     "only_if_data.parquet",
    "仅数学":         "only_math_data.parquet",
    "仅代码":         "only_code_data.parquet",
    "创意+指令":      "cw_if_data.parquet",
    "创意+数学":      "cw_math_data.parquet",
    "创意+代码":      "cw_code_data.parquet",
    "指令+数学":      "if_math_data.parquet",
    "指令+代码":      "if_code_data.parquet",
    "数学+代码":      "math_code_data.parquet",
    "创意+指令+数学": "cw_if_math_data.parquet",
    "创意+指令+代码": "cw_if_code_data.parquet",
    "创意+数学+代码": "cw_math_code_data.parquet",
    "指令+数学+代码": "if_math_code_data.parquet",
    "四类全含":       "all_categories_data.parquet",
}

# 子集中英文标签映射，供 C16–C23 可视化函数共用
SUBSET_LABELS_EN: dict[str, str] = {
    "全量":           "Full",
    "无类别":         "No category",
    "仅创意写作":     "CW only",
    "仅指令遵循":     "IF only",
    "仅数学":         "Math only",
    "仅代码":         "Code only",
    "创意+指令":      "CW + IF",
    "创意+数学":      "CW + Math",
    "创意+代码":      "CW + Code",
    "指令+数学":      "IF + Math",
    "指令+代码":      "IF + Code",
    "数学+代码":      "Math + Code",
    "创意+指令+数学": "CW + IF + Math",
    "创意+指令+代码": "CW + IF + Code",
    "创意+数学+代码": "CW + Math + Code",
    "指令+数学+代码": "IF + Math + Code",
    "四类全含":       "All four",
}

TOKEN_COLUMN_SPECS: dict[str, tuple[str, str]] = {
    "a_tokens":    ("metadata_a",    "token_a"),
    "b_tokens":    ("metadata_b",    "token_b"),
    "user_tokens": ("metadata_user", "token_user"),
}

COUNT_COLUMN_SPECS: dict[str, tuple[str, str]] = {
    "a_header_count": ("metadata_a", "header_a"),
    "a_list_count":   ("metadata_a", "list_a"),
    "a_bold_count":   ("metadata_a", "bold_a"),
    "b_header_count": ("metadata_b", "header_b"),
    "b_list_count":   ("metadata_b", "list_b"),
    "b_bold_count":   ("metadata_b", "bold_b"),
}

CATEGORY_BOOL_SPECS: dict[str, str] = {
    "creative_writing_bool": "cw",
    "if_bool":               "if",
    "math_bool":             "math",
    "code_bool":             "code",
}


# 路径工厂


def get_dir(key: str, root: Path | str | None = None) -> Path:
    """
    按目录键名返回对应的标准目录路径。

    数据目录键：raw / integrated / optimized / subsets / length / format
    输出目录键：report / table / picture
    """

    if key not in DIR_LAYOUTS:
        raise KeyError(f"未知目录键: {key}（可用：{list(DIR_LAYOUTS)}）")
    root_path = Path.cwd() if root is None else Path(root)
    return root_path.joinpath(*DIR_LAYOUTS[key])


def get_path(key: str,
             file_name: str | None = None,
             root: Path | str | None = None) -> Path:
    """
    返回指定目录中某个文件的路径。

    file_name 为 None 时尝试使用该键的默认文件名（仅 integrated / optimized 有默认值）。
    """

    resolved = file_name or _DEFAULT_FILES.get(key)
    if resolved is None:
        raise ValueError(f"key={key} 需要显式传入 file_name")
    return get_dir(key, root) / resolved


def get_analysis_subset_paths(root: Path | str | None = None,
                               include_full: bool = True) -> dict[str, Path]:
    """返回分析链通用的 16 个纯净分区子集路径映射（含全量时共 17 项）。"""

    subset_dir = get_dir("subsets", root)
    subset_paths = {
        name: subset_dir / file_name
        for name, file_name in ANALYSIS_SUBSET_FILE_NAMES.items()
    }
    if include_full:
        return {"全量": get_path("optimized", root=root), **subset_paths}
    return subset_paths


def load_parquet_or_none(file_path: Path | str | None = None,
                          *,
                          key: str | None = None,
                          file_name: str | None = None,
                          root: Path | str | None = None) -> pd.DataFrame | None:
    """读取 parquet 文件；可直接传 file_path，也可传 key/file_name 组合。"""

    if file_path is None:
        if key is None:
            raise ValueError("file_path 和 key 至少要提供一个")
        path = get_path(key, file_name=file_name, root=root)
    else:
        path = Path(file_path)

    if not path.exists():
        print(f"  ERROR: 文件不存在: {path}")
        return None

    try:
        return pd.read_parquet(path)
    except Exception as exc:
        print(f"  ERROR: 读取 parquet 文件失败: {exc}")
        return None


def safe_int_count(value: Any) -> int:
    """将 dict / 数值 / 缺失值统一转换为整数总计。"""

    if isinstance(value, dict):
        return int(sum(item for item in value.values() if isinstance(item, (int, float))))
    if value is None:
        return 0
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0
    if np.isnan(numeric_value):
        return 0
    return int(numeric_value)


# 临时列派生


def with_length_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """为分析阶段添加 a_tokens、b_tokens、user_tokens 临时列。"""

    result = df.copy()
    for column_name, (metadata_column, token_key) in TOKEN_COLUMN_SPECS.items():
        if metadata_column in result.columns:
            result[column_name] = result[metadata_column].apply(
                lambda value, k=token_key: safe_int_count(value.get(k, 0))
                if isinstance(value, dict)
                else 0
            )
    return result


def with_flat_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    """为分析阶段补齐旧逻辑依赖的临时列，不改变持久化 schema。"""

    result = with_length_tokens(df)

    for column_name, (metadata_column, count_key) in COUNT_COLUMN_SPECS.items():
        if metadata_column in result.columns:
            result[column_name] = result[metadata_column].apply(
                lambda value, k=count_key: safe_int_count(value.get(k, 0))
                if isinstance(value, dict)
                else 0
            )

    if "category_tag" in result.columns:
        for column_name, nested_key in CATEGORY_BOOL_SPECS.items():
            result[column_name] = result["category_tag"].apply(
                lambda value, k=nested_key: bool(value.get(k, False))
                if isinstance(value, dict)
                else False
            )

    if "criteria" in result.columns:
        for crit_key in CRITERIA_KEYS:
            result[crit_key] = result["criteria"].apply(
                lambda value, k=crit_key: value.get(k) if isinstance(value, dict) else None
            )

    return result