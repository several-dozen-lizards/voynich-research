"""Read-only witness and arithmetic audit; no new optimization."""
from pathlib import Path
import sys,json,gzip,collections
T=Path(__file__).resolve().parent;R=T.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(R))
import common as core

def load(name):return json.loads((T/name).read_text(encoding='utf8'))
def main():
 manifest=json.loads((R/'TARGET_MANIFEST.json').read_text(encoding='utf8'));assert all(core.sha(R/p)==h for p,h in manifest['files'].items())
 items=core.load('ITEMS.json');names=core.names();books=core.codebooks();labels=[x['alternatives'] for x in load('TARGET_INPUT.json')['items']];count=collections.Counter()
 def check(value,bundles):
  assert len(value['models'])==32 and len({(m['language'],m['family'],m.get('table')) for m in value['models']})==32
  for model in value['models']:
   assert model['score']==model['upper_bound']==len(model['matched'])
   assert len({x['item'] for x in model['matched']})==model['score'];count['model_witnesses']+=1
   if model['family']!='naibbe':
    mapping={(g,p):c for g,p,c in model['mapping']};assert len(mapping)==len(model['mapping']) and len({(g,c) for g,p,c in model['mapping']})==len(mapping)
   for match in model['matched']:
    i=match['item'];word=names[model['language']][items[i]['month_number']];assert match['label'] in bundles[i]
    if model['family']=='naibbe':assert ''.join(u for u,g in match['path'])==word and ''.join(g for u,g in match['path'])==match['label'] and all(books[model['table']][u]==g for u,g in match['path'])
    else:assert ''.join(mapping['A' if model['family']=='mono' else core.position(j,len(word)),p] for j,p in enumerate(word))==match['label']
    count['matched_item_witnesses']+=1
  selected=min(value['models'],key=lambda m:(-m['score'],core.FAMILIES.index(m['family']),core.LANGS.index(m['language']),core.TABLES.index(m['table']) if 'table' in m else -1))
  assert value['selected']==selected and value['score']==selected['score']
 observed=load('OBSERVED.json');check(observed,labels);result=load('RESULT.json');assert result['observed_maximum']==observed['score']
 for cell in result['language_family_scores']:assert cell['score']==max(m['score'] for m in observed['models'] if m['language']==cell['language'] and m['family']==cell['family'])
 for bank in result['null_banks']:
  scores=[]
  with gzip.open(T/f"NULLS_s{bank['seed']}.jsonl.gz",'rt',encoding='utf8') as f:
   for i,line in enumerate(f):
    value=json.loads(line);assignment=core.load('SHUFFLES.json')[str(bank['seed'])]['nulls'][i];assert value['index']==i and value['assignment']==assignment;check(value,[labels[j] for j in assignment]);scores.append(value['score']);count['null_records']+=1
  assert len(scores)==99 and bank['null_at_least_observed']==sum(s>=observed['score'] for s in scores)
  assert bank['p']==(1+bank['null_at_least_observed'])/100 and {str(k):v for k,v in sorted(collections.Counter(scores).items())}==bank['null_histogram']
 prior=load('PREEXISTING_FILES.json');assert all(core.sha(R/p)==h for p,h in prior.items())
 earlier=core.load('PRESERVATION_BEFORE.json');assert all(core.sha(Path(p))==h for p,h in earlier.items())
 assert core.load('RUN_STATE.json')['native_gate']=='CLOSED';p8=R.parent/'phase8_alignment_v1';assert json.loads((p8/'QUALIFICATION.json').read_text(encoding='utf8'))['status']=='FAIL'
 reg=core.load('REGISTRATION.json');assert [p for p,h in reg['files'].items() if core.sha(R/p)!=h]==['RUN_STATE.json']
 assert core.sha(R/'RUN_STATE.registered_snapshot.json')==reg['files']['RUN_STATE.json']
 output=dict(status='PASS_SAVED_TARGET_WITNESSES_ARITHMETIC_AND_PRESERVATION',new_fits_in_audit=0,counts=dict(count),preexisting_calibration_files_preserved=len(prior),earlier_files_preserved=len(earlier),changed_preexisting_files=0,native_tracks='CLOSED',Phase8_FAIL_preserved=True,strict_calibration_receipt_defect='PRESERVED_MUTABLE_RUN_STATE_ONLY',target_manifest_sha256=core.sha(R/'TARGET_MANIFEST.json'))
 (T/'AUDIT.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
