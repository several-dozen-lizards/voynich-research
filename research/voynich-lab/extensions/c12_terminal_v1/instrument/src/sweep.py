"""Registered shorthand grids; identical neural instrument and noise channel."""
from src.train import *
from src.extend_phase3 import typed,read
from src.phase3 import load_words,layout,relabel,rng_for
from src.encoders import encode,expansive
from src.noise import inject
from src.metrics import measure

def settings():
    p5=json.loads((ROOT/'configs/phase5.json').read_text())
    result=[dict(encoder=c,aggressiveness=a) for c in ['C4','C5','C6'] for a in p5['shorthand_aggressiveness']]
    result += [dict(encoder='C12',aggressiveness=.65,sequence_length=l,slot_rigidity=r)
               for l in p5['C12_sequence_lengths'] for r in p5['C12_slot_rigidities']]
    return result

def prepare_sweeps(experiment):
    experiment.mkdir(parents=True,exist_ok=True)
    if (experiment/'model_free.csv').exists():
        features=read(experiment/'model_free.csv')
        data={(f'SW{i:02d}',v):typed(read(experiment/f'SW{i:02d}/{v}.csv')) for i in range(len(settings())) for v in ['clean','noise']}
        return data,features
    p3=json.loads((ROOT/'configs/phase3.json').read_text());primary=typed(read(ROOT/'data/voynich/ZL_running.csv'))
    words,_=load_words(p3['source_slices']['C1'],34509)
    noise=json.loads((ROOT/'report/noise_model.json').read_text())['rates']
    data={};features=[]
    for index,setting in enumerate(settings()):
        code=f'SW{index:02d}';folder=experiment/code;folder.mkdir(parents=True,exist_ok=True)
        current={**p3,'encoder_aggressiveness':setting['aggressiveness']}
        c=setting['encoder']
        if c=='C12':out,metadata=expansive(words,rng_for(1729,c),current,setting['sequence_length'],setting['slot_rigidity'])
        else:out,metadata=encode(words,c,rng_for(1729,c),current)
        rows=layout(out,primary,c);rows,mapping=relabel(rows)
        alphabet=set(''.join(r['text_eva'].replace(' ','') for r in rows));rng=rng_for(1729,c+':noise');noisy=[]
        for r in rows:
            text,ops,raw=inject(r['text_eva'],noise,alphabet,rng);noisy.append({**r,'text_eva':text})
        dump(folder/'encoder.json',dict(setting=setting,metadata=metadata,mapping=mapping))
        for version,selected in [('clean',rows),('noise',noisy)]:
            table(folder/f'{version}.csv',selected);data[code,version]=selected
            result,detail=measure(selected,'T1',p3['clusters'],None)
            features.append(dict(setting=code,version=version,**setting,**result))
    table(ROOT/'report/shorthand_sweep_model_free.csv',features)
    table(experiment/'model_free.csv',features)
    return data,features

def run(experiment,config):
    data,features=prepare_sweeps(experiment);results=[];split=split_for('C1_clean')
    for (code,version),rows in data.items():
        prepared=prepare('C1_'+version,'T1',config,rows=rows,split=split)
        prepared['name']=code+'_'+version
        for pos in [False,True]:
            for seed in config['seeds']:
                job=experiment/f'{code}-{version}-p{int(pos)}-s{seed}'
                if (job/'metrics.json').exists():result=json.loads((job/'metrics.json').read_text())
                else:
                    model,result=fit(prepared,'lstm',pos,seed,config,job);del model
                    print(f'sweep {job.name}: {result["test_bpt"]:.4f} bpt',flush=True)
                results.append(result)
        del prepared
    table(ROOT/'report/shorthand_sweep_model_runs.csv',[{k:v for k,v in r.items() if k!='curve'} for r in results])
    return summarize(features,results)

def summarize(features,results):
    sys.path.insert(0,str(ROOT/'.analysis-runtime'))
    from scipy.stats import wasserstein_distance
    primary=read_rows('ZL_running');alternate=read_rows('LSI_H_running')
    lengths=lambda rows:[len(w) for r in rows for w in r['text_eva'].split()]
    zl_lengths=lengths(primary);h_lengths=lengths(alternate)
    master=read(ROOT/'report/master_metrics_extended.csv')
    z=next(r for r in master if r['corpus']=='ZL_running' and r['tokenization']=='T1')
    h=next(r for r in master if r['corpus']=='LSI_H_running' and r['tokenization']=='T1')
    entropy_band=abs(float(z['h2'])-float(h['h2']));length_band=float(wasserstein_distance(zl_lengths,h_lengths))
    gainrows=read(ROOT/'report/line_position_gain.csv')
    z_gain=next(r for r in gainrows if r['corpus']=='ZL_running' and r['architecture']=='lstm' and r['tokenization']=='T1')
    h_gain=next(r for r in gainrows if r['corpus']=='LSI_H_running' and r['architecture']=='lstm' and r['tokenization']=='T1')
    transcription_band=abs(float(z_gain['gain_mean'])-float(h_gain['gain_mean']))
    output=[]
    for f in features:
        f=dict(f)
        for key in ['h2','word_length_mean','aggressiveness','sequence_length','slot_rigidity']:
            if f.get(key) not in [None,'']:f[key]=float(f[key])
        matching=[r for r in results if r['corpus']==f['setting']+'_'+f['version']]
        gains=[]
        for seed in sorted({r['seed'] for r in matching}):
            a=next(r for r in matching if r['seed']==seed and not r['with_position'])
            b=next(r for r in matching if r['seed']==seed and r['with_position']);gains.append(a['test_bpt']-b['test_bpt'])
        mean=float(np.mean(gains));sd=float(np.std(gains,ddof=1))
        path=Path(matching[0]['run_dir']).parent/f['setting']/f"{f['version']}.csv"
        rows=read(ROOT/path)
        length_distance=float(wasserstein_distance(zl_lengths,lengths(rows)))
        h2_distance=abs(float(f['h2'])-float(z['h2']))
        gain_distance=abs(mean-float(z_gain['gain_mean']))
        gain_band=max(transcription_band,sd,float(z_gain['gain_sd']))
        output.append(dict(setting=f['setting'],encoder=f['encoder'],version=f['version'],
            aggressiveness=f['aggressiveness'],sequence_length=f.get('sequence_length'),slot_rigidity=f.get('slot_rigidity'),
            h2=f['h2'],word_length_mean=f['word_length_mean'],position_gain_mean=mean,position_gain_sd=sd,
            h2_distance=h2_distance,h2_band=entropy_band,word_length_W1=length_distance,word_length_band=length_band,
            gain_distance=gain_distance,gain_band=gain_band,
            matches_all_three=h2_distance<=entropy_band and length_distance<=length_band and gain_distance<=gain_band))
    table(ROOT/'report/shorthand_sweep.csv',output)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(15,5),layout='constrained')
    for ax,key,label,target,band in zip(axes,['h2','word_length_W1','position_gain_mean'],
            ['Character h2','Word-length W1 to ZL','Position gain (bits/token)'],
            [float(z['h2']),0,float(z_gain['gain_mean'])],[entropy_band,length_band,max(transcription_band,float(z_gain['gain_sd']))]):
        for encoder,color in zip(['C4','C5','C6','C12'],['#1c6c84','#7b5092','#ad681d','#247951']):
            for version,style in [('clean','-'),('noise',':')]:
                rows=[r for r in output if r['encoder']==encoder and r['version']==version]
                if encoder=='C12':continue
                x=[float(r['aggressiveness']) for r in rows]
                ax.plot(x,[r[key] for r in rows],style,marker='o',ms=3,label=encoder+' '+version,color=color)
        ax.axhline(target,color='black',lw=1);ax.axhspan(target-band,target+band,color='gray',alpha=.12)
        ax.set_ylabel(label);ax.set_xlabel('Aggressiveness');ax.grid(alpha=.15)
    axes[0].legend(fontsize=7,ncol=2)
    fig.suptitle('Registered shorthand grid; gray bands are descriptive ZL/LSI-H sensitivity, not formal equivalence')
    fig.savefig(ROOT/'report/shorthand_sweep.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
    for row,version in enumerate(['clean','noise']):
        current=[r for r in output if r['encoder']=='C12' and r['version']==version]
        for col,key in enumerate(['h2','word_length_W1','position_gain_mean']):
            matrix=np.array([[next(r[key] for r in current if int(r['sequence_length'])==l and float(r['slot_rigidity'])==rigidity)
                              for rigidity in [0,.5,1]] for l in [2,3,4]])
            limits=[r[key] for r in output if r['encoder']=='C12']
            ax=axes[row,col];im=ax.imshow(matrix,aspect='auto',cmap='viridis',vmin=min(limits),vmax=max(limits))
            ax.set_xticks(range(3),['0','.5','1']);ax.set_yticks(range(3),['2','3','4'])
            ax.set_xlabel('Slot rigidity');ax.set_ylabel('Sequence length')
            ax.set_title(version+' · '+['h2 (bits/character)','Word-length W1 to ZL','Position gain (bits/token)'][col])
            for i in range(3):
                for j in range(3):
                    red,green,blue,_=im.cmap(im.norm(matrix[i,j]))
                    color='black' if .2126*red+.7152*green+.0722*blue>.5 else 'white'
                    ax.text(j,i,f'{matrix[i,j]:.3f}',ha='center',va='center',color=color,fontsize=9)
            fig.colorbar(im,ax=ax)
    fig.suptitle('C12 expansive shorthand: registered two-parameter grid (no interpolation)')
    fig.savefig(ROOT/'report/C12_sweep_grid.png',dpi=160);plt.close(fig)
    return output
