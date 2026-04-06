import pandas as pd
import os
from collections import Counter

def touch_category_tag():
    """
    分析 category_tag 字段
    """
    file_path = os.getcwd() + r"\Data\integrated_data\integrated_data.parquet"

    print(f"正在分析文件: {os.path.basename(file_path)}")
    df = pd.read_parquet(file_path)
    print(f"  数据形状: {df.shape}")

    creative_writing_count = Counter()
    creative_writing_score_count = Counter()

    complexity_count = Counter()
    creativity_count = Counter()
    domain_knowledge_count = Counter()
    problem_solving_count = Counter()
    real_world_count = Counter()
    specificity_count = Counter()
    technical_accuracy_count = Counter()

    if_count = Counter()
    if_score_count = Counter()

    math_count = Counter()

    language_count = Counter()

    is_code_count = Counter()

    for idx in range(len(df)):
        cate_tag = df.iloc[idx]['category_tag']

        creative_writing_count[cate_tag['creative_writing_v0.1']['creative_writing']] += 1
        creative_writing_score_count[cate_tag['creative_writing_v0.1']['score']] += 1

        crit = cate_tag['criteria_v0.1']
        
        complexity_count[crit['complexity']] += 1
        creativity_count[crit['creativity']] += 1
        domain_knowledge_count[crit['domain_knowledge']] += 1
        problem_solving_count[crit['problem_solving']] += 1
        real_world_count[crit['real_world']] += 1
        specificity_count[crit['specificity']] += 1
        technical_accuracy_count[crit['technical_accuracy']] += 1

        if_count[cate_tag['if_v0.1']['if']] += 1
        if_score_count[cate_tag['if_v0.1']['score']] += 1

        math_count[cate_tag['math_v0.1']['math']] += 1

        language_count[df.iloc[idx]['language']] += 1

        is_code_count[df.iloc[idx]['is_code']] += 1

    print("=" * 80)    

    print(f"发现 {len(creative_writing_count)} 种不同的 creative_writing 值")
    print(f"  creative_writing  值列表: {sorted(creative_writing_count.keys())}")
    print(f"  creative_writing  值分布: \n   creative_writing    数量")
    for tag in sorted(creative_writing_count.keys()):
        print(f"{tag:^10}{creative_writing_count[tag]}")
    
    print(f"\n发现 {len(creative_writing_score_count)} 种不同的 creative_writing 的 score 值")
    print(f"  score  值列表: {creative_writing_score_count.keys()}")
    print(f"  score  值分布: \n   score    数量")
    for tag in creative_writing_score_count.keys():
        print(f"     {tag}    {creative_writing_score_count[tag]}")

    print("=" * 80)

    print(f"发现 {len(complexity_count)} 种不同的 complexity 值")
    print(f"  complexity 值列表: {sorted(complexity_count.keys())}")
    print(f"  complexity 值分布: \n   complexity    数量")
    for tag in sorted(complexity_count.keys()):
        print(f"{tag:^10}{complexity_count[tag]}")
    
    print(f"\n发现 {len(creativity_count)} 种不同的 creativity 值")
    print(f"  creativity 值列表: {sorted(creativity_count.keys())}")
    print(f"  creativity 值分布: \n   creativity    数量")
    for tag in sorted(creativity_count.keys()):
        print(f"{tag:^10}{creativity_count[tag]}")
    
    print(f"\n发现 {len(domain_knowledge_count)} 种不同的 domain_knowledge 值")
    print(f"  domain_knowledge 值列表: {sorted(domain_knowledge_count.keys())}")
    print(f"  domain_knowledge 值分布: \n   domain_knowledge    数量")
    for tag in sorted(domain_knowledge_count.keys()):
        print(f"{tag:^10}{domain_knowledge_count[tag]}")
    
    print(f"\n发现 {len(problem_solving_count)} 种不同的 problem_solving 值")
    print(f"  problem_solving 值列表: {sorted(problem_solving_count.keys())}")
    print(f"  problem_solving 值分布: \n   problem_solving    数量")
    for tag in sorted(problem_solving_count.keys()):
        print(f"{tag:^10}{problem_solving_count[tag]}")

    print(f"\n发现 {len(real_world_count)} 种不同的 real_world 值")
    print(f"  real_world 值列表: {sorted(real_world_count.keys())}")
    print(f"  real_world 值分布: \n   real_world    数量")
    for tag in sorted(real_world_count.keys()):
        print(f"{tag:^10}{real_world_count[tag]}")
    
    print(f"\n发现 {len(specificity_count)} 种不同的 specificity 值")
    print(f"  specificity 值列表: {sorted(specificity_count.keys())}")
    print(f"  specificity 值分布: \n   specificity    数量")
    for tag in sorted(specificity_count.keys()):
        print(f"{tag:^10}{specificity_count[tag]}")

    print(f"\n发现 {len(technical_accuracy_count)} 种不同的 technical_accuracy 值")
    print(f"  technical_accuracy 值列表: {sorted(technical_accuracy_count.keys())}")
    print(f"  technical_accuracy 值分布: \n    technical_accuracy    数量")
    for tag in sorted(technical_accuracy_count.keys()):
        print(f"{tag:^20}{technical_accuracy_count[tag]}")

    print("=" * 80)

    print(f"发现 {len(if_count)} 种不同的 if 值")
    print(f"  if 值列表: {sorted(if_count.keys())}")
    print(f"  if 值分布: \n    if     数量")
    for tag in sorted(if_count.keys()):
        print(f"{tag:^10}{if_count[tag]:^8}")

    print(f"\n发现 {len(if_score_count)} 种不同的 if 的 score 值")
    print(f"  score 值列表: {if_score_count.keys()}")
    print(f"  score 值分布: \n    score    数量")
    for tag in if_score_count.keys():
        print(f"     {tag}    {if_score_count[tag]}")

    print("=" * 80)

    print(f"发现 {len(math_count)} 种不同的 math 值")
    print(f"  math 值列表: {sorted(math_count.keys())}")
    print(f"  math 值分布: \n   math    数量")
    for tag in sorted(math_count.keys()):
        print(f"{tag:^10}{math_count[tag]}")

    print("=" * 80)

    print(f"发现 {len(language_count)} 种不同的 language 值")
    print(f"  language 值列表: {sorted(language_count.keys())}")
    print(f"  language 值分布: \n   language    数量")
    for tag in sorted(language_count.keys()):
        print(f"{tag:^10}{language_count[tag]}")
    
    print("=" * 80)

    print(f"发现 {len(is_code_count)} 种不同的 is_code 值")
    print(f"  is_code 值列表: {sorted(is_code_count.keys())}")
    print(f"  is_code 值分布: \n   is_code    数量")
    for tag in sorted(is_code_count.keys()):
        print(f"{tag:^10}{is_code_count[tag]}")

if __name__ == "__main__":
    print("=" * 80)
    print("分析 category_tag 字段")
    print("=" * 80)

    touch_category_tag()