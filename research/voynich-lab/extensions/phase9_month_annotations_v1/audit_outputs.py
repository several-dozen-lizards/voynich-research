"""Post-outcome read-only validation of saved witnesses/arithmetic; no fits."""
from common import *
from collections import Counter

def main():
 reg=load('REGISTRATION.json');drift=[p for p,h in reg['files'].items() if sha(R/p)!=h]
 assert drift==['RUN_STATE.json'],drift
 assert sha(R/'RUN_STATE.registered_snapshot.json')==reg['files']['RUN_STATE.json']
 assert load('RECEIPT_DEVIATION.json')['changed_registered_files']==drift
 # Preserve the strict manifest failure. This post-outcome audit does not
 # modify the frozen verifier or accept any code/data/source drift.
 ready=load('DATA_READY.json');assert all(sha(R/p)==h for p,h in ready['files'].items());items=load('ITEMS.json');lexicons=names();books=codebooks();shuffles=load('SHUFFLES.json');results=load('RESULTS.json');qualification=load('QUALIFICATION.json');counts=Counter();pvalues={'positive':[],'negative':[]};transitions=Counter()
 assert len(results)==320 and all(r['status']=='COMPLETE' for r in results)
 def checkfit(fit,labels):
  assert len(fit['models'])==32
  identities={(m['family'],m['language'],m.get('table')) for m in fit['models']};assert len(identities)==32
  for model in fit['models']:
   assert model['score']==model['upper_bound']==len(model['matched'])
   assert len({x['item'] for x in model['matched']})==model['score']
   counts['model_witnesses']+=1
   if model['family']!='naibbe':
    mapping={(g,p):c for g,p,c in model['mapping']};assert len(mapping)==len(model['mapping'])
    reverse={(g,c):p for g,p,c in model['mapping']};assert len(reverse)==len(model['mapping'])
   for match in model['matched']:
    i=match['item'];assert match['label'] in labels[i];name=lexicons[model['language']][items[i]['month_number']]
    if model['family']=='naibbe':
     assert ''.join(u for u,g in match['path'])==name
     assert ''.join(g for u,g in match['path'])==match['label']
     assert all(books[model['table']][u]==g for u,g in match['path'])
    else:
     encoded=''.join(mapping['A' if model['family']=='mono' else position(j,len(name)),p] for j,p in enumerate(name));assert encoded==match['label']
   counts['matched_item_witnesses']+=model['score']
  chosen=min(fit['models'],key=lambda m:(-m['score'],FAMILIES.index(m['family']),LANGS.index(m['language']),TABLES.index(m['table']) if 'table' in m else -1))
  assert fit['selected']==chosen and fit['score']==max(m['score'] for m in fit['models'])
 for row in results:
  data=load('data/'+row['id']+'.json');labels=[alternatives(t) for t in data['labels']];observed=load('results/'+row['id']+'/OBSERVED.json');checkfit(observed,labels);assert row['score']==observed['score'];nullscores=[]
  with gzip.open(R/'results'/row['id']/'NULLS.jsonl.gz','rt',encoding='utf8') as f:
   for index,line in enumerate(f):
    value=json.loads(line);perm=shuffles[str(row['seed'])]['nulls'][index];assert value['index']==index and value['assignment']==perm;checkfit(value,[labels[i] for i in perm]);nullscores.append(value['score']);counts['null_records']+=1
  assert len(nullscores)==99;expected=(1+sum(s>=observed['score'] for s in nullscores))/100;assert row['p']==expected and row['rejection']==(expected<=.05);pvalues[row['kind']].append(expected)
  if row['kind']=='positive':
   family='naibbe' if row['encoder'].startswith('naibbe_') else row['encoder'];candidates=[m for m in observed['models'] if m['language']==row['language'] and m['family']==family];best=max(m['score'] for m in candidates);winners=[m for m in candidates if m['score']==best]
   if family=='naibbe':expected_recovery=best==12 and len(winners)==1 and winners[0]['table']==data['truth']['table']
   else:
    mapping={(g,p):c for g,p,c in winners[0]['mapping']};expected_recovery=best==12 and all(mapping.get((g,p))==c for g,p,c in data['truth']['observed_mapping'])
   assert row['recovery']['recovered']==expected_recovery;counts['positive_mapping_recovered']+=expected_recovery;counts['positive_recovery_and_rejection']+=expected_recovery and expected<=.05
   # Independently check saved encoding truth against names and full labels.
   full=[letters(t) for t in data['labels']]
   if family=='naibbe':
    assert len(data['truth']['naibbe_source_units'])==12
    for item,units,cipher in zip(items,data['truth']['naibbe_source_units'],full):assert ''.join(units)==lexicons[row['language']][item['month_number']] and ''.join(books[data['truth']['table']][u] for u in units)==cipher
   else:
    mapping={(g,p):c for g,p,c in data['truth']['observed_mapping']}
    for item,cipher in zip(items,full):
     name=lexicons[row['language']][item['month_number']];assert ''.join(mapping['A' if family=='mono' else position(j,len(name)),p] for j,p in enumerate(name))==cipher
  else:
   positive=load('data/'+row['id'].removesuffix('negative')+'positive.json');assert data['labels']==[positive['labels'][i] for i in shuffles[str(row['seed'])]['negative_assignment']];assert data['truth']==positive['truth'];counts['negative_rejections']+=row['rejection']
 for cell in qualification['cells']:
  pos=[r for r in results if r['language']==cell['language'] and r['encoder']==cell['encoder'] and r['kind']=='positive'];neg=[r for r in results if r['language']==cell['language'] and r['encoder']==cell['encoder'] and r['kind']=='negative'];assert len(pos)==len(neg)==5
  recovered=sum(r['recovery']['recovered'] for r in pos);positive=sum(r['recovery']['recovered'] and r['p']<=.05 for r in pos);negative=sum(r['p']<=.05 for r in neg);passed=positive>=4 and negative<=1
  assert (recovered,positive,negative,passed)==(cell['mapping_recovered'],cell['positive_recovery_and_rejection'],cell['negative_rejections'],cell['cell_pass'])
 assert qualification['status']==('PASS' if all(c['cell_pass'] for c in qualification['cells']) else 'FAIL')
 before=load('PRESERVATION_BEFORE.json');assert all(Path(p).is_file() and sha(Path(p))==h for p,h in before.items());state=load('RUN_STATE.json');assert state['native_gate']=='CLOSED' and not state['native_tracks_scored'] and not state['annotation_target_fits'];assert not (R/'targets').exists() and not (R/'TARGET_MANIFEST.json').exists()
 summary=dict(status='PASS_SAVED_WITNESSES_AND_ARITHMETIC_WITH_DOCUMENTED_RECEIPT_DEFECT',strict_full_manifest='FAIL_MUTABLE_RUN_STATE_ONLY',immutable_registered_inputs='PASS',registered_before_state_hash='PASS_RECONSTRUCTED_COPY',scope='No new fits, scoring runs or permutation draws; saved witnesses and sums only',counts=dict(counts),positive_p_range=[min(pvalues['positive']),max(pvalues['positive'])],negative_p_range=[min(pvalues['negative']),max(pvalues['negative'])],gate_recomputed=qualification['status'],preserved_prior_files=len(before),native_gate='CLOSED',annotation_target_fits=False,registration_sha256=sha(R/'REGISTRATION.json'),qualification_sha256=sha(R/'QUALIFICATION.json'))
 dump('INDEPENDENT_AUDIT.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
