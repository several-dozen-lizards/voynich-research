import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,importlib.util,collections,math
import numpy as np
from scipy.stats import chi2
R=Path(__file__).resolve().parent;P=R.parent;PREV=P/'bq2-replacement-v1'
sp=importlib.util.spec_from_file_location('r1_engine',PREV/'engine.py');r1=importlib.util.module_from_spec(sp);sp.loader.exec_module(r1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def main():
 assert not (R/'DIAGNOSIS.json').exists()
 roots=['sh-qok-context-map-v3','sh-qok-qualification-followup-v1','sh-qok-retrospective-readjudication-v1','currier-a-available-only-v1','bq2-replacement-v1']
 preserved={str(p):sha(p) for root in roots for p in (P/root).rglob('*') if p.is_file() and '__pycache__' not in p.parts};save('PRESERVATION.json',dict(hashes=preserved))
 save('DIAGNOSTIC-PLAN.json',dict(scope='Exploratory diagnosis using all5000 already-saved section-baseline control trials per reading. Not fresh qualification or manuscript scoring.',questions=['Are raw context MH effects unbiased for common+.08?','How do empirical variances, exact generating variances and mean R1 working variances differ by context?','Does the old relabeling reference or its working variance account for inflation? Compare R1 Q against chi-square3 and independently construct oracle-variance Q.','For fixed first100 trials per reading replay original bank and compare97.5% critical values with chi-square3; no seed/trial selection by flag.'],new_outcomes=0))
 events=json.loads((PREV/'MASKED.json').read_text());summaries={};critical=float(chi2.ppf(.975,3));case_records=[]
 for ri,co in enumerate(['H','F']):
  g=r1.Geometry([e for e in events if e['reading']==co]);records=[json.loads(s) for p in sorted((PREV/'trials').glob(f'{ri}-3-*.jsonl')) for s in p.read_text().splitlines()];assert len(records)==5000
  effects=[];working=[];oraclevars=[];qwork=[];qoracle=[];bankcritical=[];bias=[];storedflags=chisqflags=oracleflags=0
  base=np.array([.10,.40,.20,.15,.45]);gc=g.labels[g.gp];ps=base[gc]+.08;pc=base[gc];n=g.ns+g.nc;vg=(g.nc/n)**2*g.ns*ps*(1-ps)+(g.ns/n)**2*g.nc*pc*(1-pc);Vtrue=np.bincount(g.gp,weights=vg,minlength=len(g.pages));true_context=np.bincount(g.labels,weights=Vtrue,minlength=5)/g.dc**2
  for rec in records:
   y=g.generate('section_baseline_homogeneous',rec['outcome_seed']);assert hashlib.sha256(y.tobytes()).hexdigest()==rec['outcome_sha256'];N,V=g.terms(y);t,rd,v=r1.statistic(g,N,V,g.labels[None,:]);assert abs(float(t[0])-rec['Q'])<1e-10;to,_,_=r1.statistic(g,N,Vtrue,g.labels[None,:]);effects.append(rd);working.append(v);qwork.append(float(t[0]));qoracle.append(float(to[0]));storedflags+=rec['flag'];chisqflags+=chi2.sf(t[0],3)<=.025;oracleflags+=chi2.sf(to[0],3)<=.025
   if rec['trial']<100:
    mat=r1.labels_bank(g,rec['permutation_seed']);qq,_,_=r1.statistic(g,N,V,mat);assert hashlib.sha256(qq.tobytes()).hexdigest()==rec['permutation_Q_sha256'];bankcritical.append(float(np.quantile(qq[1:],.975,method='higher')))
  es=np.array(effects);vs=np.array(working);emp=es.var(axis=0,ddof=1);mv=vs.mean(axis=0)
  summaries[co]=dict(trials=5000,old_relabel_flags=int(storedflags),working_variance_chisq_flags=int(chisqflags),oracle_variance_chisq_flags=int(oracleflags),context_effect_bias_points={c:float(100*(es[:,i].mean()-.08)) for i,c in enumerate(r1.CONTEXTS)},context_variances={c:dict(empirical=float(emp[i]),generating_exact=float(true_context[i]),mean_R1_working=float(mv[i]),R1_working_over_true=float(mv[i]/true_context[i])) for i,c in enumerate(r1.CONTEXTS)},observed_Q975_working=float(np.quantile(qwork,.975)),observed_Q975_oracle=float(np.quantile(qoracle,.975)),chisq3_975=critical,relabel_Q975_first100=dict(mean=float(np.mean(bankcritical)),median=float(np.median(bankcritical)),range=[min(bankcritical),max(bankcritical)]))
 save('DIAGNOSIS.json',dict(status='EXPLORATORY PRIOR-CONTROL DIAGNOSIS; NOT QUALIFICATION',readings=summaries,no_new_random_outcome_coordinates=True,manuscript_scored=False,source_hashes={str(PREV/n):sha(PREV/n) for n in ['engine.py','QUALIFICATION.json','TRIAL-HASHES.json','MASKED.json']}));assert all(sha(Path(p))==h for p,h in preserved.items());print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
