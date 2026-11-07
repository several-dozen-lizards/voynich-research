from common import *

def constraints(name,label,family):
 if len(name)!=len(label):return None
 forward={};reverse={}
 for i,(p,c) in enumerate(zip(name,label)):
  group='A' if family=='mono' else position(i,len(name));a=(group,p);b=(group,c)
  if a in forward and forward[a]!=c or b in reverse and reverse[b]!=p:return None
  forward[a]=c;reverse[b]=p
 return forward,reverse

def substitution(items,labels,lexicon,family):
 options=[]
 for i,(item,variants) in enumerate(zip(items,labels)):
  name=lexicon[item['month_number']];choices=[]
  for label in variants:
   c=constraints(name,label,family)
   if c is not None:choices.append((i,label,c[0],c[1]))
  if choices:options.append(choices)
 # Exact finite branch-and-bound over compatible item/variant choices.
 options.sort(key=lambda v:(len(v),v[0][0]));best=[];bestmap={};nodes=0
 def visit(k,chosen,fwd,rev):
  nonlocal best,bestmap,nodes
  nodes+=1
  if len(chosen)+len(options)-k<=len(best):return
  if k==len(options):best=chosen.copy();bestmap=fwd.copy();return
  for i,label,extra,back in options[k]:
   if any(key in fwd and fwd[key]!=val for key,val in extra.items()):continue
   if any(key in rev and rev[key]!=val for key,val in back.items()):continue
   visit(k+1,chosen+[(i,label)],fwd|extra,rev|back)
  visit(k+1,chosen,fwd,rev)
 visit(0,[],{}, {})
 return dict(family=family,score=len(best),upper_bound=len(best),status='OPTIMAL_EXHAUSTIVE_BRANCH_AND_BOUND',nodes=nodes,matched=[dict(item=i,label=label) for i,label in best],mapping=[[g,p,c] for (g,p),c in sorted(bestmap.items())])

def decode_path(name,label,book):
 memo={}
 def visit(i,j):
  if (i,j) in memo:return memo[i,j]
  if i==len(name):return [] if j==len(label) else None
  for width in [1,2]:
   unit=name[i:i+width]
   if len(unit)!=width:continue
   glyph=book[unit]
   if label.startswith(glyph,j):
    tail=visit(i+width,j+len(glyph))
    if tail is not None:memo[i,j]=[[unit,glyph]]+tail;return memo[i,j]
  memo[i,j]=None;return None
 return visit(0,0)

def verbose(items,labels,lexicon,books):
 results=[]
 for table,book in books.items():
  matched=[]
  for i,(item,variants) in enumerate(zip(items,labels)):
   for label in variants:
    path=decode_path(lexicon[item['month_number']],label,book)
    if path is not None:matched.append(dict(item=i,label=label,path=path));break
  results.append(dict(family='naibbe',table=table,score=len(matched),upper_bound=len(matched),status='OPTIMAL_FINITE_CODEBOOK_AND_DYNAMIC_PROGRAM',matched=matched))
 return results

def fit(items,labels,allnames,books):
 results=[]
 for language in LANGS:
  lexicon=allnames[language]
  for family in ['mono','position']:results.append(dict(language=language,**substitution(items,labels,lexicon,family)))
  results.extend(dict(language=language,**r) for r in verbose(items,labels,lexicon,books))
 selected=min(results,key=lambda x:(-x['score'],FAMILIES.index(x['family']),LANGS.index(x['language']),TABLES.index(x['table']) if 'table' in x else -1))
 return dict(score=selected['score'],selected=selected,models=results)

def recovery(fits,job,truth):
 family='naibbe' if job['encoder'].startswith('naibbe_') else job['encoder']
 candidates=[r for r in fits['models'] if r['language']==job['language'] and r['family']==family]
 chosen=min(candidates,key=lambda r:(-r['score'],TABLES.index(r['table']) if 'table' in r else -1))
 if family=='naibbe':
  winners=[r['table'] for r in candidates if r['score']==chosen['score']]
  return dict(criterion='Unique global generating table identity; no claim of unique stochastic segmentation',recovered=chosen['score']==12 and len(winners)==1 and chosen['table']==truth['table'],score=chosen['score'],table=chosen['table'],tied_best_tables=winners,truth_table=truth['table'])
 expected={(g,p):c for g,p,c in truth['observed_mapping']};actual={(g,p):c for g,p,c in chosen['mapping']};correct=sum(actual.get(k)==v for k,v in expected.items())
 return dict(criterion='Every generating mapping entry observed in the 12 labels; unobserved alphabet excluded',recovered=chosen['score']==12 and correct==len(expected),correct_entries=correct,observed_entries=len(expected),score=chosen['score'])
