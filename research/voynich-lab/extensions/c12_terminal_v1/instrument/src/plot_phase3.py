"""Static descriptive figures from the saved matrix; no rankings or inference."""
import csv
import json
import os
import sys
from pathlib import Path

def plot(root):
    os.environ.setdefault('MPLCONFIGDIR',str(root/'.matplotlib-cache'))
    local_runtime=root/'.runtime'
    if local_runtime.exists():sys.path.insert(0,str(local_runtime))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with (root/'report/master_metrics.csv').open(encoding='utf-8',newline='') as f:
        rows={r['corpus']:r for r in csv.DictReader(f) if r['tokenization']=='T1'}
    names=['C'+str(i) for i in range(1,12)]
    fig,axes=plt.subplots(1,3,figsize=(15,5),layout='constrained')
    for ax,key,label in zip(axes,['h2','mi_glyph_line_word_edge','word_length_mean'],
                          ['Character h2 (bits / symbol, incl. spaces)','Glyph / line-word-edge MI (bits)','Mean word length (symbols)']):
        x=list(range(11))
        clean=[float(rows[n+'_clean'][key]) for n in names]
        noisy=[float(rows[n+'_noise'][key]) for n in names]
        for i,a,b in zip(x,clean,noisy):ax.plot([i,i],[a,b],color='#bac3c7',lw=1)
        ax.scatter(x,clean,label='Clean controls',color='#145f79',s=35,zorder=3)
        ax.scatter(x,noisy,label='Noise-injected controls',color='#b35e12',marker='x',s=45,zorder=3)
        ax.axhline(float(rows['ZL_running'][key]),color='#222222',lw=1.5,label='ZL running')
        ax.axhline(float(rows['LSI_H_running'][key]),color='#824f96',ls='--',label='LSI-H running')
        ax.set_xticks(x,names,rotation=45);ax.set_ylabel(label);ax.grid(axis='y',alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle('Phase 3 descriptive comparisons — word-matched controls; no model or generator inference')
    for ext in ['png','svg']:fig.savefig(root/f'report/phase3_comparisons.{ext}',dpi=160)
    plt.close(fig)
    details=json.loads((root/'report/growth_and_lengths.json').read_text())
    fig,axes=plt.subplots(3,4,figsize=(14,10),layout='constrained')
    for ax,name in zip(axes.flat,names):
        for key,label,color,style in [('ZL_running','ZL','#222222','-'),('LSI_H_running','LSI-H','#824f96','--'),
                (name+'_clean',name+' clean','#145f79','-'),(name+'_noise',name+' noise','#b35e12',':')]:
            points=details[key+':T3']['growth']
            ax.plot([p['tokens'] for p in points],[p['types'] for p in points],color=color,ls=style,label=label)
        ax.set_xscale('log');ax.set_yscale('log');ax.set_title(name);ax.set_xlabel('Word tokens');ax.set_ylabel('Word types')
        ax.grid(alpha=.15);ax.legend(fontsize=7)
    axes.flat[-1].axis('off')
    fig.suptitle('Word type/token growth — source-order prefixes, clean/noisy control beside both transcriptions')
    for ext in ['png','svg']:fig.savefig(root/f'report/phase3_growth.{ext}',dpi=160)
    plt.close(fig)

if __name__=='__main__':plot(Path(__file__).resolve().parents[1])
