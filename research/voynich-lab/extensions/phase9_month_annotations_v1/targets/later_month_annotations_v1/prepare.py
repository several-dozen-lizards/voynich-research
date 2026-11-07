"""Seal the authorized known-script target manifest before optimization."""
from pathlib import Path
import sys,json,hashlib,datetime
T=Path(__file__).resolve().parent;R=T.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(R))
import common as core

def save(name,value):
 (T/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

def main():
 assert not (R/'TARGET_MANIFEST.json').exists() and not (T/'OBSERVED.json').exists()
 reg=core.load('REGISTRATION.json');drift=[p for p,h in reg['files'].items() if core.sha(R/p)!=h]
 assert drift==['RUN_STATE.json'],drift
 assert core.sha(R/'RUN_STATE.registered_snapshot.json')==reg['files']['RUN_STATE.json']
 defect=core.load('RECEIPT_DEVIATION.json');assert core.sha(R/'RUN_STATE.json')==defect['current_state_sha256']
 qualification=core.load('QUALIFICATION.json');audit=core.load('INDEPENDENT_AUDIT.json');completion=core.load('COMPLETION_RECEIPT.json')
 assert qualification['status']==audit['gate_recomputed']==completion['qualification']=='PASS'
 assert len(qualification['cells'])==32 and all(c['cell_pass'] for c in qualification['cells'])
 assert core.sha(R/'OUTPUT_HASHES.json')==completion['output_manifest_sha256']
 assert core.sha(R/'RESULT_HASHES.json')==completion['result_manifest_sha256']
 assert all(core.sha(R/p)==h for p,h in core.load('OUTPUT_HASHES.json').items())
 old=core.load('PRESERVATION_BEFORE.json');assert all(core.sha(Path(p))==h for p,h in old.items())
 p8=R.parent/'phase8_alignment_v1';assert json.loads((p8/'QUALIFICATION.json').read_text(encoding='utf8'))['status']=='FAIL'
 assert core.load('RUN_STATE.json')['native_gate']=='CLOSED'
 previous={str(p.relative_to(R)):core.sha(p) for p in R.rglob('*') if p.is_file() and not p.is_relative_to(T)}
 save('PREEXISTING_FILES.json',previous)
 annotations=core.load('ANNOTATIONS.json');items=core.load('ITEMS.json')
 assert len(annotations)==len(items)==12
 for annotation,item in zip(annotations,items):
  assert annotation['script_layer']=='LATER_LATIN_SCRIPT_ANNOTATION'
  assert all(annotation[k]==item[k] for k in ['item_id','folio','section','month_number'])
 target=[dict(**item,source_reading=a['annotation_source_reading'],alternatives=core.alternatives(a['annotation_source_reading'])) for item,a in zip(items,annotations)]
 save('TARGET_INPUT.json',dict(script_layer='LATER_LATIN_SCRIPT_ANNOTATION',source='Original frozen ANNOTATIONS.json; no new transcription or correction',items=target))
 input_files={str(p.relative_to(R)):core.sha(p) for p in T.iterdir() if p.is_file()}
 for name in ['REGISTRATION.json','QUALIFICATION.json','INDEPENDENT_AUDIT.json','COMPLETION_RECEIPT.json','RECEIPT_DEVIATION.json','RUN_STATE.registered_snapshot.json','RUN_STATE.json','PERIOD_NAMES.json','NORMALIZED_NAMES.json','ANNOTATIONS.json','ITEMS.json','SHUFFLES.json','common.py','matcher.py','author/naibbe_tables.csv']:
  input_files[name]=core.sha(R/name)
 manifest=dict(status='SEALED_BEFORE_TARGET_OPTIMIZATION',date='2026-10-27',sealed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='User explicitly requested the later month annotation target test after calibration, under the frozen rules, with the target manifest sealed first.',target='Twelve later Latin-script zodiac month annotations only',native_tracks='CLOSED_UNCONDITIONALLY',calibration_status='PASS_32_OF_32',receipt_defect='STRICT_FULL_MANIFEST_FAIL_MUTABLE_RUN_STATE_ONLY_PRESERVED',changes_to_rules_or_names=False,observed_fit='One deterministic fit of every original language/family/submodel',null_banks=core.SEEDS,null_permutations_per_bank=99,permutation_source='Original frozen SHUFFLES.json; no new draws',bank_reporting='Report all five separately; no selected seed, pooled p-value, minimum-p rule or new decision gate',maximum='Maximum full-item exact-match count over all 32 frozen language/family/submodels; denominator 12',family_table='All 4 languages x 3 families; Naibbe family score maximizes over all 6 published fixed tables, with every table score retained',files=input_files)
 (R/'TARGET_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
 assert all(core.sha(R/p)==h for p,h in input_files.items())
 print('SEALED target manifest; no target optimization performed. All five frozen banks retained; native tracks CLOSED.')
if __name__=='__main__':main()
