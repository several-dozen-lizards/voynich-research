from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;P=T.parent.parent;V=P/'system-types-v5';sys.path.insert(0,str(V))
from GENERATORS import generate
from core import group_inventory,group_rank_mapping,canonical_hash
from transfer_policy import FrozenCodebook,transfer_slots

def save(n,x):
 p=R/n;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def transformed(entries,family,seed):
 sizes=[len(e['tokens']) for e in entries];source=[w for e in entries for w in e['tokens']];known=[w if w is not None else '<SOURCE_UNKNOWN>' for w in source]
 g=generate(family,dict(abbreviation_probability=.5,symbol_probability=.5,context_variants=True,allow_source_wrap=False,source_start=0),seed,source=known,line_lengths=sizes)
 groups=[w for row in g['lines'] for w in row];assert len(groups)==len(source);assert g['source_wraps']==0
 masks=[]
 for i,w in enumerate(source):
  if w is None:groups[i]=None;masks.append(dict(slot=i,reason='source_unknown'))
  elif family=='G3' and w=='et' and i and source[i-1] is None:groups[i]=None;masks.append(dict(slot=i,reason='unknown_predecessor_context'))
 return dict(groups=groups,masks=masks,lengths=sizes,source_slots=len(source),source_wraps=g['source_wraps'],source=source,seed=seed)
def render(entries,groups,view):
 result=[];cursor=0
 for e in entries:
  n=len(e['tokens']);result.append(dict(unit=e['unit'],folio=e['unit'],tokens=view['tokens'][cursor:cursor+n],source_tokens=e['tokens'],source_unit_groups=groups[cursor:cursor+n],gold_slots=e['gold_slots'],gold_complexion=e['gold_complexion']));cursor+=n
 assert cursor==view['original_slots'];return result

def main(stage):
 seal=json.loads((R/'PRE-GENERATION-SEAL.json').read_text());assert all(sha(R/p)==h for p,h in seal['local'].items());assert all(sha(P/p)==h for p,h in seal['project'].items())
 source=json.loads((R/'SOURCE-ENTRIES.json').read_text())['entries'];cached=json.loads((T/'DISCOVERY-PARAGRAPHS.json').read_text());summary=[]
 for family,fi in [('G2',0),('G3',100)]:
  for scribe in ['1','2']:
   name=family+'-s'+scribe;seed=848200+fi+int(scribe);mapseed=848300+fi+int(scribe)
   entries=[e for e in source if e['arm']==('DISCOVERY' if stage=='discovery' else 'CONFIRMATION')]
   if stage=='discovery':
    target=[w for p in cached if p['scribe']==scribe for w in p['tokens'] if w];inventory=group_inventory(target,max_atoms=3);save(name+'/INVENTORY.json',inventory)
    g=transformed(entries,family,seed);fit=[w for w in g['groups'] if w is not None]
    try:receipt=group_rank_mapping(fit,inventory,seed=mapseed)
    except ValueError as err:
     save(name+'/MODEL.json',dict(status='NOT_ESTIMABLE_MAPPING_CAPACITY',error=str(err)));summary.append(dict(cell=name,status='NOT_ESTIMABLE_MAPPING_CAPACITY'));continue
    book=FrozenCodebook(tuple(sorted(receipt['mapping'].items())),'development',canonical_hash(fit),canonical_hash(inventory));view=transfer_slots(g['groups'],book)
    assert not view['new_unseen_slots'];save(name+'/MODEL.json',dict(status='FROZEN_DISCOVERY_ONLY',mapping=receipt,training_sha256=book.training_sha256,target_inventory_sha256=book.target_inventory_sha256,source_sha256=sha(R/'SOURCE-ENTRIES.json'),generator_seed=seed,mapping_seed=mapseed))
   else:
    freeze=json.loads((R/name/'CANDIDATE-FREEZE.json').read_text());
    if freeze['discovery']['selected'] is None:
     summary.append(dict(cell=name,status='NOT_RUN_NO_CANDIDATE'));continue
    model=json.loads((R/name/'MODEL.json').read_text());receipt=model['mapping'];book=FrozenCodebook(tuple(sorted(receipt['mapping'].items())),'development',model['training_sha256'],model['target_inventory_sha256'])
    g=transformed(entries,family,seed+10000);view=transfer_slots(g['groups'],book)
   save(name+'/'+stage.upper()+'-TRANSFORM.json',g);save(name+'/'+stage.upper()+'-TRANSFER.json',view);save(name+'/'+stage.upper()+'.json',render(entries,g['groups'],view))
   summary.append(dict(cell=name,status=view['primary_transfer_status'],entries=len(entries),source_slots=view['original_slots'],source_unknown_slots=view['baseline_unknown_slots'],new_unseen_slots=view['new_unseen_slots'],context_unknown_masks=sum(e['reason']=='unknown_predecessor_context' for e in g['masks'])))
 save(stage.upper()+'-GENERATION.json',summary);print(json.dumps(summary))
if __name__=='__main__':main(sys.argv[1])
