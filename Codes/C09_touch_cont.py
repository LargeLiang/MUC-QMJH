import pandas as pd
import os
from collections import Counter

def touch_cont():
    """
    分析 type 字段
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"

    # 统计 conversation_a 中的 item 个数，即 len(content)
    a_cont_item_counts = Counter()
    # 记录 conversation_a 中 content 缺失的 id 
    a_missing_cont_ids = set()

    # 统计 conversation_a 中 content 的次级结构：type、text、image、mimeType
    a_type_counts = Counter()
    a_text_counts = Counter()
    a_image_counts = Counter()
    a_mimeType_counts = Counter()

    # 统计 conversation_b 中的 item 个数，即 len(content)
    b_cont_item_counts = Counter()
    # 记录 conversation_b 中 content 缺失的 id 
    b_missing_cont_ids = set()

    # 统计 conversation_a 中 content 的次级结构：type、text、image、mimeType
    b_type_counts = Counter()
    b_text_counts = Counter()
    b_image_counts = Counter()
    b_mimeType_counts = Counter()
    
    print(f"正在分析文件: {os.path.basename(file_path)}")
    df = pd.read_parquet(file_path)
    print(f"  数据形状: {df.shape}")

    for idx in range(len(df)):
        id = df.iloc[idx]['id']

        conv_a = df.iloc[idx]['conversation_a']
        for side in conv_a:
            a_cont = side['content']
            a_cont_item_counts[len(a_cont)] += 1
            if len(a_cont) == 0:
                a_missing_cont_ids.add(id)
            else:
                a_type = a_cont[0]['type']
                a_type_counts[a_type] += 1
                a_text = a_cont[0]['text']
                a_text_counts[a_text] += 1
                a_image = a_cont[0]['image']
                a_image_counts[a_image] += 1
                a_mimeType = a_cont[0]['mimeType']
                a_mimeType_counts[a_mimeType] += 1

        conv_b = df.iloc[idx]['conversation_b']
        for side in conv_b:
            b_cont = side['content']
            b_cont_item_counts[len(b_cont)] += 1
            if len(b_cont) == 0:
                b_missing_cont_ids.add(id)
            else:
                b_type = b_cont[0]['type']
                b_type_counts[b_type] += 1
                b_text = b_cont[0]['text']
                b_text_counts[b_text] += 1
                b_image = b_cont[0]['image']
                b_image_counts[b_image] += 1
                b_mimeType = b_cont[0]['mimeType']
                b_mimeType_counts[b_mimeType] += 1

    print("=" * 80)    
    
    print(f"在 conversation_a 中发现 {len(a_cont_item_counts)} 种 len(content) 值")
    print(f"  len(content) 值列表: {sorted(a_cont_item_counts.keys())}")
    print(f"  len(content) 值分布: \n    len(content)      数量")
    for item in sorted(a_cont_item_counts.keys()):
        print(f"    {item:^15}{a_cont_item_counts[item]:^10}")
    
    print("-" * 80)  

    print(f"在 conversation_a 中发现 {len(a_type_counts)} 种 type 值")
    print(f"  type 值列表: {sorted(a_type_counts.keys())}")

    print("-" * 80)  

    print(f"在 conversation_a 中发现 {len(a_text_counts)} 种 text 值")
    print(" 最常出现的text（前3）为：")
    a_common_texts = a_text_counts.most_common(10)
    for idx in range(3):
        print(f"  {a_common_texts[idx]}")

    print("-" * 80)  

    print(f"在 conversation_a 中发现 {len(a_image_counts)} 种 image 值")
    print(f"  image 值列表: {sorted(a_image_counts.keys())}")

    print("-" * 80)

    print(f"在 conversation_a 中发现 {len(a_mimeType_counts)} 种 mimeType 值")
    print(f"  mimeType 值列表: {sorted(a_mimeType_counts.keys())}")

    print("=" * 80)    
    
    print(f"在 conversation_b 中发现 {len(b_cont_item_counts)} 种 len(content) 值")
    print(f"  len(content) 值列表: {sorted(b_cont_item_counts.keys())}")
    print(f"  len(content) 值分布: \n    len(content)      数量")
    for item in sorted(b_cont_item_counts.keys()):
        print(f"    {item:^15}{b_cont_item_counts[item]:^10}")
    
    print("-" * 80)  

    print(f"在 conversation_b 中发现 {len(b_type_counts)} 种 type 值")
    print(f"  type 值列表: {sorted(b_type_counts.keys())}")

    print("-" * 80)  

    print(f"在 conversation_b 中发现 {len(b_text_counts)} 种 text 值")
    print(" 最常出现的text（前3）为：")
    b_common_texts = b_text_counts.most_common(10)
    for idx in range(3):
        print(f"  {b_common_texts[idx]}")

    print("-" * 80)  

    print(f"在 conversation_b 中发现 {len(b_image_counts)} 种 image 值")
    print(f"  image 值列表: {sorted(b_image_counts.keys())}")

    print("-" * 80)

    print(f"在 conversation_b 中发现 {len(b_mimeType_counts)} 种 mimeType 值")
    print(f"  mimeType 值列表: {sorted(b_mimeType_counts.keys())}")

if __name__ == "__main__":
    print("=" * 80)
    print("分析 content 字段")
    print("=" * 80)

    touch_cont()