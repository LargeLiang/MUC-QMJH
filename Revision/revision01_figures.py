"""Grayscale manuscript figures sourced only from revision result tables."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'基于大语言模型输出文本的选择偏好研究/draft_v3/assets'
DATA=ROOT/'Revision/revision01_v3'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei'], 'axes.unicode_minus':False,
                         'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':230})
    table=pd.read_csv(DATA/'associations.csv')
    features=['log_token_ratio','header_density_diff','bold_density_diff','list_density_diff']
    labels=['长度对数比','标题密度差','粗体密度差','列表密度差']
    fig,axes=plt.subplots(1,2,figsize=(9,3.5),gridspec_kw={'width_ratios':[1,1.8]})
    for ax,fs,ls in [(axes[0],features[:1],labels[:1]),(axes[1],features[1:],labels[1:])]:
        for j,(label,title,marker,col) in enumerate([('full','全量','o','0.05'),('english','英语','s','0.4'),('single_turn','单轮','^','0.65')]):
            t=table[(table.model==label)&(table.scheme=='prompt_first')].set_index('feature').loc[fs]
            ax.errorbar(t.odds_ratio,np.arange(len(fs))+(j-1)*.2,
                        xerr=np.array([t.odds_ratio-t.ci_low,t.ci_high-t.odds_ratio]),fmt=marker,color=col,label=title,capsize=3,ms=4)
        ax.set_yticks(range(len(fs)),ls);ax.invert_yaxis();ax.axvline(1,color='0.6',ls='--',lw=.8)
        ax.set_xlabel('统一尺度 OR 及95%区间');ax.grid(axis='x',alpha=.15)
    axes[1].legend(frameon=False,ncol=3,loc='lower right')
    fig.tight_layout();save(fig,'adjusted_associations')
    pred=pd.read_csv(DATA/'predictions.csv')
    fig,ax=plt.subplots(figsize=(7.6,3.4))
    for model,label,ls,col in [('linear','线性 logit','--','0.5'),('spline','限制性三次样条','-','0.05')]:
        t=pred[pred.model==model]
        ax.plot(t.ratio,t.prediction,ls=ls,color=col,label=label)
        ax.fill_between(t.ratio,t.ci_low,t.ci_high,color=col,alpha=.12)
    ax.set_xscale('log');ax.set_xticks([.25,.5,1,2,4],['0.25','0.5','1','2','4'])
    ax.set_xlabel('有方向长度比 r = A侧长度 / B侧长度');ax.set_ylabel('平均预测 A 侧获胜概率')
    ax.legend(frameon=False);ax.grid(alpha=.15);fig.tight_layout();save(fig,'length_curve')
    audit=pd.read_csv(ROOT/'基于大语言模型输出文本的选择偏好研究/draft_v2/assets/audit_strata.csv')
    fig,ax=plt.subplots(figsize=(7.6,3.2));y=audit.longer_win_fraction
    ax.errorbar(range(3),y,yerr=np.array([y-audit.ci_low,audit.ci_high-y]),fmt='o',color='0.1',capsize=5)
    ax.set_xticks(range(3),['R ≤ 1.25','1.25 < R ≤ 2','R > 2']);ax.set_xlim(-.4,2.4)
    ax.set_ylabel('较长回答获胜比例');ax.set_ylim(.48,.73);ax.axhline(.5,color='0.5',ls='--')
    for i,v in enumerate(y): ax.annotate(f'{v:.2%}',(i,v),xytext=(0,12),textcoords='offset points',ha='center')
    ax.grid(axis='y',alpha=.15);fig.tight_layout();save(fig,'audit_strata')


def save(fig,name):
    for ext in ['png','pdf']:fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__': main()
