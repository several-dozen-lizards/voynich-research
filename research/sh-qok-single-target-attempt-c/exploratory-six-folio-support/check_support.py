from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction
from datetime import datetime,timezone
import json,hashlib,sys

R=Path(__file__).resolve().parent
C=R.parent
sys.path.insert(0,str(C))
import engine

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Keep prior check intact.'
    frozen=json.loads((C/'SUPPORT-FREEZE.json').read_text())['hashes']
    for p,h in frozen.items():assert sha(Path(p))==h
    panels=json.loads((C/'PANELS.json').read_text())
    folios=sorted(r['folio'] for r in panels['freshness_audit'] if r['panel']=='P1' and not r['prior_runs']['v75']['scored_sh_qok'] and not r['prior_runs']['v77']['scored_sh_qok'])
    assert len(folios)==6
    save('PROTOCOL.json',dict(status='EXPLORATORY (E): outcome-masked support-only subset audit',utc=datetime.now(timezone.utc).isoformat(),folios=folios,
        selection='Exactly P1 folios whose frozen historical membership audit marks no sh-qok score in v75 and v77. Chosen after aggregate attempt-C outcomes were known.',
        freshness='Not in those earlier searches; already included in scored attempt C. This is not a new held-out sample.',
        support='Unchanged family-stratified attempt-C H1 support: V=sum ns*nc/(ns+nc), at least8 supported exact physical-page folios, V>=80, maxpageV/V<=.25. H/F separate; first-position eligible; other ending retained.',
        stop='Do not compute subset qok outcomes, effects, p-values or power; report support gate only. Failed gate means NOT ESTIMABLE under this protocol, not negative evidence.',
        verification='Recompute support independently using rational arithmetic and compare stored full-panel strata restricted to the six pages.',
        hashes={str(p):sha(p) for p in [Path(__file__),C/'engine.py',C/'MASKED.json',C/'SUPPORT.json',C/'PANELS.json']}))
    data=json.loads((C/'MASKED.json').read_text());assert all('y' not in r and 'outcome' not in r and 'follower' not in r for r in data)
    full=json.loads((C/'SUPPORT.json').read_text());results={};checks=[]
    for tr in ['H','F']:
        cell='P1-'+tr;ev=[r for r in data if r['cell']==cell and r['folio'] in folios]
        result=engine.support(ev)
        counts=defaultdict(lambda:[0,0])
        for v in ev:counts[v['folio'],v['family']][0 if v['prefix']=='sh' else 1]+=1
        page=defaultdict(Fraction)
        for (pg,f),(sh,ch) in counts.items():page[pg]+=Fraction(sh*ch,sh+ch)
        V=sum(page.values(),Fraction(0));npage=sum(v>0 for v in page.values());maxshare=max(page.values(),default=Fraction(0))/V if V else None
        assert abs(float(V)-result['V'])<1e-10 and npage==result['supported_pages']
        assert maxshare is None or abs(float(maxshare)-result['max_page_share'])<1e-10
        previous=[s for s in full[cell]['strata'] if s['folio'] in folios]
        assert sum(s['sh'] for s in previous)==result['sh'] and sum(s['ch'] for s in previous)==result['ch']
        assert abs(sum(s['V'] for s in previous)-float(V))<1e-10
        failed=[]
        if V<80:failed.append('V < 80')
        if npage<8:failed.append('fewer than 8 supported physical pages')
        if maxshare is None or maxshare>Fraction(1,4):failed.append('largest page share exceeds 25% or no support')
        result.update(status='NOT ESTIMABLE' if failed else 'SUPPORT PASSES',classification='EXPLORATORY (E)',failed_gate_components=failed,
            per_folio=[dict(folio=pg,sh=sum(v['prefix']=='sh' for v in ev if v['folio']==pg),ch=sum(v['prefix']=='ch' for v in ev if v['folio']==pg),V=float(page.get(pg,0))) for pg in folios])
        results[cell]=result
        checks.append(dict(cell=cell,exact_rational_V=str(V),masked_events_verified=len(ev),independent_support_agrees=True,restricted_previous_strata_agree=True))
    save('SUPPORT.json',results)
    save('VERIFICATION.json',dict(status='PASS',checks=checks,subset_outcomes_computed=False,subset_inference_performed=False))
    text='EXPLORATORY (E) — six-folio P1 support audit\n\n'
    text+='Both readings are NOT ESTIMABLE under the unchanged H1 support gate. Six physical pages cannot meet its minimum of eight, irrespective of qok outcomes.\n\n'
    text+='Folios: '+', '.join(folios)+'.\n\n'
    text+='| Reading | sh / ch origins | V (required ≥80) | Supported pages (required ≥8) | Largest page share (required ≤25%) |\n|---|---:|---:|---:|---:|\n'
    for cell,r in results.items():text+=f"| {cell} | {r['sh']} / {r['ch']} | {r['V']:.3f} | {r['supported_pages']} | {100*r['max_page_share']:.2f}% |\n"
    text+='\n| Folio | H sh / ch | H V | F sh / ch | F V |\n|---|---:|---:|---:|---:|\n'
    for i,pg in enumerate(folios):
        h=results['P1-H']['per_folio'][i];f=results['P1-F']['per_folio'][i]
        text+=f"| {pg} | {h['sh']} / {h['ch']} | {h['V']:.3f} | {f['sh']} / {f['ch']} | {f['V']:.3f} |\n"
    text+='\nThe subset was selected after attempt C’s aggregate result. These six pages were outside the listed historical sh→qok searches, but their outcomes were already included in attempt C. They are not a fresh held-out sample. No subset outcomes, effects, p-values or power estimates were computed, no support thresholds were relaxed, and H/F were not pooled. A failed support gate says nothing about whether the dependency exists.\n\n'
    text+='Verification independently recomputed the support using exact rational arithmetic and matched the corresponding strata in the previously frozen full-panel support file.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps(dict(folios=folios,results={k:{f:r[f] for f in ['status','sh','ch','V','supported_pages','supported_strata','max_page_share','failed_gate_components']} for k,r in results.items()}),indent=2))

if __name__=='__main__':main()
