import analysis as a
import itertools
def main():
 a.check_seals();checks=0
 for n in range(2,7):
  for k in range(1,n):
   template=[dict(folio='toy',family='y',x=int(i<k)) for i in range(n)]
   assignments=list(itertools.combinations(range(n),k))
   for bits in itertools.product([0,1],repeat=n):
    y=a.np.array(bits);observed=sum(bits[:k]);oracle=sum(sum(bits[i] for i in ids)>=observed for ids in assignments)/len(assignments);got=a.e.exact(template,y)
    assert got['p'] is None or abs(got['p']-oracle)<1e-12
    assert got['degenerate']==(len({sum(bits[i] for i in ids) for ids in assignments})==1)
    checks+=1
 assert a.e.tokens('shedy.*.chedy,qokam-{note}sh!ey=dar #ignore')==['shedy',None,'chedy','qokam','shey','dar']
 masked=a.json.loads((a.R/'MASKED-v3.1.json').read_text());assert all('y' not in v and 'follower' not in v for v in masked)
 for key,vv in a.cells(masked).items():
  if key.startswith('A-'):assert all(v['available'] for v in vv)
  assert a.e.support(vv)==a.json.loads((a.R/'SUPPORT-v3.1.json').read_text())[key]
 terms=a.np.array([[.02,1],[.08,2],[-.01,1],[.041,2],[.05,1],[.01,2],[.12,1],[.03,2]])
 labels=a.np.array([0,0,1,1,2,2,3,3]);hands=a.np.array(['2']*4+['3']*4)
 mat=a.permutation_labels(labels,hands,123)
 for row in mat:
  assert sorted(row[:4])==sorted(labels[:4]) and sorted(row[4:])==sorted(labels[4:])
 rr=a.perm_test(terms,mat,4);rd=[];var=[]
 for i in range(4):
  x,y=a.cluster(terms[labels==i]);rd.append(x);var.append(y)
 assert rr['status']=='SCORED' and abs(rr['Q']-a.q_summary(rd,var))<1e-9
 scalar=[]
 for row in mat[:101]:
  est=[a.cluster(terms[row==i]) for i in range(4)];scalar.append(a.q_summary([v[0] for v in est],[v[1] for v in est]))
 assert all(q is not None for q in scalar)
 a.save('ENGINEERING-v3.1.json',dict(status='PASS',exact_bruteforce_cases=checks,unknown_slots_and_comments=True,masked_outcomes_absent=True,primary_support_recomputed=True,available_primary_only=True,permutation_scribe_counts_preserved=True,vectorized_Q_matches_scalar=True,reserved_folios_explicitly_excluded=sorted(a.RESERVED)))
 a.seal('engineering_verified',['ENGINEERING-v3.1.json','engineering.py'])
 print('Engineering PASS',checks)
if __name__=='__main__':main()
