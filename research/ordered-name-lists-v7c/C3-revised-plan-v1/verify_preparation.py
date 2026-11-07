"""Engineering and preservation checks only. Does not score or open payloads."""
from pathlib import Path
import json,hashlib,copy
from admission import require_scientific_release
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parent
checks=[]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(n,v):checks.append(dict(check=n,pass_check=bool(v)))
def verify_manifest(folder,name,external):
 m=read(folder/name)
 for x in m['files']:check('preserved '+str(folder.name)+'/'+x['path'],sha(folder/x['path'])==x['sha256'])
 for x in m.get(external,[]):check('preserved dependency '+x['path'],sha(folder/x['path'])==x['sha256'])
verify_manifest(B/'C1-source-freeze-v1','FREEZE.json','external_source_dependencies')
verify_manifest(B/'C2-open-v1','DELIVERY-FREEZE.json','none')
verify_manifest(B/'amendment-v7.3','DELIVERY-FREEZE.json','external_policy_outputs')
plan=read(B/'C3-preflight-v1/PLAN.json')
for name,x in plan['inputs'].items():check('preflight pinned '+name,sha(x['path'])==x['sha256'])
check('preflight 131 checks passed',read(B/'C3-preflight-v1/VERIFICATION.json')['status']=='PASS' and read(B/'C3-preflight-v1/VERIFICATION.json')['checks_run']==131)
s=read(P/'STATUS.json');R=P/'registration'
allowed=set(('f70v1','f71r','f71v','f72r1','f70v2','f72r2','f72r3','f72v3'))
pages=read(R/'PAGES.json');figures=read(R/'FIGURE-TASKS.json');labels=read(R/'LOCUS-TASKS.json')
check('exactly eight open panels',len(pages)==8 and {x['folio'] for x in pages}==allowed)
check('179 unique candidate figure locations',len(figures)==179 and len({x['figure_id'] for x in figures})==179)
check('178 unique source loci',len(labels)==178 and len({x['source_locus_id'] for x in labels})==178)
for x in pages:
 check('image hash agrees '+x['folio'],sha(R/x['image'])==x['sha256'] and sha(x['upstream_source'])==x['sha256'])
check('coordinate exception for Cancer retained',next(x for x in pages if x['folio']=='f72r3')['old_point_to_display']=='identity')
check('image framing explicitly unverified',all(x['frame_verified'] is False for x in pages))
check('figure tasks open only',all(x['folio'] in allowed for x in figures))
check('locus tasks open only',all(x['folio'] in allowed for x in labels))
check('all ownership and boxes unfilled',all(x['figure_bbox'] is None and x['physical_label_id'] is None and x['label_bbox'] is None and x['source_locus_id'] is None for x in figures) and all(x['physical_label_id'] is None and x['label_bbox'] is None and x['figure_id'] is None for x in labels))
check('179 candidate slots retained in each pass',all(len(read(R/n)['figure_decisions'])==179 for n in ('PASS-A-TEMPLATE.json','PASS-B-TEMPLATE.json')))
check('both passes explicitly unfilled and not independent',all(read(R/n)['status']=='UNFILLED_NOT_INDEPENDENT_REGISTRATION' and read(R/n)['reviewer'] is None and read(R/n)['independent_of_other_pass'] is None for n in ('PASS-A-TEMPLATE.json','PASS-B-TEMPLATE.json')))
check('missing Gemini label not invented',not any(x['source_locus_id']=='f72r2.S1.14' for x in labels))
check('Gemini S0 unknown K availability not inferred',all(x['K'] is None for x in labels if x['source_unit']=='f72r2.S0'))
check('Leo uncertainty retained',any(x['folio']=='f72v3' and x['uncertain_presence'] is not None for x in figures))
check('Pisces remains29',sum(x['folio']=='f70v2' for x in figures)==29)
check('Gemini remains30 includingS0',sum(x['folio']=='f72r2' for x in figures)==30 and sum(x['folio']=='f72r2' and x['band']=='extra-top' for x in figures)==5)
# Explicit field contract: no decoded words or historical target payloads in the registrar tasks.
figkeys={'figure_id','folio','band','v84_index','v84_head_hint','v84_label_hint','uncertain_presence','hint_status','figure_bbox','physical_label_id','label_bbox','source_locus_id','association_status','alternatives','reviewer','evidence'}
lockeys={'source_locus_id','folio','source_unit','H','K','physical_label_id','label_bbox','figure_id','reviewer','evidence','status'}
check('figure field whitelist',all(set(x)==figkeys for x in figures))
check('locus field whitelist',all(set(x)==lockeys for x in labels))
check('reading fields header flags only',all(set(x[r]).issubset({'present','readable','header_line','basis'}) for x in labels for r in ('H','K') if x[r] is not None))
check('source-only spatial guide fields',all(set(x)=={'source_unit','spatial_cues','warning'} for x in read(R/'HEADER-ORDER-GUIDE.json')))
source=read(P/'historical-sources/LAPIDARY-COLLATION-TEMPLATE.json')
check('360 unfilled degree worksheets, no source admission',len(source['rows'])==360 and len({(x['sign'],x['degree']) for x in source['rows']})==360 and all(x['native_name'] is None and x['degree_attestation'] is None for x in source['rows']) and source['status']=='UNFILLED_NOT_ADMITTED')
wrong=read(P/'historical-sources/WRONG-UNIT-COLLATION-TEMPLATE.json')
check('30 unfilled wrong-unit source positions',len(wrong['rows'])==30 and all(x['Greek_name'] is None for x in wrong['rows']))
for x in read(P/'historical-sources/NATIVE-ACQUISITION.json'):check('native acquisition '+x['file'],x['status']=='OK' and sha(P/'historical-sources'/x['file'])==x['sha256'])
check('no source admission, registration completion or scoring claimed',s['new_source_profiles_admitted']==0 and s['completed_registration_passes']==0 and s['C3_fits']==0 and s['C3_scientific_qualification']=='NOT_RUN' and s['scientific_admission'] is False)
check('six of ten looks preserved',s['C2_looks_used']==6 and s['C2_look_cap']==10)
check('unchanged arms and alpha',s['eligible_C_arms']==['C-FULL','C-STEM','C-MRK'] and s['alpha_each']=='1/1200')
check('vault closed and unauthorized',s['vault_open'] is False and s['vault_authorized'] is False)
# Even fabricated authorization cannot release the preparation-only entrypoint.
for attempt in ({},{'vault_authorized':True},{'scientific_admission':True,'qualification':'PASS'}):
 try:require_scientific_release(**attempt);blocked=False
 except RuntimeError:blocked=True
 check('release gate rejects '+str(attempt),blocked)
failed=[x for x in checks if not x['pass_check']]
out=dict(status='ENGINEERING_PREPARATION_CHECKS_PASS' if not failed else 'FAIL',checks_run=len(checks),failed=failed,checks=checks,scientific_qualification=False,vault_open=False)
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],checks_run=len(checks),failed=failed)))
raise SystemExit(1 if failed else 0)
