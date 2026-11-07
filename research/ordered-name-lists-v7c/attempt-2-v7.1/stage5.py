"""Final C2 qualification through existing, hash-qualified v5 entrypoint."""
import sys,json,time,random,copy
from pathlib import Path
P=Path(__file__).parent;V5=P.parent.parent/'system-types-v5'
sys.path.insert(0,str(P/'vendor'));sys.path.insert(0,str(V5));sys.path.insert(0,str(P.parent/'HARNESS'));sys.path.insert(0,str(P))
from run_attempt2 import read,save,bank,keys,loadold,observed
from verdict_v71 import verdict,clopper_upper
from harness import *
from source_contract import produce_from_development
from source_cut2 import load_cut2_development

def owner_check():
 q=json.loads((V5/'source-cut-2/QUALIFICATION-PLAN-v2.json').read_text())
 def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 for name,digest0 in q['owners'].items():
  if h(V5/name)!=digest0:raise RuntimeError('qualified owner drift '+name)
 return {'qualified_plan_sha256':h(V5/'source-cut-2/QUALIFICATION-PLAN-v2.json'),'owners':q['owners']}

def generate():
 provenance=owner_check();corpus=load_cut2_development('Latin');inventory=json.loads((V5/'EVA-GROUP-INVENTORIES.json').read_text())['A-1-H']
 data=loadold('KNOWN-CIPHER-DATA.json');geometry=[len(r['words']) for r in data['held'][:40]]
 generated={}
 for i,family in enumerate(('G1','G2','G3','G4','G5','G6')):
  result=produce_from_development(family,{},1720+i,corpus=corpus,inventory=inventory,line_lengths=None if family=='G5' else geometry,line_count=41)
  rows=[]
  for j,line in enumerate(result['lines']):
   words=[]
   for word in line:
    if not isinstance(word,str) or not word.isascii() or not word.isalpha() or word.lower()!=word:raise RuntimeError('nonEVA generator word')
    words.append([('INIT_A' if at==0 and c=='a' else 'u'+c) for at,c in enumerate(word)])
   rows.append({'id':family+':'+str(j),'folio':'synthetic-'+family,'custody':'demonstrated_unbuilt','section':'herbal','class':'HERBAL','words':words})
  generated[family]={'rows':rows,'mechanism_receipt':result,'seed':1720+i}
 save('V5-C2-DATA.json',{'owner_qualification':provenance,'development_source_sha256':corpus.development_sha256,'inventory_sha256':digest(inventory),'family_params':{},'generated':generated,'scope':'engineering mechanisms, no claim of v5 survival or historical equivalence; G5 published implementation/native geometry/seed exclusion retained'})
 return generated

def loadcase(name):
 q=read(name+'-PROVISIONAL.json');data=loadold('KNOWN-CIPHER-DATA.json') if name in ('CLEAN','CORRUPT') else read(name+'-DATA.json')
 seed=q['seed'];k=q['key'];ks=keys(k,seed)
 real=read('banks/'+name+'-real.json')['scores'];controls={c:read('banks/'+name+'-'+c+'.json')['scores'] for c in ('C1-word','C1-glyph')}
 return q,data,k,ks,real,controls

def main():
 state=read('RUN-STATE.json')
 if state['phase']!='qualified-v5-C2-required':raise RuntimeError('stages1–4 must finish first')
 generated=read('V5-C2-DATA.json')['generated'] if (P/'V5-C2-DATA.json').exists() else generate()
 save('RUN-STATE.json',{'phase':'v5-C2-control-distributions','status':'RUNNING'})
 cleanq,data,k,ks,real,cleancontrols=loadcase('CLEAN')
 finalbanks={}
 for category in ('CLEAN','CORRUPT'):
  q,dd,kk,kks,rr,cc=loadcase(category);finalbanks[category]={}
  for family,item in generated.items():
   finalbanks[category]['C2:'+family]=bank(category+'-C2-'+family,kk,kks,dd['train'],item['rows'],dd['target'],dd['lexicons'])
 results={}
 for name in ('CLEAN','CORRUPT','NOISY-H','NOISY-F'):
  q,dd,kk,kks,rr,cc=loadcase(name);cc.update(finalbanks['CORRUPT' if name=='CORRUPT' else 'CLEAN'])
  res=verdict(kk,q['observed'],rr,cc);save(name+'-FINAL.json',res);results[name]=res
 proposals=read('NEGATIVE-PROPOSALS-PROVISIONAL.json');cc=cleancontrols|finalbanks['CLEAN'];finalneg=[]
 rng=random.Random(1711)
 for item in proposals:
  rk=random_key(k,rng)
  assert digest(rk)==item['key_sha256']
  z=verdict(rk,item['observed'],real,cc);finalneg.append({'index':item['index'],'key_sha256':item['key_sha256'],'result':z})
 save('NEGATIVE-PROPOSALS-FINAL.json',finalneg);tally=dict(Counter(x['result']['verdict'] for x in finalneg));n=len(finalneg);passed=tally.get('PASS',0);upper=clopper_upper(passed,n)
 # Required trap verdicts are reported from the preregistered actual manuscript training/held slices.
 # If necessary rank/coherence already fails, later C2 controls cannot turn it into PASS.
 trap={r:read('TRAP-'+r+'-PROVISIONAL.json')['result'] for r in ('H','F')}
 gates={'true_key':results['CLEAN']['verdict']=='PASS','noisy_H':results['NOISY-H']['verdict']=='PASS','noisy_F':results['NOISY-F']['verdict']=='PASS','negative_notPASS_at_least99pct':1-passed/n>=.99,'negative_CP_upper_at_most3pct':upper<=.03,'actual_trap_H_FAIL':trap['H']['verdict']=='FAIL','actual_trap_F_FAIL':trap['F']['verdict']=='FAIL','v5_C2_all6families':set(generated)==set(('G1','G2','G3','G4','G5','G6'))}
 result={'version':'v7.1','status':'QUALIFIED_ON_DECLARED_ENGINEERING_SCOPE' if all(gates.values()) else 'NOT_QUALIFIED','gates':gates,'clean':results['CLEAN'],'corrupt':results['CORRUPT'],'noisy_H':results['NOISY-H'],'noisy_F':results['NOISY-F'],'negative':{'n':n,'tally':tally,'PASS_rate':passed/n,'notPASS_rate':1-passed/n,'CP_one_sided95_upper':upper,'CP_two_sided95_upper_sensitivity':clopper_upper(passed,n,.975),'PARTIAL_reported_not_gated':True},'actual_traps':trap,'C2_scope':'G1–G6 one fixed default development-source realization per family; control distributions use1000C3keys each; no v5 claim/recovery or reserve body opened','limitations':['Known positive is same-work edited Latin and artificial lines, not independent historical decipherment validation','Noise follows measured nonzodiac character disagreement with substitution-only channel; boundary errors not represented','Trap C2 is provisional surrogate; if necessary coherence/rank fails no possible matched control completion can createPASS. Do not mislabel this as complete C2 trap evaluation.','v6 multi-token adapter/E2/E5 detailed qualification remains outside this initial batch; all B/C gates remain locked'],'attempt1_unchanged':True}
 save('QUALIFICATION.json',result);save('RUN-STATE.json',{'phase':'complete','status':result['status']});print(json.dumps({'status':result['status'],'gates':gates,'negative':result['negative'],'verdicts':{n:r['verdict'] for n,r in results.items()}}),flush=True)

if __name__=='__main__':main()
