import pandas as pd
import os
from collections import Counter

def verify_token_correction():
    """
    分析 conv_metadata 字段
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"

    print(f"正在分析文件: {os.path.basename(file_path)}")
    df = pd.read_parquet(file_path)
    print(f"  数据形状: {df.shape}")

    # 判断 conversation_b 中 role 为 'user' 的 num_tokens 之和 是否总等于 sum_user_tokens，若否，记录反例数量
    check_point_1 = 0

    # 判断 conversation_b 中 role 为 'assistant' 的 num_tokens 之和 是否总等于 sum_assistant_b_tokens
    check_point_2 = True

    # 判断 conversation_b 中 role 为 'user' 的 num_tokens 之和 是否总小于 sum_user_tokens
    check_point_3 = True
    
    for idx in range(len(df)):
        conv_meta = df.iloc[idx]['conv_metadata']

        user_token_1 = conv_meta['sum_user_tokens']
        user_token_2 = 0
        b_token_1 = conv_meta['sum_assistant_b_tokens']
        b_token_2 = 0

        conv_b = df.iloc[idx]['conversation_b']
        for side in conv_b:
            num_tokens = side['num_tokens']
            role = side['role']

            if(role == 'assistant'):
                b_token_2 += num_tokens
            else:
                user_token_2 += num_tokens

        if user_token_1 != user_token_2:
            check_point_1 += 1

        if b_token_1 != b_token_2:
            check_point_2 = False
        
        if user_token_1 < user_token_2:
            check_point_3 = False

    print("conversation_b 中 role 为 'user' 的 num_tokens 之和 是否总等于 sum_user_tokens：",check_point_1 == 0)
    if check_point_1 != 0:
        print(f"  反例数量为：{check_point_1}")
    print("conversation_b 中 role 为 'assistant' 的 num_tokens 之和 是否总等于 sum_assistant_b_tokens:",check_point_2)
    print("conversation_b 中 role 为 'user' 的 num_tokens 之和 是否总小于 sum_user_tokens",check_point_3)

if __name__ == "__main__":
    print("=" * 80)
    print("分析 token 相关字段")
    print("=" * 80)

    verify_token_correction()