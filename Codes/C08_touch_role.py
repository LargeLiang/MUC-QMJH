import pandas as pd
import os
from collections import Counter

def touch_role():
    """
    分析 role 字段
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"

    unique_a_roles = set()
    unique_a_role_counts = Counter()
    unique_b_roles = set()
    unique_b_role_counts = Counter()
    
    print(f"正在分析文件: {os.path.basename(file_path)}")
    df = pd.read_parquet(file_path)
    print(f"  数据形状: {df.shape}")

    for idx in range(len(df)):
        conv_a = df.iloc[idx]['conversation_a']
        for side in conv_a:
            a_role = side['role']
            unique_a_roles.add(a_role)
            unique_a_role_counts[a_role] += 1


        conv_b = df.iloc[idx]['conversation_b']
        for side in conv_b:
            b_role = side['role']
            unique_b_roles.add(b_role)
            unique_b_role_counts[b_role] += 1

    print("=" * 80)    

    print(f"在 conversation_a 中发现 {len(unique_a_roles)} 种不同的 role 值")
    print(f"  role 值列表: {sorted(unique_a_roles)}")
    print(f"  role 值分布: \n   role    数量")
    for role in sorted(unique_a_roles):
        print(f"{role:^10}{unique_a_role_counts[role]}")
    
    print("=" * 80)

    print(f"在 conversation_b 中发现 {len(unique_b_roles)} 种不同的 role 值")
    print(f"  role 值列表: {sorted(unique_b_roles)}")
    print(f"  role 值分布: \n   role    数量")
    for role in sorted(unique_b_roles):
        print(f"{role:^10}{unique_b_role_counts[role]}")

if __name__ == "__main__":
    print("=" * 80)
    print("分析 role 字段")
    print("=" * 80)

    touch_role()