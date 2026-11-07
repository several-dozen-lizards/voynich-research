from common import *
import shutil,ast,itertools
from matcher import substitution,decode_path

def main():
 assert not (R/'REGISTRATION.json').exists()
 prior=R.parent/'phase9_crib_v1';p8=R.parent/'phase8_alignment_v1'
 for name,h in json.loads((prior/'SOURCE_FREEZE.json').read_text(encoding='utf8'))['files'].items():assert sha(prior/name)==h
 shutil.copyfile(prior/'sources/primary_name_evidence.json',R/'sources/german_previously_collated.json');shutil.copyfile(prior/'sources/german_name_evidence.json',R/'sources/german_prior_calendar.json')
 rows=load('PERIOD_NAMES.json')
 for row in rows:
  if row['language']=='German' and row['month']==4:row['saved_source']='sources/german_previously_collated.json'
  if row['language']=='German' and row['month']==5:row['saved_source']='sources/german_prior_calendar.json'
 dump('PERIOD_NAMES.json',rows)
 lex=names();assert all(set(d)==set(range(3,13)) for d in lex.values()) and all(set(v)<=set(ALPHABET) and v for d in lex.values() for v in d.values())
 items=[{k:x[k] for k in ['item_id','folio','section','month_number']} for x in load('ANNOTATIONS.json')];assert len(items)==12
 dump('ITEMS.json',items);dump('NORMALIZED_NAMES.json',lex)
 assignments={}
 for seed in SEEDS:
  rng=random.Random(sid(seed,'null_assignments'));perms=[]
  while len(perms)<99:
   p=rng.sample(range(12),12)
   if p not in perms:perms.append(p)
  assignments[str(seed)]=dict(nulls=perms,negative_assignment=random.Random(sid(seed,'independent_assignment')).sample(range(12),12))
 dump('SHUFFLES.json',assignments);dump('JOBS.json',jobs())
 # Engineering only: no historical name or annotation fits.
 assert plain('JWK')=='iuuc' and alternatives('a(b)c(d)')==['abc','abcd','ac','acd']
 toy=[dict(month_number=1),dict(month_number=2)];assert substitution(toy,[['xy'],['xz']],{1:'ab',2:'ac'},'mono')['score']==2
 assert substitution(toy,[['xy'],['zz']],{1:'ab',2:'ac'},'mono')['score']==1
 assert substitution(toy,[['xyw'],['zvx']],{1:'aba',2:'bab'},'position')['score']==2
 assert substitution(toy,[['xyw'],['zvx']],{1:'aba',2:'bab'},'mono')['score']==0
 assert decode_path('ab','xy',{'a':'x','b':'y','ab':'xy'}) is not None
 words=['aba','bca','ddb','acd'];labels=[['xyx'],['yzx'],['uuy'],['xzu']];tiny=[dict(month_number=i) for i in range(4)];lexicon=dict(enumerate(words));brute=0
 for p in itertools.permutations('xyzu'):
  mapping=dict(zip('abcd',p));brute=max(brute,sum(''.join(mapping[c] for c in w)==ls[0] for w,ls in zip(words,labels)))
 assert substitution(tiny,labels,lexicon,'mono')['score']==brute
 books=codebooks();assert len(books)==6 and all(len(book)==552 for book in books.values())
 for table,book in books.items():assert decode_path('abc',book['ab']+book['c'],book) is not None
 for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
 dump('ENGINEERING.json',dict(status='PASS_TOY_CHECKS_ONLY',global_consistency=True,positional_difference=True,exact_mono_bruteforce_parity=True,finite_parenthesis_expansion=True,all_six_codebooks=True,historical_month_fits=0,annotation_fits=0,native_fits=0))
 old={str(p.resolve()):sha(p) for folder in [prior,p8] for p in folder.rglob('*') if p.is_file()};dump('PRESERVATION_BEFORE.json',old)
 dump('RUN_STATE.json',dict(status='REGISTERED_CALIBRATION_PENDING',annotation_gate='CLOSED',native_gate='CLOSED',native_tracks_scored=False,annotation_target_fits=False,Phase8_FAIL_preserved=True))
 files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
 dump('REGISTRATION.json',dict(status='FROZEN_BEFORE_CONTROL_GENERATION_AND_SCORING',date='2026-10-27',scope='Later Latin-script month annotations: calibration only; native tracks closed',files=files,language_month_cells=40,positive_datasets=160,negative_datasets=160,qualification_cells=32,null_permutations=99,annotation_target_fits=False,native_gate='CLOSED'))
 print('REGISTERED: forty cited cells; 320 calibration datasets; no name/annotation/native scoring yet.')
if __name__=='__main__':main()
