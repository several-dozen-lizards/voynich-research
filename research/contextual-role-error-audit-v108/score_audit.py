from pathlib import Path
import json,collections,math,hashlib
P=Path(__file__).resolve().parent;OLD=P.parent/'contextual-role-recovery-v107'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in load(P/'SCORE-AUDIT-FREEZE.json').items():assert sha(P/n)==h,n
rows=load(OLD/'BLIND-INPUT.json');key=load(OLD/'ANSWER-KEY.json');saved=load(OLD/'SUPERVISED-DIAGNOSTIC.json');audit=[json.loads(l) for l in (P/'OCCURRENCE-AUDIT.jsonl').read_text(encoding='utf8').splitlines()];byid={r['id']:r for r in audit};out=[];details=[]
def feats(r):
 c=r['context'];return [str(i)+':'+t for i,t in enumerate(c)]+['L:'+c[0]+'|'+c[1],'R:'+c[2]+'|'+c[3]]
for panel in saved:
 st=panel['stratum'];roles=load(OLD/'PROTOCOL.json')['historical']['targets'][st.split('|')[1]];tr=[r for r in rows if r['stratum']==st and r['split']=='train' and key[r['id']]['upos'] in roles];cc=collections.defaultdict(collections.Counter);total=collections.Counter();vocab=set()
 for r in tr:
  y=key[r['id']]['upos'];ff=feats(r);cc[y].update(ff);total[y]+=len(ff);vocab.update(ff)
 labels=sorted(cc);small=min(labels,key=lambda y:(total[y],y));stats=collections.Counter();examples=[]
 for pred in panel['predictions']:
  r=byid[pred['id']];ff=feats(r);known=[f for f in ff if f in vocab];unseen=[f for f in ff if f not in vocab];gold=pred['gold'];other=next(y for y in labels if y!=gold)
  scores={y:sum(math.log((cc[y][f]+1)/(total[y]+len(vocab)+1)) for f in ff) for y in labels};reconstructed=max(labels,key=lambda y:scores[y]);assert reconstructed==pred['prediction']
  seenmargin=sum(math.log((cc[gold][f]+1)/(total[gold]+len(vocab)+1))-math.log((cc[other][f]+1)/(total[other]+len(vocab)+1)) for f in known)
  unseenmargin=len(unseen)*math.log((total[other]+len(vocab)+1)/(total[gold]+len(vocab)+1));assert abs(seenmargin+unseenmargin-(scores[gold]-scores[other]))<1e-10
  error=reconstructed!=gold;override=bool(error and known and seenmargin>0 and seenmargin+unseenmargin<0);zero=not known
  stats['n']+=1;stats['errors']+=error;stats['all_features_unseen']+=zero;stats['all_unseen_errors']+=zero and error;stats['unseen_terms_override_correct_seen_margin']+=override;stats['errors_with_one_or_more_unseen_features']+=error and bool(unseen)
  if zero:assert reconstructed==small
  d={'id':r['id'],'stratum':st,'gold':gold,'saved_prediction':reconstructed,'n_known':len(known),'n_unseen':len(unseen),'known_feature_gold_margin':seenmargin,'unseen_feature_gold_margin':unseenmargin,'unseen_terms_override_correct_seen_margin':override,'all_unseen_default_to_smaller_training_class':zero,'smaller_training_class':small};details.append(d)
 out.append({'stratum':st,'original_status':next(a['previous_status'] for a in audit if a['stratum']==st),'binary_training_occurrences':dict(collections.Counter(key[r['id']]['upos'] for r in tr)),'small_class':small,'vocabulary_size':len(vocab),'counts':dict(stats)})
(P/'SCORE-DECOMPOSITION.json').write_text(json.dumps({'scope':'Exact decomposition of SAVED supervised scores, not a modified classifier or new accuracy result. Unknown-feature handling and edge effects diagnosed after exposed results.','panels':out,'rows':details},indent=2),encoding='utf8')
edge=[]
for st in sorted({r['stratum'] for r in audit}):
 for cl in sorted({r['cluster'] for r in audit if r['stratum']==st}):
  rr=[r for r in audit if r['stratum']==st and r['split']=='train' and r['cluster']==cl];edge.append({'stratum':st,'cluster':cl,'train_n':len(rr),'first_two_positions':sum(r['target_index']<2 for r in rr),'last_two_positions':sum(len(r['source_tokens'])-1-r['target_index']<2 for r in rr),'immediate_left':dict(collections.Counter(r['context'][1] for r in rr).most_common(5)),'training_gold':dict(collections.Counter(r['gold'] for r in rr))})
(P/'CLUSTER-BOUNDARY-AUDIT.json').write_text(json.dumps(edge,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
