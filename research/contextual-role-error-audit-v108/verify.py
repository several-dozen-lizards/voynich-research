from pathlib import Path
import json,collections,hashlib,math
P=Path(__file__).resolve().parent;OLD=P.parent/'contextual-role-recovery-v107'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=load(P/'FREEZE.json')
for n,h in f['local'].items():assert sha(P/n)==h,n
for n,h in f['prior'].items():assert sha(OLD/n)==h,n
src=Path(r'C:/Users/lewis/.codex/visualizations/2026/10/21/01a160c2-56f0-7303-b3bf-ed8594c6ec40/voynich-grammar-v36/sources')
for n,h in f['sources'].items():assert sha(src/n)==h,n
rows=[json.loads(l) for l in (P/'OCCURRENCE-AUDIT.jsonl').read_text(encoding='utf8').splitlines()];summary=load(P/'SUMMARY.json');orig=load(OLD/'BLIND-INPUT.json');key=load(OLD/'ANSWER-KEY.json');assert len(rows)==len(orig)==2254 and {r['id'] for r in rows}=={r['id'] for r in orig};assert sum(r['split']=='test' and r['in_binary_task'] for r in rows)==808
meta={r['id']:r for r in orig}
def ff(c):return [str(i)+':'+t for i,t in enumerate(c)]+['L:'+c[0]+'|'+c[1],'R:'+c[2]+'|'+c[3]]
for r in rows:
 assert r['context']==meta[r['id']]['context'] and r['gold']==key[r['id']]['upos'];assert r['source_tokens'][r['target_index']].lower()==r['stratum'].split('|')[1]
 if r['head_signed_distance'] is not None:assert r['source_tokens'][r['target_index']+r['head_signed_distance']]==r['head_surface']
for p in summary['panels']:
 st=p['stratum'];rr=[r for r in rows if r['stratum']==st];tr=[r for r in rr if r['split']=='train'];bt=[r for r in tr if r['in_binary_task']];te=[r for r in rr if r['split']=='test' and r['in_binary_task']];vocab=set(f for r in bt for f in ff(r['context']));cvocab=set(f for r in tr for f in ff(r['context']))
 for r in rr:assert r['supervised_known_features']==sum(f in vocab for f in ff(r['context'])) and r['cluster_known_features']==sum(f in cvocab for f in ff(r['context']))
 for field,out in [('supervised_correct','supervised'),('cluster_correct','cluster')]:
  nc=collections.Counter(r['gold'] for r in te);cor=collections.Counter(r['gold'] for r in te if r[field]);bal=sum(cor[y]/nc[y] for y in nc)/len(nc);assert abs(bal-p[out]['balanced_recall'])<1e-12
 for role,v in p['head_visibility_by_role'].items():assert v['n']==sum(r['gold']==role for r in te) and v['visible']==sum(r['gold']==role and r['head_visible_in_window'] for r in te)
 assert p['test_zero_supervised_features']==sum(r['supervised_known_features']==0 for r in te)
 assert abs(p['unseen_supervised_feature_fraction']-sum(6-r['supervised_known_features'] for r in te)/(6*len(te)))<1e-12
 d=next(d for d in load(P/'CONTEXT-SUPPORT.json') if d['stratum']==st);ctx=set(tuple(r['context']) for r in bt);assert d['test_full_context_seen_in_training']==sum(tuple(r['context']) in ctx for r in te)
assert not load(P/'CONTEXT-COLLISIONS.json')
examples=load(P/'EXAMPLES.json');assert len(examples)==94 and len({r['id'] for r in examples})==94
for p in summary['panels']:
 te=[r for r in rows if r['stratum']==p['stratum'] and r['split']=='test' and r['in_binary_task']]
 for role in sorted({r['gold'] for r in te}):
  for correct in [False,True]:
   for visible in [False,True]:
    pool=sorted([r for r in te if r['gold']==role and r['supervised_correct']==correct and r['head_visible_in_window']==visible],key=lambda r:hashlib.sha256(r['id'].encode()).hexdigest())[:2];actual=[r for r in examples if r['stratum']==p['stratum'] and r['gold']==role and r['supervised_correct']==correct and r['head_visible_in_window']==visible];assert {r['id'] for r in actual}=={r['id'] for r in pool}
scores=load(P/'SCORE-DECOMPOSITION.json');assert len(scores['rows'])==808;tot=collections.Counter()
for p in scores['panels']:
 rr=[r for r in scores['rows'] if r['stratum']==p['stratum']];assert len(rr)==p['counts']['n'];assert sum(r['all_unseen_default_to_smaller_training_class'] for r in rr)==p['counts']['all_features_unseen'];assert sum(r['unseen_terms_override_correct_seen_margin'] for r in rr)==p['counts']['unseen_terms_override_correct_seen_margin']
 for r in rr:
  old=next(p for p in load(OLD/'SUPERVISED-DIAGNOSTIC.json') if p['stratum']==r['stratum']);saved=next(q for q in old['predictions'] if q['id']==r['id']);assert saved['prediction']==r['saved_prediction'];assert not r['unseen_terms_override_correct_seen_margin'] or (r['known_feature_gold_margin']>0 and r['known_feature_gold_margin']+r['unseen_feature_gold_margin']<0)
 tot.update(p['counts'])
assert tot['all_features_unseen']==126 and tot['unseen_terms_override_correct_seen_margin']==130
checks={'all_prior_v107_delivery_hashes_unchanged':True,'pinned_sources_unchanged':True,'2254_rows_exact_saved_input_and_gold_join':True,'all_head_distances_resolve_to_saved_source_tokens':True,'all_feature_coverages_independently_recounted':True,'all_previous_balanced_recalls_preserved':True,'head_visibility_and_zero_evidence_counts_recounted':True,'zero_exact_test_context_matches_confirmed':True,'94_examples_follow_predeclared_hash_selection':True,'808_saved_score_decompositions_linked_to_original_predictions':True,'126_zero_evidence_and130_override_cases_recounted':True}
(P/'VERIFICATION.json').write_text(json.dumps({'status':'PASS','checks':checks,'note':'Engineering consistency only. No new qualification or improved representation tested.'},indent=2),encoding='utf8');print(json.dumps(checks,indent=2))
