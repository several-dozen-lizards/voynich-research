"""Source integrity and invariant checks. No statistical fit or claim verdict."""
from pathlib import Path
import json,hashlib,re,unicodedata
P=Path(__file__).parent;B=P.parent;checks=[]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(name,value):checks.append(dict(check=name,pass_check=bool(value)))
scope=read(P/'SCOPE.json')
for path,digest in scope['inputs'].items():ck('prior freeze/budget unchanged '+path,sha(B/path)==digest)
for folder,manifest,ext in [('C1-source-freeze-v1','FREEZE.json','external_source_dependencies'),('C2-open-v1','DELIVERY-FREEZE.json','none'),('amendment-v7.3','DELIVERY-FREEZE.json','external_policy_outputs'),('C3-revised-plan-v1','DELIVERY-FREEZE.json','dependencies')]:
 d=B/folder;m=read(d/manifest)
 for x in m['files']:ck('preserved '+folder+'/'+x['path'],sha(d/x['path'])==x['sha256'])
 for x in m.get(ext,[]):ck('preserved dependency '+x['path'],sha(d/x['path'])==x['sha256'])
for acq in sorted(P.glob('ACQUISITION*.json')):
 for x in read(acq):
  if x['status']=='OK':ck('download intact '+x['file'],sha(P/'sources'/x['file'])==x['sha256'])
ck('failed apparatus PDF request retained',any(x['status']=='FAILED' for x in read(P/'ACQUISITION-3.json')))
ck('failed native Greek catalogue route retained',any(x['status']=='FAILED' for x in read(P/'ACQUISITION-6.json')))
# Native source references resolve; uncertainty is not converted into alternatives.
for name in ('ARIES-SPELLING-COLLATION.json','TAURUS-SPELLING-COLLATION.json'):
 data=read(P/name);rows=data['rows']
 ck(name+' thirty ordered degrees',[r['degree'] for r in rows]==list(range(1,31)))
 ck(name+' not final paleography',data['complete_native_paleographic_collation'] is False and data['independent_review'] is False)
 for r in rows:
  native=r['native'];ck(name+' source exists '+str(r['degree']),(P/native.get('image',native.get('native_image','MISSING'))).is_file())
  ck(name+' no scoring admission '+str(r['degree']),r['scientific_admission'] is False)
 ck(name+' uncertainty retained',len([r for r in rows if r['native']['uncertain']])==(6 if name.startswith('ARIES') else 8))
slot=read(P/'LAPIDARY-360-SLOT-AUDIT.json');rows=slot['slots']
ck('360 distinct sign-degree positions',len(rows)==360 and len({(r['sign'],r['degree']) for r in rows})==360)
ck('301 locator entries and59 unrepresented slots',slot['represented_locator_slots']==301 and slot['unrepresented_slots']==59)
expected={('Leo',d) for d in range(1,30)}|{('Aquarius',29),('Aquarius',30)}|{('Pisces',d) for d in range(1,29)}
actual={(r['sign'],r['degree']) for r in rows if r['locator_heading'] is None}
ck('missing positions exact, no sequence compaction',actual==expected)
ck('no claim names invented in slot audit',all(r['claim_name'] is None for r in rows))
source=read(P/'LAPIDARY-CONTENTS-INVENTORY.json')
ck('contents301 native checks not faked',len(source['rows'])==301 and all(r['native_verified'] is False for r in source['rows']))
g=read(P/'WRONG-UNIT-GREEK-COLLATION.json');greek=g['rows']
ck('thirty ordered Greek entries',[r['position'] for r in greek]==list(range(1,31)) and len({r['name'] for r in greek})==30)
ck('all thirty Greek edition readings visual checked',all(r['Hatzfeld1936_visual_checked'] for r in greek))
ck('edition-specific section continuation preserved',[r['section'] for r in greek]==['2.3.2']*26+['2.3.3']*4 and all(r['Hatzfeld_section']=='2.3.2' for r in greek))
ck('last four source names retained',[r['name'] for r in greek[-4:]]==['Εὐμάθης','Ἀριστοτέλης','Ἱππόμαχος','Μνησιθείδης'])
ck('Greek native edition begins eta-Melobios',greek[2]['name']=='Μηλόβιος')
ck('both pre1440 witness profiles complete and equal',len(g['witness_profiles'])==2 and all(x['names']==[r['name'] for r in greek] for x in g['witness_profiles']))
ck('Greek witness support not mislabeled direct image collation',all(x['evidence_type']=='EDITOR_REPORTED_WITNESS_PROFILE' and x['direct_manuscript_image_collation'] is False and x['scientific_admission'] is False for x in g['witness_profiles']))
ck('late spelling alternatives both excluded',len(g['late_apparatus_variants'])==2 and all(x['status']=='EXCLUDED_FROM_PRE1440_VARIANTS' for x in g['late_apparatus_variants']))
ck('apparatus abbreviation not silently expanded',g['late_apparatus_variants'][1]['variant']=='θεαγ.')
ck('derived ASCII not attested Latin variant',all(re.fullmatch('[a-z]+',r['ASCII_working_form']) and r['ASCII_status']=='DERIVED_ENGINEERING_FORM_NOT_ATTESTED_LATIN_SPELLING_NOT_ADOPTED_FOR_SCORING' for r in greek))
ck('rough breathing working transform traceable',greek[3]['ASCII_working_form']=='hippolochos' and greek[5]['ASCII_working_form']=='hieron')
blob=(P/'sources/xenophon-perseus.xml').read_bytes();gitsha=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
tree=read(P/'sources/greek-repo-tree.json');expectedsha=next(x['sha'] for x in tree if x['name'].endswith('grc2.xml'))
ck('Perseus bytes match observed Git blob',gitsha==expectedsha)
s=read(P/'STATUS.json')
ck('source supplement remains unadmitted',s['new_scoring_profiles_admitted']==0 and s['C3_fits']==0 and scope['new_C3_fits']==0)
ck('no new C2 look',s['C2_looks_used']==6 and s['C2_look_cap']==10 and scope['new_C2_looks']==0)
ck('vault closed',scope['vault_open'] is False and s['vault_open'] is False)
ck('60 native degree entries first pass, not all301 certified',s['Lapidary_native_degree_entries_first_pass']==60 and s['Greek_direct_manuscript_image_collation'] is False)
failed=[x for x in checks if not x['pass_check']]
out=dict(status='SOURCE_INTEGRITY_AND_PRESERVATION_PASS' if not failed else 'FAIL',checks_run=len(checks),failed=failed,checks=checks,scientific_qualification=False,source_admission=False,vault_open=False)
(P/'VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(status=out['status'],checks_run=len(checks),failed=failed)))
raise SystemExit(1 if failed else 0)
