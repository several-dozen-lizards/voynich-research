"""Presentation only; consumes frozen saved results and controls."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(R/'runtime-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
d=json.loads((R/'RESULTS.json').read_text());c=json.loads((R/'CONTROLS.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(12,5.5),gridspec_kw={'width_ratios':[1,1.5]})
colors={'H':'#176b87','F':'#ad5c27'}
for j,co in enumerate(('H','F')):
    p=d['results'][co]['primary'];x=1000*p['delta_nats_per_origin'];lo,hi=np.array(p['score_bootstrap']['CI95_nats_per_origin'])*1000
    axes[0].errorbar(x,j,xerr=[[x-lo],[hi-x]],fmt='o',color=colors[co],capsize=4,label=co)
    sensitivity=[1000*r['delta_nats_per_origin'] for r in d['results'][co]['partition_sensitivities']]
    axes[0].scatter(sensitivity,np.repeat(j-.12,4),marker='|',color=colors[co],alpha=.8)
axes[0].set_yticks([0,1],['H','F']);axes[0].invert_yaxis();axes[0].axvline(0,color='#666',ls='--',lw=1)
axes[0].set_title('Manuscript: held-out score difference')
axes[0].set_xlabel('Varying − common LL, nats / 1,000 origins\nNegative favors common')
scenarios=['common_OR1','common_OR2','modest_heterogeneous','strong_heterogeneous']
labels=['Common OR 1','Common OR 2','Modest variation\nOR 1.5 vs 2.5','Strong variation\nOR 1 vs 4']
for j,co in enumerate(('H','F')):
    for i,scenario in enumerate(scenarios):
        values=[r['delta_nats_per_origin']*1000 for r in c['records'] if r['reading']==co and r['scenario']==scenario]
        y=i+(-.13 if j==0 else .13)
        axes[1].scatter(values,np.repeat(y,len(values)),s=14,color=colors[co],alpha=.55,label=co if i==0 else None)
        axes[1].plot([float(np.mean(values))],[y],marker='D',color=colors[co],ms=5)
axes[1].set_yticks(range(4),labels);axes[1].invert_yaxis();axes[1].axvline(0,color='#666',ls='--',lw=1)
axes[1].set_title('Known conditional-effect controls (20 each)');axes[1].legend(frameon=False)
axes[1].set_xlabel('Varying − common LL, nats / 1,000 origins')
for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.15)
fig.suptitle('v4.2-C2 · retrospective predictive comparison',fontsize=14)
fig.text(.02,.025,'Left bars: score-bootstrap intervals conditional on fitted training sets; small ticks: four fixed partition checks.\nRight: all fixed control datasets and their means. Modest heterogeneity was often missed. No equivalence or constant-strength claim.',fontsize=8,color='#444')
fig.tight_layout(rect=(0,.12,1,.93));fig.savefig(R/'predictive-comparison.png',dpi=180);fig.savefig(R/'predictive-comparison.svg');plt.close(fig)
