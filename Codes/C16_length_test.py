# -*- coding: utf-8 -*-
"""
Wilcoxon Signed-Rank Test for Preference Analysis
基于Wilcoxon符号秩检验的偏好存在性检验
对总体数据和各类别子集进行分析
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
from datetime import datetime

class PreferenceAnalyzer:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.getcwd(), "Data", "optimized_data")
        self.data_dir = data_dir
        self.results = {}
        self.report_lines = []
        
    def calculate_token_diff(self, row):
        """
        计算token差值: d_i = 获胜模型的token数 - 落败模型的token数
        """
        if row["winner"] == "model_a":
            return row["a_tokens"] - row["b_tokens"]
        else:
            return row["b_tokens"] - row["a_tokens"]
    
    def perform_wilcoxon_test(self, df, subset_name):
        """
        执行Wilcoxon符号秩检验
        """
        # 过滤有效数据
        df = df[df["winner"].isin(["model_a", "model_b"])].copy()
        
        if len(df) == 0:
            return None
        
        # 计算token差值
        df["token_diff"] = df.apply(self.calculate_token_diff, axis=1)
        
        # 分离零值和非零值
        df_nonzero = df[df["token_diff"] != 0].copy()
        n_zero = len(df) - len(df_nonzero)
        
        if len(df_nonzero) == 0:
            return {
                'subset_name': subset_name,
                'n_total': len(df),
                'n_nonzero': 0,
                'n_zero': n_zero,
                'positive_count': 0,
                'negative_count': 0,
                'positive_ratio': np.nan,
                'mean_diff': np.nan,
                'median_diff': np.nan,
                'statistic': np.nan,
                'p_value': np.nan,
                'significant': False,
                'error': 'No non-zero differences'
            }
        
        # 计算正负差值
        positive_count = (df_nonzero["token_diff"] > 0).sum()
        negative_count = (df_nonzero["token_diff"] < 0).sum()
        
        # 执行Wilcoxon检验
        try:
            statistic, p_value = wilcoxon(
                df_nonzero["token_diff"],
                alternative="greater"
            )
        except Exception as e:
            return {
                'subset_name': subset_name,
                'n_total': len(df),
                'n_nonzero': len(df_nonzero),
                'n_zero': n_zero,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'positive_ratio': positive_count / len(df_nonzero),
                'mean_diff': df_nonzero["token_diff"].mean(),
                'median_diff': df_nonzero["token_diff"].median(),
                'statistic': np.nan,
                'p_value': np.nan,
                'significant': False,
                'error': str(e)
            }
        
        return {
            'subset_name': subset_name,
            'n_total': len(df),
            'n_nonzero': len(df_nonzero),
            'n_zero': n_zero,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'positive_ratio': positive_count / len(df_nonzero),
            'mean_diff': df_nonzero["token_diff"].mean(),
            'median_diff': df_nonzero["token_diff"].median(),
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'error': None
        }
    
    def load_and_test_dataset(self, filename, subset_name):
        """
        加载数据集并进行检验
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print("Warning: {} not found".format(filepath))
            return None
        
        df = pd.read_parquet(filepath)
        result = self.perform_wilcoxon_test(df, subset_name)
        
        if result is not None:
            self.results[subset_name] = result
        
        return result
    
    def run_all_tests(self):
        """
        对总体数据和各类别子集进行检验（与 C17 格式保持一致）
        """
        root_df_path = os.path.join(self.data_dir, "optimized_data.parquet")
        if not os.path.exists(root_df_path):
            raise FileNotFoundError(f"{root_df_path} not found")

        print("Loading full dataset for subset-based testing...")
        df = pd.read_parquet(root_df_path)
        df = df[df["winner"].isin(["model_a", "model_b"])].copy()

        subsets = {
            'Overall Data (Total)': df,
            'Creative Writing': df[df['creative_writing_bool'] == True],
            'Instruction Following': df[df['if_bool'] == True],
            'Math': df[df['math_bool'] == True],
            'Only Creative Writing': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == False) & (df['math_bool'] == False)],
            'Only IF': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == True) & (df['math_bool'] == False)],
            'Only Math': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == True)],
            'CW & IF': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True)],
            'CW & Math': df[(df['creative_writing_bool'] == True) & (df['math_bool'] == True)],
            'IF & Math': df[(df['if_bool'] == True) & (df['math_bool'] == True)],
            'All Categories': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True) & (df['math_bool'] == True)],
            'No Category': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == False)],
        }

        print("\n" + "="*80)
        print("Performing Wilcoxon Signed-Rank Tests for all subsets...")
        print("="*80)

        for subset_name, subset_df in subsets.items():
            result = self.perform_wilcoxon_test(subset_df, subset_name)
            if result is not None:
                self.results[subset_name] = result
                status = "PASS" if result['significant'] else "FAIL"
                print("[{}] {} - n={} (p={:.4f})".format(
                    status, subset_name, result['n_total'], result.get('p_value', np.nan)))
    
    def generate_report(self):
        """
        生成详细报告
        """
        report = []
        report.append("="*80)
        report.append("Wilcoxon Signed-Rank Test Report")
        report.append("Preference Existence Test for LLM Output Texts")
        report.append("="*80)
        report.append("")
        report.append("Generation Time: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        report.append("")
        
        report.append("="*80)
        report.append("TEST DESIGN & HYPOTHESIS")
        report.append("="*80)
        report.append("")
        report.append("Null Hypothesis (H0):")
        report.append("  The median of token differences equals 0")
        report.append("  (No preference for response length)")
        report.append("")
        report.append("Alternative Hypothesis (H1):")
        report.append("  The median of token differences > 0")
        report.append("  (Users prefer longer responses)")
        report.append("")
        report.append("Significance Level: alpha = 0.05")
        report.append("")
        report.append("Token Difference Calculation:")
        report.append("  d_i = tokens(winning_model) - tokens(losing_model)")
        report.append("  - Positive d_i: winning model has more tokens (longer)")
        report.append("  - Negative d_i: winning model has fewer tokens (shorter)")
        report.append("")
        
        report.append("="*80)
        report.append("RESULTS SUMMARY TABLE")
        report.append("="*80)
        report.append("")
        
        # 生成汇总表
        summary_data = []
        for subset_name, result in sorted(self.results.items()):
            if result['error'] is None:
                summary_data.append({
                    'Subset': subset_name,
                    'N_total': result['n_total'],
                    'N_nonzero': result['n_nonzero'],
                    'Positive': result['positive_count'],
                    'Negative': result['negative_count'],
                    'Pos_Ratio': "{:.2%}".format(result['positive_ratio']),
                    'Median_Diff': "{:.2f}".format(result['median_diff']),
                    'T_Statistic': "{:.2f}".format(result['statistic']),
                    'P_Value': "{:.6f}".format(result['p_value']),
                    'Significant': "***" if result['significant'] else "ns"
                })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            report.append(df_summary.to_string(index=False))
        
        report.append("")
        report.append("Note: *** = p < 0.05 (significant); ns = not significant")
        report.append("")
        
        report.append("="*80)
        report.append("DETAILED TEST RESULTS")
        report.append("="*80)
        report.append("")
        
        for subset_name in sorted(self.results.keys()):
            result = self.results[subset_name]
            
            report.append("-"*80)
            report.append("Subset: {}".format(result['subset_name']))
            report.append("-"*80)
            
            if result['error'] is not None:
                report.append("Error: {}".format(result['error']))
                report.append("")
                continue
            
            report.append("Sample Information:")
            report.append("  Total samples: {}".format(result['n_total']))
            report.append("  Non-zero differences: {}".format(result['n_nonzero']))
            report.append("  Zero differences (tied): {}".format(result['n_zero']))
            report.append("")
            
            report.append("Token Difference Distribution:")
            report.append("  Positive (winner longer): {} ({:.2%})".format(
                result['positive_count'], result['positive_ratio']))
            report.append("  Negative (winner shorter): {} ({:.2%})".format(
                result['negative_count'], 1 - result['positive_ratio']))
            report.append("")
            
            report.append("Descriptive Statistics:")
            report.append("  Mean difference: {:.2f} tokens".format(result['mean_diff']))
            report.append("  Median difference: {:.2f} tokens".format(result['median_diff']))
            report.append("")
            
            report.append("Wilcoxon Test Results:")
            report.append("  Test Statistic (T): {:.2f}".format(result['statistic']))
            report.append("  P-value (one-tailed, greater): {:.6f}".format(result['p_value']))
            report.append("")
            
            if result['p_value'] < 0.001:
                sig_level = "p < 0.001 ***"
            elif result['p_value'] < 0.01:
                sig_level = "p < 0.01 **"
            elif result['p_value'] < 0.05:
                sig_level = "p < 0.05 *"
            else:
                sig_level = "p >= 0.05 (ns)"
            
            report.append("Conclusion:")
            if result['significant']:
                report.append("  Reject H0 ({})".format(sig_level))
                report.append("  → There is SIGNIFICANT statistical evidence that users")
                report.append("    prefer LONGER responses in this subset.")
            else:
                report.append("  Fail to reject H0 ({})".format(sig_level))
                report.append("  → There is NOT sufficient evidence to conclude that")
                report.append("    users prefer longer responses in this subset.")
            
            # 补充分析
            if result['positive_ratio'] > 0.5:
                report.append("  + Descriptively: {:.1%} of winning models are longer,".format(
                    result['positive_ratio']))
                report.append("    suggesting a directional preference for length.")
            else:
                report.append("  - Descriptively: only {:.1%} of winning models are longer.".format(
                    result['positive_ratio']))
            
            report.append("")
        
        report.append("="*80)
        report.append("OVERALL SUMMARY & INTERPRETATION")
        report.append("="*80)
        report.append("")
        
        significant_subsets = [name for name, result in self.results.items() 
                              if result['error'] is None and result['significant']]
        
        report.append("Subsets with significant length preference (p < 0.05):")
        if significant_subsets:
            for subset in significant_subsets:
                result = self.results[subset]
                report.append("  - {}: p = {:.6f}, n = {}".format(
                    subset, result['p_value'], result['n_nonzero']))
        else:
            report.append("  (None)")
        
        report.append("")
        report.append("Overall Findings:")
        report.append("  This analysis examines whether user preferences systematically")
        report.append("  favor longer AI responses across different response categories.")
        report.append("")
        
        return "\n".join(report)
    
    def save_report(self, output_path=None):
        """
        保存报告到文件
        """
        if output_path is None:
            output_path = os.path.join(os.getcwd(), "Reports", "R08_wilcoxon_test_report.txt")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\nReport saved to: {}".format(output_path))
        return output_path


def main():
    # 初始化分析器
    analyzer = PreferenceAnalyzer()
    
    # 执行所有检验
    analyzer.run_all_tests()
    
    # 生成并保存报告
    report = analyzer.generate_report()
    analyzer.save_report()
    
    # 打印简要结果
    print("\n" + "="*80)
    print("QUICK SUMMARY")
    print("="*80)
    print(report[:2000] + "\n... (see full report for details) ...\n")


if __name__ == "__main__":
    main()