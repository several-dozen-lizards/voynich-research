"""Frozen diagnostic only. No proposed key, C3 policy, or verdict is changed."""
import copy,json,random,statistics,sys,hashlib,time
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
P=Path(__file__).parent;A2=P.parent/'attempt-2-v7.1';OLD=P.parent/'HARNESS'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(A2/'diagnostics'))
from harness import random_key,digest,decode_word,decode_record,raw_scores
from source_control_adapter import make_control,tokenize
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

def save(n,x):
 f=P/n;f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def load(n):return json.loads((A2/n).read_text(encoding='utf8'))

@lru_cache(maxsize=250000)
def hit(w,lex):
 return w is not None and process.extractOne(w,lex,scorer=Levenshtein.normalized_distance,score_cutoff=.25) is not None

def decoder(k):
 rules=defaultdict(list)
 for r in k['rules']:rules[r['unit']].append(r)
 def decode(word,section):
  if not word:return None
  out=[]
  for i,u in enumerate(word):
   if u not in k['map']:return None
   pos='single' if len(word)==1 else 'first' if i==0 else 'last' if i==len(word)-1 else 'interior'
   ctx={'position':pos,'left':word[i-1] if i else '^','right':word[i+1] if i+1<len(word) else '$','section':section}
   values={r['value'] for r in rules[u] if all(ctx.get(a)==b for a,b in r['when'].items())}
   if len(values)>1:return None
   out.append(next(iter(values)) if values else k['map'][u])
  return ''.join(out)
 return decode

def indicators(k,rows,lex):
 d=decoder(k);return [int(hit(d(w,r['section']),lex)) for r in rows for w in r['words']]

def grouped_random_key(k,rng):
 z=copy.deepcopy(k)
 for isword in (False,True):
  uu=[u for u in z['map'] if u.startswith('WORD:')==isword];vv=[z['map'][u] for u in uu];rng.shuffle(vv)
  for u,v in zip(uu,vv):z['map'][u]=v
 vv=[r['value'] for r in z['rules']];rng.shuffle(vv)
 for r,v in zip(z['rules'],vv):r['value']=v
 return z

def totals(matrix):return [sum(v) for v in matrix]
def tail(observed,values):return (1+sum(v>=observed for v in values))/(len(values)+1)

def audit_reading(reading):
 k=load('TRAP-'+reading+'-KEY.json');data=load('TRAP-'+reading+'-DATA.json');lex=tuple(data['lexicons']['HERBAL']);held=data['held']
 slices=load('TRAP-SLICES.json')['readings'][reading]['held'];assert len(held)==len(slices)
 raw=[];events=[];decode=decoder(k);native=caused=0
 for row,s in zip(held,slices):
  assert row['id']==reading+':'+s['locus'] and len(row['words'])==len(s['tokens'])
  rr=copy.deepcopy(row);rr['raw_words']=s['tokens'];raw.append(rr)
  for i,(u,w) in enumerate(zip(row['words'],s['tokens'])):
   out=decode(u,row['section']);assert out==decode_word(u,k,row['section'])
   cls='native_unknown' if w is None else 'known_WORD' if len(u)==1 and u[0].startswith('WORD:') else 'character_fallback'
   native+=w is None;caused+=w is not None and out is None
   best=process.extractOne(out,lex,scorer=Levenshtein.normalized_distance,score_cutoff=.25) if out is not None else None
   events.append({'id':row['id'],'word_index':i,'source':w,'units':u,'group':cls,'decoded':out,'lexicon_match':best[0] if best else None,'normalized_distance':best[1] if best else None,'real_hit':int(best is not None),'decode_unknown_origin':'native' if w is None else 'key' if out is None else None})
 observed=[e['real_hit'] for e in events];rng=random.Random(719);rks=[random_key(k,rng) for _ in range(1000)]
 oldbank=load('banks/TRAP-'+reading+'-real.json');assert oldbank['key_hashes']==[digest(z) for z in rks]
 original=[];perkey=[]
 for i,z in enumerate(rks):
  hits=indicators(z,held,lex);original.append(hits)
  assert sum(hits)==oldbank['scores'][i]['E1']['success']
  if i<10:
   assert hits==[int(hit(decode_word(w,z,r['section']),lex)) for r in held for w in r['words']]
  perkey.append({'index':i,'key_sha256':digest(z),'total':sum(hits),'groups':{g:sum(v for v,e in zip(hits,events) if e['group']==g) for g in ('known_WORD','character_fallback','native_unknown')}})
 for i,e in enumerate(events):
  e['original_C3_hit_count']=sum(x[i] for x in original);e['original_C3_hit_probability']=e['original_C3_hit_count']/1000
  e['real_minus_C3_mean_hit']=e['real_hit']-e['original_C3_hit_probability']
 groups={}
 for g in ('known_WORD','character_fallback','native_unknown'):
  indices=[i for i,e in enumerate(events) if e['group']==g];dist=[sum(x[i] for i in indices) for x in original];s=sum(observed[i] for i in indices)
  groups[g]={'slots':len(indices),'real_hits':s,'C3_median_hits':statistics.median(dist),'C3_mean_hits':statistics.mean(dist),'C3_p':tail(s,dist)}
 # Sensitivity has separate randomization and receipts, never replaces C3.
 rng=random.Random(2719);sensitivity=[]
 for i in range(1000):
  z=grouped_random_key(k,rng);hits=indicators(z,held,lex)
  sensitivity.append({'index':i,'key_sha256':digest(z),'total':sum(hits),'fallback':sum(v for v,e in zip(hits,events) if e['group']=='character_fallback')})
 # Source-first spelling control; raw glyphs are shuffled BEFORE fixed tokenization.
 c1=make_control(raw,k,'training_whole_word','C1-glyph',802)
 control_observed=indicators(k,c1,lex);c1dist=[sum(indicators(z,c1,lex)) for z in rks]
 edits=sum(a!=b for a,b in zip([w for r in raw for w in r['raw_words']],[w for r in c1 for w in r['control_raw_words']]) if a is not None)
 oldc1=load('banks/TRAP-'+reading+'-C1-glyph.json');oldchanges=sum(a!=b for r,cr in zip(held,__import__('harness').shuffle_glyphs(held,random.Random(802))) for a,b in zip(r['words'],cr['words']))
 save('C1-SOURCE-FIRST-'+reading+'.json',{'rows':c1,'original_C3_keys':[digest(z) for z in rks],'E1_null_hit_totals':c1dist,'real_key_on_control_hits':sum(control_observed),'raw_words_changed':edits,'old_unit_array_words_changed':oldchanges,'status':'DIAGNOSTIC_NOT_REQUALIFICATION'})
 # Complete E1-only native C2 receipts with the same frozen word tokenizer.
 gen=load('V5-C2-DATA.json')['generated'];c2={}
 for family,item in gen.items():
  rr=[]
  for i,line in enumerate(item['mechanism_receipt']['lines']):
   section=held[i%len(held)]['section'];rr.append({'id':family+':'+str(i),'section':section,'words':[tokenize(w,k,'training_whole_word') for w in line]})
  vv=[sum(indicators(z,rr,lex)) for z in rks];n=sum(len(r['words']) for r in rr);cut=sorted(vv)[949]/n
  c2[family]={'source_rows':rr,'slots':n,'C3_hit_totals':vv,'C3_p95_rate':cut,'real_held_rate_exceeds':sum(observed)/len(observed)>cut,'key_hashes':[digest(z) for z in rks]}
  print(reading,'C2',family,'complete',flush=True)
 save('C2-E1-'+reading+'.json',{'status':'DIAGNOSTIC_E1_ONLY','families':c2})
 summary={'reading':reading,'original_verdict_preserved':'PARTIAL','slots':len(events),'observed_hits':sum(observed),'original_C3_median_hits':statistics.median(totals(original)),'original_C3_p':tail(sum(observed),totals(original)),'groups':groups,'native_uncertain_slots':native,'key_induced_unknown_slots':caused,'sensitivity_not_operational_C3':{'seed':2719,'n':1000,'median_hits':statistics.median(x['total'] for x in sensitivity),'mean_hits':statistics.mean(x['total'] for x in sensitivity),'p':tail(sum(observed),[x['total'] for x in sensitivity])},'source_C1b':{'raw_words_changed':edits,'old_unit_array_words_changed':oldchanges,'control_C3_p95_rate':sorted(c1dist)[949]/len(events),'real_rate_exceeds':sum(observed)>sorted(c1dist)[949]},'C2_families_completed':list(c2),'rank_and_rule':'The original E1 rank is unchanged by any matched-control completion. StrictFAIL cannot be obtained by repairing C1 alone.'}
 save('TOKEN-RECEIPTS-'+reading+'.json',events);save('ORIGINAL-C3-DECOMPOSITION-'+reading+'.json',perkey);save('STRATIFIED-SENSITIVITY-'+reading+'.json',sensitivity);save('SUMMARY-'+reading+'.json',summary)
 print(json.dumps(summary),flush=True);return summary

if __name__=='__main__':
 started=time.time();out={r:audit_reading(r) for r in ('H','F')};save('RESULTS.json',{'status':'DIAGNOSIS_COMPLETE_NO_QUALIFICATION_CHANGE','readings':out,'seconds':time.time()-started,'specification_changed':False,'attempts_rescored_for_admission':False})
