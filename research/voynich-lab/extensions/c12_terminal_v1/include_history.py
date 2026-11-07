"""Inventory and copy an older registered, generated but unscored grid."""
from common import *
import shutil
old=R.parent/'prior_work_v1/runs/additions';reg=json.loads((old/'registry.json').read_text());snap=json.loads((R/'INPUT_SNAPSHOT.json').read_text());historical=[]
for name in sorted({n.rsplit('_',1)[0] for n in reg}):
    meta=json.loads((old/'data'/name/'metadata.json').read_text())
    historical.append(dict(setting=name,mode='legacy_mixed_codebook',fraction=meta['fraction_requested'],sequence_length=meta['sequence_length'],slot_rigidity=meta['slot_rigidity'],aggressiveness=.65,old_reference=None,role='historical'))
    for version in ['clean','noise']:
        entry=reg[name+'_'+version];assert entry['split']==json.loads((I/'configs/page_split.json').read_text())
        src=LAB/entry['path'];dst=R/'data'/name/f'{version}.csv';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        snap.setdefault('comparison_source_hashes',{})[str(src.relative_to(LAB))]=sha(src)
    shutil.copyfile(old/'data'/name/'metadata.json',R/'data'/name/'metadata.json')
for name in ['registry.json','PARTIAL_DATA_FREEZE.json','REGISTRATION.json','C12_SELECTION.json']:
    shutil.copyfile(old/name,R/'reference'/('legacy_'+name))
    snap['reference_hashes'][str((R/'reference'/('legacy_'+name)).relative_to(R))]=sha(R/'reference'/('legacy_'+name))
dump(R/'HISTORICAL_SETTINGS.json',historical);dump(R/'INPUT_SNAPSHOT.json',snap)
common=(R/'common.py').read_text().replace('    return out\ndef tensor_fingerprint',"    return out+json.loads((R/'HISTORICAL_SETTINGS.json').read_text())\ndef tensor_fingerprint")
(R/'common.py').write_text(common,encoding='utf8')
gen=(R/'generate.py').read_text().replace("if s['role']!='comparison':continue","if s['role']=='terminal':continue")
(R/'generate.py').write_text(gen,encoding='utf8')
# Preserve the first engineering-only inventory; no metrics or model jobs exist.
(R/'DATA_READY.json').rename(R/'INITIAL_ENGINEERING_INVENTORY.json')
print('Included frozen historical settings',len(historical))
