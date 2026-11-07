from pathlib import Path
import json,hashlib,math,importlib.util
import numpy as np
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 q=json.loads((R/'QUALIFICATION.json').read_text());results=json.loads((R/'RESULTS.json').read_text());diagnosis=json.loads((R/'DIAGNOSIS.json').read_text())
 sp=importlib.util.spec_from_file_location('fixed_engine',R/'engine.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 events=json.loads((R/'MASKED.json').read_text());analytic={}
 def expected_product(n,p):return (n*(n-1)*p*(1-p)+n/2+.25)/(n+1)**2
 for co in ['H','F']:
  g=module.Geometry([e for e in events if e['reading']==co]);c=g.labels[g.gp];base=np.array([.10,.40,.20,.15,.45])[c];ns,nc=g.ns,g.nc;n=ns+nc
  expect=(nc/n)**2*ns*expected_product(ns,base+.08)+(ns/n)**2*nc*expected_product(nc,base)
  truth=(nc/n)**2*ns*(base+.08)*(1-base-.08)+(ns/n)**2*nc*base*(1-base)
  ev=np.bincount(c,weights=expect,minlength=5)/g.dc**2;tv=np.bincount(c,weights=truth,minlength=5)/g.dc**2
  analytic[co]={name:dict(exact_expected_R1_working_variance=float(ev[j]),exact_true_variance=float(tv[j]),expected_ratio=float(ev[j]/tv[j]),observed_R1_ratio=diagnosis['readings'][co]['context_variances'][name]['R1_working_over_true']) for j,name in enumerate(module.CONTEXTS)}
 explanation=dict(status='DETERMINISTIC ANALYTIC CONFIRMATION OF OLD-CONTROL DIAGNOSIS; NO NEW OUTCOMES',formula='For Y~Binomial(n,p), E[((Y+.5)/(n+1))*(1-(Y+.5)/(n+1))] = [n(n-1)p(1-p)+n/2+1/4]/(n+1)^2.',singleton='n1 gives.1875 regardless of p: lower than true variance near p.5, higher for rare baselines. R1 pools many such margin-level terms, producing context-dependent variance bias when baselines differ.',readings=analytic,new_random_draws=0,protocol_or_gate_changes=0)
 (R/'ANALYTIC-DIAGNOSIS.json').write_text(json.dumps(explanation,indent=2),encoding='utf-8')
 first,rest=(R/'REPORT.md').read_text(encoding='utf-8').split('\n',1);front=['','V2 passed calibration in both readings. The qualified manuscript test detected no within-scribe heterogeneity: H rawp=.8343, F rawp=.7097, conservative Holm2p=1 for both. This is not evidence of constant strength: planted+.12 power is only38.0%–43.0%, and the descriptive τ² intervals are broad.','','| Reading | Largest required-null upper bound | Previously failing section-baseline control | Planted-positive power range |','|---|---|---|---|']
 for co in ['H','F']:
  controls=q['results'][co]['controls'];worst=max(c['simultaneous_exact_CI95'][1] for c in controls[:8]);sec=next(c for c in controls if c['scenario']=='section_baseline_homogeneous');powers=[c['rate'] for c in controls[8:]];front.append(f"| {co} | {worst:.3%} | {sec['flags']}/{sec['n']}={sec['rate']:.3%}, CI[{sec['simultaneous_exact_CI95'][0]:.3%},{sec['simultaneous_exact_CI95'][1]:.3%}] | {min(powers):.1%}–{max(powers):.1%} |")
 front+=['','All required-null upper bounds are below2.5% under these authored controls, stronger than the frozen5% practical-tolerance requirement. No nominal alarms occurred. These statements concern this qualification run, not universal nominal calibration.','','The old failure has an analytic explanation as well as the saved simulation diagnosis. For a binomial margin with n=1, the R1 half-count plug-in variance product is always.1875. True Bernoulli variance is.24 at p=.40 and.25 at p=.50, but.09 at p=.10. Thus the same regularizer understates uncertainty for high baselines while overstating it for rare baselines. The exact expected R1 variance ratios below reproduce the observed control pattern.','','| Context | H expected R1 variance / true variance | F expected R1 variance / true variance |','|---|---|---|']
 for name in module.CONTEXTS:front.append(f"| {name} | {analytic['H'][name]['expected_ratio']:.4f} | {analytic['F'][name]['expected_ratio']:.4f} |")
 front+=['','The generating variances are known in the old synthetic control. Substituting them brought chi-square rejection rates to2.44% H/2.16% F, whereas changing only the reference with the old working variance left3.78% H/3.38% F. Re-labeling also produced somewhat lower critical values, but reference replacement alone was insufficient. This diagnostic uses old outcomes, not fresh qualification; V2 qualification uses independent new coordinates.','','Context effects remain the original aggregate MH contrasts. The supplemental table below uses the original descriptive bootstrap CIs unchanged; it is not another set of section tests.','','| Context | H effect [original descriptive95% CI], points | F effect [original descriptive95% CI], points |','|---|---|---|']
 old=json.loads((R.parent/'sh-qok-context-map-v3/PART-B-ESTIMATES.json').read_text())
 for name in module.CONTEXTS:
  values=[]
  for co in ['H','F']:
   rr=old[name+'-'+co]['aggregate'];values.append(f"{rr['effect_points']:+.3f} [{rr['CI95_points'][0]:+.3f},{rr['CI95_points'][1]:+.3f}]")
  front.append(f"| {name} | {values[0]} | {values[1]} |")
 front+=['','For both readings, working-model τ² estimates are zero and I² estimates are zero. The Q-profile upper bounds permit between-context standard deviations up to approximately'+f" {100*math.sqrt(results['readings']['H']['random_effects_descriptive']['Q_profile95'][1]):.2f} points H and {100*math.sqrt(results['readings']['F']['random_effects_descriptive']['Q_profile95'][1]):.2f} points F."+' The scientific strength-variation question therefore remains unresolved; zero point estimates do not establish homogeneity.','','No earlier result was rewritten: original B-Q2 and R1 remain unqualified. The larger-of-two-variances rule was frozen before fresh support/controls, and no controls or thresholds were revised after results.','']
 lines=(first+'\n'+'\n'.join(front)+'\n'+rest.lstrip('\n')).splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|---') and i and lines[i-1].startswith('|'):lines[i]='|'+'---|'*(lines[i-1].count('|')-1)
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(line)['hashes'].items():assert sha(R/n)==h
 ver=json.loads((R/'VERIFICATION.json').read_text());ver['presentation_note']='Added deterministic analytic diagnosis, control/power summary, unchanged descriptive context CIs, uncertainty interpretation and table formatting; no statistic or frozen rule changed.';ver['artifact_hashes']={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'};(R/'VERIFICATION.json').write_text(json.dumps(ver,indent=2),encoding='utf-8');assert all(sha(R/p)==h for p,h in ver['artifact_hashes'].items());print(json.dumps(dict(prior_files_preserved=ver['prior_files_preserved'],artifact_hashes_verified=len(ver['artifact_hashes']),readings={co:r['status'] for co,r in results['readings'].items()},analytic_ratios=analytic),indent=2))
if __name__=='__main__':main()
