from pathlib import Path
import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;P=T.parent.parent;OLD=T/'positive-control-1';sys.path.insert(0,str(P/'system-types-v5'))
from transfer_policy import FrozenCodebook,transfer_slots
sp=importlib.util.spec_from_file_location('old_positive_adapter',OLD/'generate_positive.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
for s in ['LATIN-PRE-DISCOVERY-SEAL.json','LATIN-PRE-CONFIRMATION-SEAL.json']:
 seal=json.loads((R/s).read_text());assert all(sha(Path(p))==h for p,h in seal['files'].items())
entries=[e for e in json.loads((OLD/'SOURCE-ENTRIES.json').read_text())['entries'] if e['arm']=='CONFIRMATION'];gold={e['unit']:e['gold_slots'] for e in json.loads((OLD/'GOLD-AUDIT.json').read_text())['entries']};results=[]
for family,fi in [('G2',0),('G3',100)]:
 for scribe in ['1','2']:
  name=family+'-s'+scribe;folder=R/'latin'/name;freeze=json.loads((folder/'CANDIDATE-FREEZE.json').read_text())
  if freeze['discovery']['candidate'] is None:results.append(dict(cell=name,status='NOT_RUN_NO_CANDIDATE'));continue
  model=json.loads((folder/'MODEL.json').read_text());receipt=model['mapping'];book=FrozenCodebook(tuple(sorted(receipt['mapping'].items())),'development',model['training_sha256'],model['target_inventory_sha256']);g=a.transformed(entries,family,848200+fi+int(scribe)+10000);view=transfer_slots(g['groups'],book);pp=a.render(entries,g['groups'],view)
  for p in pp:p['gold_slots_corrected']=gold[p['unit']]
  save(folder/'CONFIRMATION-TRANSFORM.json',g);save(folder/'CONFIRMATION-TRANSFER.json',view);save(folder/'CONFIRMATION.json',pp)
  results.append(dict(cell=name,status=view['primary_transfer_status'],paragraphs=len(pp),source_slots=view['original_slots'],native_unknown_slots=sum(w is None for e in entries for w in e['tokens']),masked_slots=view['baseline_unknown_slots'],new_unseen_slots=view['new_unseen_slots']))
save(R/'LATIN-CONFIRMATION-GENERATION.json',results);print(json.dumps(results))
