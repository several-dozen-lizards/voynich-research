import execute as b
def worker(task):
 ri,si,t=task;co=['H','F'][ri];scene=['homogeneous_null','homogeneous_positive'][si];vv=b.HJ[co];outseed=5100000+ri*100000+si*1000+t;rng=b.np.random.default_rng(outseed)
 y=(rng.random(len(vv))<b.np.array([.2+(.08*v['x'] if si==1 else 0) for v in vv])).astype(int)
 for v,yy in zip(vv,y):v['y']=int(yy)
 cs=['C1','C2','C3','C4','C5'];terms,lab,hands,pages=b.a.hetero_data(vv,cs);banks=[]
 for bi in [0,1,2]:
  seed=6100000+ri if bi==0 else [913261,ri,si,t,bi];mat=b.HBASE[co] if bi==0 else b.a.permutation_labels(lab,hands,seed);rr=b.a.perm_test(terms,mat,5)
  detail=b.bank_details(terms,mat,pages,cs) if rr['p'] is None else dict(undefined_shuffles=0,observed_defined=True,undefined_contexts=[],context_counts={c:int((lab==j).sum()) for j,c in enumerate(cs)})
  # Merge repeated receipt keys explicitly; no statistic, seed, gate or abstention rule changes.
  banks.append(rr|detail|dict(bank_index=bi,seed=seed,flag=rr['p'] is not None and rr['p']<=.025))
 return dict(reading=co,reading_index=ri,scenario=scene,scenario_index=si,trial=t,outcome_seed=outseed,outcome_sha256=b.hashlib.sha256(y.astype(b.np.uint8).tobytes()).hexdigest(),banks=banks)
if __name__=='__main__':
 b.verify();note=b.json.loads((b.RUN/'IMPLEMENTATION-RECEIPT-FIX.json').read_text());assert all(b.sha(p)==h for p,h in note['hashes'].items());b.hetero_one=worker;b.hetero()
