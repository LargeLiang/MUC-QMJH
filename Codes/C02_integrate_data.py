"""
C02_integrate_data

将原始 7 个 parquet 分片合并为单一整合文件。

功能：
- 逐一读取 train-00000 至 train-00006 共 7 个原始 parquet 分片
- 使用 pd.concat 合并所有分片并重置索引
- 输出至 Data/integrated_data/integrated_data.parquet

数据流向：
  原始 7 个 parquet 分片 → pd.concat → integrated_data.parquet（135,634 行 × 14 列）
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from time import perf_counter
from typing import Iterable
from tqdm import tqdm

from accessor import get_dir


def get_raw_parquet_file_paths(root: Path | str | None = None,
                               shard_count: int = 7) -> list[Path]:
    """
    返回项目根目录下的原始 parquet 分片路径列表。

    参数说明：
    - root：项目根目录（默认值为当前工作目录）
    - shard_count：分片数量（默认值为 7）

    返回值：
    - 原始分片路径列表
    """

    root_path = Path.cwd() if root is None else Path(root)
    data_dir = root_path / "Data" / "lmarena-aiarena-human-preference-140k" / "Data"
    return [data_dir / f"train-{i:05d}-of-00007.parquet" for i in range(shard_count)]


def save_parquet_with_progress(
    df: pd.DataFrame,
    output_file: Path | str,
    chunk_size: int = 10000,
) -> float:
    """
    分块写入 parquet 文件，并仅在保存阶段显示进度条。

    参数说明：
    - df：待保存的整合数据表
    - output_file：输出 parquet 文件路径
    - chunk_size：每次写入的行数（默认值：10000）

    返回值：
    - 保存耗时（秒）
    """

    output_path: Path = Path(output_file)
    save_start: float = perf_counter()
    total_rows: int = len(df)

    if total_rows == 0:
        df.to_parquet(output_path, index=False)
        return perf_counter() - save_start

    total_chunks: int = (total_rows + chunk_size - 1) // chunk_size
    first_chunk_end: int = min(chunk_size, total_rows)
    first_table: pa.Table = pa.Table.from_pandas(df.iloc[:first_chunk_end], preserve_index=False)

    with tqdm(total=total_chunks, desc="保存 parquet 文件", unit="chunk") as save_progress:
        with pq.ParquetWriter(output_path, first_table.schema) as writer:
            writer.write_table(first_table)
            save_progress.update(1)
            save_progress.set_postfix_str(f"已写行数={first_chunk_end}/{total_rows}")

            for start_idx in range(first_chunk_end, total_rows, chunk_size):
                end_idx: int = min(start_idx + chunk_size, total_rows)
                chunk_table: pa.Table = pa.Table.from_pandas(
                    df.iloc[start_idx:end_idx],
                    schema=first_table.schema,
                    preserve_index=False,
                    safe=False,
                )
                writer.write_table(chunk_table)
                save_progress.update(1)
                save_progress.set_postfix_str(f"已写行数={end_idx}/{total_rows}")

    return perf_counter() - save_start


def integrate_original_data(file_paths: Iterable[Path] | None = None, output_dir: Path | str | None = None) -> None:
    """
    将原始 parquet 分片逐个读取并合并为一个整合文件。

    支持自定义文件路径列表和输出目录，增强代码可复用性和测试友好性。
    """

    # 支持传入自定义文件路径列表，便于测试或在不同目录下运行脚本
    # 将路径集合转为列表，便于多次计算长度和循环访问
    if file_paths is None:
        file_paths : list[Path] = get_raw_parquet_file_paths()
    else:
        file_paths : list[Path] = list(file_paths)

    # 默认输出目录为当前工作目录下的 Data/integrated_data
    if output_dir is None:
        output_dir : Path = get_dir("integrated")
    else:
        output_dir : Path = Path(output_dir)

    # 提前创建目录，避免后续保存时因目录不存在而失败
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file : Path = output_dir / "integrated_data.parquet"

    # 用于缓存成功读取的 DataFrame 分片
    df_list: list[pd.DataFrame] = []
    processed_files : int = 0
    total_files : int = len(file_paths)
    read_start : float = perf_counter()

    for file_idx, file_path in enumerate(file_paths, start=1):
        print("=" * 80)
        print(f"处理文件 {file_idx}/{total_files}: {file_path}")

        file_path : Path = Path(file_path)

        # 如果文件不存在，则输出警告并继续检查下一个文件
        if not file_path.exists():
            print(f"  WARNING: 文件不存在，已跳过: {file_path}")
            continue

        # 读取 parquet 文件，并对读取异常进行捕获
        try:
            df : pd.DataFrame = pd.read_parquet(file_path)
        except Exception as exc:
            print(f"  ERROR: 读取 parquet 文件失败: {exc}")
            continue

        processed_files += 1
        print(f"  读取成功，数据形状: {df.shape}")

        # 收集当前文件的 DataFrame，后续统一合并
        df_list.append(df)

    read_elapsed : float = perf_counter() - read_start

    print("=" * 80)
    print(f"分片读取完成，耗时: {read_elapsed:.2f} 秒")

    # 如果没有任何有效文件，则无需继续后续合并和保存步骤
    if not df_list:
        print("未读取到任何有效 parquet 文件，未生成整合数据。")
        return

    concat_start : float = perf_counter()

    # 按行合并所有读取到的 DataFrame，避免索引重复
    integrated_df : pd.DataFrame = pd.concat(df_list, ignore_index=True)
    concat_elapsed : float = perf_counter() - concat_start
    print(f"合并完成，数据结构： {integrated_df.shape}")
    print(f"数据合并耗时: {concat_elapsed:.2f} 秒")

    # 将整合结果写入 parquet 文件，并对写入异常进行捕获
    try:
        save_elapsed : float = save_parquet_with_progress(integrated_df, output_file)
    except Exception as exc:
        print(f"  ERROR: 保存整合文件失败: {exc}")
        return

    print(f"已保存整合数据至: {output_file}")
    print(f"文件保存耗时: {save_elapsed:.2f} 秒")
    print(f"已成功处理文件数: {processed_files}/{total_files}")

if __name__ == "__main__":
    print("=" * 80)
    print("整合各个parquet文件")

    integrate_original_data()
