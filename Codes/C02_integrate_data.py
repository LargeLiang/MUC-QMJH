import pandas as pd
from pathlib import Path
from typing import Iterable

def get_parquet_file_paths(root: Path | str | None = None) -> list[Path]:
    """构造原始 parquet 分片文件的规范路径列表。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root = Path.cwd()
    root_path = Path(root)

    # 原始数据文件位于项目根目录下的 Data/lmarena-aiarena-human-preference-140k/Data
    data_dir = root_path / "Data" / "lmarena-aiarena-human-preference-140k" / "Data"
    return [data_dir / f"train-{i:05d}-of-00007.parquet" for i in range(7)]


def integrate_original_data(file_paths: Iterable[Path] | None = None, output_dir: Path | str | None = None) -> None:
    """
    将原始 parquet 分片逐个读取并合并为一个整合文件。

    支持自定义文件路径列表和输出目录，增强代码可复用性和测试友好性。
    """

    # 支持传入自定义文件路径列表，便于测试或在不同目录下运行脚本
    if file_paths is None:
        file_paths = get_parquet_file_paths()

    # 将路径集合转为列表，便于多次计算长度和循环访问
    file_paths = list(file_paths)

    # 默认输出目录为当前工作目录下的 Data/integrated_data
    if output_dir is None:
        output_dir = Path.cwd() / "Data" / "integrated_data"
    else:
        output_dir = Path(output_dir)

    # 提前创建目录，避免后续保存时因目录不存在而失败
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "integrated_data.parquet"

    # 用于缓存成功读取的 DataFrame 分片
    df_list: list[pd.DataFrame] = []
    processed_files : int = 0

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
            df = pd.read_parquet(file_path)
        except Exception as exc:
            print(f"  ERROR: 读取 parquet 文件失败: {exc}")
            continue

        processed_files += 1
        print(f"  读取成功，数据形状: {df.shape}")

        # 收集当前文件的 DataFrame，后续统一合并
        df_list.append(df)

    print("=" * 80)

    # 如果没有任何有效文件，则无需继续后续合并和保存步骤
    if not df_list:
        print("未读取到任何有效 parquet 文件，未生成整合数据。")
        return

    # 按行合并所有读取到的 DataFrame，避免索引重复
    integrated_df = pd.concat(df_list, ignore_index=True)
    print(f"合并完成，总行数: {len(integrated_df)}, 总列数: {integrated_df.shape[1]}")

    # 将整合结果写入 parquet 文件，并对写入异常进行捕获
    try:
        integrated_df.to_parquet(output_file, index=False)
    except Exception as exc:
        print(f"  ERROR: 保存整合文件失败: {exc}")
        return

    print(f"已保存整合数据至: {output_file}")
    print(f"已成功处理文件数: {processed_files}/{len(file_paths)}")

if __name__ == "__main__":
    print("=" * 80)
    print("整合各个parquet文件")

    integrate_original_data()