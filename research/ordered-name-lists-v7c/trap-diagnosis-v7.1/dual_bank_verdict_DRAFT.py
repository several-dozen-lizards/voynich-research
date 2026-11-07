"""INACTIVE proposed v7.2 combiner. No actual score is reclassified here."""

def combine(original,role):
 shared99=sorted(set(original['above_99'])&set(role['above_99']))
 shared998=sorted(set(original['above_998'])&set(role['above_998']))
 passed=original['verdict']=='PASS' and role['verdict']=='PASS' and len(shared99)>=2
 return {'status':'DRAFT_NOT_AUTHORIZED','verdict':'PASS' if passed else 'PARTIAL' if shared998 else 'FAIL','shared_above99':shared99,'shared_above998':shared998,'original_verdict':original['verdict'],'role_verdict':role['verdict'],'admission_active':False}
