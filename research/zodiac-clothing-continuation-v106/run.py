import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
import sys,json,hashlib,time,importlib.util,itertools
P=Path(__file__).resolve().parent; OLD=P.parent/'zodiac-qualification-v85'; V86=P.parent/'zodiac-457-v86'
spec=importlib.util.spec_from_file_location('frozen_v85',OLD/'run.py'); engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
np=engine.np
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,o): (P/n).write_text(json.dumps(o,indent=2),encoding='utf-8')
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def verify():
    f=load(P/'APPLICATION-FREEZE.json')
    for n,h in f['sha256'].items(): assert sha(P/n)==h,n
    for n,h in f['inherited'].items(): assert sha(P/n)==h,n
    for n,h in load(OLD/'FREEZE.json')['sha256'].items(): assert sha(OLD/n)==h,n
def raw_candidates():
    # Diagnostic traversal aliases; scoring still calls the original scorer.
    for inward,cw,ef,er,ar,tr in itertools.product([0,1],repeat=6):
        orders=[]
        for si,panels in enumerate(engine.signpanels):
            panels=panels[::-1] if (si==0 and ar) or (si==1 and tr) else panels
            seq=[]
            for pb in panels:
                bands=pb[:2] if si==2 else pb
                bands=bands if inward else bands[::-1]
                q=np.concatenate([b if cw else b[::-1] for b in bands])
                if si==2:
                    e=pb[2][::-1] if er else pb[2]; q=np.r_[e,q] if ef else np.r_[q,e]
                seq.extend(q)
            orders.append(np.array(seq))
        for phase in range(30):
            for table,subset in [('457','F')]+[('458',''.join(c for j,c in enumerate(['L','d','s','v']) if bits>>j&1)) for bits in range(1,16)]:
                x=np.zeros(120,dtype=np.int8)
                for si,order in enumerate(orders):
                    cats=engine.TABLES[engine.SIGNS[si]][table+'_degrees']
                    x[order]=[int(cats[(i+phase)%30] in subset) for i in range(30)]
                yield x,[inward,cw,ef,er,ar,tr,phase,table,subset]
def observed_scores(X,y):
    mask=np.isfinite(y); xx=X.astype(np.float32).copy(); yy=np.nan_to_num(y).astype(np.float32)
    for b in engine.BLOCKS:
        obs=b[mask[b]]
        if len(obs): xx[:,obs]-=xx[:,obs].mean(axis=1,keepdims=True); yy[obs]-=yy[obs].mean()
    xx[:,~mask]=0; yy[~mask]=0
    den=np.sqrt((xx*xx).sum(axis=1)*(yy*yy).sum())
    signed=np.divide(xx@yy,den,out=np.zeros(len(xx),dtype=np.float32),where=den>0)
    return signed,float((yy*yy).sum())
if __name__=='__main__':
    if sys.argv[1]=='freeze':
        assert not (P/'APPLICATION-FREEZE.json').exists()
        ann=load(P.parent/'zodiac-mapping-v84/ANNOTATIONS.json'); panels={p['folio']:p for p in ann}
        observations=load(P.parent/'zodiac-image-audit-v88/OBSERVATIONS.json'); revised={r['id']:r for r in observations}
        assert len(revised)==len(observations)
        order=[('f70v1',['outer','inner']),('f71r',['outer','inner']),('f71v',['outer','inner']),('f72r1',['outer','inner']),('f72r2',['outer','inner','extra-top']),('f72r3',['outer','middle','inner'])]
        maps={'body':{'garment visible':1,'bare torso visible':0,None:None},'enclosure':{'enclosing vessel visible':1,'no enclosing vessel visible':0,None:None}}
        records=[]; blocks=[]
        for folio,groups in order:
            for group in groups:
                rr=sorted([r for r in panels[folio]['rows'] if r['group']==group],key=lambda r:r['index'])
                assert len(rr)==len(engine.BLOCKS[len(blocks)])
                blocks.append({'folio':folio,'group':group,'indices':list(range(len(records),len(records)+len(rr)))})
                for r in rr:
                    original=r.copy()
                    assert r['id'] in revised
                    obs=revised[r['id']]
                    assert (obs['folio'],obs['group'],obs['index'])==(folio,group,r['index'])
                    r=dict(r,body=obs['body'],enclosure=obs['enclosure'],original_annotation=original,audit_evidence=obs)
                    records.append({'slot':len(records),'folio':folio,'sign':panels[folio]['sign'],'figure_id':r['id'],'group':group,'index':r['index'],'body':maps['body'][r.get('body')],'enclosure':maps['enclosure'][r.get('enclosure')],'source':r})
        assert len(records)==120
        dump('INPUT.json',{'records':records,'blocks':blocks,'encoding':{'body':'1 garment visible;0 bare torso visible;null ambiguous','enclosure':'1 vessel visible;0 no vessel visible;null ambiguous'},'excluded':{'Pisces':'29 visible figures','Leo':'uncertain-presence fold figure'},'heldout':'Virgo Libra Scorpio Sagittarius remain unscored'})
        dump('APPLICATION.json',{'scope':'Development signs Aries Taurus Gemini Cancer only;120 slots. No held-out scoring in this application.', 'scorer':'Unmodified v85.score_engine, all18424 unique templates/30720 raw rules from457+458,199 within-group cyclic shifts,absolute block-centered correlation,Bonferroni2.', 'seeds':{'body':1060001,'enclosure':1060002},'qualifying':'Adjustedp<=.05 AND positive within-block observed variance. Constant-after-centering features are not estimable, not evidence against a table.', 'ambiguity':'Existing nulls remain NaN; do not infer sex, pigment, label ownership, or supply gaps. Synthetic qualification does not establish power under actual ambiguity masks.', 'winner_freeze':'Retain every raw traversal alias within1e-7 of the observed maximum, with signed polarity. Freeze the whole candidate set if significant; do not choose an arbitrary representative. If no feature qualifies, freeze an empty winning set and preserve top fits as nonqualifying diagnostics. No held-out inspection to break ties.', 'ties':'Candidate score equality tolerance matches existing1e-7 null comparison. Table458 remains in corrected search; its prior qualification is pooled(v85), not separate like457(v86).', 'preread':'Corrected observations frozen in v88 before this application. Same-agent previously exposed audit; not independent annotation. v87 and v88 preserved. This is a revised developmental analysis, not fresh confirmation. This application freezes serialization, seeds and winner reporting before scoring.'})
        dump('APPLICATION-FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sha256':{n:sha(P/n) for n in ['run.py','INPUT.json','APPLICATION.json']},'inherited':{str(Path('..')/folder/name):sha(P.parent/folder/name) for folder,name in [('zodiac-qualification-v85','run.py'),('zodiac-qualification-v85','TABLES.json'),('zodiac-457-v86','templates.npy'),('zodiac-457-v86','keys.json'),('zodiac-457-v86','RESULTS.json'),('zodiac-mapping-v84','ANNOTATIONS.json'),('zodiac-image-audit-v88','OBSERVATIONS.json'),('zodiac-image-audit-v88','OBSERVATION-FREEZE.json'),('zodiac-image-audit-v88','AUDIT-PROTOCOL.json')]}})
        print('Application frozen; no scores calculated.')
    elif sys.argv[1]=='score':
        verify(); assert not (P/'RESULTS.json').exists()
        data=load(P/'INPUT.json'); config=load(P/'APPLICATION.json'); X=np.load(V86/'templates.npy'); keys=load(V86/'keys.json')
        lookup={x.tobytes():i for i,x in enumerate(X)}; aliases=[[] for _ in X]; rawcount=0
        for x,k in raw_candidates(): aliases[lookup[x.tobytes()]].append(k); rawcount+=1
        assert rawcount==30720 and all(aliases)
        results=[]; winners=[]; diagnostics=[]
        for feature in ['body','enclosure']:
            y=np.array([np.nan if r[feature] is None else r[feature] for r in data['records']])
            result=engine.score_engine(X,y,np.random.default_rng(config['seeds'][feature])); signed,var=observed_scores(X,y)
            assert abs(max(np.abs(signed))-result['score'])<1e-6
            tied=np.flatnonzero(np.abs(signed)>=result['score']-1e-7) if var>0 else np.array([],dtype=int)
            candidates=[{'unique_template':int(i),'signed_correlation':float(signed[i]),'polarity':'selected table subset -> feature1' if signed[i]>0 else 'selected table subset -> feature0','raw_key':k} for i in tied for k in aliases[i]]
            qualified=var>0 and result['p_two_features']<=.05
            counts=[]
            for b in data['blocks']:
                v=y[b['indices']]; obs=v[np.isfinite(v)]
                counts.append({**b,'known':len(obs),'unknown':int(np.isnan(v).sum()),'ones':int(obs.sum()),'within_block_variance_sum':float(((obs-obs.mean())**2).sum()) if len(obs) else 0})
            result.update(feature=feature,known=int(np.isfinite(y).sum()),unknown=int(np.isnan(y).sum()),within_block_variance_sum=var,estimable=var>0,qualified=qualified,tied_unique_templates=len(tied),tied_raw_rules=len(candidates),block_support=counts)
            results.append(result); diagnostics.append({'feature':feature,'qualified':qualified,'top_rules':candidates})
            if qualified: winners.append({'feature':feature,'adjusted_p':result['p_two_features'],'candidate_rules':candidates})
            dump(feature+'-all-scores.json',[{'template':i,'signed_score':float(v),'key':keys[i],'aliases':aliases[i]} for i,v in enumerate(signed)])
            print(feature,json.dumps({k:v for k,v in result.items() if k!='block_support'}),flush=True)
        dump('RESULTS.json',results); dump('TOP-FITS.json',diagnostics)
        dump('WINNING-RULES.json',{'status':'candidate set frozen; no held-out scoring' if winners else 'No qualifying rule; held-out signs remain unscored','key_fields':['inward','clockwise','extra_first','extra_reverse','Aries_panel_reverse','Taurus_panel_reverse','degree_offset','table','subset'],'winners':winners,'warning':'Equivalent development fits may diverge on new signs; no held-out tie breaking authorized here.'})
        verify()
        dump('WINNER-FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'heldout_scored':False,'sha256':{n:sha(P/n) for n in ['APPLICATION-FREEZE.json','RESULTS.json','TOP-FITS.json','WINNING-RULES.json','body-all-scores.json','enclosure-all-scores.json']}})
