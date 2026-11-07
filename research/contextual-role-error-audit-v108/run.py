from pathlib import Path
import json,hashlib,collections,math,time
P=Path(__file__).resolve().parent;OLD=P.parent/'contextual-role-recovery-v107'
H=Path(r'C:/Users/lewis/.codex/visualizations/2026/10/21/01a160c2-56f0-7303-b3bf-ed8594c6ec40');SOURCE=H/'voynich-grammar-v36/sources'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def features(r):
 c=r['context'];return [str(i)+':'+t for i,t in enumerate(c)]+['L:'+c[0]+'|'+c[1],'R:'+c[2]+'|'+c[3]]
def counts(values):return dict(collections.Counter(values))
def metric(rows,field):
 rows=[r for r in rows if r.get(field) is not None];gold=counts(r['gold'] for r in rows);correct=counts(r['gold'] for r in rows if r[field]);return {'n':len(rows),'correct':sum(correct.values()),'accuracy':sum(correct.values())/len(rows) if rows else None,'by_role':{k:{'n':v,'correct':correct.get(k,0),'recall':correct.get(k,0)/v} for k,v in gold.items()},'balanced_recall':sum(correct.get(k,0)/v for k,v in gold.items())/len(gold) if gold else None}
def groupmetrics(rows,field,group):return {str(v):metric([r for r in rows if r[group]==v],field) for v in sorted({r[group] for r in rows},key=str)}
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for n,h in f['prior'].items():assert sha(OLD/n)==h,n
 for n,h in f['sources'].items():assert sha(SOURCE/n)==h,n

def run():
 verify();assert not (P/'SUMMARY.json').exists();rows=load(OLD/'BLIND-INPUT.json');key=load(OLD/'ANSWER-KEY.json');result=load(OLD/'RESULTS.json');sup=load(OLD/'SUPERVISED-DIAGNOSTIC.json');assign=load(OLD/'ASSIGNMENTS.json');cfg=load(OLD/'PROTOCOL.json')['historical'];rowmap={r['id']:r for r in rows}
 needed={(r['id'].split(':')[0],r['sentence_id']) for r in rows};sentences={}
 for part in ['train','dev','test']:
  for block in (SOURCE/f'la_proiel-ud-{part}.conllu').read_text(encoding='utf8').strip().split('\n\n'):
   lines=block.splitlines();sid=next((l.split(' = ',1)[1] for l in lines if l.startswith('# sent_id = ')),None)
   if (part,sid) not in needed:continue
   ts=[l.split('\t') for l in lines if l and not l.startswith('#') and l.split('\t')[0].isdigit()];assert all(len(t)==10 for t in ts)
   sentences[(part,sid)]={'tokens':ts,'source':next(l.split(' = ',1)[1] for l in lines if l.startswith('# source = ')),'text':next((l.split(' = ',1)[1] for l in lines if l.startswith('# text = ')),' '.join(t[1] for t in ts))}
 assert set(sentences)==needed
 fixed={r['stratum']:r for r in result['results']};supervised={r['stratum']:r for r in sup};fits={r['stratum']:r for r in assign};allrows=[];panels=[];examples=[];collisions=[]
 for st in sorted(fixed):
  rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];roles=cfg['targets'][rs[0]['target']];binarytr=[r for r in tr if key[r['id']]['upos'] in roles];vocab={f for r in tr for f in features(r)};nvocab={f for r in binarytr for f in features(r)};freq=collections.Counter(f for r in binarytr for f in features(r));trainsets=[(r,set(features(r))) for r in binarytr]
  cps={r['id']:r for r in fixed[st]['actual']['predictions']};nps={r['id']:r for r in supervised[st]['predictions']};aa={r['id']:r for r in fits[st]['actual']['assignments']};clusterprofiles=[]
  for cluster in sorted({a['cluster'] for a in aa.values()}):
   rr=[r for r in rs if r['split']=='train' and aa[r['id']]['cluster']==cluster];fc=collections.Counter(f for r in rr for f in features(r));clusterprofiles.append({'cluster':cluster,'train_n':len(rr),'train_gold':counts(key[r['id']]['upos'] for r in rr),'mapped_label':fixed[st]['actual']['mapping'].get(str(cluster)),'test_gold':counts(key[r['id']]['upos'] for r in rs if r['split']=='test' and aa[r['id']]['cluster']==cluster),'most_common_features':fc.most_common(12)})
  panelrows=[]
  for r in rs:
   part,sid,tid=r['id'].split(':');s=sentences[(part,sid)];ts=s['tokens'];idx=next(i for i,t in enumerate(ts) if t[0]==tid);t=ts[idx];assert t[1].lower()==r['target'] and t[3]==key[r['id']]['upos'];headid=t[6];hi=next((i for i,v in enumerate(ts) if v[0]==headid),None);head=ts[hi] if hi is not None else None;dist=hi-idx if hi is not None else None
   def at(j):
    if not 0<=j<len(ts):return '#edge'
    step=1 if j>idx else -1
    return '#barrier' if any(not any(c.isalnum() for c in ts[k][1]) for k in range(idx+step,j+step,step)) else ts[j][1].lower()
   assert r['context']==[at(j) for j in [idx-2,idx-1,idx+1,idx+2]]
   ff=features(r);ns=sum(f in nvocab for f in ff);cs=sum(f in vocab for f in ff);known_words=[c for c in r['context'] if not c.startswith('#')];real_seen=sum((str(i)+':'+c) in nvocab for i,c in enumerate(r['context']) if not c.startswith('#'))
   visible=dist is not None and 0<abs(dist)<=2 and at(hi) not in ['#barrier','#edge'];pred=cps.get(r['id']);nb=nps.get(r['id']);gold=key[r['id']]['upos'];shared=[]
   if r['split']=='test' and gold in roles:
    fset=set(ff);best_by_role={role:max((len(fset&f) for z,f in trainsets if key[z['id']]['upos']==role),default=None) for role in roles};same=best_by_role[gold];other=best_by_role[next(z for z in roles if z!=gold)];near='same_role_stronger' if same>other else 'other_role_stronger' if same<other else 'tied';top=max(best_by_role.values());nearrows=[z for z,f in trainsets if len(fset&f)==top];nearrows=sorted(nearrows,key=lambda z:hashlib.sha256(z['id'].encode()).hexdigest())[:3];shared=[{'id':z['id'],'gold':key[z['id']]['upos'],'context':z['context'],'overlap':len(fset&set(features(z)))} for z in nearrows]
   else:best_by_role={};near=None
   o={'id':r['id'],'stratum':st,'previous_status':fixed[st]['status'],'split':r['split'],'block':r['page'],'reference':r['source_ref'],'gold':gold,'in_binary_task':gold in roles,'source_text':s['text'],'source_tokens':[v[1] for v in ts],'target_token_id':tid,'target_index':idx,'context':r['context'],'cluster':aa[r['id']]['cluster'],'cluster_prediction':pred['prediction'] if pred else None,'cluster_correct':pred['prediction']==gold if pred else None,'supervised_prediction':nb['prediction'] if nb else None,'supervised_correct':nb['prediction']==gold if nb else None,'cluster_known_features':cs,'supervised_known_features':ns,'supervised_coverage_bin':'0-1' if ns<=1 else '2-3' if ns<=3 else '4-6','known_unigram_features':sum(f in nvocab for f in ff[:4]),'known_pair_features':sum(f in nvocab for f in ff[4:]),'real_neighbor_n':len(known_words),'real_neighbors_seen':real_seen,'edge_present':'#edge' in r['context'],'barrier_present':'#barrier' in r['context'],'head_token_id':headid,'head_surface':head[1] if head else None,'head_upos':head[3] if head else None,'target_deprel':t[7],'head_signed_distance':dist,'head_visible_in_window':visible,'head_missing_or_root':hi is None,'target_features':t[5],'head_features':head[5] if head else None,'nearest_overlap_by_gold_role':best_by_role,'nearest_role_comparison':near,'nearest_training_examples':shared};allrows.append(o);panelrows.append(o)
  test=[r for r in panelrows if r['split']=='test' and r['in_binary_task']];fullcontext=collections.defaultdict(list)
  for r in panelrows:
   if r['in_binary_task']:fullcontext[tuple(r['context'])].append(r)
  mixed=[(c,rr) for c,rr in fullcontext.items() if len({r['gold'] for r in rr})>1]
  for c,rr in mixed:collisions.append({'stratum':st,'context':list(c),'gold_counts':counts(r['gold'] for r in rr),'ids':[r['id'] for r in rr]})
  collision_n=sum(len(rr) for c,rr in mixed);insample=sum(max(collections.Counter(r['gold'] for r in rr).values()) for rr in fullcontext.values())/sum(len(rr) for rr in fullcontext.values())
  summary={'stratum':st,'previous_status':fixed[st]['status'],'n':len(panelrows),'test_binary_n':len(test),'cluster':metric(test,'cluster_correct'),'supervised':metric(test,'supervised_correct'),'cluster_profiles':clusterprofiles,'binary_mapping_collapsed':len(set(fixed[st]['actual']['mapping'].values()))<2,'test_zero_cluster_features':sum(r['cluster_known_features']==0 for r in test),'test_zero_supervised_features':sum(r['supervised_known_features']==0 for r in test),'unseen_supervised_feature_fraction':sum(6-r['supervised_known_features'] for r in test)/(6*len(test)),'unseen_pair_feature_fraction':sum(2-r['known_pair_features'] for r in test)/(2*len(test)),'real_neighbor_unseen_fraction':1-sum(r['real_neighbors_seen'] for r in test)/max(1,sum(r['real_neighbor_n'] for r in test)),'supervised_by_coverage':groupmetrics(test,'supervised_correct','supervised_coverage_bin'),'supervised_by_head_visibility':groupmetrics(test,'supervised_correct','head_visible_in_window'),'cluster_by_head_visibility':groupmetrics(test,'cluster_correct','head_visible_in_window'),'supervised_by_nearest_role':groupmetrics(test,'supervised_correct','nearest_role_comparison'),'supervised_by_edge':groupmetrics(test,'supervised_correct','edge_present'),'head_visibility_by_role':{role:{'n':sum(r['gold']==role for r in test),'visible':sum(r['gold']==role and r['head_visible_in_window'] for r in test),'root_or_missing':sum(r['gold']==role and r['head_missing_or_root'] for r in test)} for role in roles},'identical_context_mixed_groups':len(mixed),'identical_context_mixed_occurrences':collision_n,'in_sample_context_majority_accuracy_not_predictive_bound':insample}
  # Role-conditioned coverage/head tables preserve imbalance within the descriptive bins.
  summary['role_conditioned']={role:{'coverage':groupmetrics([r for r in test if r['gold']==role],'supervised_correct','supervised_coverage_bin'),'head_visibility':groupmetrics([r for r in test if r['gold']==role],'supervised_correct','head_visible_in_window')} for role in roles}
  panels.append(summary)
  for role in roles:
   for correct in [False,True]:
    for visible in [False,True]:
     rr=[r for r in test if r['gold']==role and r['supervised_correct']==correct and r['head_visible_in_window']==visible];rr.sort(key=lambda r:hashlib.sha256(r['id'].encode()).hexdigest());examples.extend(rr[:2])
 with (P/'OCCURRENCE-AUDIT.jsonl').open('x',encoding='utf8') as f:
  for r in allrows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 synth=[json.loads(l) for l in (OLD/'synthetic-trials.jsonl').read_text().splitlines()];sd=[]
 for regime in sorted({r['regime'] for r in synth}):
  rr=[r for r in synth if r['regime']==regime];sd.append({'regime':regime,'n':len(rr),'selected_k':counts(str(r['selected_k']) for r in rr),'overpartitioned':sum(r['selected_k'] is not None and r['selected_k']>r['true_k'] for r in rr),'underpartitioned':sum(r['selected_k'] is not None and r['selected_k']<r['true_k'] for r in rr),'abstained':sum(r['selected_k'] is None for r in rr)})
 dump('SUMMARY.json',{'scope':'Retrospective descriptive diagnosis only; no new predictive scores or manuscript inference.','all_occurrences':len(allrows),'binary_test_occurrences':sum(r['split']=='test' and r['in_binary_task'] for r in allrows),'panels':panels,'synthetic_error_directions':sd});dump('EXAMPLES.json',examples);dump('CONTEXT-COLLISIONS.json',collisions)
 lines=[]
 for r in examples:
  toks=r['source_tokens'].copy();toks[r['target_index']]='['+toks[r['target_index']]+']';lines.extend([r['stratum']+' '+r['id']+' '+r['reference'],f"Gold {r['gold']}; cluster {r['cluster_prediction']}; supervised {r['supervised_prediction']}; correct {r['supervised_correct']}; head {r['head_surface']} ({r['head_upos']}) at {r['head_signed_distance']}; visible {r['head_visible_in_window']}",'Context: '+' / '.join(r['context']),'Sentence: '+' '.join(toks),'Nearest training: '+json.dumps(r['nearest_training_examples'],ensure_ascii=False),''])
 (P/'EXAMPLES.txt').write_text('\n'.join(lines),encoding='utf8');verify();print(json.dumps({'occurrences':len(allrows),'examples':len(examples),'panels':[{k:r[k] for k in ['stratum','binary_mapping_collapsed','test_zero_supervised_features','unseen_supervised_feature_fraction','unseen_pair_feature_fraction','real_neighbor_unseen_fraction']} for r in panels]},indent=2))
if __name__=='__main__':
 import sys
 if sys.argv[1]=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'prior':load(OLD/'SHA256SUMS.json'),'sources':load(OLD/'FREEZE.json')['external'] and {Path(n).name:h for n,h in load(OLD/'FREEZE.json')['external'].items()}});print('Audit code, plan and all prior artifacts sealed; no new counts computed.')
 else:run()
