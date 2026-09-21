"""Assemble v3 from verified tables; keep v2 intact."""
from pathlib import Path
import re, json
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'基于大语言模型输出文本的选择偏好研究'
HERE=PAPER/'draft_v3'
DATA=ROOT/'Revision/revision01_v3'
T=pd.read_csv(DATA/'associations.csv')
S=pd.read_csv(DATA/'sem_products.csv')
F=['log_token_ratio','header_density_diff','bold_density_diff','list_density_diff']
N=dict(zip(F,['长度对数比','标题密度差','粗体密度差','列表密度差']))


def pval(v):return '$<0.001$' if v<.001 else f'{v:.4f}'
def get(model,f,scheme='prompt_first'):return T[(T.model==model)&(T.feature==f)&(T.scheme==scheme)].iloc[0]
def ci(row):return f'[{row.ci_low:.4f}, {row.ci_high:.4f}]'
def table(caption,label,header,rows,spec,note=''):
    return '\n'+rf'\begin{{table}}[htbp]\centering\small\caption{{{caption}}}\label{{{label}}}'+'\n'+rf'\begin{{tabular}}{{{spec}}}\toprule'+'\n'+header+r'\\\midrule'+'\n'+'\n'.join(rows)+r'\bottomrule\end{tabular}'+'\n'+rf'\par\smallskip\footnotesize {note}'+'\n'+r'\end{table}'+'\n'


def main():
    assert json.loads((DATA/'manifest.json').read_text())['status']=='complete'
    HERE.mkdir(exist_ok=True)
    old=(PAPER/'draft_v2/manuscript.tex').read_text(encoding='utf-8')
    prefix=old.split('\\section{配对统计模型与审计方法}')[0]
    prefix=prefix.replace('修订稿 v2','修订稿 v3').replace('基于配对 Logistic 模型的审计应用','基于成对比较模型与探索性路径的审计应用')
    abstract='基于LMArena的108,154条评价记录，构建成对比较模型并保留SEM探索性路径分析。明确胜负样本中，长度与粗体密度呈正关联，标题对子集敏感，列表密度证据不足。聚类推断与月份控制下主要方向保持，但长度存在明显非线性，粗体存在性未获同样支持。进一步描述明确选择状态，提出含方差估计及预算分配的分层审计方案。结果限于观察性关联，格式重解析不替代人工验证。'
    prefix=re.sub(r'\\noindent\\textbf\{摘要：\}.*?(?=\n\n)',lambda _:r'\noindent\textbf{摘要：}'+abstract,prefix,count=1,flags=re.S)
    english='Using 108,154 LMArena evaluation records, this study combines a paired-comparison logistic model with exploratory observed-variable path analysis. Among decisive pairs, response length and bold density show positive conditional associations with choice. Heading associations are subset-sensitive, while list-density evidence is inconclusive. Prompt-cluster inference, model-pair clustering, month adjustment, and alternative Markdown parsing support the main density-based directions. However, restricted cubic splines reveal substantial length nonlinearity, and bold presence does not show the same association as bold density. A separate symmetric model describes whether an evaluation is decisive. The audit application retains unresolved evaluations and specifies stratified estimation, finite-population variance, and budget allocation. Path products describe candidate associations rather than causal mediation. Automated parsing agreement does not establish measurement validity; a blinded sample of 400 responses has been prepared for independent human review. The proposed audit allocation has not been validated through content review or training experiments.'
    prefix=re.sub(r'\\noindent\\textbf\{Abstract:\}.*?(?=\n\n)',lambda _:r'\noindent\textbf{Abstract:} '+english,prefix,count=1,flags=re.S)
    prefix=re.sub(r'\\noindent\\textbf\{关键词：\}[^\n]*',lambda _:r'\noindent\textbf{关键词：}大语言模型；人类偏好；成对比较；探索性路径分析；数据审计',prefix)
    prefix=re.sub(r'\\noindent\\textbf\{Key words:\}[^\n]*',lambda _:r'\noindent\textbf{Key words:} large language models; human preference; paired comparison; exploratory path analysis; data audit',prefix)
    prefix=prefix.replace('An Audit Application Using a Paired Logistic Model','An Audit Application Using Paired Comparisons and Exploratory Paths')
    prefix=prefix.replace('后两类保留用于描述和审计分层，不并入二元胜负模型', '后两类保留用于描述、明确选择状态建模和审计分层，不并入条件胜负模型')
    prefix=prefix.replace('本文未重新实现 Markdown 解析器，故这些指标表示上游识别规则下的形式数量，不等于经人工验证的结构质量或视觉效果。', '主分析使用上游计数；补充分析使用Mistune AST重新解析全部助手消息，按标题块、列表条目和strong片段分别计数，排除代码和原始HTML节点，并逐消息累加。重解析只构成替代测量，不是人工金标准；两种口径均不等于结构质量或视觉效果。')
    prefix=prefix.replace('主模型将四个形式指标在相应分析子集中分别标准化，即 $z_{ki}=(x_{ki}-\\bar x_k)/s_k$，其中 $s_k$ 采用分母为该子集样本数的标准差。','主模型将四个形式指标统一按全量明确胜负样本标准化，即 $z_{ki}=(x_{ki}-\\bar x_k)/s_k$，其中 $s_k$ 采用分母为78,959的标准差；英语、单轮和密度敏感性模型均沿用该尺度。')
    prefix=prefix.replace('子集间指标标准差不同，不能直接将 OR 差异解释为同一原始单位的关联变化。','本次统一标准化单位，但重叠子集的点估计差异仍不构成独立复制或正式异质性检验。')
    prefix+='\n按唯一记录id从原始分片连接时间及用户文本，全部108,154条记录匹配且时间无缺失，覆盖2025年4月17日至7月24日的4个自然月。原始schema没有稳定用户标识，不能把唯一会话视为唯一用户。\n\n'
    methods=(ROOT/'Revision/revision01_methods.tex').read_text(encoding='utf-8')
    results=r'''\section{实证结果与敏感性分析}
\subsection{描述结果及主模型}
明确胜负样本中有187对等长，78,772对不等长；较长回答获胜49,130对，占62.37\%。胜者减败者的中位长度差为125 tokens。标题、粗体、列表密度较高者的未调整获胜比例分别为55.30\%、55.80\%、50.33\%，各自非零差分母为49,087、70,187和69,296。这些描述比例不衡量独立格式作用。

全量比较图包含52个模型，形成一个连通分量；主设计矩阵秩为90，英语和单轮分别为69和89。拟合收敛，未出现分离警告，更换参考模型后焦点系数和预测概率保持数值一致；尚未完成线性规划式分离检验。首提示词有75,862簇，其中73,826为单例，最大簇10条；完整序列有76,213簇；无序模型对有1,201簇，最大簇267条。提示词重复较少解释了其标准误与HC0接近，但不能据此排除同用户跨提示词的依赖。

表\ref{tab:reg}采用首提示词聚类推断。全量长度OR为1.6196；其单位为长度对数比增加全量标准差1.0224，相当于原长度比乘以约2.780，不是增加一个token。该OR是线性设定的平均斜率摘要，后文的非线性检验表明不能将其视为所有长度区间共同适用的恒定关联。
'''
    rows=[]
    for subset,name in [('full','全量'),('english','英语'),('single_turn','单轮')]:
        for f in F:
            t=get(subset,f);rows.append(f'{name} & {N[f]} & {t.odds_ratio:.4f} & {ci(t)} & {pval(t.p_holm)}'+r'\\')
    results+=table('统一标准化下的条件选择关联','tab:reg','样本 & 特征 & OR & 95\%区间 & Holm $p$',rows,'llrrr','注：全量78,959对，英语42,001对，单轮67,608对；首提示词聚类。12项为一个校正家族。')
    results+=r'''
全量标题关联较弱，英语子集区间跨1，单轮标题虽逐项区间略高于1，Holm校正后仍不显著；粗体密度在三个样本中保持正关联，列表密度均缺乏明确支持。模型身份项只能吸收平均模型差异，不能测量具体回答的正确性或必要信息量。
\begin{figure}[htbp]\centering\includegraphics[width=\textwidth]{adjusted_associations.pdf}
\caption{三个重叠样本的条件关联。统一标准化尺度，首提示词聚类逐项区间；左右面板横轴范围不同。}\label{fig:reg}\end{figure}

\subsection{聚类 时间及函数形式}
将首提示词聚类改为完整序列或模型对聚类后，全量标题仍通过各自方案的Holm校正；模型对方案的标题校正$p=0.0275$，粗体为$p<0.001$。因此本次结果不支持“聚类必然使标题消失”的预设判断，但标题的子集敏感性仍然存在。
月份调整后的长度OR为1.6195，粗体密度为1.0556；去除长度比两端各1\%后长度OR升至1.7630，说明总体线性斜率对尾部范围敏感。限制性三次样条的非线性联合检验在首提示词聚类下$p<0.001$，模型对聚类下亦$p<0.001$。原始对数比节点约为$-1.6409,-0.3448,0.3442,1.6551$，对应长度比约为0.194、0.708、1.411、5.234。
\begin{figure}[htbp]\centering\includegraphics[width=.94\textwidth]{length_curve.pdf}
\caption{长度与选择的标准化预测关联。阴影为首提示词聚类Delta法95\%逐点区间，固定观察到的格式密度与其他协变量，横轴为A/B有方向长度比。}\label{fig:curve}\end{figure}

图\ref{fig:curve}显示线性与样条在不同长度范围的拟合差异。曲线展示0.25至4的长度比，该区间位于观察长度比的1\%至99\%分位范围内；但边际范围内不保证全部协变量组合都有共同支持。非线性显著不自动确定最优复核阈值，也不证明某一长度比例是因果拐点。
'''
    sf=T[(T.model=='spline_format')&(T.scheme=='prompt_first')].set_index('feature')
    results+=f"\n样条结果方程下，标题、粗体及列表密度OR分别为{sf.loc[F[1],'odds_ratio']:.4f}、{sf.loc[F[2],'odds_ratio']:.4f}、{sf.loc[F[3],'odds_ratio']:.4f}，三个格式项的Holm校正值依次为{pval(sf.loc[F[1],'p_holm'])}、{pval(sf.loc[F[2],'p_holm'])}、{pval(sf.loc[F[3],'p_holm'])}。完整敏感性表同时保留原线性基准，避免只报告符合预期的设定。\n"
    results+=r'''
\subsection{明确选择状态与格式测量}
平局和双方差合计29,195条，占保留样本约26.99\%。表\ref{tab:decisive}考察是否产生明确胜负，单位为全部保留样本中绝对差指标的一个标准差。它与表\ref{tab:reg}使用不同结果变量和尺度，不能横向比较OR大小或把状态模型称为选择偏差校正。
'''
    rows=[]
    for f in F:
        t=get('decisive_stage',f);rows.append(f'{N[f]}绝对值 & {t.odds_ratio:.4f} & {ci(t)} & {pval(t.p_holm)}'+r'\\')
    results+=table('形成明确胜负的关联','tab:decisive','特征 & OR & 95\%区间 & Holm $p$',rows,'lrrr','注：108,154条，控制月份及对称模型身份项，首提示词聚类；4项校正。')
    results+=r'''
长度差异、标题及列表密度差异与形成明确选择正相关，粗体密度绝对差缺乏同样证据。这表明“是否明确选择”与“明确选择后哪侧获胜”应分开讨论。

对216,308个侧别回答，AST重解析与上游计数的完全一致率，标题为98.96\%、列表97.89\%、粗体96.88\%；存在性一致率分别为99.55\%、99.68\%、99.85\%。这些是口径一致性，不是相对于人工真值的准确率。替代计数模型中，长度OR为1.6187、粗体密度OR为1.0569，主要方向与原计数接近。
'''
    pr=get('format_presence','bold_density_diff')
    results+=f"\n然而，改用格式存在性后，粗体差值OR为{pr.odds_ratio:.4f}，95\\%区间{ci(pr)}，校正$p={pr.p_holm:.4f}$，未获得明确关联证据。因而结论应限定为粗体密度，不能泛化成“使用粗体即可提高被选择概率”。存在性与密度的单位和研究问题不同。\n"
    results+=r'''
已按上游三种格式存在性组合分8层，每层随机抽取50个回答，共400个，隐藏模型、胜负与自动计数，准备独立双人复核和裁决。因尚未取得人工标注，本稿不报告人工precision、recall或内容质量改善。稀有语法边界另由可复现代码样例检查，不冒充概率样本的人工验证。

\FloatBarrier
\section{探索性路径分析}
\subsection{观测变量广义路径框架}
保留SEM框架下的探索性尝试，以长度指向标题、列表、粗体密度，再由格式指向选择，同时保留长度至选择的路径。这里没有潜变量或测量模型；三个连续格式方程采用OLS，二元选择方程采用Logistic，并允许格式残差相关。对$k\in\{H,S,B\}$，有
\begin{equation}
 z_{ki}=\alpha_k+a_kz_{Li}+\bm\gamma_k^\top\bm X_i
 +\theta_{k,m_{Ai}}-\theta_{k,m_{Bi}}+\varepsilon_{ki}.
\end{equation}
选择方程使用式\eqref{eq:logit}，格式系数记为$b_k$。方向为事后探索设定，无时间先后或干预识别；不使用由同一样本胜率构造的能力代理，也不因列表不显著而删除其路径。

对七个焦点系数，先计算同一配对对各方程估计的影响贡献，再按首提示词求和形成跨方程聚类夹心协方差；完整序列和模型对方案作敏感性分析。方程间使用各自参数数目进行有限样本修正，保留$a$与$b$的估计相关。三个子集共21条路径在每种协方差方案内实施Holm校正。

从联合渐近正态分布模拟50,000次参数，种子20260921，取$a_kb_k$的2.5\%及97.5\%分位数。该区间条件于观察到的标准化尺度，为逐项参数模拟区间，不是Bootstrap，也未经多重校正。$a_kb_k$只用于描述线性工作模型中的候选关联通路，不是概率变化、自然间接效应或中介比例；不将其与长度系数相加解释为约简Logistic模型的总效应。
\subsection{路径结果与模型依赖}
'''
    rows=[]
    for label,title in [('full','全量'),('english','英语'),('single_turn','单轮')]:
        for f in F[1:]:
            t=S[(S.model==label)&(S.scheme=='prompt_first')&(S.via==f)].iloc[0]
            rows.append(f'{title} & 长度$\\to${N[f][:2]}$\\to$选择 & {t.estimate:.5f} & [{t.ci_low:.5f}, {t.ci_high:.5f}]'+r'\\')
    results+=table('探索性路径乘积','tab:paths','样本 & 候选通路 & 乘积 & 95\%模拟区间',rows,'llrr','注：统一全量尺度，首提示词聚类协方差；子集重叠，区间逐项。箭头不证明因果方向。')
    results+=r'''
经粗体密度的乘积在三个样本中均为正，模型对聚类及AST替代计数下亦保持该方向；标题通路在英语子集中区间跨零，列表通路均跨零。单轮标题乘积逐项区间虽排除零，不能据此绕过其选择路径的多重校正判断。

上述分解依赖线性格式方程及线性logit长度项，而主结果已检出明显非线性，因此本节是线性工作模型的探索性补充。样条方程中不存在适用于全部长度范围的单一$a_kb_k$，本稿不将原乘积包装成已通过非线性验证的机制。替代方向、格式间反馈、共享长度分母及未观测内容质量仍可产生相似关联。分方程估计没有整体协方差结构拟合检验，故不报告CFI、TLI或RMSEA。

\FloatBarrier
\section{偏好数据审计应用}
\subsection{包含未决评价的分层报告}
按式\eqref{eq:ratio}划分三层，保留明确胜负、平局和双方差。表\ref{tab:audit}展示真实样本；较长者获胜的分母仅为本层不等长且明确胜负配对，分别为15,777、27,017、35,978。
'''
    rows=[r'$R\leq1.25$ & 23,536 & 15,964 & 32.17 & 52.46\\',r'$1.25<R\leq2$ & 37,992 & 27,017 & 28.89 & 59.26\\',r'$R>2$ & 46,626 & 35,978 & 22.84 & 69.06\\']
    results+=table('真实长度分层及评价构成','tab:audit','长度层 & 全部记录 & 明确胜负 & 未决比例(\%) & 较长者胜(\%)',rows,'lrrrr','注：未决包括平局与双方差，分母为本层全部记录。')
    results+=r'''
长度接近层未决比例为32.17\%，长度比超过2的层为22.84\%。若只复核明确胜负，将忽略与长度结构有关的未决记录。但分层比例上升可能反映内容充分性、任务或模型构成，不能把较大长度差直接判为错误标签。
\begin{figure}[htbp]\centering\includegraphics[width=.9\textwidth]{audit_strata.pdf}
\caption{各长度层中较长回答获胜比例。精确二项区间仅为配对独立假设下的描述区间，未作聚类修正。}\label{fig:audit}\end{figure}

\subsection{总体争议率估计及预算分配}
若目标是估计人工复核中的总体争议率，设层大小为$N_h$，$W_h=N_h/N$，层内简单随机不放回抽样量为$b_h$，争议指示为$a_{hj}$，则
\begin{equation}
 \widehat A=\sum_h W_h\widehat p_h,\qquad
 \widehat p_h=b_h^{-1}\sum_{j=1}^{b_h}a_{hj}.
\end{equation}
在各层独立抽样条件下，其设计方差为\cite{rice}
\begin{equation}
 \operatorname{Var}(\widehat A)=\sum_hW_h^2
 \left(1-\frac{b_h}{N_h}\right)\frac{S_h^2}{b_h},
 \qquad S_h^2=\frac{1}{N_h-1}\sum_{j=1}^{N_h}(a_{hj}-p_h)^2.
\end{equation}
实际估计以样本方差$s_h^2$代入，故每个用于估计方差的层需至少2条；小层或全同值样本的区间应谨慎处理。$S_h$必须对应人工争议指标，不能用长度、胜率或未决率的变异冒充。

等成本、固定总样本量$\sum_hb_h=B$且忽略整数和容量限制时，最小化方差得到Neyman分配
\begin{equation}
 b_h=B\frac{N_hS_h}{\sum_kN_kS_k}.
\end{equation}
不同单位成本$c_h$且约束为$\sum_hc_hb_h=C$时，连续解满足$b_h\propto N_hS_h/\sqrt{c_h}$。实际执行需设置最低样本量、不超过层容量并按明确规则取整；若要求层间比较，不能只按总体估计精度配置预算。

以300条内容复核预算为例，三层等额分配为100、100、100；按真实层大小比例分配并采用最大余数法取整为65、106、129。在未知争议率时，采用各层相同的保守方差假设，Neyman分配近似退化为比例分配；这只是设计情景。获得独立先导复核后，才能用各层争议方差计算针对该目标的Neyman配置。为避免自适应抽样解释复杂化，可将先导样本与正式估计样本分开，正式样本在方案冻结后抽取。

若进一步按评价状态交叉分层，$h$应指长度层与状态的交叉层；不等概率抽样需记录纳入概率并据此估计总体。格式测量盲审的400个侧别回答与这里300条配对内容复核是不同任务和单位，不能相互替代。

\subsection{实际应用范围}
复核时应隐藏原始胜负，评价正确性、相关性、覆盖及组织方式，记录独立判断与依据；合理偏好分歧不自动等于错误标签。长度、粗体密度可作为候选监测特征，标题需结合场景，列表密度不宜单独作为剔除依据。不能为了使较长者胜率接近50\%而删样，也不能从当前OR直接生成去偏权重。

本文已完成真实分层、条件及状态模型、格式替代测量与抽样设计，尚未实施独立内容复核、抽样效率比较、奖励模型训练或榜单校准。应用贡献是可复现的审计步骤和统计设计，不是已验证的争议发现率或去偏收益。

\section{结论与局限}
成对比较模型显示长度与粗体密度同人类选择存在正关联，标题较弱且对子集敏感，列表密度证据不足。聚类、月份及替代解析检查保留主要密度结论，但长度存在明显非线性，截尾改变线性斜率，粗体存在性也未表现出同样支持。因此应报告模型和测量依赖，而不能把某一种格式概括为普遍有效的编辑策略。

SEM观测变量路径分析作为探索保留：线性工作设定下，经粗体密度的关联乘积方向较一致，标题及列表的证据受限。该分解不识别因果机制，也未通过非线性路径模型验证。明确选择状态分析进一步说明未决评价应进入审计抽样框。

分层估计方差和预算分配连接了统计分析与复核操作，但仍需人工格式与内容验证。单平台、未观测质量、未知用户依赖、提示词近似重复、模型随时间变化和密度分母耦合限制了推广；精确提示词及模型对聚类没有覆盖全部依赖来源。后续应优先完成已准备的盲审，并在独立数据上检验审计方案，不以增加统计模型数量代替应用验证。
'''
    bibliography=old[old.index('\\begin{thebibliography}'):]
    bibliography=bibliography.replace('Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference[EB/OL]. (2024-03-07)[2026-09-21]. \\url{https://arxiv.org/abs/2403.04132}.','Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference[C]//Proceedings of the 41st International Conference on Machine Learning. PMLR, 2024, 235: 8359--8388. \\url{https://proceedings.mlr.press/v235/chiang24b.html}.')
    bibliography=re.sub(r'\\bibitem\{dubois\}[^\n]*',lambda _:r'\bibitem{dubois} DUBOIS Y, LIANG P, HASHIMOTO T B. Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators[C]//Conference on Language Modeling. 2024. \url{https://openreview.net/pdf?id=CybBmzWBX0}.',bibliography)
    extra=r'''
\bibitem{firth} FIRTH D. Bradley--Terry Models in R[J]. Journal of Statistical Software, 2005, 12(1): 1--12. \url{https://doi.org/10.18637/jss.v012.i01}.
\bibitem{cameron} CAMERON A C, MILLER D L. A Practitioner's Guide to Cluster-Robust Inference[J]. Journal of Human Resources, 2015, 50(2): 317--372. \url{https://doi.org/10.3368/jhr.50.2.317}.
\bibitem{harrell} HARRELL F E. Regression Modeling Strategies[M]. 2nd ed. Cham: Springer, 2015. \url{https://doi.org/10.1007/978-3-319-19425-7}.
\bibitem{rice} RICE J A. Mathematical Statistics and Data Analysis[M]. 3rd ed. Belmont: Thomson Brooks/Cole, 2007.
'''
    bibliography=bibliography.replace('\\end{thebibliography}',extra+'\\end{thebibliography}')
    complete=prefix+methods+results+'\n\\FloatBarrier\n'+bibliography
    # Number bibliography in first-citation order.
    order=[]
    for match in re.finditer(r'\\cite\{([^}]+)\}',complete.split('\\begin{thebibliography}')[0]):
        for key in match[1].split(','):
            if key not in order:order.append(key)
    items=dict(re.findall(r'\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem|\\end\{thebibliography\})',bibliography,re.S))
    complete=complete[:complete.index('\\begin{thebibliography}')]+r'\begin{thebibliography}{99}\small'+'\n'+'\n'.join(r'\bibitem{'+k+'} '+items[k].strip() for k in order)+'\n\\end{thebibliography}\n\\end{document}\n'
    (HERE/'manuscript.tex').write_text(complete,encoding='utf-8')
    (HERE/'build').mkdir(exist_ok=True)
    print('Chinese abstract characters',len(re.findall(r'[\u4e00-\u9fff]',abstract)))
    print('English abstract words',len(english.split()))


if __name__=='__main__': main()
