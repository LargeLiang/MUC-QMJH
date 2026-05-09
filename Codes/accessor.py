"""
accessor

提供项目级的数据访问共享函数。

本模块统一承接三类职责：
- 项目数据与输出目录的路径工厂
- nested optimized_data schema 的安全读取与兼容列派生
- 配对分析中复用的防御式计数与 winner 定向差值 helper
"""

from pathlib import Path
from typing import Any, Iterable, Mapping

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

DATA_DIR_LAYOUTS: dict[str, tuple[str, ...]] = {
    "raw": ("Data", "lmarena-aiarena-human-preference-140k", "Data"),
    "integrated": ("Data", "integrated_data"),
    "optimized": ("Data", "optimized_data"),
    "subsets": ("Data", "subsets"),
    "length": ("Data", "length_data"),
    "format": ("Data", "format_data"),
}

DEFAULT_DATA_FILES: dict[str, str] = {
    "integrated": "integrated_data.parquet",
    "optimized": "optimized_data.parquet",
}

ANALYSIS_SUBSET_FILE_NAMES: dict[str, str] = {
    "无类别": "no_category_data.parquet",
    "仅创意写作": "only_cw_data.parquet",
    "仅指令遵循": "only_if_data.parquet",
    "仅数学": "only_math_data.parquet",
    "仅代码": "only_code_data.parquet",
    "创意+指令": "cw_if_data.parquet",
    "创意+数学": "cw_math_data.parquet",
    "创意+代码": "cw_code_data.parquet",
    "指令+数学": "if_math_data.parquet",
    "指令+代码": "if_code_data.parquet",
    "数学+代码": "math_code_data.parquet",
    "创意+指令+数学": "cw_if_math_data.parquet",
    "创意+指令+代码": "cw_if_code_data.parquet",
    "创意+数学+代码": "cw_math_code_data.parquet",
    "指令+数学+代码": "if_math_code_data.parquet",
    "四类全含": "all_categories_data.parquet",
}

OUTPUT_DIR_LAYOUTS: dict[str, tuple[str, ...]] = {
    "report": ("Reports",),
    "table": ("Tables",),
    "picture": ("Pictures",),
}

TOKEN_COLUMN_SPECS: dict[str, tuple[str, str]] = {
    "a_tokens": ("metadata_a", "token_a"),
    "b_tokens": ("metadata_b", "token_b"),
    "user_tokens": ("metadata_user", "token_user"),
}

COUNT_COLUMN_SPECS: dict[str, tuple[str, str]] = {
    "a_header_count": ("metadata_a", "header_a"),
    "a_list_count": ("metadata_a", "list_a"),
    "a_bold_count": ("metadata_a", "bold_a"),
    "b_header_count": ("metadata_b", "header_b"),
    "b_list_count": ("metadata_b", "list_b"),
    "b_bold_count": ("metadata_b", "bold_b"),
}

CATEGORY_BOOL_SPECS: dict[str, str] = {
    "creative_writing_bool": "cw",
    "if_bool": "if",
    "math_bool": "math",
    "code_bool": "code",
}


def resolve_root_path(root: Path | str | None = None) -> Path:
    """规范化项目根目录路径。"""

    if root is None:
        return Path.cwd()
    return Path(root)


def _join_path(root: Path | str | None, parts: tuple[str, ...]) -> Path:
    """在项目根目录下拼接路径片段。"""

    return resolve_root_path(root).joinpath(*parts)


def get_data_dir(data_key: str, root: Path | str | None = None) -> Path:
    """按数据目录 key 返回 Data 下的标准目录。"""

    if data_key not in DATA_DIR_LAYOUTS:
        raise KeyError(f"未知 data_key: {data_key}")
    return _join_path(root, DATA_DIR_LAYOUTS[data_key])


def get_data_path(data_key: str,
                  file_name: str | None = None,
                  root: Path | str | None = None) -> Path:
    """返回指定数据目录中的文件路径；未传 file_name 时尝试使用默认文件名。"""

    resolved_file_name = file_name or DEFAULT_DATA_FILES.get(data_key)
    if resolved_file_name is None:
        raise ValueError(f"data_key={data_key} 需要显式传入 file_name")
    return get_data_dir(data_key, root) / resolved_file_name


def build_data_paths(data_key: str,
                     file_map: Mapping[str, str],
                     root: Path | str | None = None) -> dict[str, Path]:
    """将名称到文件名的映射展开为指定数据目录下的绝对路径映射。"""

    return {
        key: get_data_path(data_key, file_name, root)
        for key, file_name in file_map.items()
    }


def get_output_dir(output_kind: str, root: Path | str | None = None) -> Path:
    """按输出类型返回标准输出目录。"""

    if output_kind not in OUTPUT_DIR_LAYOUTS:
        raise KeyError(f"未知 output_kind: {output_kind}")
    return _join_path(root, OUTPUT_DIR_LAYOUTS[output_kind])


def get_output_path(output_kind: str,
                    file_name: str,
                    root: Path | str | None = None) -> Path:
    """返回指定输出目录中的文件路径。"""

    return get_output_dir(output_kind, root) / file_name


def build_output_paths(output_kind: str,
                       file_map: Mapping[str, str],
                       root: Path | str | None = None) -> dict[str, Path]:
    """将名称到文件名的映射展开为指定输出目录下的绝对路径映射。"""

    return {
        key: get_output_path(output_kind, file_name, root)
        for key, file_name in file_map.items()
    }


def get_analysis_subset_paths(root: Path | str | None = None,
                              include_full: bool = True) -> dict[str, Path]:
    """返回分析链通用的 16 个纯净分区子集路径映射。"""

    subset_paths = build_data_paths("subsets", ANALYSIS_SUBSET_FILE_NAMES, root)
    if include_full:
        return {"全量": get_data_path("optimized", root=root), **subset_paths}
    return subset_paths


def get_raw_parquet_file_paths(root: Path | str | None = None,
                               shard_count: int = 7) -> list[Path]:
    """返回原始 parquet 分片文件路径列表。"""

    data_dir = get_data_dir("raw", root)
    return [data_dir / f"train-{i:05d}-of-00007.parquet" for i in range(shard_count)]


def load_parquet_or_none(file_path: Path | str | None = None,
                         *,
                         data_key: str | None = None,
                         file_name: str | None = None,
                         root: Path | str | None = None) -> pd.DataFrame | None:
    """读取 parquet 文件；可直接传 file_path，也可传 data_key/file_name 组合。"""

    if file_path is None:
        if data_key is None:
            raise ValueError("file_path 和 data_key 至少要提供一个")
        path = get_data_path(data_key, file_name=file_name, root=root)
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


def get_nested_token(metadata: Any, token_key: str) -> int:
    """从 metadata 字典中安全提取 token 总量。"""

    if isinstance(metadata, dict):
        return safe_int_count(metadata.get(token_key, 0))
    return 0


def sum_nested_counts(metadata: Any, count_key: str) -> int:
    """对 metadata 内的格式计数字段求和。"""

    if not isinstance(metadata, dict):
        return 0
    return safe_int_count(metadata.get(count_key, {}))


def get_nested_bool(container: Any, key: str) -> bool:
    """从嵌套字典中安全提取布尔值。"""

    if isinstance(container, dict):
        return bool(container.get(key, False))
    return False


def get_nested_value(container: Any, key: str) -> Any:
    """从嵌套字典中安全提取原始值。"""

    if isinstance(container, dict):
        return container.get(key)
    return None


def oriented_winner_difference(a_values: Iterable[Any],
                               b_values: Iterable[Any],
                               winner_values: Iterable[Any]) -> np.ndarray:
    """按 winner 方向构造获胜方减落败方的差值数组。"""

    a_array = np.asarray(a_values, dtype=np.float64)
    b_array = np.asarray(b_values, dtype=np.float64)
    winner_array = np.asarray(winner_values)
    return np.where(winner_array == "model_a", a_array - b_array, b_array - a_array)


def oriented_winner_density_difference(a_counts: Iterable[Any],
                                       b_counts: Iterable[Any],
                                       a_tokens: Iterable[Any],
                                       b_tokens: Iterable[Any],
                                       winner_values: Iterable[Any]) -> np.ndarray:
    """按 winner 方向构造格式密度差值数组。"""

    a_count_array = np.asarray(a_counts, dtype=np.float64)
    b_count_array = np.asarray(b_counts, dtype=np.float64)
    a_token_array = np.asarray(a_tokens, dtype=np.float64)
    b_token_array = np.asarray(b_tokens, dtype=np.float64)

    a_density = a_count_array / (a_token_array + 1.0)
    b_density = b_count_array / (b_token_array + 1.0)
    return oriented_winner_difference(a_density, b_density, winner_values)


def with_length_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """为分析阶段添加 a_tokens、b_tokens、user_tokens 临时列。"""

    result = df.copy()

    for column_name, (metadata_column, token_key) in TOKEN_COLUMN_SPECS.items():
        if metadata_column in result.columns:
            result[column_name] = result[metadata_column].apply(
                lambda value, nested_key=token_key: get_nested_token(value, nested_key)
            )

    return result


def with_flat_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    """为分析阶段补齐旧逻辑依赖的临时列，不改变持久化 schema。"""

    result = with_length_tokens(df)

    for column_name, (metadata_column, count_key) in COUNT_COLUMN_SPECS.items():
        if metadata_column in result.columns:
            result[column_name] = result[metadata_column].apply(
                lambda value, nested_key=count_key: sum_nested_counts(value, nested_key)
            )

    if "category_tag" in result.columns:
        for column_name, nested_key in CATEGORY_BOOL_SPECS.items():
            result[column_name] = result["category_tag"].apply(
                lambda value, key=nested_key: get_nested_bool(value, key)
            )

    if "criteria" in result.columns:
        for key in CRITERIA_KEYS:
            result[key] = result["criteria"].apply(lambda value, criterion_key=key: get_nested_value(value, criterion_key))

    return result