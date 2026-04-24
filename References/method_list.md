# 项目统计学方法清单

这份清单只整理 Codes 目录中真正参与结果解释的统计学概念，重点覆盖三类内容：检验方法、效应量、计算概念。它的作用不是替代脚本，而是把“代码里用了什么方法、这些方法各自在回答什么问题、应该先看哪份入门说明”一次性列清楚。

## 整理原则

- 只收录已经出现在项目脚本中的概念，不额外扩展教材外的新方法。
- 优先整理会直接影响结论解释的概念，而不是一般性的编程技巧。
- 对高度相关但在解释上可以独立成立的概念，分别给出单独入门文档。
- 对紧贴母方法、单独拆开反而会割裂理解的子概念，放入对应母文档统一讲解，例如 caliper、公共支持区间、pseudo R²、AIC/BIC。

## 一、描述统计与基础计算

| 概念 | 主要回答的问题 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- |
| 描述统计 | 数据大致长什么样，均值、标准差、胜率、样本占比是多少 | [C14](../Codes/C14_visualize_length_preference.py), [C15](../Codes/C15_visualize_format_preference.py), [C22](../Codes/C22_sem_analysis.py) | [descriptive_statistics_method_introduction.md](methods/descriptive_statistics_method_introduction.md) |
| 相关分析与趋势线 | 长度差或格式密度变化时，胜率是否同步变化，变化形状是否近似线性或弯曲 | [C14](../Codes/C14_visualize_length_preference.py) | [correlation_and_trend_method_introduction.md](methods/correlation_and_trend_method_introduction.md) |
| 文本格式密度 | 在不同长度文本之间，如何公平比较标题、列表、粗体的使用强度 | [C15](../Codes/C15_visualize_format_preference.py), [C18](../Codes/C18_pure_effect.py), [C22](../Codes/C22_sem_analysis.py) | [text_density_method_introduction.md](methods/text_density_method_introduction.md) |
| z-score 标准化 | 不同量纲的变量如何放到同一个模型里比较 | [C18](../Codes/C18_pure_effect.py), [C22](../Codes/C22_sem_analysis.py) | [z_score_standardization_method_introduction.md](methods/z_score_standardization_method_introduction.md) |

## 二、检验方法与区间估计

| 概念 | 主要回答的问题 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- |
| Wilcoxon 符号秩检验 | 在配对数据里，差值是否系统性偏向某一方 | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [wilcoxon_signed_rank_test_method_introduction.md](methods/wilcoxon_signed_rank_test_method_introduction.md) |
| 卡方检验 | 两个分类变量是否有关联，例如“是否有格式”与“是否获胜”是否独立 | [C17](../Codes/C17_format_test.py) | [chi_square_test_method_introduction.md](methods/chi_square_test_method_introduction.md) |
| Bonferroni 校正 | 同时做很多次检验时，如何控制误报概率 | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [bonferroni_correction_method_introduction.md](methods/bonferroni_correction_method_introduction.md) |
| Bootstrap 置信区间 | 不想过度依赖正态分布假设时，如何给效应或中介路径提供区间估计 | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C22](../Codes/C22_sem_analysis.py) | [bootstrap_confidence_interval_method_introduction.md](methods/bootstrap_confidence_interval_method_introduction.md) |

## 三、效应量

| 概念 | 主要回答的问题 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- |
| Rank-biserial 相关 | Wilcoxon 检验发现差异后，差异到底有多大 | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [rank_biserial_correlation_method_introduction.md](methods/rank_biserial_correlation_method_introduction.md) |
| Cohen's d 与 Hedges' g | 两组均值差异折算成“标准差单位”后有多大 | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [cohens_d_and_hedges_g_method_introduction.md](methods/cohens_d_and_hedges_g_method_introduction.md) |
| Odds Ratio 与 95% CI | 处理变量每增加一个单位，获胜赔率大约变成原来的几倍 | [C18](../Codes/C18_pure_effect.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [odds_ratio_and_confidence_interval_method_introduction.md](methods/odds_ratio_and_confidence_interval_method_introduction.md) |
| 平均边际效应 AME | 一个变量变化后，获胜概率平均会增加或减少多少 | [C18](../Codes/C18_pure_effect.py) | [average_marginal_effect_method_introduction.md](methods/average_marginal_effect_method_introduction.md) |
| Wald 部分相关 r | 在回归框架中，单个系数的局部效应强度有多大 | [C18](../Codes/C18_pure_effect.py) | [wald_partial_r_method_introduction.md](methods/wald_partial_r_method_introduction.md) |

## 四、回归、混淆控制与因果稳健性

| 概念 | 主要回答的问题 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- |
| 逻辑回归 | 当结果是二值变量时，如何同时控制多个解释变量 | [C18](../Codes/C18_pure_effect.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [logistic_regression_method_introduction.md](methods/logistic_regression_method_introduction.md) |
| 混淆比例 | 加入控制变量后，粗效应有多少被解释掉了 | [C18](../Codes/C18_pure_effect.py) | [confounding_proportion_method_introduction.md](methods/confounding_proportion_method_introduction.md) |
| 倾向得分 | 在观察性数据里，样本接受“处理”的倾向有多大 | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [propensity_score_method_introduction.md](methods/propensity_score_method_introduction.md) |
| 逆概率加权 IPW | 用权重把处理组和对照组重新拉回到可比状态 | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [inverse_probability_weighting_method_introduction.md](methods/inverse_probability_weighting_method_introduction.md) |
| ATE 与 ESS | 平均处理效应是多少，加权后还有多少“有效样本量” | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [average_treatment_effect_and_ess_method_introduction.md](methods/average_treatment_effect_and_ess_method_introduction.md) |
| 标准化均值差 SMD | 处理组和对照组在协变量上是否真的平衡 | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [standardized_mean_difference_method_introduction.md](methods/standardized_mean_difference_method_introduction.md) |
| 倾向得分匹配 PSM | 能否直接找出“很像”的处理组和对照组做匹配比较 | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [propensity_score_matching_method_introduction.md](methods/propensity_score_matching_method_introduction.md) |

## 五、机制分析与结构方程模型

| 概念 | 主要回答的问题 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- |
| 结构方程模型 SEM | 长度、格式、中介路径和偏好结果能否放进同一个整体框架 | [C22](../Codes/C22_sem_analysis.py) | [sem_method_introduction.md](methods/sem_method_introduction.md) |
| 直接效应、间接效应、总效应 | 一个变量对结果的影响，有多少是直接的，有多少是通过中介传递的 | [C22](../Codes/C22_sem_analysis.py) | [direct_indirect_total_effects_method_introduction.md](methods/direct_indirect_total_effects_method_introduction.md) |
| SEM 拟合指标 | SEM 模型整体拟合得好不好，主模型和扩展模型谁更稳 | [C22](../Codes/C22_sem_analysis.py) | [sem_fit_indices_method_introduction.md](methods/sem_fit_indices_method_introduction.md) |

## 建议阅读顺序

如果是零基础读者，建议按下面顺序进入：

1. 先看描述统计、格式密度、z-score 标准化。
2. 再看 Wilcoxon、卡方、Bonferroni、Bootstrap、几种效应量。
3. 然后进入逻辑回归、OR、AME、混淆比例。
4. 再学习倾向得分、IPW、ATE、SMD、PSM。
5. 最后阅读 SEM、效应分解和拟合指标。

这样读的好处是：先理解“如何看数据”，再理解“如何检验差异”，最后理解“如何控制混淆并解释机制”。