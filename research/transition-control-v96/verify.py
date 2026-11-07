from pathlib import Path
import collections,hashlib,json,re
from fractions import Fraction
from engine import state,edges,score,convolve,assess
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');nulls=load(R/'NULL-DISTRIBUTIONS.json');q=load(R/'QUALIFICATION.json');assert q['status']=='PASS'
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','qualify.py','run.py'] else P/n).read_bytes()).hexdigest()==h
for n,h in load(P/'opening-order-audit-v75/FREEZE.json').items():assert hashlib.sha256((P/'opening-order-audit-v75'/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
raw=load(P/'frequency-atlas-v48/rows.json');source={(r[0],r[6]):r for r in raw};prior=load(P/'one-gap-order-v78/RESULTS.json');spanchecks=0
for p in d['panels']:
 if p['status']!='complete':continue
 totals=[]
 for view in p['views']:
  if view['status']!='complete':continue
  mode=view['view'];neutral=mode=='non_target_middle';poly={0:1};D=0;ways=1;edgecounts=[0]*9
  for s in view['span_records']:
   ws=source[(p['reading'],s['locator'])][7];i=s['start_ordinal']-1;assert ws[i:i+len(s['tokens'])]==s['tokens'] and None not in s['tokens'];assert (i==0 or ws[i-1] is None) and (i+len(s['tokens'])==len(ws) or ws[i+len(s['tokens'])] is None)
   seq=tuple(map(state,s['tokens']));assert list(seq)==s['classes'] and list(edges(seq))==s['adjacent_class_counts'];assert score(seq,neutral)==s['observed_D'];D+=s['observed_D']
   hist={int(k):int(v,16) for k,v in s['score_support'].items()};assert hist.get(s['observed_D'],0)>0;assert sum(hist.values())==int(s['class_paths_hex'],16);ways*=sum(hist.values());poly=convolve(poly,hist);spanchecks+=1
   edgecounts=[a+b for a,b in zip(edgecounts,s['adjacent_class_counts'])]
  saved=next(n for n in nulls if n['original_panel_index']==p['original_panel_index'] and n['view']==mode);assert poly=={int(k):int(v,16) for k,v in saved['weights_hex'].items()};assert sum(poly.values())==ways==int(saved['total_ways_hex'],16)
  assert assess(poly,D,p['opening_pairs']*28)==view['result']
  old=next(z for z in prior['panels'] if z['original_panel_index']==p['original_panel_index'] and z['view']==mode);assert D==old['result']['observed_D']
  totals.append(ways)
  # Independent exact tail in rational mean-distance form, without assess().
  mean=Fraction(sum(k*v for k,v in poly.items()),ways);tail=sum(v for k,v in poly.items() if abs(Fraction(k)-mean)>=abs(Fraction(D)-mean));assert hex(tail)==view['result']['tail_numerator_hex']
 assert len(set(totals))==1
 print('verified',p['section'],p['reading'],flush=True)
verification=dict(qualification_before_corpus='PASS',frozen_methods_and_original_source_hashes='pass',source_span_boundaries_and_states='pass',span_views_checked=spanchecks,exact_histogram_convolution_replay='all complete panel views',independent_rational_tail_counts='pass',same_observed_D_as_v78='pass',same_path_counts_between_views='pass',no_Monte_Carlo_floor='exact integer counts; each view resolution audited',browser_visual_review='not performed; prior local-file URL policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(verification,indent=2),encoding='utf-8');print('Exact transition-control source counts and tails verified.')
