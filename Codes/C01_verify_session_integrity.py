"""
C01_verify_session_integrity

校验原始 parquet 分片中的 evaluation_session_id 是否跨文件重复。

功能：
- 逐一读取 train-00000 至 train-00006 共 7 个原始 parquet 分片
- 统计全局与各文件内的唯一 session_id 数量
- 若全局去重数 < 各文件唯一数之和，说明同一会话被拆分至不同分片

数据流向：
  原始 7 个 parquet 分片 → session_id 集合比较 → 控制台结论输出
"""

import pandas as pd
from pathlib import Path
from typing import Iterable

def get_parquet_file_paths(root: Path | str | None = None) -> list[Path]:
    """构造原始 parquet 分片文件的规范路径列表。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # 原始数据文件位于项目根目录下的 Data/lmarena-aiarena-human-preference-140k/Data
    data_dir : Path = root_path / "Data" / "lmarena-aiarena-human-preference-140k" / "Data"
    return [data_dir / f"train-{i:05d}-of-00007.parquet" for i in range(7)]


def verify_session_integrity(file_paths: Iterable[Path] | None = None) -> None:
    """
    校验原始 parquet 分片中的 evaluation_session_id 是否跨文件重复。

    如果各文件唯一值数量之和大于全局唯一值数量，则表示同一个 session_id
    出现在多个文件中，说明会话被拆分到不同 shard。
    """

    # 支持传入自定义文件路径列表，便于测试或在不同目录下运行脚本
    if file_paths is None:
        file_paths : list[Path] = get_parquet_file_paths()
    else:
        file_paths : list[Path] = list(file_paths)

    # 用于存储所有处理文件中去重后的 session_id
    all_unique_session_ids: set = set()
    
    # 记录每个文件内唯一 session_id 数量之和，用于与全局去重后数量对比
    total_unique_count: int = 0
    
    # 记录实际成功读取并处理的文件数量
    processed_files: int = 0

    for file_idx, file_path in enumerate(file_paths, start=1):
        print("=" * 80)
        print(f"处理文件 {file_idx}/{len(file_paths)}: {file_path}")

        file_path = Path(file_path)

        # 如果文件不存在，则输出警告并继续检查下一个文件
        if not file_path.exists():
            print(f"  WARNING: 文件不存在，已跳过: {file_path}")
            continue

        # 读取 parquet 文件，并对读取异常进行捕获
        try:
            df : pd.DataFrame= pd.read_parquet(file_path)
        except Exception as exc:
            print(f"  ERROR: 读取 parquet 文件失败: {exc}")
            continue

        processed_files += 1
        print(f"  读取成功，数据形状: {df.shape}")

        # 直接通过 pandas 提取当前文件中唯一的 session_id
        unique_session_ids : set = set(df["evaluation_session_id"].dropna().unique())
        print(f"  发现 {len(unique_session_ids)} 种不同的 evaluation_session_id")

        # 累加全局唯一 session_id 并统计当前文件的唯一值数量
        all_unique_session_ids.update(unique_session_ids)
        total_unique_count += len(unique_session_ids)

    # 输出最终验证结果
    print("=" * 80)
    print("验证结果")
    print("=" * 80)
    print(f"已成功处理文件数: {processed_files}/{len(file_paths)}")
    print(f"全局 evaluation_session_id 唯一值数量: {len(all_unique_session_ids)}")
    print(f"各文件 evaluation_session_id 唯一值数量之和: {total_unique_count}")

    # 如果各文件唯一值始终一致，则不会出现跨文件重复 session_id
    if total_unique_count != len(all_unique_session_ids):
        print("  结论: 跨 parquet 文件存在重复的 evaluation_session_id。")
        print("  说明: 数据分片存在会话拆分，建议先合并相关分片后再分析。")
    else:
        print("  结论: 跨 parquet 文件不存在重复的 evaluation_session_id。")
        print("  说明: 数据分片上的会话完整，可按文件逐一分析。")
    
if __name__ == "__main__":
    print("=" * 80)
    print("验证数据分割后的会话完整性")

    # file_paths : list[Path] =  # 可选：传入自定义文件路径列表

    # 调用主函数，可选择传入参数 file_paths
    verify_session_integrity()