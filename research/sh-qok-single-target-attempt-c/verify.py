"""Independent source/event/effect audit. Does not import extraction or effect engine."""
from pathlib import Path
import csv,json,re,hashlib,math
from collections import defaultdict,Counter
from datetime import datetime,timezone
import numpy as np

R=Path(__file__).resolve().parent

def audit():
    protocol=json.loads((R/'PROTOCOL.json').read_text());sources=protocol['sources']
    rawpath=next(Path(p) for p in sources if 'text16e6' in p);metapath=next(Path(p) for p in sources if 'Davis-hands' in p)
    meta={r['Folio']:r for r in csv.DictReader(metapath.open(encoding='utf-8-sig'))}
    expected=[];bycell=defaultdict(list);alllines=set()
    for raw in rawpath.read_text(encoding='latin1').splitlines():
        match=re.match(r'^<([^>]+)>\s*(.*)',raw)
        if not match:continue
        loc,txt=match.groups()
        if ';' not in loc:continue
        loc,tr=loc.rsplit(';',1);bits=loc.split('.')
        if len(bits)!=3 or tr not in ['H','F'] or not bits[1].startswith('P'):continue
        pg=bits[0]
        if pg not in meta or meta[pg]['Scribe'] not in ['2','3']:continue
        hand,sec=meta[pg]['Scribe'],meta[pg]['Section']
        p='P0' if (hand=='2' and sec=='Balneological') or (hand=='3' and sec=='Starred paragraphs') else 'P1' if hand=='2' else 'P2'
        assert (loc,tr) not in alllines;alllines.add((loc,tr))
        clean=re.sub(r'\{[^}]*\}','',txt.partition('#')[0]);clean=''.join(c for c in clean if c!='!' and not c.isspace())
        pieces=[s for s in re.split('[.,=\\-]',clean) if s!=''];words=[s if s.isascii() and s.isalpha() and s.islower() else None for s in pieces]
        for i,w in enumerate(words):
            if w is not None and w[:2] not in ['sh','ch']:continue
            reason='unknown_origin' if w is None else 'origin_at_end' if i==len(words)-1 else 'following_unknown' if words[i+1] is None else ''
            suffix=None if w is None else next((s for s in ['eey','edy','ey','y'] if w.endswith(s)),'other')
            follower=words[i+1] if i+1<len(words) else None
            y=int(follower[:3]=='qok') if not reason else None
            cell=p+'-'+tr
            row=dict(cell=cell,folio=pg,line=loc,position=str(i),origin=w or '',follower=follower or '',family=suffix or '',outcome='' if y is None else str(y),exclusion_reason=reason)
            expected.append(row)
            if not reason:bycell[cell].append(dict(page=pg,family=suffix,x=int(w[:2]=='sh'),y=y,hand=hand))
    actual=list(csv.DictReader((R/'EVENTS.csv').open(encoding='utf-8',newline='')))
    assert len(actual)==len(expected)
    for i,(a,b) in enumerate(zip(actual,expected)):
        assert all(a[k]==v for k,v in b.items()),('event mismatch',i,b)
    counts={};effects={};support=json.loads((R/'SUPPORT.json').read_text());primary=json.loads((R/'PRIMARY.json').read_text());p0=json.loads((R/'DESCRIPTIVE-P0.json').read_text())
    def independent_effect(ev):
        strata=defaultdict(lambda:[0,0,0,0]);pages=defaultdict(lambda:[0.,0.])
        for v in ev:
            t=strata[v['page'],v['family']];j=0 if v['x'] else 1;t[j]+=1;t[2+j]+=v['y']
        for (pg,f),(ns,nc,a,b) in strata.items():
            if ns and nc:
                weight=1/(1/ns+1/nc);pages[pg][0]+=weight*(a/ns-b/nc);pages[pg][1]+=weight
        total=sum(v[1] for v in pages.values())
        return (100*sum(v[0] for v in pages.values())/total if total else None),strata,pages
    for cell in ['P1-H','P1-F','P2-H','P2-F']:
        ev=bycell[cell];value,strata,pages=independent_effect(ev);s=support[cell]
        assert len(ev)==s['eligible_origins'];assert sum(v['x'] for v in ev)==s['sh']
        V=sum(v[1] for v in pages.values());assert abs(V-s['V'])<1e-8
        assert sum(v[1]>0 for v in pages.values())==s['supported_pages']
        assert sum(ns>0 and nc>0 for ns,nc,a,b in strata.values())==s['supported_strata']
        ex=Counter(v['exclusion_reason'] for v in expected if v['cell']==cell and v['exclusion_reason'])
        assert dict(ex)==s['exclusions']
        r=next(r for r in primary if r['cell']==cell)
        assert (value is None and r['effect_points'] is None) or abs(value-r['effect_points'])<1e-9
        # Independent bootstrap replay, using multinomial page multiplicities rather than gathering 2-D terms.
        pgs=sorted({v['page'] for v in ev});rng=np.random.default_rng(240100+['P1-H','P1-F','P2-H','P2-F'].index(cell));values=[]
        if V:
            for _ in range(4999):
                chosen=rng.integers(len(pgs),size=len(pgs));weights=Counter(chosen.tolist());num=den=0.
                for j,k in weights.items():
                    a,b=pages.get(pgs[j],[0,0]);num+=k*a;den+=k*b
                if den:values.append(100*num/den)
            assert np.allclose(np.quantile(values,[.025,.975]),r['CI95_points'],atol=1e-9)
        counts[cell]=dict(events=len(ev),exclusions=dict(ex),V=V);effects[cell]=value
    for r in p0:
        _,hand,tr=r['cell'].split('-');ev=[v for v in bycell['P0-'+tr] if v['hand']==hand]
        value,_,_=independent_effect(ev);assert len(ev)==r['events'] and abs(value-r['effect_points'])<1e-9
        assert not any(k in r for k in ['p','holm_p'])
        effects[r['cell']]=value
    secondary=json.loads((R/'SECONDARY.json').read_text())
    for r in secondary:
        if 'probabilities' not in r:continue
        y=np.array([v['y'] for v in bycell[r['cell']]])
        for cal in r['calibration']:
            assert set(cal['train_folios']).isdisjoint(cal['test_folios'])
            assert set(cal['inner_fit']).isdisjoint(cal['inner_validation'])
            assert set(cal['inner_fit'])|set(cal['inner_validation'])==set(cal['train_folios'])
        losses={m:-(y*np.log2(pr)+(1-y)*np.log2(1-np.array(pr))) for m,pr in r['probabilities'].items()}
        for m,l in losses.items():assert abs(float(l.mean())-r['losses_bits'][m])<1e-10
        folios={v['page'] for v in bycell[r['cell']]};gains=[]
        for fol in folios:
            ix=[i for i,v in enumerate(bycell[r['cell']]) if v['page']==fol];gains.append(float((losses['P'][ix]-losses['J'][ix]).mean()))
        assert abs(float(np.mean(gains))-r['gain_bits'])<1e-10
    frozen=0
    for name in ['FREEZE.json','SUPPORT-FREEZE.json','QUALIFICATION-FREEZE.json']:
        for p,h in json.loads((R/name).read_text())['hashes'].items():
            assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('hash',p);frozen+=1
    phases=[json.loads(v) for v in (R/'PHASES.jsonl').read_text().splitlines()]
    order=[v['phase'] for v in phases]
    assert order.index('support_frozen')<order.index('qualification_complete')<order.index('first_manuscript_outcome_computation')
    result=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),independent_raw_parser=True,all_event_rows_verified=len(expected),counts=counts,effects_points=effects,bootstrap_CI_independent_replay=True,H2_losses_and_fold_separation=True,P0_no_pvalues=True,frozen_hash_checks=frozen,phase_order_verified=True)
    (R/'VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':audit()
