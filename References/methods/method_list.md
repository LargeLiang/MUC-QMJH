# 项目统计学方法清单

这份清单只整理 Codes 目录中真正参与结果解释的统计学概念。它不替代脚本，而是把“代码里用了什么方法、这些方法第一次在哪个脚本真正进入分析链、应该读哪份入门说明”一次性列清楚。

如果你希望先看“所有方法是怎样被串成一条研究链的”，建议先读 [统计方法逻辑链条图](../Introductions/statistical_logic_chain.md)。

如果你希望进一步看“这些方法在论文写作中应该落到哪一章，以及它们在研究推进中如何前后承接”，建议再读 [论文写作版方法逻辑图与研究时间轴图](../paper_method_maps.md)。

## 整理原则

- 只收录已经出现在项目脚本中的概念，不额外扩展教材外的新方法。
- 编号顺序按 C14 到 C22 中“第一次进入结果解释”的先后排列，而不是按教材学科分类排列。
- 同一方法如果在多个脚本中反复使用，只在首次进入分析链的位置定编号，后面脚本继续复用同一编号。
- 对紧贴母方法、单独拆开反而会割裂理解的子概念，放入对应母文档统一讲解，例如 caliper、公共支持区间、pseudo R²、AIC/BIC。

## 方法总表（按分析链首次出现顺序）

| 编号 | 概念 | 主要回答的问题 | 首次出现 | 主要脚本 | 入门文档 |
| --- | --- | --- | --- | --- | --- |
| M01 | 描述统计 | 数据大致长什么样，均值、标准差、胜率、样本占比是多少 | [C14](../Codes/C14_visualize_length_preference.py) | [C14](../Codes/C14_visualize_length_preference.py), [C15](../Codes/C15_visualize_format_preference.py), [C22](../Codes/C22_sem_analysis.py) | [M01_描述统计.md](methods/M01_描述统计.md) |
| M02 | 相关分析与趋势线 | 长度差变化时，胜率是否同步变化，变化形状是否近似线性或弯曲 | [C14](../Codes/C14_visualize_length_preference.py) | [C14](../Codes/C14_visualize_length_preference.py) | [M02_相关分析与趋势线.md](methods/M02_相关分析与趋势线.md) |
| M03 | 文本格式密度 | 在不同长度文本之间，如何公平比较标题、列表、粗体的使用强度 | [C15](../Codes/C15_visualize_format_preference.py) | [C15](../Codes/C15_visualize_format_preference.py), [C18](../Codes/C18_pure_effect.py), [C22](../Codes/C22_sem_analysis.py) | [M03_文本格式密度.md](methods/M03_文本格式密度.md) |
| M04 | Wilcoxon 符号秩检验 | 在配对数据里，差值是否系统性偏向某一方 | [C16](../Codes/C16_length_test.py) | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [M04_Wilcoxon符号秩检验.md](methods/M04_Wilcoxon符号秩检验.md) |
| M05 | Bonferroni 校正 | 同时做很多次检验时，如何控制误报概率 | [C16](../Codes/C16_length_test.py) | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [M05_Bonferroni校正.md](methods/M05_Bonferroni校正.md) |
| M06 | Bootstrap 置信区间 | 不想过度依赖正态分布假设时，如何给效应或中介路径提供区间估计 | [C16](../Codes/C16_length_test.py) | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C22](../Codes/C22_sem_analysis.py) | [M06_Bootstrap置信区间.md](methods/M06_Bootstrap置信区间.md) |
| M07 | Rank-biserial 相关 | Wilcoxon 检验发现差异后，差异方向性到底有多强 | [C16](../Codes/C16_length_test.py) | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [M07_Rank-biserial相关.md](methods/M07_Rank-biserial相关.md) |
| M08 | Cohen's d 与 Hedges' g | 两组均值差异折算成“标准差单位”后有多大 | [C16](../Codes/C16_length_test.py) | [C16](../Codes/C16_length_test.py), [C17](../Codes/C17_format_test.py) | [M08_Cohens_d与Hedges_g.md](methods/M08_Cohens_d与Hedges_g.md) |
| M09 | 卡方检验 | 两个分类变量是否有关联，例如“是否有格式”与“是否获胜”是否独立 | [C17](../Codes/C17_format_test.py) | [C17](../Codes/C17_format_test.py) | [M09_卡方检验.md](methods/M09_卡方检验.md) |
| M10 | z-score 标准化 | 不同量纲的变量如何放到同一个模型里比较 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py), [C22](../Codes/C22_sem_analysis.py) | [M10_z-score标准化.md](methods/M10_z-score标准化.md) |
| M11 | 逻辑回归 | 当结果是二值变量时，如何同时控制多个解释变量 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [M11_逻辑回归.md](methods/M11_逻辑回归.md) |
| M12 | Odds Ratio 与 95% CI | 处理变量每增加一个单位，获胜赔率大约变成原来的几倍 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py), [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [M12_Odds_Ratio与95CI.md](methods/M12_Odds_Ratio与95CI.md) |
| M13 | 平均边际效应 AME | 一个变量变化后，获胜概率平均会增加或减少多少 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py) | [M13_平均边际效应AME.md](methods/M13_平均边际效应AME.md) |
| M14 | Wald 部分相关 r | 在回归框架中，单个系数的局部效应强度有多大 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py) | [M14_Wald部分相关r.md](methods/M14_Wald部分相关r.md) |
| M15 | 混淆比例 | 加入控制变量后，粗效应有多少被解释掉了 | [C18](../Codes/C18_pure_effect.py) | [C18](../Codes/C18_pure_effect.py) | [M15_混淆比例.md](methods/M15_混淆比例.md) |
| M16 | 倾向得分 | 在观察性数据里，样本接受“处理”的倾向有多大 | [C19](../Codes/C19_length_effect_robust.py) | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [M16_倾向得分.md](methods/M16_倾向得分.md) |
| M17 | 逆概率加权 IPW | 用权重把处理组和对照组重新拉回到可比状态 | [C19](../Codes/C19_length_effect_robust.py) | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py) | [M17_逆概率加权IPW.md](methods/M17_逆概率加权IPW.md) |
| M18 | ATE 与 ESS | 平均处理效应是多少，加权后还有多少“有效样本量” | [C19](../Codes/C19_length_effect_robust.py) | [C19](../Codes/C19_length_effect_robust.py), [C20](../Codes/C20_format_effect_robust.py), [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [M18_ATE与ESS.md](methods/M18_ATE与ESS.md) |
| M19 | 倾向得分匹配 PSM | 能否直接找出“很像”的处理组和对照组做匹配比较 | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [M19_倾向得分匹配PSM.md](methods/M19_倾向得分匹配PSM.md) |
| M20 | 标准化均值差 SMD | 处理组和对照组在协变量上是否真的平衡 | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [C21](../Codes/C21_enhanced_matching_diagnostics.py) | [M20_标准化均值差SMD.md](methods/M20_标准化均值差SMD.md) |
| M21 | 结构方程模型 SEM | 长度、格式、中介路径和偏好结果能否放进同一个整体框架 | [C22](../Codes/C22_sem_analysis.py) | [C22](../Codes/C22_sem_analysis.py) | [M21_结构方程模型SEM.md](methods/M21_结构方程模型SEM.md) |
| M22 | 直接效应、间接效应、总效应 | 一个变量对结果的影响，有多少是直接的，有多少是通过中介传递的 | [C22](../Codes/C22_sem_analysis.py) | [C22](../Codes/C22_sem_analysis.py) | [M22_直接效应_间接效应_总效应.md](methods/M22_直接效应_间接效应_总效应.md) |
| M23 | SEM 拟合指标 | SEM 模型整体拟合得好不好，主模型和扩展模型谁更稳 | [C22](../Codes/C22_sem_analysis.py) | [C22](../Codes/C22_sem_analysis.py) | [M23_SEM拟合指标.md](methods/M23_SEM拟合指标.md) |

## 建议阅读顺序

如果是零基础读者，建议直接按 M01 到 M23 顺序往后读。最自然的进入方式是：

1. 先读 M01-M03，理解描述统计、趋势线和格式密度这些“现象层”工具。
2. 再读 M04-M09，掌握第三阶段正式检验使用的差异检验、校正和效应量。
3. 然后读 M10-M15，进入 C18 的净效应建模与回归解释层。
4. 再读 M16-M20，理解 C19-C21 的倾向得分、IPW、ATE、PSM 与平衡性诊断。
5. 最后读 M21-M23，进入 C22 的机制建模与效应分解。

这样读的好处是：顺着脚本执行顺序走，方法和结果会更容易对上号。