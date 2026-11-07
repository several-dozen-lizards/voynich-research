"""RD-FO3: published G5/G6 fingerprints and junction-directed origin, calibration only."""
import argparse
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
LAB=HERE.parents[1];WORK=LAB.parent
sys.path.insert(0,str(LAB/'extensions/ringdir_v2'))
import run_v2 as v
REG=HERE/'registration'
OUT=LAB/'results/ringdir/followup_v3'
MASTER=2026110604
TS=WORK/'system-types-v5'
MANIFEST=TS/'SOURCES/timm-schinner-manifest.json'
MAIN=TS/'SOURCES/timm-schinner/source/src/main'
v.OUT=OUT;v.SEED=MASTER


def check_published():
    m=v.load(MANIFEST)
    for item in m['files']:
        assert v.rd.sha(TS/item['path'])==item['sha256'],item['path']
    return m['commit']


def paths():
    p={HERE/n for n in ['PROTOCOL.md','run_followup.py','test_followup.py','verify_followup.py']}
    p.add(LAB/'report/HANDOFF_RD_2026-11-06.md')
    old=v.load(LAB/'extensions/ringdir_v2/registration/REGISTRATION.json')
    p.update(WORK/n for n in old['hashes'])
    for folder in ['results/ringdir/phase0_v1','results/ringdir/circular_v2','results/ringdir/preflight',
                   'results/ringdir/v2','extensions/ringdir_v2/registration','extensions/ringdir_v2/reporting_receipt']:
        p.update(f for f in (LAB/folder).rglob('*') if f.is_file())
    p.update(TS/f['path'] for f in v.load(MANIFEST)['files'])
    runtime=TS/'RUNTIME/MANIFEST.json'
    p.update([MANIFEST,runtime,Path(v.load(runtime)['java']),Path(v.load(runtime)['javac']),
              TS/'GENERATORS/__init__.py',TS/'published_g5.py',LAB/'extensions/ringdir_v2/finalize_reports.py'])
    return sorted(p)


def register():
    assert not OUT.exists()
    v.check();commit=check_published()
    assert v.load(LAB/'results/ringdir/v2/VERIFICATION.json')['status']=='PASS'
    REG.mkdir()
    v.save(REG/'REGISTRATION.json',dict(id='RD-FO3',utc=v.stamp(),seed=MASTER,published_commit=commit,
        scope='published G5/G6 fingerprint and S-glyph-directed S-p1 paragraph origin only',
        hashes={str(p.relative_to(WORK)):v.rd.sha(p) for p in paths()},python=sys.version))
    for n in ['PROTOCOL.md','run_followup.py','test_followup.py','verify_followup.py']:
        (REG/n).write_bytes((HERE/n).read_bytes())
    (REG/'CORRECTED_HANDOFF.md').write_bytes((LAB/'report/HANDOFF_RD_2026-11-06.md').read_bytes())
    print('REGISTERED RD-FO3 before generation/fitting/scoring',flush=True)


def check():
    for n,h in v.load(REG/'REGISTRATION.json')['hashes'].items():
        assert v.rd.sha(WORK/n)==h,n


def parse_g5(raw):
    lines=[line.strip() for line in raw.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert len(lines)>1,'No generated lines beyond initialization'
    words=[w for line in lines[1:] for w in line.split()]
    assert all(re.fullmatch('[a-zA-Z]+',w) for w in words),'Unexpected nonalphabetic generated token'
    return words,lines[0],len(lines)-1


def command(args,folder,name):
    try:
        result=subprocess.run(args,cwd=folder,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
    except subprocess.TimeoutExpired as e:
        (folder/(name+'.stdout.txt')).write_text(str(e.stdout or ''),encoding='utf-8')
        (folder/(name+'.stderr.txt')).write_text(str(e.stderr or ''),encoding='utf-8')
        v.save(folder/(name+'.command.json'),dict(args=args,timeout=120,status='TIMEOUT'))
        raise
    (folder/(name+'.stdout.txt')).write_text(result.stdout,encoding='utf-8')
    (folder/(name+'.stderr.txt')).write_text(result.stderr,encoding='utf-8')
    v.save(folder/(name+'.command.json'),dict(args=args,returncode=result.returncode))
    result.check_returncode()


def generated_data(words,name):
    held=[]
    for i in range(0,len(words['held']),512):
        held.append([dict(id=f'{name}:{i}',family=f'{name}block:{i}',words=words['held'][i:i+512],scribe='',section='')])
    return dict(train=[[dict(words=words['train'])]],held=held,trainlines=[],heldlines=[])


def generate_g5(folder,counts):
    commit=check_published();runtime=v.load(TS/'RUNTIME/MANIFEST.json')
    classes=folder/'classes';classes.mkdir()
    javafiles=sorted((MAIN/'java').rglob('*.java'))
    command([runtime['javac'],'-encoding','UTF-8','-d',str(classes)]+list(map(str,javafiles)),folder,'compile')
    assert (classes/'de/voynich/text/SelfCitationTextGenerator.class').exists()
    words={};receipt={}
    for split,seed in [('train',4011),('held',4012)]:
        dest=folder/split;dest.mkdir();(dest/'generated').mkdir()
        settings={'save.path':'./generated/','save.filename':'text.txt','text.lines_to_create':'4000',
                  'method.random':'pseudo','method.random.pseudo.seed':str(seed),'method.canFollow':'curveline'}
        text=(MAIN/'resources/conf.properties').read_text(encoding='utf-8')
        text+='\n'+'\n'.join(k+'='+val for k,val in settings.items())+'\n'
        (dest/'conf.properties').write_text(text,encoding='utf-8')
        command([runtime['java'],'-cp',str(dest)+os.pathsep+str(classes),'de.voynich.text.SelfCitationTextGenerator'],dest,'generate')
        rawfile=dest/'generated/text.txt'
        seq,initial,nlines=parse_g5(rawfile.read_text(encoding='utf-8-sig'))
        if len(seq)<counts[split]:raise ValueError(f'SOURCE_TOO_SHORT {split}: {len(seq)} < {counts[split]}')
        words[split]=seq[:counts[split]]
        receipt[split]=dict(seed=seed,available=len(seq),retained=counts[split],generated_lines=nlines,
            initialization_line_excluded=initial,initialization_influences_descendants=True,
            config_sha256=v.rd.sha(dest/'conf.properties'),raw_sha256=v.rd.sha(rawfile),settings=settings)
    v.save(folder/'generation.json',dict(published_commit=commit,surrogate_used=False,receipt=receipt,words=words,
        caveat='Published Voynich-inspired rules and Voynich-derived initialization are retained; not an independent natural-language control.'))
    return generated_data(words,'G5_published')


def generate_g6(folder,counts):
    spec=importlib.util.spec_from_file_location('rdfo3_generators',TS/'GENERATORS/__init__.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    words={}
    for split,seed in [('train',4021),('held',4022)]:
        result=mod.generate('G6',{},seed,line_lengths=[counts[split]])
        v.save(folder/(split+'_generator.json'),dict(seed=seed,result=result))
        words[split]=[''.join(u) for u in result['lines'][0]]
        assert len(words[split])==counts[split]
    v.save(folder/'generation.json',dict(words=words,caveat='Fixed simplified table/grille engineering implementation, not an authenticated historical reconstruction.'))
    return generated_data(words,'G6')


def origin(folder,data,corpus):
    folder.mkdir(parents=True)
    candidates=v.complete_paragraphs(data['heldlines']);supported=[];support=[]
    for b in [4,5]:
        ss=[c for c in candidates if v.rd.binof(len(c['words']))==b];nf=len({c['family'] for c in ss})
        support.append(dict(bin=b,n=len(ss),families=nf))
        if len(ss)>=30 and nf>=8:supported.append(b)
    v.rd.table(folder/'support.csv',support)
    if not supported:return v.finish(folder,'FAIL_UNSUPPORTED',support=support)
    r=v.rng('O3/'+corpus);stimuli=[];keys=[]
    for c in candidates:
        if v.rd.binof(len(c['words'])) not in supported:continue
        s,k=v.rd.make_case(c,str(len(keys)),'circular',corpus,r,True);stimuli.append(s);keys.append(k)
    v.seal(folder,stimuli,keys)
    p1=v.p1_fit(data['trainlines']);models=v.fit_models(data)
    v.save(folder/'p1_model.json',dict(first_rate=p1[0],other_rate=p1[1],window=p1[2]))
    for sig in ['word','glyph']:
        v.rd.table(folder/(sig+'_model.csv'),[dict(a=a,b=b,count=n) for (a,b),n in sorted(models[sig].items())])
    values=[]
    for s in v.rd.loadlines(folder/'stimuli.jsonl'):
        profile=v.p1_profiles(s['words'],p1)
        shuffled=s['words'][:];r.shuffle(shuffled);nullprofile=v.p1_profiles(shuffled,p1)
        gs,_=v.dscore(s['words'],models['glyph'],'glyph');ws,_=v.dscore(s['words'],models['word'],'word')
        ng,_=v.dscore(shuffled,models['glyph'],'glyph')
        peaks=[v.rd.argmax_tie(p,r) for p in profile];npeaks=[v.rd.argmax_tie(p,r) for p in nullprofile]
        choose=lambda score,p:None if v.rd.sign(score)==0 else p[int(score<0)]
        values.append(dict(id=s['id'],profiles=profile,peaks=peaks,glyph_score=gs,word_score=ws,
            selected_peak=choose(gs,peaks),word_selected_peak=choose(ws,peaks),null_words=shuffled,
            null_profiles=nullprofile,null_peaks=npeaks,null_glyph_score=ng,null_selected_peak=choose(ng,npeaks)))
    v.scores_saved(folder,values);keyed=v.openkey(folder);vs={x['id']:x for x in values};trials=[]
    for k in keyed:
        x=vs[k['id']];acceptable=v.rd.window_union(k['boundaries'],k['n']);chance=len(acceptable)/k['n']
        hit=int(x['selected_peak'] in acceptable);nhit=int(x['null_selected_peak'] in acceptable)
        isolated=int(x['peaks'][int(k['reverse'])] in acceptable)
        trials.append(dict(**k,hit=hit,chance=chance,excess=hit-chance,null_excess=nhit-chance,
            word_hit=int(x['word_selected_peak'] in acceptable),isolated_hit=isolated,no_call=x['selected_peak'] is None,
            direction_correct=int(v.rd.sign(x['glyph_score'])==(-1 if k['reverse'] else 1))))
    v.rd.table(folder/'trials.csv',trials);bins=[]
    for b in supported:
        ss=[t for t in trials if t['bin']==b];hit=sum(t['hit'] for t in ss)/len(ss)
        ex=v.ci(ss,'excess',str(folder)+str(b)+'ex');nu=v.ci(ss,'null_excess',str(folder)+str(b)+'null')
        nullpass=-.15<=nu[0]<=0<=nu[1]<=.15
        bins.append(dict(bin=b,n=len(ss),families=len({t['family'] for t in ss}),hit_rate=hit,
            mean_chance=sum(t['chance'] for t in ss)/len(ss),excess_ci=ex,null_excess_ci=nu,null_passed=nullpass,
            passed=nullpass and hit>=.5 and ex[0]>0,
            isolated_hit_rate=sum(t['isolated_hit'] for t in ss)/len(ss),
            paired_word_hit_rate=sum(t['word_hit'] for t in ss)/len(ss),
            direction_accuracy=sum(t['direction_correct'] for t in ss)/len(ss),no_calls=sum(t['no_call'] for t in ss)))
    v.save(folder/'bins.json',bins)
    status='FAIL_NULL' if not all(b['null_passed'] for b in bins) else ('PASS' if any(b['passed'] for b in bins) else 'FAIL_ORIGIN')
    return v.finish(folder,status,bins=bins,primary='junction-directed S-p1 paragraph origin')


def failed(folder,error):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'EXECUTION_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
    return v.finish(folder,'FAIL_EXECUTION',error=str(error),retried=False)


def run():
    check();OUT.mkdir();v.save(OUT/'RUN_START.json',dict(utc=v.stamp(),registration_sha256=v.rd.sha(REG/'REGISTRATION.json')))
    data=v.datasets();targets=[]
    for t in v.rows(LAB/'results/ringdir/preflight/ring_inventory.csv'):
        if t['type']=='circular' and float(t['eva_codepoint_count'])/int(t['word_count'])>=2 and float(t['unknown_word_count'])/int(t['word_count'])<=.2 and t['is_spurious']!='True' and t['is_alternate_branch']!='True':targets.append(t)
    counts={s:sum(len(l['words']) for l in data['ZL'][key]) for s,key in [('train','trainlines'),('held','heldlines')]}
    assert counts==dict(train=8776,held=13299)
    results=[]
    for name,generate in [('G5_published',generate_g5),('G6',generate_g6)]:
        folder=OUT/'F'/name;folder.mkdir(parents=True)
        try: generated=generate(folder,counts)
        except Exception as e:results.append(failed(folder,e));continue
        models=v.fit_models(generated)
        for sig in ['word','glyph']:
            chain=folder/sig
            try:results.append(v.direction_chain(chain,generated,targets,sig,models[sig]))
            except Exception as e:results.append(failed(chain,e))
    for corpus in ['ZL','Latin']:
        folder=OUT/'O'/corpus/'p1_glyph_directed'
        try:results.append(origin(folder,data[corpus],corpus))
        except Exception as e:results.append(failed(folder,e))
    for r in results:r['chain']=r['chain'].replace('\\','/')
    check();save_summary(results)
    v.save(OUT/'ARTIFACT_MANIFEST.json',dict(hashes={str(p.relative_to(OUT)):v.rd.sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print('RD-FO3 COMPLETE; prior runs unchanged; targets closed',flush=True)


def save_summary(results):
    v.save(OUT/'SUMMARY.json',results)
    summary=[]
    for r in results:
        summary.append(dict(chain=r['chain'],status=r['status'],L_min=r.get('L_min'),
                            passing_bins=json.dumps(r.get('passing_bins',[])),bins=json.dumps(r.get('bins',[]))))
    v.rd.table(OUT/'summary.csv',summary)
    failedchains=[r['chain'] for r in results if r['status'].startswith('FAIL')]
    v.save(OUT/'STATUS.json',dict(status='COMPLETE_WITH_FAILURES' if failedchains else 'COMPLETE',
        failed_chains=failedchains,prior_runs_unchanged=True,real_ring_scores_computed=False,
        radial='HELD',phase1_run=False,corrected_order_generated=False))
    text=['# RD-FO3 calibration follow-up','', '| Chain | Status | L_min |','|---|---|---:|']
    text += [f"| {r['chain']} | {r['status']} | {r.get('L_min') or '—'} |" for r in results]
    text += ['', '| System | Whole-word L_min | Junction-feature L_min |','|---|---:|---:|']
    prior=v.rows(LAB/'results/ringdir/v2/summary.csv')
    for corpus in ['Latin','G2','G3','G4','Naibbe','ZL']:
        cells=[]
        for sig in ['word','glyph']:
            row=next(x for x in prior if x['corpus']==corpus and x['signal']==sig)
            cells.append((row['D_L_min'] if corpus in ['Latin','ZL'] else row['F_L_min']) or 'FAIL')
        text.append('| '+corpus+' | '+' | '.join(cells)+' |')
    for corpus in ['G5_published','G6']:
        cells=[]
        for sig in ['word','glyph']:
            row=next((x for x in results if x['chain']==f'F/{corpus}/{sig}'),None)
            cells.append(str(row['L_min']) if row and row.get('L_min') else ('FAIL' if row else 'NOT_RUN'))
        text.append('| '+corpus+' (new) | '+' | '.join(cells)+' |')
    text += ['', '| Origin corpus | Words | n | Junction-directed hit | Chance | Excess95%CI | Gate |',
             '|---|---|---:|---:|---:|---|---|']
    for r in results:
        if not r['chain'].startswith('O/'):continue
        for b in r.get('bins',[]):
            text.append(f"| {r['chain'].split('/')[1]} | {v.rd.BINS[b['bin']][0]}–{v.rd.BINS[b['bin']][1]} | {b['n']} | "
                f"{b['hit_rate']:.1%} | {b['mean_chance']:.1%} | {b['excess_ci'][0]:.3f}–{b['excess_ci'][1]:.3f} | {b['passed']} |")
    text += ['', 'Full direction curves, support, ties and shuffle nulls are in each chain report/bin table. '
        'S-p1 isolated and paired word-directed diagnostics are descriptive; the new primary gate uses '
        'junction-inferred orientation, including its own inferred-orientation shuffled null.','',
        'G5 is the pinned published Java implementation, not the v5 surrogate. Published Voynich-inspired '
        'rules and initialization are retained; the literal first seed line is excluded but influences '
        'descendants. G6 is a fixed simplified table/grille implementation. Neither result identifies '
        'a historical mechanism; one realization is not a generator-class rejection.','',
        'These are new registered calibration runs motivated by earlier outcomes. Old gates/results are '
        'unchanged. Paragraph-to-ring transfer remains untested. Latin origin has artificial source layout. '
        'Real-ring scores, radial text, visual comparisons and corrected orders remain closed.','']
    (OUT/'report.md').write_text('\n'.join(text),encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
    for ax,name in zip(axes,['G5_published','G6']):
        for sig in ['word','glyph']:
            row=next((x for x in results if x['chain']==f'F/{name}/{sig}'),None)
            if not row:continue
            bs=row.get('bins',[])
            ax.plot([b['length_min'] for b in bs],[b['accuracy'] for b in bs],'o-',label=sig)
        ax.axhline(.8,color='gray',ls='--');ax.set_title(name);ax.set_xlabel('Lower word-length bin edge')
        ax.set_ylim(0,1.03)
        if ax.lines:ax.legend()
    axes[0].set_ylabel('Sealed reversal recovery; ties wrong')
    fig.suptitle('RD-FO3 fixed generator realizations; full cluster intervals in bin tables')
    fig.tight_layout();fig.savefig(OUT/'fingerprint_curves.png',dpi=150);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','run'])
    register() if p.parse_args().action=='register' else run()
