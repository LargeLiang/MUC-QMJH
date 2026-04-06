# -*- coding: utf-8 -*-
"""
Data Subset Division by Category Tag
根据 category_tag 将优化数据划分为多个子集
"""
import pandas as pd
import os

def divide_subset_by_category():
    """
    根据 category_tag 中的三个类别标签将数据划分为子集
    """
    file_path = os.path.join(os.getcwd(), "Data", "optimized_data", "optimized_data.parquet")
    output_dir = os.path.join(os.getcwd(), "Data", "optimized_data")
    
    print("Loading optimized data...")
    df = pd.read_parquet(file_path)
    print("Data shape: {}".format(df.shape))
    
    # Single category subsets
    print("\nCreating single category subsets...")
    
    creative_writing_df = df[df['creative_writing_bool'] == True].copy()
    creative_writing_df.to_parquet(os.path.join(output_dir, "creative_writing_data.parquet"), index=False)
    cw_count = len(creative_writing_df)
    print("  creative_writing_data: {} rows".format(cw_count))
    
    if_df = df[df['if_bool'] == True].copy()
    if_df.to_parquet(os.path.join(output_dir, "if_data.parquet"), index=False)
    if_count = len(if_df)
    print("  if_data: {} rows".format(if_count))
    
    math_df = df[df['math_bool'] == True].copy()
    math_df.to_parquet(os.path.join(output_dir, "math_data.parquet"), index=False)
    math_count = len(math_df)
    print("  math_data: {} rows".format(math_count))
    
    # Pure subsets (only one category)
    print("\nCreating pure subsets (single category only)...")
    
    only_cw_mask = (df['creative_writing_bool'] == True) & (df['if_bool'] == False) & (df['math_bool'] == False)
    only_if_mask = (df['creative_writing_bool'] == False) & (df['if_bool'] == True) & (df['math_bool'] == False)
    only_math_mask = (df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == True)
    
    only_creative_writing_df = df[only_cw_mask].copy()
    only_creative_writing_df.to_parquet(os.path.join(output_dir, "only_creative_writing_data.parquet"), index=False)
    print("  only_creative_writing: {} rows".format(len(only_creative_writing_df)))
    
    only_if_df = df[only_if_mask].copy()
    only_if_df.to_parquet(os.path.join(output_dir, "only_if_data.parquet"), index=False)
    print("  only_if: {} rows".format(len(only_if_df)))
    
    only_math_df = df[only_math_mask].copy()
    only_math_df.to_parquet(os.path.join(output_dir, "only_math_data.parquet"), index=False)
    print("  only_math: {} rows".format(len(only_math_df)))
    
    # Two-category intersections
    print("\nCreating two-category intersections...")
    
    cw_if_mask = (df['creative_writing_bool'] == True) & (df['if_bool'] == True)
    cw_if_df = df[cw_if_mask].copy()
    cw_if_df.to_parquet(os.path.join(output_dir, "creative_writing_if_data.parquet"), index=False)
    print("  creative_writing_if: {} rows".format(len(cw_if_df)))
    
    cw_math_mask = (df['creative_writing_bool'] == True) & (df['math_bool'] == True)
    cw_math_df = df[cw_math_mask].copy()
    cw_math_df.to_parquet(os.path.join(output_dir, "creative_writing_math_data.parquet"), index=False)
    print("  creative_writing_math: {} rows".format(len(cw_math_df)))
    
    if_math_mask = (df['if_bool'] == True) & (df['math_bool'] == True)
    if_math_df = df[if_math_mask].copy()
    if_math_df.to_parquet(os.path.join(output_dir, "if_math_data.parquet"), index=False)
    print("  if_math: {} rows".format(len(if_math_df)))
    
    # All three categories
    print("\nCreating all-category subset...")
    
    all_three_mask = (df['creative_writing_bool'] == True) & (df['if_bool'] == True) & (df['math_bool'] == True)
    all_three_df = df[all_three_mask].copy()
    all_three_df.to_parquet(os.path.join(output_dir, "all_categories_data.parquet"), index=False)
    print("  all_categories: {} rows".format(len(all_three_df)))
    
    # No category
    print("\nCreating no-category subset...")
    
    none_mask = (df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == False)
    none_df = df[none_mask].copy()
    none_df.to_parquet(os.path.join(output_dir, "no_category_data.parquet"), index=False)
    print("  no_category: {} rows".format(len(none_df)))
    
    # Generate report
    print("\n" + "="*70)
    print("DATA SUBSET DIVISION REPORT")
    print("="*70)
    
    report_file = os.path.join(os.getcwd(), "Reports", "R07_subset_division_report.txt")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("Data Subset Division Report\n")
        f.write("="*70 + "\n\n")
        
        f.write("ORIGINAL DATA:\n")
        f.write("  Total rows: {}\n\n".format(len(df)))
        
        f.write("SINGLE CATEGORY SUBSETS:\n")
        f.write("  creative_writing: {} rows\n".format(cw_count))
        f.write("  if: {} rows\n".format(if_count))
        f.write("  math: {} rows\n\n".format(math_count))
        
        f.write("PURE SUBSETS (Single Category Only):\n")
        f.write("  only_creative_writing: {} rows\n".format(len(only_creative_writing_df)))
        f.write("  only_if: {} rows\n".format(len(only_if_df)))
        f.write("  only_math: {} rows\n\n".format(len(only_math_df)))
        
        f.write("TWO-CATEGORY INTERSECTIONS:\n")
        f.write("  creative_writing & if: {} rows\n".format(len(cw_if_df)))
        f.write("  creative_writing & math: {} rows\n".format(len(cw_math_df)))
        f.write("  if & math: {} rows\n\n".format(len(if_math_df)))
        
        f.write("ALL-CATEGORY SUBSET:\n")
        f.write("  all_categories: {} rows\n\n".format(len(all_three_df)))
        
        f.write("NO-CATEGORY SUBSET:\n")
        f.write("  no_category: {} rows\n\n".format(len(none_df)))
    
    print("\nReport saved to: {}".format(report_file))
    
    # Summary
    print("\nSubset files created:")
    print("  1. creative_writing_data.parquet")
    print("  2. if_data.parquet")
    print("  3. math_data.parquet")
    print("  4. only_creative_writing_data.parquet")
    print("  5. only_if_data.parquet")
    print("  6. only_math_data.parquet")
    print("  7. creative_writing_if_data.parquet")
    print("  8. creative_writing_math_data.parquet")
    print("  9. if_math_data.parquet")
    print(" 10. all_categories_data.parquet")
    print(" 11. no_category_data.parquet")
    print("\nAll subsets created successfully!")


if __name__ == "__main__":
    divide_subset_by_category()
