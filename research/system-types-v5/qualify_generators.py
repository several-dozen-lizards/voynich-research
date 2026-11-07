"""Predeclared sandbox mechanism controls. Never imports or computes H1–H8."""
from pathlib import Path
from collections import Counter
import json,sys,random,math,re,time
import numpy as np
from core import (sha,save,canonical_hash,load_evt,panels,group_inventory,group_rank_mapping,
                  render_groups,fit_summary,eva_atoms)
from GENERATORS import generate
from sandbox import DATA
from published_g5 import run_published,compile_source,verify_source

ROOT=Path(__file__).resolve().parent
OWNERS=['core.py','GENERATORS/__init__.py','published_g5.py','qualify_generators.py','test_sandbox.py','held.py',
        'SOURCES/macer-floridus/words.json','SOURCES/macer-floridus/MANIFEST.json','SOURCES/timm-schinner-manifest.json','RUNTIME/MANIFEST.json',
        'registry.py','test_registry.py','RULE-SOURCES.json','transfer_policy.py','test_transfer_policy.py',
        'UNKNOWN-AND-LENGTH-POLICY.json','LATIN-SOURCE-UNITS.json','LANGUAGE-SOURCE-SPLITS.json']

def plan():
    if (ROOT/'FREEZE.json').exists():raise RuntimeError('claim freeze exists')
    p=ROOT/'QUALIFICATION-PLAN-v5.json'
    if p.exists():raise FileExistsError('preserve old plan; archive it explicitly before a new cut')
    save(p,dict(tier='sandbox',claim_freeze=False,version='mechanism-controls-5',supersedes='qualification4 preserved; policy2 distinguishes native missingness from newly unseen units; development-only non-wrapping generation retained',
        seeds=list(range(61000,61020)),source='edited Macer development chapters only; no calibration/reserve words used to fit generated mappings',
        source_split='exact current Latin development source IDs; source windows stay contiguous and do not wrap',
        layouts=[[10]*100,[3,5,8,12]*25],
        generator_controls='G1 sequence exact; G2 p0 identity/p1 all registered suffix opportunities; G3 p0 reduces to G2/p1 et symbol coverage; G4 widths1..3 and nulls independent seeded table, boundaries retained; G6 every output reconstructed from physical table coordinates; G5 unmodified published source compiled, repeat-seed equality, distinct seeds, output-only lines and seed-line omission for summaries',
        stochastic_gate='G2 p=.35: changed-word count within5 binomial SD of expected across qualification source per draw, record all counts',
        mapping='all20 seeds ×two layouts ×G1–G4 ×10 panels; observed1..3 EVA-atom groups; G4 group widths assigned by frequency-rank mapping within max_expansion; zero merges; inverse with retained unit boundaries; unsupported capacity=FAIL',
        held_gate='H1–H8 never called; full recovery/confusion requires later claim freeze and remains unrun',
        files={name:sha(ROOT/name) for name in OWNERS}))
    print('Qualification plan sealed; held gate remains locked.')

def check(condition,message):
    if not condition:raise AssertionError(message)

def flatten(g):return [w for line in g['lines'] for w in line]

def run():
    if (ROOT/'FREEZE.json').exists():raise RuntimeError('claim freeze exists')
    p=json.loads((ROOT/'QUALIFICATION-PLAN-v5.json').read_text())
    check(all(sha(ROOT/name)==digest for name,digest in p['files'].items()),'qualification owner changed after plan')
    begin=time.time()
    source=json.loads((ROOT/'LATIN-SOURCE-UNITS.json').read_text())
    split=json.loads((ROOT/'LANGUAGE-SOURCE-SPLITS.json').read_text())['Latin']
    selected=set(split['development']['units'])
    check(not selected.intersection(split['reserve']['units']) and not selected.intersection(split['calibration']['units']),'source partitions overlap')
    source_words=[w for unit in source if unit['unit'] in selected for w in unit['words']]
    save(ROOT/'DEVELOPMENT-MECHANISM-SOURCE.json',dict(source_units=sorted(selected),words=len(source_words),
         source_sha256=canonical_hash(source_words),partition='development',reserve_fitted=False,calibration_fitted=False,
         historical_source_receipt_preserved='SOURCE-SPLIT.json'))
    rows,manifest=load_evt(DATA/'text16e6.original.evt',DATA/'Davis-hands.original.csv')
    inventories={ '-'.join(key):group_inventory([w for r in cell for w in r['tokens'] if w]) for key,cell in panels(rows).items() }
    save(ROOT/'EVA-GROUP-INVENTORIES.json',inventories)
    controls=[];mapping=[];fit=[];failures=[]
    endings=('que','rum','us','um','em','am')
    for family in ['G1','G2','G3','G4','G6']:
        for seed in p['seeds']:
            for layout_id,layout in enumerate(p['layouts']):
                params={'abbreviation_probability':.35,'symbol_probability':.6,'null_probability':.1,'allow_source_wrap':False}
                g=generate(family,params,seed,source=source_words,line_lengths=layout)
                words=flatten(g);count=sum(layout)
                check(g==generate(family,params,seed,source=source_words,line_lengths=layout),'repeat-seed changed')
                check([len(line) for line in g['lines']]==layout,'layout not respected')
                if family!='G6':
                    check(g['source_wraps']==0,'source wrapped')
                    origin=source_words[g['source_offset']:g['source_offset']+count]
                detail={}
                if family=='G1':check([''.join(w) for w in words]==origin,'G1 changed source order/letters')
                if family in ('G2','G3'):
                    zero=generate(family,dict(params,abbreviation_probability=0,symbol_probability=0),seed,source=source_words,line_lengths=layout)
                    check([''.join(w) for w in flatten(zero)]==origin,'zero settings do not reduce to G1')
                    base=generate('G2',params,seed,source=source_words,line_lengths=layout)
                    opportunities=sum(any(w.endswith(s) and len(w)>len(s) for s in endings) for w in origin)
                    changed=sum(w!=list(o) for w,o in zip(flatten(base),origin))
                    check(abs(changed-.35*opportunities)<=5*math.sqrt(opportunities*.35*.65)+1,'G2 probability control')
                    full=generate('G2',dict(params,abbreviation_probability=1),seed,source=source_words,line_lengths=layout)
                    check(sum(w!=list(o) for w,o in zip(flatten(full),origin))==opportunities,'G2 missed eligible suffix')
                    detail.update(abbreviation_opportunities=opportunities,changed=changed)
                    if family=='G3':
                        no_symbols=generate('G3',dict(params,symbol_probability=0),seed,source=source_words,line_lengths=layout)
                        check(flatten(no_symbols)==flatten(base),'G3 p0 does not reduce to G2')
                        all_symbols=generate('G3',dict(params,symbol_probability=1),seed,source=source_words,line_lengths=layout)
                        symbol_count=sum(w[0].startswith('<TIRONIAN_ET>') for w in flatten(all_symbols))
                        check(symbol_count==origin.count('et'),'G3 missed et symbol opportunity')
                        detail.update(symbol_opportunities=origin.count('et'))
                if family=='G4':
                    for unit_word,word in zip(words,origin):
                        code_units=[u for u in unit_word if u!='<NULL>']
                        check(len(code_units)==len(word),'G4 source-letter correspondence')
                    detail.update(null_units=sum(w.count('<NULL>') for w in words))
                if family=='G6':
                    for draw in g['draws']:
                        check(draw['word']==''.join(g['table'][r][c] for r,c in draw['coordinates']),'G6 coordinate oracle')
                    detail.update(grille_draws=len(g['draws']),empty_skips=sum(not d['emitted'] for d in g['draws']))
                    lines=[[''.join(w) for w in line] for line in g['lines']]
                    fit.append(dict(family=family,seed=seed,layout=layout_id,summary=fit_summary(lines)))
                controls.append(dict(family=family,seed=seed,layout=layout_id,status='PASS',**detail))
                if family in ('G1','G2','G3','G4'):
                    for cell,inventory in sorted(inventories.items()):
                        try:
                            receipt=group_rank_mapping(words,inventory,max_width=g['max_expansion'] if family=='G4' else 3)
                            if family=='G4':check(all(1<=len(eva_atoms(v))<=3 for v in receipt['mapping'].values()),'G4 mapped group width')
                            rendered=render_groups(words,receipt)
                            inverse={v:k for k,v in receipt['mapping'].items()}
                            check([[inverse[group] for group in spans] for spans in rendered['mapped_unit_groups']]==words,'unit-boundary reverse map failed')
                            cursor=0;lines=[]
                            for length in layout:
                                lines.append(rendered['words'][cursor:cursor+length]);cursor+=length
                            summary=fit_summary(lines)
                            fit.append(dict(family=family,seed=seed,layout=layout_id,cell=cell,summary=summary))
                            mapping.append(dict(family=family,seed=seed,layout=layout_id,cell=cell,status='PASS',units=len(receipt['mapping']),mapping=receipt))
                        except (ValueError,AssertionError) as error:
                            entry=dict(family=family,seed=seed,layout=layout_id,cell=cell,status='FAIL',reason=str(error))
                            failures.append(entry);mapping.append(entry)
        save(ROOT/'MECHANISM-CONTROLS.json',controls);save(ROOT/'GROUP-MAPPING-QUALIFICATION.json',mapping)
    compile_source()
    published=[]
    for seed in (19,23,31,43,59):
        a=run_published(f'qualified-{seed}-a',seed=seed,lines=100)
        b=run_published(f'qualified-{seed}-b',seed=seed,lines=100)
        check(a['raw']==b['raw'],'published G5 repeat-seed mismatch')
        lines=[line.split() for line in a['raw'].splitlines() if line.strip() and not line.startswith('#')]
        check(len(lines)==100,('published G5 wrong line count',len(lines)))
        check(all(re.fullmatch('[a-z]+',word) for line in lines for word in line),'published G5 output contamination')
        # Upstream emits its initial seed line as first line. Exclude it from fit controls.
        fit.append(dict(family='G5-published',seed=seed,seed_line_excluded=True,summary=fit_summary(lines[1:])))
        published.append(dict(seed=seed,status='PASS',lines=len(lines),sha256=sha(a['path']),repeat_sha256=sha(b['path'])))
    check(len(set(x['sha256'] for x in published))==len(published),'G5 distinct seeds produced same whole output')
    save(ROOT/'G5-PUBLISHED-QUALIFICATION.json',dict(status='MECHANICAL_FIDELITY_PASS',source_commit=verify_source(),trials=published,
         source_modified=False,claim_recovery_run=False,seed_line_excluded_from_fit=True))
    save(ROOT/'S-FIT-GENERATOR-CONTROLS.json',fit)
    save(ROOT/'QUALIFICATION-FAILURES.json',failures)
    result=dict(status='SANDBOX_MECHANISMS_PASS' if not failures else 'MAPPING_QUALIFICATION_INCOMPLETE',
         claim_ready=False,mechanism_trials=len(controls),mapping_trials=len(mapping),mapping_passes=sum(x['status']=='PASS' for x in mapping),
         mapping_failures=len(failures),published_G5_repeat_trials=len(published),
         scope='Mechanics, provenance and mapping; not manuscript fit, model discrimination, historical frequencies or full recovery gate',
         H3='UNRESOLVED',held_scoring_run=False,FREEZE_exists=False,plan_sha256=sha(ROOT/'QUALIFICATION-PLAN-v5.json'),
         source_partition='development only',source_wrapping=False,reserve_used_for_mapping_fit=False,
         source_fidelity=dict(G1='Latin herbal source qualified for extraction/mechanics; other languages pending',
            G2='Cappelli-style sourced rule subset on edited herbal; not real diplomatic control',
            G3='et symbol attested, context variants explicit synthetic parameter; broad medical concept inventory pending',
            G4='one source letter to1..3 EVA-atom span plus optional null, explicit position variants',
            G5='unmodified published code, not surrogate',G6='Rugg mechanism relationships, explicit parametric table and movement, not exact historical table'),
         elapsed_seconds=time.time()-begin)
    save(ROOT/'GENERATOR-QUALIFICATION.json',result)
    print(json.dumps(result))

if __name__=='__main__':
    {'plan':plan,'run':run}[sys.argv[1]]()
