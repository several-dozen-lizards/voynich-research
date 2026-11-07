from common import *
from matcher import fit,recovery
import multiprocessing as mp

def worker(job):
 resultpath=R/'results'/job['id']/'RESULT.json'
 if resultpath.exists():return json.loads(resultpath.read_text(encoding='utf8'))
 data=load('data/'+job['id']+'.json');items=load('ITEMS.json');lexicons=names();books=codebooks();labels=[alternatives(x) for x in data['labels']];stage='observed_fit'
 try:
  observed=fit(items,labels,lexicons,books);dump('results/'+job['id']+'/OBSERVED.json',observed);stage='null_fits';nullscores=[];permutations=load('SHUFFLES.json')[str(job['seed'])]['nulls'];out=R/'results'/job['id']/'NULLS.jsonl.gz';out.parent.mkdir(parents=True,exist_ok=True)
  with gzip.open(out,'wt',encoding='utf8',newline='\n') as f:
   for index,perm in enumerate(permutations):
    shuffled=fit(items,[labels[i] for i in perm],lexicons,books);nullscores.append(shuffled['score']);f.write(json.dumps(dict(index=index,assignment=perm,**shuffled),ensure_ascii=False,allow_nan=False)+'\n')
  p=(1+sum(s>=observed['score'] for s in nullscores))/100;stage='recovery';rec=recovery(observed,job,data['truth']) if job['kind']=='positive' else None
  result=dict(**job,status='COMPLETE',score=observed['score'],p=p,rejection=p<=.05,recovery=rec,null_min=min(nullscores),null_max=max(nullscores),null_invariant=min(nullscores)==max(nullscores))
 except Exception as error:result=dict(**job,status='FAILED',active_stage=stage,error=repr(error))
 dump('results/'+job['id']+'/RESULT.json',result);return result

def main():
 verify();assert not (R/'QUALIFICATION.json').exists();ready=load('DATA_READY.json');assert all(sha(R/p)==h for p,h in ready['files'].items());results=[]
 with mp.Pool(3) as pool:
  for row in pool.imap_unordered(worker,ready['jobs'],chunksize=1):
   results.append(row);dump('PROGRESS.json',dict(complete=len(results),scheduled=len(ready['jobs']),native_gate='CLOSED'));print('CALIBRATION',len(results),'/',len(ready['jobs']),row['id'],row['status'],flush=True)
 dump('RESULTS.json',results);cells=[]
 for language in LANGS:
  for encoder in ['mono','position']+['naibbe_'+t for t in TABLES]:
   pos=[r for r in results if (r['language'],r['encoder'],r['kind'])==(language,encoder,'positive')];neg=[r for r in results if (r['language'],r['encoder'],r['kind'])==(language,encoder,'negative')];assert len(pos)==len(neg)==5
   goodpos=[r for r in pos if r['status']=='COMPLETE'];goodneg=[r for r in neg if r['status']=='COMPLETE'];recover=sum(r['recovery']['recovered'] for r in goodpos);positive=sum(r['recovery']['recovered'] and r['rejection'] for r in goodpos);negative=sum(r['rejection'] for r in goodneg);passed=len(goodpos)==len(goodneg)==5 and positive>=4 and negative<=1
   cells.append(dict(language=language,encoder=encoder,valid_positive=len(goodpos),valid_negative=len(goodneg),mapping_recovered=recover,positive_recovery_and_rejection=positive,negative_rejections=negative,cell_pass=passed))
 passed=all(c['cell_pass'] for c in cells);dump('QUALIFICATION.json',dict(status='PASS' if passed else 'FAIL',cells=cells,all_cells_required=True,native_tracks='CLOSED',annotation_target_fits=False));dump('RUN_STATE.json',dict(status='CALIBRATION_PASSED_ANNOTATION_PENDING' if passed else 'STOPPED_CALIBRATION_FAILED',annotation_gate='QUALIFIED_PENDING_TARGET_MANIFEST' if passed else 'CLOSED',native_gate='CLOSED',native_tracks_scored=False,annotation_target_fits=False,Phase8_FAIL_preserved=True))
 print('QUALIFICATION','PASS' if passed else 'FAIL',sum(c['cell_pass'] for c in cells),'/',len(cells))
if __name__=='__main__':main()
