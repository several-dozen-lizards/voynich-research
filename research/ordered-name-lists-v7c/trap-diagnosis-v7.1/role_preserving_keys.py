"""Candidate supplementary null, INACTIVE for admission.
Groups derive only from declared KEY rule-condition structure, never from names,
held-out inputs, decoded values or scored outcomes. Original C3 is untouched.
"""
import copy,json,random
from collections import defaultdict,Counter

def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def role_signature(key,unit):
 return tuple(sorted(canonical(r['when']) for r in key['rules'] if r['unit']==unit))

def structure(key):
 base=defaultdict(list);context=defaultdict(list)
 for u in key['units']:base[role_signature(key,u)].append(u)
 for i,r in enumerate(key['rules']):context[(role_signature(key,r['unit']),canonical(r['when']))].append(i)
 return list(base.values()),list(context.values())

def random_role_key(key,rng):
 out=copy.deepcopy(key);base_groups,rule_groups=structure(key)
 for uu in base_groups:
  vv=[key['map'][u] for u in uu];rng.shuffle(vv)
  for u,v in zip(uu,vv):out['map'][u]=v
 for rr in rule_groups:
  vv=[key['rules'][i]['value'] for i in rr];rng.shuffle(vv)
  for i,v in zip(rr,vv):out['rules'][i]['value']=v
 return out

def invariants(original,draw):
 if original['units']!=draw['units'] or original['value_inventory']!=draw['value_inventory'] or original['condition_inventory']!=draw['condition_inventory']:return False
 if len(original['rules'])!=len(draw['rules']):return False
 for a,b in zip(original['rules'],draw['rules']):
  if {k:v for k,v in a.items() if k!='value'}!={k:v for k,v in b.items() if k!='value'}:return False
 groups,rules=structure(original)
 return all(Counter(original['map'][u] for u in g)==Counter(draw['map'][u] for u in g) for g in groups) and all(Counter(original['rules'][i]['value'] for i in g)==Counter(draw['rules'][i]['value'] for i in g) for g in rules)
