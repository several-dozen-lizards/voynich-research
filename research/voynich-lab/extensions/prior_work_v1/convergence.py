"""Headline-only validation-plateau reruns; original 96-step fits are untouched."""
import time,math,statistics
from .common import *
from .additions import prepared,data
from src import train
from src.train import torch,F,LanguageModel,autocast,initialize,evaluate
import numpy as np

class Plateau:
    def __init__(self,settings):
        self.settings=settings;self.material_best=float('inf');self.raw_best=float('inf');self.raw_best_step=0;self.stale=0;self.lr_stale=0
    def observe(self,loss,step):
        raw=loss<self.raw_best
        if raw:self.raw_best=loss;self.raw_best_step=step
        if loss<self.material_best-self.settings['minimum_improvement_bpt']:
            self.material_best=loss;self.stale=0;self.lr_stale=0
        else:self.stale+=1;self.lr_stale+=1
        reduce=self.lr_stale>=self.settings['LR_plateau_patience']
        if reduce:self.lr_stale=0
        stop=step>=self.settings['minimum_steps'] and self.stale>=self.settings['patience_checks'] and not raw
        return raw,reduce,stop

def fit(p,pos,seed,cfg,settings,folder,cap):
    folder.mkdir(parents=True,exist_ok=True);initialize(seed);device='cuda'
    model=LanguageModel(len(p['vocabulary']),'transformer',pos,cfg).to(device)
    optimizer=torch.optim.AdamW(model.parameters(),lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'],fused=True)
    tensors={key:value.to(device) for key,value in p['tensors'].items()}
    generator=torch.Generator(device=device).manual_seed(seed+811);controller=Plateau(settings)
    curve=[];seen=0;step=0;best_state=None;current_lr=cfg['learning_rate'];last=folder/'RESUME.pt';qualified=False
    if last.exists():
        state=torch.load(last,map_location=device,weights_only=False);model.load_state_dict(state['model']);optimizer.load_state_dict(state['optimizer'])
        step=state['step'];curve=state['curve'];seen=state['seen'];current_lr=state['lr'];best_state={k:v.cpu() for k,v in state['best_state'].items()}
        controller.__dict__.update(state['controller']);generator.set_state(state['generator'].cpu());torch.set_rng_state(state['torch_rng'].cpu());torch.cuda.set_rng_state(state['cuda_rng'].cpu())
    start=time.perf_counter()
    while step<cap:
        step+=1;model.train();indices=torch.randint(len(tensors['train']),(cfg['batch_size'],),generator=generator,device=device)
        batch=tensors['train'][indices];optimizer.zero_grad(set_to_none=True)
        scale=min(1,step/max(1,cfg.get('warmup_steps',8)))
        for group in optimizer.param_groups:group['lr']=current_lr*scale
        with autocast():
            logits=model(batch[:,0],batch[:,2]);loss=F.cross_entropy(logits.reshape(-1,logits.shape[-1]),batch[:,1].reshape(-1),ignore_index=0)
        if not torch.isfinite(loss):raise RuntimeError('Nonfinite training loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),cfg['gradient_clip']);optimizer.step();seen+=int((batch[:,1]!=0).sum())
        if step%settings['validation_every']==0 or step==cap:
            value=evaluate(model,tensors['validation'],cfg['batch_size'])['bits_per_token'];raw,reduce,stop=controller.observe(value,step)
            if raw:best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            curve.append(dict(step=step,validation_bpt=value,train_batch_bpt=float(loss.detach())/math.log(2),learning_rate=current_lr,stale_checks=controller.stale))
            if reduce:current_lr=max(settings['minimum_LR'],current_lr*settings['LR_factor'])
            if stop:qualified=True;break
    if not qualified:
        torch.save(dict(model=model.state_dict(),optimizer=optimizer.state_dict(),step=step,curve=curve,seen=seen,lr=current_lr,
            best_state=best_state,controller=controller.__dict__,generator=generator.get_state(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state()),last)
    model.load_state_dict(best_state);test=evaluate(model,tensors['test'],cfg['batch_size'],details=True)
    test_bpc=(test['bits_per_token']*test['tokens']+float(p['escape']['test'].sum()))/p['character_counts']['test']
    validation_bpc=(controller.raw_best*p['oov']['validation']['tokens']+float(p['escape']['validation'].sum()))/p['character_counts']['validation']
    recent=curve[-min(8,len(curve)):];slope=float(np.polyfit([r['step'] for r in recent],[r['validation_bpt'] for r in recent],1)[0]) if len(recent)>1 else None
    result=dict(corpus=p['name'],tokenization=p['scheme'],architecture='transformer',with_position=pos,seed=seed,
        parameter_count=model.count,steps=step,step_cap=cap,selected_step=controller.raw_best_step,plateau_qualified=qualified,
        unfinished_at_cap=not qualified,literal_final_checkpoint_best=controller.raw_best_step==step,recent_validation_slope=slope,
        validation_bpt=controller.raw_best,validation_bpc_with_escape=validation_bpc,test_bpt=test['bits_per_token'],test_bpc_with_escape=test_bpc,
        test_unknown_rate=test['unknown_rate'],training_tokens_seen=seen,effective_token_epochs=seen/p['oov']['train']['tokens'],seconds=time.perf_counter()-start,
        curve=curve,run_dir=str(folder.relative_to(ROOT)),device=device,stopping='validation only, raw-min checkpoint; no test-based decision')
    if p['name'] in ['ZL_running','LSI_H_running']:
        totals={language:dict(bits=0.,tokens=0,characters=0,escape_bits=0.) for language in ['A','B']}
        for block in p['metadata']:
            if block['split']!='test':continue
            bi=block['block_index']
            for j,meta in enumerate(block['metadata']):
                if meta is None or meta[4] not in totals:continue
                t=totals[meta[4]];t['bits']+=float(test['losses'][bi,j]);t['tokens']+=1;t['characters']+=len(meta[2].replace(' ',''));t['escape_bits']+=float(p['escape']['test'][bi,j])
        result['currier_test']={language:{**r,'bpt':r['bits']/r['tokens'],'bpc_with_escape':(r['bits']+r['escape_bits'])/r['characters']} for language,r in totals.items() if r['tokens']}
    spec=dict(corpus=p['name'],tokenization=p['scheme'],architecture='transformer',with_position=pos,seed=seed,
        training=cfg,stopping=settings,vocabulary=p['vocabulary'],bpe_merges=p['merges'],page_split=p['split'])
    dump(folder/'config.json',spec);dump(folder/f'metrics-cap{cap}.json',result);dump(folder/'metrics.json',result)
    if seed==1729:torch.save(dict(state_dict=best_state,spec=spec),folder/'model.pt')
    del model,optimizer,tensors;return result

def names(extra):
    selected=['ZL_running','LSI_H_running']
    for name,m in registry().items():
        if name.startswith(('C1_','C9_','C13_','C15_','C18_')) and not m.get('analysis_only'):selected.append(name)
    selected += [name for name in extra if name.startswith('C12_fullbest_')]
    return selected

def run(wait_for_matrix=False):
    folder=EXT/'runs/additions';extra=json.loads((folder/'registry.json').read_text()) if (folder/'registry.json').exists() else data()
    if wait_for_matrix:
        while not (EXT/'report/NEURAL_STATUS.json').exists():time.sleep(5)
    settings=json.loads((EXT/'phase6_additions.json').read_text())['convergence'];cfg=json.loads((ROOT/'configs/phase4.json').read_text())
    selected=names(extra);jobs=[(name,scheme,pos,seed) for name in selected for scheme in ['T1','T2'] for pos in [False,True] for seed in cfg['seeds']]
    dump(folder/'CONVERGENCE_FREEZE.json',dict(config_sha256=sha(EXT/'phase6_additions.json'),code_sha256=sha(Path(__file__)),corpora=selected,total_runs=len(jobs)))
    # The selected full-grid C12 setting was absent from the old transformer
    # matrix. Supply its matched96-step comparator rather than substitute the
    # original length3/rigidity.5 C12 setting.
    for name in [n for n in extra if n.startswith('C12_fullbest_')]:
        for scheme in ['T1','T2']:
            p=prepared(name,scheme,cfg,extra)
            for pos in [False,True]:
                for seed in cfg['seeds']:
                    path=folder/'fullbest_96'/f'{name}-{scheme}-p{int(pos)}-s{seed}'
                    if not (path/'metrics.json').exists():model,_=train.fit(p,'transformer',pos,seed,cfg,path);del model
    cap=settings['initial_step_cap'];pending=jobs;results={}
    while pending:
        p=None;last=None
        for index,(name,scheme,pos,seed) in enumerate(pending,1):
            job=folder/'convergence'/f'{name}-{scheme}-p{int(pos)}-s{seed}'
            if (job/'metrics.json').exists():r=json.loads((job/'metrics.json').read_text())
            else:r=None
            if r is None or not r['plateau_qualified'] and r['step_cap']<cap:
                if last!=(name,scheme):p=prepared(name,scheme,cfg,extra);last=(name,scheme)
                try:r=fit(p,pos,seed,cfg,settings,job,cap)
                except Exception as error:dump(job/'FAILED.json',dict(error=repr(error)));raise
            results[name,scheme,pos,seed]=r
            progress('headline convergence reruns',completed=len(results),total=len(jobs),cap=cap,last=job.name,steps=r['steps'])
        unfinished=[key for key,r in results.items() if not r['plateau_qualified']]
        fraction=len(unfinished)/len(jobs);by_corpus={name:sum(key[0]==name for key in unfinished)/sum(key[0]==name for key in results) for name in selected}
        if fraction<.1 and max(by_corpus.values())<.1:break
        if cap>=settings['maximum_step_cap']:break
        cap=min(settings['maximum_step_cap'],cap*settings['cap_extension_factor']);pending=unfinished
    all_results=list(results.values());table(EXT/'report/convergence_runs.csv',[{k:v for k,v in r.items() if k not in ['curve','currier_test']} for r in all_results])
    table(EXT/'report/convergence_status_by_corpus.csv',[dict(corpus=name,unfinished_fraction=value) for name,value in by_corpus.items()])
    dump(EXT/'report/CONVERGENCE_STATUS.json',dict(status='PASS' if fraction<.1 and max(by_corpus.values())<.1 else 'NOT_QUALIFIED',
        runs=len(jobs),unfinished_fraction=fraction,literal_endpoint_best_fraction=sum(r['literal_final_checkpoint_best'] for r in all_results)/len(all_results),
        final_cap=cap,criterion='global and each source corpus unfinished fraction strictly below10%',test_used_for_stopping=False))
    summarize(all_results)

def summarize(results):
    baseline=[]
    for folder in [ROOT/'runs/phase4-de886963575d',EXT/'runs/models',EXT/'runs/additions/fullbest_96']:
        baseline.extend(json.loads(p.read_text()) for p in folder.glob('*/metrics.json'))
    output=[]
    for name,scheme,pos in sorted({(r['corpus'],r['tokenization'],r['with_position']) for r in results}):
        current=[r for r in results if (r['corpus'],r['tokenization'],r['with_position'])==(name,scheme,pos)]
        old=[r for r in baseline if (r['corpus'],r['tokenization'],r['with_position'],r['architecture'])==(name,scheme,pos,'transformer')]
        assert len(old)==len(current)==5
        output.append(dict(corpus=name,tokenization=scheme,with_position=pos,
            fixed96_bpt_mean=statistics.mean(r['test_bpt'] for r in old),fixed96_bpt_sd=statistics.stdev(r['test_bpt'] for r in old),
            converged_bpt_mean=statistics.mean(r['test_bpt'] for r in current),converged_bpt_sd=statistics.stdev(r['test_bpt'] for r in current),
            fixed96_bpc_mean=statistics.mean(r['test_bpc_with_escape'] for r in old),converged_bpc_mean=statistics.mean(r['test_bpc_with_escape'] for r in current),
            mean_steps=statistics.mean(r['steps'] for r in current),plateau_qualified_seeds=sum(r['plateau_qualified'] for r in current)))
    table(EXT/'report/convergence_comparison.csv',output);gains=[]
    for name,scheme in sorted({(r['corpus'],r['tokenization']) for r in results}):
        rs=[r for r in results if r['corpus']==name and r['tokenization']==scheme]
        values=[next(r['test_bpt'] for r in rs if r['seed']==s and not r['with_position'])-next(r['test_bpt'] for r in rs if r['seed']==s and r['with_position']) for s in config()['seeds']]
        gains.append(dict(corpus=name,tokenization=scheme,gain_mean=statistics.mean(values),gain_sd=statistics.stdev(values)))
    table(EXT/'report/converged_position_gain.csv',gains)
if __name__=='__main__':run('--wait-for-matrix' in sys.argv)
