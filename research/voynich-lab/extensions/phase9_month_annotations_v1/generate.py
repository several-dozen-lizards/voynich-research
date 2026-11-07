from common import *

def bracket(text,month):
 count=2 if month==9 else 1 if month in [10,11] else 0
 indices=sorted({max(1,min(len(text)-2,(i+1)*len(text)//(count+1))) for i in range(count)})
 return ''.join('('+c+')' if i in indices else c for i,c in enumerate(text))

def encode(job,items,lexicons,books):
 rng=random.Random(sid(job['language'],job['encoder'],job['seed'],'encoding'));alphabet=list(ALPHABET);mapping={};book=None
 if job['encoder'].startswith('naibbe_'):book=books[job['encoder'][7:]]
 else:
  for group in ['A'] if job['encoder']=='mono' else ['B','M','E']:
   perm=rng.sample(alphabet,len(alphabet));mapping.update({(group,p):c for p,c in zip(alphabet,perm)})
 labels=[];observed={};paths=[]
 for item in items:
  name=lexicons[job['language']][item['month_number']]
  if book is not None:
   units=[];i=0
   while i<len(name):
    width=1 if i==len(name)-1 or rng.random()<17/36 else 2;units.append(name[i:i+width]);i+=width
   cipher=''.join(book[u] for u in units);paths.append(units)
  else:
   units=[]
   for i,p in enumerate(name):
    group='A' if job['encoder']=='mono' else position(i,len(name));c=mapping[group,p];units.append(c);observed[group,p]=c
   cipher=''.join(units)
  labels.append(bracket(cipher,item['month_number']))
 return labels,dict(table=job['encoder'][7:] if book is not None else None,observed_mapping=[[g,p,c] for (g,p),c in sorted(observed.items())],naibbe_source_units=paths)

def main():
 verify();assert not (R/'DATA_READY.json').exists();items=load('ITEMS.json');lexicons=names();books=codebooks();shuffles=load('SHUFFLES.json');scheduled=jobs()
 for job in scheduled:
  labels,truth=encode(job,items,lexicons,books)
  if job['kind']=='negative':labels=[labels[i] for i in shuffles[str(job['seed'])]['negative_assignment']]
  dump('data/'+job['id']+'.json',dict(job=job,labels=labels,truth=truth))
 dump('DATA_READY.json',dict(status='FROZEN_CONTROL_BANK_GENERATED',jobs=scheduled,files={str(p.relative_to(R)):sha(p) for p in (R/'data').glob('*.json')},target_annotation_fits=False,native_tracks='CLOSED'))
 print('Generated',len(scheduled),'datasets; no annotation or native target fit.')
if __name__=='__main__':main()
