"""Independent completeness/preservation audit; no scientific gate is hidden."""
from .common import *
from collections import Counter
import gzip,zipfile,xml.etree.ElementTree as ET

def verify():
    checks=[];failures=[]
    def check(label,ok,detail=None):
        checks.append(dict(check=label,pass_=bool(ok),detail=detail))
        if not ok:failures.append(label)
    for name in ['FREEZE.json','EM_FREEZE.json','runs/CLASSIFIER_CODE_FREEZE.json']:
        expected=json.loads((EXT/name).read_text());drift=[p for p,h in expected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
        check(name+' unchanged',not drift,dict(files=len(expected),drift=drift))
    preserved=json.loads((EXT/'runs/PRIOR_ARTIFACT_PRESERVATION.json').read_text());drift=[p for p,h in preserved.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    check('accepted Phase4/5 artifact bytes preserved',not drift,dict(files=len(preserved),drift=drift))
    prior=json.loads((ROOT/'runs/phase5-c2f38fa45d6b/OUTPUT_HASHES.json').read_text())
    prior_drift=[p for p,h in prior.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    check('accepted Phase5 original output hashes match',not prior_drift,prior_drift)
    check('accepted Phase5 verification retained',json.loads((ROOT/'report/PHASE5_VERIFICATION.json').read_text())['status']=='PASS')
    reg=registry();cfg=config();runs=[json.loads(p.read_text()) for p in (EXT/'runs/models').glob('*/metrics.json')]
    keys=[(r['corpus'],r['tokenization'],r['architecture'],r['with_position'],r['seed']) for r in runs]
    expected={(name,t,a,pos,s) for name,m in reg.items() if not m.get('analysis_only') for t in (['T4'] if m['legacy'] else ['T1','T2','T3','T4']) for a in ['lstm','transformer'] for pos in [False,True] for s in cfg['seeds']}
    check('complete unique added neural matrix',len(keys)==len(set(keys)) and set(keys)==expected,dict(actual=len(keys),expected=len(expected)))
    check('local CUDA model size cap',all(r['device']=='cuda' and r['parameter_count']<=5000000 for r in runs))
    master=read(EXT/'report/master_metrics.csv');base=read(EXT/'report/natural_baseline_metrics.csv')
    check('all 69 corpus views times four tokenizations',len(master)==276 and len({(r['corpus'],r['tokenization']) for r in master})==276)
    check('294 Wikipedia and24 historical views times four',len(base)==1272 and len({r['corpus'] for r in base if r['family']=='Wikipedia'})==294 and len({r['corpus'] for r in base if r['family']=='Historical'})==24)
    check('18 historical work families',len({r['work_family'] for r in base if r['family']=='Historical'})==18)
    conv=[json.loads(p.read_text()) for p in (EXT/'runs/additions/convergence').glob('*/metrics.json')];cs=json.loads((EXT/'report/CONVERGENCE_STATUS.json').read_text())
    check('440 unique headline convergence runs',len(conv)==440 and len({(r['corpus'],r['tokenization'],r['with_position'],r['seed']) for r in conv})==440)
    check('strict global and per-corpus <10% unfinished',cs['status']=='PASS' and cs['unfinished_fraction']<.1 and all(float(r['unfinished_fraction'])<.1 for r in read(EXT/'report/convergence_status_by_corpus.csv')),cs)
    check('40 fullbest C12 matched96 comparators',len(list((EXT/'runs/additions/fullbest_96').glob('*/metrics.json')))==40)
    partial=read(EXT/'report/C12_partial_sweep.csv');pf=json.loads((EXT/'runs/additions/PARTIAL_DATA_FREEZE.json').read_text())
    check('partial data frozen bytes unchanged',all(sha(ROOT/p)==h for p,h in pf.items()))
    check('24 partial rows and240 fits',len(partial)==24 and len(list((EXT/'runs/additions/partial_models').glob('*/metrics.json')))==240)
    cf=list((EXT/'runs/classifier/crossfit').glob('*/metrics.json'));check('320 new control reference fits',len(cf)==320,len(cf))
    reference=json.loads((EXT/'runs/classifier/REFERENCE_RECEIPT.json').read_text())
    for key,value in reference.items():
        name=key.rsplit(':p',1)[0];path=ROOT/value['path'];r=read(path);expected_words=sum(len(v['text_eva'].split()) for v in corpus(name))
        check('reference coverage '+key,len(r)==expected_words and len({(v['line_id'],int(v['word_index'])) for v in r})==expected_words and sha(path)==value['sha256'])
    for p in (EXT/'runs/classifier/crossfit').glob('*/LEAKAGE_RECEIPT.json'):
        r=json.loads(p.read_text());check('heldout disjoint '+p.parent.name,not (set(r['test_leaves'])&(set(r['train_leaves'])|set(r['validation_leaves']))))
    for tag in ['all_families','exclude_C10_C11']:
        r=json.loads((EXT/f'report/classifier_{tag}_result.json').read_text());receipts=json.loads((EXT/f'report/classifier_{tag}_purge_receipts.json').read_text())
        check('classifier ancestry disjoint '+tag,all(not set(v['train_ancestry'])&(set(v['test_ancestry'])|set(v['validation_ancestry'])) and not set(v['test_ancestry'])&set(v['validation_ancestry']) for v in receipts))
        if tag=='exclude_C10_C11':check('classifier exact requested class universe',set(r['classes'])=={f'C{i}' for i in list(range(1,10))+list(range(12,19))})
    ms=read(EXT/'report/mixture_summary.csv');mr=read(EXT/'report/mixture_results.csv')
    check('all62 corpus mixtures and five-seed K1/2/3',len(ms)==372 and len(mr)==2790,dict(summary=len(ms),runs=len(mr)))
    qual=json.loads((EXT/'report/C14_QUALIFICATION_STATUS.json').read_text());check('C14 partial qualification retained',qual.get('status')=='PARTIAL_QUALIFICATION',qual)
    topics=read(EXT/'report/within_cell_section_probes.csv');check('59 actual/fake topic corpus views',len({r['corpus'] for r in topics})==59)
    check('real topic/hand metadata ZL-only',all(r['corpus']=='ZL_running' or r.get('label_kind')!='source_section' for r in topics))
    check('dictionary noisy positives and nulls retained',len(read(EXT/'report/C16_dictionary_null_summary.csv'))==32 and all(any(r['corpus']==n for r in read(EXT/'report/C16_dictionary_hits.csv')) for n in [f'C16_{l}_{v}_{n}' for l in ['Latin','Hebrew'] for v in ['vowels','novowels'] for n in ['clean','noise']]))
    kh=EXT/'c16_kh_ranking_v2';kr=json.loads((kh/'REGISTRATION.json').read_text());kd=[p for p,h in kr['inputs'].items() if sha(ROOT.parent/p)!=h]
    check('C16-KH original v1 inputs unchanged',not kd,kd)
    ratings=json.loads((kh/'blind/ratings.json').read_text());check('200 source-stripped blank blind rows',len(ratings)==200 and all(r['coherence_0_4']==r['grammaticality_0_4']==r['comments']=='' and set(r)=={'item_id','decoded_line','coherence_0_4','grammaticality_0_4','comments'} for r in ratings))
    with zipfile.ZipFile(kh/'blind/rater-only.zip') as z:check('rater package includes XLSX and no key',set(z.namelist())=={'ratings.csv','ratings.json','INSTRUCTIONS.txt','ratings.xlsx'})
    with zipfile.ZipFile(kh/'outputs/01a1785e-be24-71f3-9d83-66fe2f091b06/ratings.xlsx') as z:
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));nonblank=[]
        for cell in sheet.findall('.//s:c',ns):
            a=cell.attrib['r'];col=''.join(c for c in a if c.isalpha());row=int(''.join(c for c in a if c.isdigit()))
            if col in ['C','D','E'] and row>=2 and (cell.find('s:v',ns) is not None or cell.find('s:is',ns) is not None or cell.find('s:f',ns) is not None):nonblank.append(a)
        check('saved XLSX human rating fields empty',not nonblank,nonblank)
    result=dict(status='PASS' if not failures else 'FAIL',checks=checks,failures=failures,prior_artifacts=len(preserved),new_neural_matrix=len(runs),headline_convergence=len(conv),partial_fits=240,classifier_reference_fits=len(cf),sealed_keys_opened=False,scientific_limits=['partial C14 qualification','unrated blind export','original KH LM retained','exploratory partial C12','uncalibrated classifier scores'])
    dump(EXT/'report/PHASE6_VERIFICATION.json',result)
    if failures:raise RuntimeError('Phase6 verification failures: '+str(failures))
    return result
if __name__=='__main__':verify()
