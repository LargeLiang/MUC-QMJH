# -*- coding: utf-8 -*-
import pandas as pd
import os

# Set working directory
os.chdir(r"d:\Files\25_10_22_青苗计划")

# Read data
file_path = r"Data\optimized_data\optimized_data.parquet"
output_dir = r"Data\optimized_data"

print("Loading optimized data...")
df = pd.read_parquet(file_path)
print("Data shape: {}".format(df.shape))

# Single category subsets
print("\nCreating single category subsets...")
df[df['creative_writing_bool']==True].to_parquet(os.path.join(output_dir, "creative_writing_data.parquet"), index=False)
print("  creative_writing_data: {} rows".format((df['creative_writing_bool']==True).sum()))

df[df['if_bool']==True].to_parquet(os.path.join(output_dir, "if_data.parquet"), index=False)
print("  if_data: {} rows".format((df['if_bool']==True).sum()))

df[df['math_bool']==True].to_parquet(os.path.join(output_dir, "math_data.parquet"), index=False)
print("  math_data: {} rows".format((df['math_bool']==True).sum()))

# Pure subsets (only one category)
print("\nCreating pure subsets...")
only_cw = df[(df['creative_writing_bool']==True) & (df['if_bool']==False) & (df['math_bool']==False)]
only_cw.to_parquet(os.path.join(output_dir, "only_creative_writing_data.parquet"), index=False)
print("  only_creative_writing: {} rows".format(len(only_cw)))

only_if = df[(df['creative_writing_bool']==False) & (df['if_bool']==True) & (df['math_bool']==False)]
only_if.to_parquet(os.path.join(output_dir, "only_if_data.parquet"), index=False)
print("  only_if: {} rows".format(len(only_if)))

only_math = df[(df['creative_writing_bool']==False) & (df['if_bool']==False) & (df['math_bool']==True)]
only_math.to_parquet(os.path.join(output_dir, "only_math_data.parquet"), index=False)
print("  only_math: {} rows".format(len(only_math)))

# Two-category intersections
print("\nCreating two-category intersections...")
cw_if = df[(df['creative_writing_bool']==True) & (df['if_bool']==True)]
cw_if.to_parquet(os.path.join(output_dir, "creative_writing_if_data.parquet"), index=False)
print("  creative_writing_if: {} rows".format(len(cw_if)))

cw_math = df[(df['creative_writing_bool']==True) & (df['math_bool']==True)]
cw_math.to_parquet(os.path.join(output_dir, "creative_writing_math_data.parquet"), index=False)
print("  creative_writing_math: {} rows".format(len(cw_math)))

if_math = df[(df['if_bool']==True) & (df['math_bool']==True)]
if_math.to_parquet(os.path.join(output_dir, "if_math_data.parquet"), index=False)
print("  if_math: {} rows".format(len(if_math)))

# All three categories
print("\nCreating all-category subset...")
all_three = df[(df['creative_writing_bool']==True) & (df['if_bool']==True) & (df['math_bool']==True)]
all_three.to_parquet(os.path.join(output_dir, "all_categories_data.parquet"), index=False)
print("  all_categories: {} rows".format(len(all_three)))

# No category
print("\nCreating no-category subset...")
no_category = df[(df['creative_writing_bool']==False) & (df['if_bool']==False) & (df['math_bool']==False)]
no_category.to_parquet(os.path.join(output_dir, "no_category_data.parquet"), index=False)
print("  no_category: {} rows".format(len(no_category)))

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print("Total rows in original data: {}".format(len(df)))
print("Total rows in subsets: {}".format(
    len(only_cw) + len(only_if) + len(only_math) + 
    len(cw_if) + len(cw_math) + len(if_math) + 
    len(all_three) + len(no_category)
))
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
print("\nDone!")
