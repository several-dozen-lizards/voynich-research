"""Apply the unchanged registered matcher to the sealed known-script target."""
from pathlib import Path
import sys,json,gzip,collections,statistics
T=Path(__file__).resolve().parent;R=T.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(R))
import common as core
from matcher import fit

def save(name,value):
 (T/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

def main():
 assert (R/'TARGET_MANIFEST.json').exists() and not (T/'RESULT.json').exists() and not (T/'OBSERVED.json').exists()
 manifest=json.loads((R/'TARGET_MANIFEST.json').read_text(encoding='utf8'))
 assert all(core.sha(R/p)==h for p,h in manifest['files'].items())
 assert manifest['native_tracks']=='CLOSED_UNCONDITIONALLY' and manifest['null_banks']==core.SEEDS
 data=json.loads((T/'TARGET_INPUT.json').read_text(encoding='utf8'));items=core.load('ITEMS.json');labels=[x['alternatives'] for x in data['items']];lexicon=core.names();books=core.codebooks()
 observed=fit(items,labels,lexicon,books);save('OBSERVED.json',observed)
 cells=[]
 for language in core.LANGS:
  for family in core.FAMILIES:
   models=[m for m in observed['models'] if m['language']==language and m['family']==family];score=max(m['score'] for m in models)
   cells.append(dict(language=language,family=family,score=score,denominator=12,fraction=score/12,best_tables=[m['table'] for m in models if m['score']==score] if family=='naibbe' else None))
 save('LANGUAGE_FAMILY_SCORES.json',cells);banks=[];shuffles=core.load('SHUFFLES.json')
 for seed in core.SEEDS:
  scores=[]
  with gzip.open(T/f'NULLS_s{seed}.jsonl.gz','wt',encoding='utf8',newline='\n') as f:
   for index,assignment in enumerate(shuffles[str(seed)]['nulls']):
    result=fit(items,[labels[i] for i in assignment],lexicon,books);scores.append(result['score']);f.write(json.dumps(dict(index=index,assignment=assignment,**result),ensure_ascii=False,allow_nan=False)+'\n')
  exceed=sum(s>=observed['score'] for s in scores);banks.append(dict(seed=seed,null_draws=99,observed_maximum=observed['score'],null_min=min(scores),null_max=max(scores),null_mean=statistics.mean(scores),null_histogram=dict(sorted(collections.Counter(scores).items())),null_at_least_observed=exceed,p=(1+exceed)/100,null_invariant=min(scores)==max(scores)))
  print('TARGET BANK',seed,'observed',observed['score'],'null >= observed',exceed,'/99','p',(1+exceed)/100,flush=True)
 save('RESULT.json',dict(status='COMPLETE',target='Later Latin-script month annotations only',observed_maximum=observed['score'],denominator=12,fraction=observed['score']/12,selected=observed['selected'],all_best_models=[dict(language=m['language'],family=m['family'],table=m.get('table')) for m in observed['models'] if m['score']==observed['score']],language_family_scores=cells,null_banks=banks,bank_policy='All five frozen banks reported separately; no pooling/selection',native_tracks_scored=False,Phase8_status='FAIL_PRESERVED',original_receipt_defect='PRESERVED',target_manifest_sha256=core.sha(R/'TARGET_MANIFEST.json')))
 save('TARGET_RUN_STATE.json',dict(status='COMPLETE_KNOWN_SCRIPT_TARGET',annotation_target_fit=True,native_tracks='CLOSED',native_tracks_scored=False,Phase8_FAIL_preserved=True,original_receipt_defect_preserved=True))
 print('COMPLETE known-script target only; native tracks CLOSED.')
if __name__=='__main__':main()
