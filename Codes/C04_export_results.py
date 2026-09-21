"""C04: generate readable tables and figures from the current run only."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def markdown(frame):
    def cell(value):
        if isinstance(value, (float, np.floating)):
            return f'{value:.6g}' if np.isfinite(value) else 'NA'
        return str(value).replace('|', '/')
    lines = ['| ' + ' | '.join(map(str, frame.columns)) + ' |',
             '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |']
    lines += ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in frame.itertuples(index=False, name=None)]
    return '\n'.join(lines)


def export(df, tests, models, out):
    attrition = pd.read_csv(out / 'attrition.csv')
    decisive = int(df.winner.isin(['model_a', 'model_b']).sum())
    report = f'# 配对观察性关联：{out.run_id}\n\n'
    report += f'清洗后 {len(df):,} 个唯一会话的首轮评价；明确胜负 {decisive:,}。会话唯一不保证用户或提示词独立。平局保留在数据及描述表中，不进入二元胜负分析。\n\n'
    report += '## 样本流失（按首次失败原因，互斥计数）\n\n' + markdown(attrition) + '\n\n'
    report += '## 全量配对检验\n\n' + markdown(tests[tests.subset == 'full']) + '\n\n'
    report += '## 调整后的关联\n\n' + markdown(models) + '\n\n'
    report += ('长度采用 log(A tokens/B tokens)，格式采用每千 token 密度差，四者同时入模并在各分析子集中分别标准化。控制任务标签、提示词属性、输入长度、轮数、语言和模型身份对比。OR 为每一标准差变化的条件优势比；平均导数由逐行预测概率计算，不是均值处边际效应，也不是实际增加一个标准差的离散概率变化。不同子集的标准差不同，OR 不可直接解释为同一尺度效应。\n\n'
               '全部检验双侧。配对表全部 sign/McNemar 检验构成一个 Holm 家族，三个回归的全部 12 个焦点系数构成另一个家族。图表中的 95% 区间是逐项区间，不是多重比较同时区间；Wilcoxon 仅补充且未校正，其差值分布对称性未被保证。原始表 p=0 表示浮点下溢而不是概率严格为零，回归另提供 log_p_value。\n\n'
               'HC0 标准误假定观测间独立；同一匿名用户跨会话相关、重复提示词、时间漂移仍未充分处理。没有独立回答质量测量，风格和内容同时产生，模型身份控制不等于题目级质量控制。排除平局及严格文本配对改变目标总体。英语、单轮是重叠敏感性子集，不是独立复制。小任务组合样本不宜作实质推断。\n\n'
               '本轮只重构工程组织和产物追踪，不宣称已修复全部统计局限。旧 IPW、匹配、SEM 保留在 Legacy，不作为当前推断依据。论文旧图表尚未自动替换；关联不可改称偏见、纯效应或因果机制。\n')
    (out / 'REPORT.md').write_text(report, encoding='utf-8')

    fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    ax.barh(attrition.reason_first_failure, attrition.n, color='#3A759C')
    ax.set_xscale('symlog', linthresh=1)
    ax.set_xlabel('Records (symmetric log scale)')
    ax.set_title(f'Sample accounting | {out.run_id}')
    for i, n in enumerate(attrition.n):
        ax.text(n, i, f' {n:,}', va='center', fontsize=8)
    ax.margins(x=.15)
    fig.savefig(out / 'sample_flow.png', dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    features = list(models.feature.unique())
    colors = ['#286DA8', '#C76D2B', '#438858']
    for i, (label, color) in enumerate(zip(['full', 'english', 'single_turn'], colors)):
        part = models[models.subset == label].set_index('feature').loc[features]
        y = np.arange(len(features)) + (i-1)*.18
        ax.errorbar(part.odds_ratio, y,
                    xerr=[part.odds_ratio-part.ci_low, part.ci_high-part.odds_ratio],
                    fmt='o', capsize=3, label=label, color=color, markersize=4)
    ax.set_yticks(np.arange(len(features)), features)
    ax.axvline(1, color='gray', linestyle='--', linewidth=1)
    ax.set_xscale('log')
    ax.set_xlabel('Adjusted OR per within-subset SD; pointwise 95% CI')
    ax.set_title('Observational associations, not causal effects')
    ax.legend()
    fig.savefig(out / 'associations.png', dpi=180)
    plt.close(fig)
