"""
C16_length_test

对优化数据集及各任务类别子集执行长度偏好 Wilcoxon 符号秩检验。

假设：
  H₀: median(δᵢ) = 0
  H₁: median(δᵢ) > 0
  其中 δᵢ = tokens(获胜模型) − tokens(落败模型)

仅保留 winner ∈ {model_a, model_b} 的行（排除 tie、both_bad）。

输出指标（每个子集）：
  n_pairs、pct_winner_longer、median_diff、Bootstrap 95% CI、
  Wilcoxon W、p 值（原始 + Bonferroni 校正）、rank-biserial r、效应分级

数据流向：
  Data/optimized_data/  →  Wilcoxon 检验  →  Reports/R13_wilcoxon_length_test_report.txt
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# 路径工厂
# ---------------------------------------------------------------------------

def get_data_dir(root: Path | str | None = None) -> Path:
    """返回优化数据目录的默认路径。"""
    if root is None:
        return Path.cwd() / "Data" / "optimized_data"
    return Path(root) / "Data" / "optimized_data"


# ---------------------------------------------------------------------------
# 子集定义：(标签, 文件名)
# 全量使用 optimized_data.parquet，其余使用 C13 生成的子集文件
# ---------------------------------------------------------------------------
SUBSETS: List[tuple[str, str]] = [
    ("全量",             "optimized_data.parquet"),
    # 16 个纯净分区（互不重叠，完整覆盖全量）
    ("无类别",           "no_category_data.parquet"),
    ("仅创意写作",       "only_cw_data.parquet"),
    ("仅指令遵循",       "only_if_data.parquet"),
    ("仅数学",           "only_math_data.parquet"),
    ("仅代码",           "only_code_data.parquet"),
    ("创意+指令",        "cw_if_data.parquet"),
    ("创意+数学",        "cw_math_data.parquet"),
    ("创意+代码",        "cw_code_data.parquet"),
    ("指令+数学",        "if_math_data.parquet"),
    ("指令+代码",        "if_code_data.parquet"),
    ("数学+代码",        "math_code_data.parquet"),
    ("创意+指令+数学",   "cw_if_math_data.parquet"),
    ("创意+指令+代码",   "cw_if_code_data.parquet"),
    ("创意+数学+代码",   "cw_math_code_data.parquet"),
    ("指令+数学+代码",   "if_math_code_data.parquet"),
    ("四类全含",         "all_categories_data.parquet"),
]

# 每个子集有效对数的最小阈值（低于此数则跳过）
MIN_PAIRS = 30

# Bootstrap 置信区间重采样次数
N_BOOTSTRAP = 1000

# 效应量分级阈值（Cohen's 惯例）
EFFECT_THRESHOLDS = [(0.1, "可忽略"), (0.3, "小"), (0.5, "中"), (float("inf"), "大")]


# ---------------------------------------------------------------------------
# 核心计算
# ---------------------------------------------------------------------------

def _build_diff(df: pd.DataFrame) -> np.ndarray:
    """
    构造 δᵢ = tokens(获胜模型) − tokens(落败模型)。

    排除 winner ∈ {tie, both_bad}，仅保留方向明确的配对。
    """
    mask = df["winner"].isin(["model_a", "model_b"])
    sub = df[mask].copy()
    delta = np.where(
        sub["winner"] == "model_a",
        sub["a_tokens"].values - sub["b_tokens"].values,
        sub["b_tokens"].values - sub["a_tokens"].values,
    )
    return delta.astype(np.float64)


def _bootstrap_ci(arr: np.ndarray, n_boot: int = N_BOOTSTRAP,
                  rng: Optional[np.random.Generator] = None) -> tuple[float, float]:
    """
    计算中位数的 Bootstrap 百分位置信区间（95%）。

    参数说明：
    - arr：差值数组
    - n_boot：重采样次数
    - rng：随机数生成器（可传入固定 seed，默认新建）

    返回：(ci_low, ci_high)
    """
    if rng is None:
        rng = np.random.default_rng(42)
    medians = np.array([
        np.median(rng.choice(arr, size=len(arr), replace=True))
        for _ in range(n_boot)
    ])
    return float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def _effect_level(r: float) -> str:
    """根据 rank-biserial r 的绝对值返回效应分级标签。"""
    abs_r = abs(r)
    if abs_r < 0.1:
        return "可忽略"
    elif abs_r < 0.3:
        return "小"
    elif abs_r < 0.5:
        return "中"
    else:
        return "大"


def _cohens_d(arr: np.ndarray) -> tuple[float, float]:
    """
    计算 Cohen's d 和 Hedges' g（参数效应量，非正态分布下仅供参考）。

    参数说明：
    - arr：差值数组（含零值）

    返回值：(cohen_d, hedges_g)；非零样本 < 3 时返回 (nan, nan)。
    """
    nonzero = arr[arr != 0]
    n = len(nonzero)
    if n < 3:
        return np.nan, np.nan
    d = float(nonzero.mean() / nonzero.std(ddof=1))
    g = d * (1 - 3 / (4 * n - 9))
    return round(d, 4), round(g, 4)


def run_one_subset(label: str, df: pd.DataFrame) -> Optional[Dict]:
    """
    对单个子集执行完整检验流程。

    参数说明：
    - label：子集标签（用于报告显示）
    - df：子集 DataFrame（包含 winner、a_tokens、b_tokens 列）

    返回：结果字典，若有效对数 < MIN_PAIRS 则返回 None
    """
    delta = _build_diff(df)
    n_pairs = len(delta)

    if n_pairs < MIN_PAIRS:
        print(f"  [{label}] 有效对数 {n_pairs} < {MIN_PAIRS}，跳过")
        return None

    # 排除差值为 0 的对（Wilcoxon 默认行为）
    nonzero = delta[delta != 0]
    n_nonzero = len(nonzero)

    # Wilcoxon 符号秩检验（单侧，H₁: median > 0）
    stat, p_raw = wilcoxon(delta, alternative="greater", zero_method="wilcox")

    # Rank-biserial 相关系数
    # scipy wilcoxon(alternative='greater') 返回负秩和 W⁻
    # 公式：r_rb = 1 - 2W⁻ / (n*(n+1))，此时 r_rb > 0 表示正向效应
    if n_nonzero > 0:
        r_rb = float(1 - 2 * stat / (n_nonzero * (n_nonzero + 1)))
    else:
        r_rb = 0.0

    # 中位差值与 Bootstrap CI
    median_diff = float(np.median(delta))
    ci_low, ci_high = _bootstrap_ci(delta)

    # 胜者更长的统计
    n_longer = int(np.sum(delta > 0))
    pct_longer = n_longer / n_pairs * 100

    cohen_d, hedges_g = _cohens_d(delta)

    result = {
        "label":            label,
        "n_pairs":          n_pairs,
        "n_winner_longer":  n_longer,
        "pct_winner_longer": round(pct_longer, 2),
        "median_diff":      round(median_diff, 1),
        "ci_low":           round(ci_low, 1),
        "ci_high":          round(ci_high, 1),
        "wilcoxon_stat":    float(stat),
        "p_value":          float(p_raw),
        # p_bonferroni 在主函数中填充（需知道 k）
        "p_bonferroni":     None,
        "rank_biserial_r":  round(r_rb, 4),
        "effect_level":     _effect_level(r_rb),
        "cohen_d":          cohen_d,
        "hedges_g":         hedges_g,
        "significant":      None,   # 在主函数中填充
    }
    return result


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------

def run_length_test(data_dir: Path | str | None = None,
                    report_dir: Path | str | None = None) -> None:
    """
    对所有预定义子集执行长度偏好 Wilcoxon 符号秩检验并生成报告。

    参数说明：
    - data_dir：子集 parquet 文件目录（默认为 Data/optimized_data）
    - report_dir：报告保存目录（默认为 Reports）
    """

    if data_dir is None:
        data_dir = get_data_dir()
    else:
        data_dir = Path(data_dir)

    if report_dir is None:
        report_dir = Path.cwd() / "Reports"
    else:
        report_dir = Path(report_dir)

    report_dir.mkdir(parents=True, exist_ok=True)

    results: List[Dict] = []

    print("=" * 80)
    print("C16 长度偏好 Wilcoxon 符号秩检验")
    print("=" * 80)

    for label, filename in SUBSETS:
        fpath = data_dir / filename
        if not fpath.exists():
            print(f"  [{label}] 文件不存在，跳过：{fpath}")
            continue

        df = pd.read_parquet(fpath, columns=["winner", "a_tokens", "b_tokens"])
        print(f"\n[{label}]  总行数={len(df):,}  读取完成")

        res = run_one_subset(label, df)
        if res is not None:
            results.append(res)

    if not results:
        print("ERROR: 无有效检验结果，退出。")
        return

    # Bonferroni 校正（k = 实际执行检验的子集数）
    k = len(results)
    for res in results:
        adj_p = min(res["p_value"] * k, 1.0)
        res["p_bonferroni"] = round(adj_p, 6)
        res["significant"] = adj_p < 0.05

    generate_report(results, k, report_dir)


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

def generate_report(results: List[Dict], k: int, report_dir: Path) -> None:
    """生成 R13 Wilcoxon 长度检验报告。"""

    report_path = report_dir / "R13_wilcoxon_length_test_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:

        f.write("=" * 80 + "\n")
        f.write("长度偏好 Wilcoxon 符号秩检验报告\n")
        f.write("=" * 80 + "\n\n")

        # 方法说明
        f.write("【检验方法】\n")
        f.write("  假设：H₀: median(δ)=0  vs  H₁: median(δ)>0（单侧）\n")
        f.write("  δᵢ = tokens(获胜模型) - tokens(落败模型)\n")
        f.write("  排除 winner∈{tie, both_bad}，仅使用方向明确的配对\n")
        f.write(f"  多重比较校正：Bonferroni（k={k} 个子集）\n")
        f.write(f"  效应量：rank-biserial r（W 统计量推导）\n")
        f.write(f"  中位差 CI：Bootstrap 百分位法（{N_BOOTSTRAP} 次重采样，seed=42）\n\n")

        # 效应量分级说明
        f.write("【效应量分级】\n")
        f.write("  |r| < 0.1  可忽略  |  0.1 ≤ |r| < 0.3  小\n")
        f.write("  0.3 ≤ |r| < 0.5  中  |  |r| ≥ 0.5  大\n\n")

        f.write("-" * 80 + "\n\n")

        for res in results:
            sig_tag = "✓ 显著" if res["significant"] else "✗ 不显著"
            f.write(f"【{res['label']}】{sig_tag}\n")
            f.write(f"  有效配对数          : {res['n_pairs']:,}\n")
            f.write(f"  胜者更长的对数       : {res['n_winner_longer']:,}  ({res['pct_winner_longer']}%)\n")
            f.write(f"  中位长度差 (tokens)  : {res['median_diff']:+.1f}  "
                    f"[Bootstrap 95% CI: {res['ci_low']:+.1f}, {res['ci_high']:+.1f}]\n")
            f.write(f"  Wilcoxon W           : {res['wilcoxon_stat']:.1f}\n")
            f.write(f"  p 值（原始）         : {res['p_value']:.4e}\n")
            f.write(f"  p 值（Bonferroni）   : {res['p_bonferroni']:.4e}\n")
            f.write(f"  rank-biserial r      : {res['rank_biserial_r']:.4f}  [{res['effect_level']}效应]\n")
            cd_str = f"{res['cohen_d']:.4f}" if not np.isnan(res['cohen_d']) else "N/A"
            hg_str = f"{res['hedges_g']:.4f}" if not np.isnan(res['hedges_g']) else "N/A"
            f.write(f"  Cohen's d / Hedges' g: {cd_str} / {hg_str}  （参数近似，仅供参考）\n")
            f.write("\n")

        # 汇总表格
        f.write("=" * 80 + "\n")
        f.write("汇总（按 rank-biserial r 排序）\n")
        f.write("=" * 80 + "\n")
        col_w = 16
        header = (f"{'子集':<{col_w}} {'n':>8} {'胜者偏长%':>10} "
                  f"{'中位差':>8} {'p(adj)':>12} {'r_rb':>8} {'d':>8} {'效应':>8} {'显著':>6}")
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        for res in sorted(results, key=lambda x: abs(x["rank_biserial_r"]), reverse=True):
            sig_mark = "✓" if res["significant"] else "✗"
            cd_str = f"{res['cohen_d']:.4f}" if not np.isnan(res['cohen_d']) else "N/A"
            row = (f"{res['label']:<{col_w}} {res['n_pairs']:>8,} "
                   f"{res['pct_winner_longer']:>9.1f}% "
                   f"{res['median_diff']:>+8.1f} "
                   f"{res['p_bonferroni']:>12.4e} "
                   f"{res['rank_biserial_r']:>8.4f} "
                   f"{cd_str:>8} "
                   f"{res['effect_level']:>8} "
                   f"{sig_mark:>6}")
            f.write(row + "\n")

        n_sig = sum(1 for r in results if r["significant"])
        f.write(f"\n显著子集数：{n_sig} / {k}（Bonferroni 校正 α=0.05）\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"\n报告已保存至: {report_path}")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 80)
    print("C16  长度偏好统计检验（Wilcoxon 符号秩 + Bonferroni + rank-biserial r）")
    print("=" * 80 + "\n")

    run_length_test()

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)
