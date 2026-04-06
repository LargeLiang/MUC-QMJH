import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from typing import Dict

def check_qualification(row) -> bool:
    check_point = True

    if row['evaluation_order'] > 1:
        check_point = False

    a_conv = row['conversation_a']
    for side in a_conv:
        a_cont = side['content']
        if len(a_cont) == 0:
            check_point = False
            break
    
    b_conv = row['conversation_b']
    for side in b_conv:
        b_cont = side['content']
        if len(b_cont) == 0:
            check_point = False
            break

    cate_tag = row['category_tag']

    if cate_tag['creative_writing_v0.1']['score'] == None:
        check_point = False

    if cate_tag['if_v0.1']['score'] == None:
        check_point = False

    if row['language'] == '<err>':
        check_point = False
        
    return check_point

def optimize_conversation(conv_a: np.ndarray, conv_b: np.ndarray) -> Dict:
    """
    优化对话，按照 role 与 turn 区分
    """
    optimized_conv = {
        'turns': len(conv_a) // 2,
        'a_conv': {},
        'b_conv': {},
        'user_conv': {}
    }
    
    for i, side in enumerate(conv_a):
        role = side['role']
        cont = side['content']
        text = cont[0]['text']
        turn = i // 2 + 1

        if role  == 'user':
            optimized_conv['user_conv'].update({f'turn_{turn}_user_text': text})
        elif role == 'assistant':
            optimized_conv['a_conv'].update({f'turn_{turn}_a_text': text})

    for i, side in enumerate(conv_b):
        role = side['role']
        cont = side['content']
        text = cont[0]['text']
        turn = i // 2 + 1

        if role == 'assistant':
            optimized_conv['b_conv'].update({f'turn_{turn}_b_text': text})
    
    return optimized_conv

def optimize_conv_metadata(metadata: Dict) -> Dict:
    """
    优化conv_metadata字段，只提取关键字段，避免过度膨胀
    """
    optimized_metadata = {
        'a_tokens': metadata['sum_assistant_a_tokens'],
        'a_header_counts': metadata['header_count_a'],
        'a_list_counts': metadata['list_count_a'],
        'a_bold_counts': metadata['bold_count_a'],
        'b_tokens': metadata['sum_assistant_b_tokens'],
        'b_header_counts': metadata['header_count_b'],
        'b_list_counts': metadata['list_count_b'],
        'b_bold_counts': metadata['bold_count_b'],
        'user_tokens': metadata['sum_user_tokens']
    }
    
    return optimized_metadata

def optimize_category_tag(category_tag: Dict) -> Dict:
    """
    优化category_tag字段，只保留关键字段与评分
    """
    optimized_category_tag = {}
    
    # creative_writing
    creative_writing = category_tag['creative_writing_v0.1']
    optimized_category_tag.update({'creative_writing_bool': creative_writing['creative_writing'],
                                   'creative_writing_score': creative_writing['score']})
    
    # instruction following
    if_data = category_tag['if_v0.1']
    optimized_category_tag.update({'if_bool': if_data['if'],
                                   'if_score': if_data['score']})
    
    # math
    math_data = category_tag['math_v0.1']
    optimized_category_tag.update({'math_bool': math_data['math']})
    
    return optimized_category_tag

def optimize_criteria(category_tag: Dict) -> Dict:
    """
    优化criteria字段，只保留关键字段
    """
    optimized_criteria = {}
    
    criteria = category_tag['criteria_v0.1']

    optimized_criteria.update({'complexity': criteria['complexity'],'creativity': criteria['creativity'],
                               'domain_knowledge': criteria['domain_knowledge'],'problem_solving': criteria['problem_solving'],
                               'real_world': criteria['real_world'],'specificity': criteria['specificity'],
                               'technical_accuracy': criteria['technical_accuracy']
                               })
    
    return optimized_criteria

def optimize_data():
    """
    优化原数据结构
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"

    output_dir = os.getcwd() + r"\Data\optimized_data"
    os.makedirs(output_dir, exist_ok=True)

    optimized_df = []

    print(f"\n处理文件: {os.path.basename(file_path)}")

    df = pd.read_parquet(file_path)
    print(f"原始数据形状: {df.shape}")
    
    optimized_rows = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="处理行"):
        # 检验是否需清除当前行
        if check_qualification(row) == True:
            optimized_row = {}

            # 可直接迁移的字段
            direct_cols = ['id', 'model_a', 'model_b', 'winner', 'language', 'is_code']
        
            for col in direct_cols:
                optimized_row[col] = row[col]
        
            optimized_row.update(optimize_conversation(row['conversation_a'], row['conversation_b']))
        
            optimized_row.update(optimize_conv_metadata(row['conv_metadata']))
        
            optimized_row.update(optimize_category_tag(row['category_tag']))
        
            optimized_row.update(optimize_criteria(row['category_tag']))

            optimized_rows.append(optimized_row)
    
    # 转换为DataFrame并保存
    optimized_df = pd.DataFrame(optimized_rows)
    output_file = os.path.join(output_dir, f"optimized_data.parquet")
    optimized_df.to_parquet(output_file, index=False)
    print(f"已保存为Parquet: {output_file}")
    print(f"处理完成！优化后数据行数: {len(optimized_df)}")
    print(f"优化后数据列数: {len(optimized_df.columns)}")
    print(f"保存到: {output_file}")

    return None

def divide_data():
    """
    划分数据集
    """

    data_path = os.getcwd() + r"\Data\optimized_data\optimized_data.parquet"
    df = pd.read_parquet(data_path)
    
    # 划分训练集、验证集、测试集
    creative_writing_df = df[~df['creative_writing_bool'].isin([True])].copy()
    if_df = df[~df['if_bool'].isin([True])].copy()
    math_df = df[~df['math_bool'].isin([True])].copy()

    # 保存划分后的数据
    output_dir = os.getcwd() + r"\Data\optimized_data"
    creative_writing_df.to_parquet(os.path.join(output_dir, "creative_writing_data.parquet"), index=False)
    if_df.to_parquet(os.path.join(output_dir, "if_data.parquet"), index=False)
    math_df.to_parquet(os.path.join(output_dir, "math_data.parquet"), index=False)

    print(f"数据划分完成！")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("优化原文件数据结构")
    print("\n" + "=" * 80)

    optimize_data() 
    divide_data()