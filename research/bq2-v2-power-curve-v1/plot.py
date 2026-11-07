import os
from pathlib import Path
R=Path(__file__).resolve().parent
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MPLCONFIGDIR']=str(R/'mpl-cache')
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import run as core
NAMES={'C1':'C1 · S2 Bath','C2':'C2 · S2 Botanical','C3':'C3 · S2 Rose','C4':'C4 · S3 Starred','C5':'C5 · S3 Botanical'}
COLORS={'C1':'#0072B2','C2':'#E69F00','C3':'#009E73','C4':'#CC79A7','C5':'#D55E00'}
def pp(x):return 'None certified' if x is None else f'{100*x:g} pp'
def main():
 core.verify();results=json.loads((R/'RESULTS.json').read_text());rows=results['rows'];curves=json.loads((R/'CURVE-THRESHOLDS.json').read_text());robust=json.loads((R/'ROBUST-THRESHOLDS.json').read_text());feas=json.loads((R/'FEASIBILITY.json').read_text());assert len(rows)==612
 charts=[]
 for co in ['H','F']:
  fig,axes=plt.subplots(2,3,figsize=(16,9),sharex=True,sharey=True)
  for bi,b in enumerate(core.COMMON):
   for ai,arch in enumerate(core.ARCH):
    ax=axes[bi,ai];zero=next(r for r in rows if r['reading']==co and r['architecture']==arch and r['common_effect']==b and r['target'] is None);notes=[]
    for target in core.v2.CONTEXTS:
     rr=[zero]+[r for r in rows if r['reading']==co and r['architecture']==arch and r['common_effect']==b and r['target']==target];x=np.array([100*r['difference'] for r in rr]);y=np.array([r['power'] if r['feasible'] else np.nan for r in rr]);lo=np.array([r['CI'][0] if r['CI'] else np.nan for r in rr]);hi=np.array([r['CI'][1] if r['CI'] else np.nan for r in rr]);color=COLORS[target]
     ax.fill_between(x,lo,hi,color=color,alpha=.08,linewidth=0);ax.plot(x,y,color=color,lw=1.5,marker='o',ms=3,label=NAMES[target]);cert=[i for i,r in enumerate(rr) if r['status']=='RELIABLY DETECTABLE'];unc=[i for i,r in enumerate(rr) if r['status']=='INCONCLUSIVE']
     if cert:ax.scatter(x[cert],y[cert],s=34,marker='D',facecolor=color,edgecolor='white',lw=.6,zorder=5)
     if unc:ax.scatter(x[unc],y[unc],s=44,marker='^',facecolor='white',edgecolor=color,lw=1.2,zorder=6)
     bad=[r for r in rr if not r['feasible']]
     if bad:notes.append(target+': '+','.join(f"{100*r['difference']:g}" for r in bad)+' infeasible')
    ax.axhline(.8,color='#333333',lw=1,ls='--');ax.set_title(f"{arch.capitalize()} baselines · common effect {100*b:g} pp",fontsize=11);ax.grid(alpha=.17);ax.set_ylim(-.015,1.025);ax.set_xlim(-1,49);ax.set_xticks([0,8,16,24,32,40,48]);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.tick_params(labelsize=9)
    if notes:ax.text(.98,.04,'\n'.join(notes),transform=ax.transAxes,ha='right',va='bottom',fontsize=8,bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
    if zero['status']!='GUARD PASS':ax.text(.5,.5,'CALIBRATION GUARD BLOCKED',transform=ax.transAxes,ha='center',color='darkred',fontsize=11)
    if ai==0:ax.set_ylabel('Detection probability',fontsize=10)
    if bi==1:ax.set_xlabel('Target section effect difference (percentage points)',fontsize=9)
  handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=5,fontsize=9,bbox_to_anchor=(.5,.025));fig.suptitle(f'V2 real-support power — {co} reading',fontsize=17,y=.985);fig.text(.5,.948,'Fixed 2,000 trials per positive point · simultaneous 95% intervals over 612 slots · unchanged detection rule',ha='center',fontsize=10);fig.text(.5,.006,'Diamond: lower power bound ≥80%   Triangle: inconclusive at80%   Lines are guides; no interpolated threshold. H/F are separate.',ha='center',fontsize=9);fig.subplots_adjust(left=.065,right=.985,top=.90,bottom=.13,hspace=.25,wspace=.12)
  base=R/f'POWER-{co}';fig.savefig(base.with_suffix('.png'),dpi=180);fig.savefig(base.with_suffix('.svg'));plt.close(fig);charts.append(base.name+'.png')
 fields=['reading','architecture','common_effect_points','target','difference_points','feasible','n','flags','power','lower','upper','status','zero_guard_job','minimum_probability','maximum_probability']
 with (R/'POWER-CELLS.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fields);w.writeheader()
  for r in rows:w.writerow(dict(reading=r['reading'],architecture=r['architecture'],common_effect_points=100*r['common_effect'],target=r['target'] or 'ZERO GUARD',difference_points=100*r['difference'],feasible=r['feasible'],n=r['n'],flags=r['flags'],power=r['power'],lower=r['CI'][0] if r['CI'] else None,upper=r['CI'][1] if r['CI'] else None,status=r['status'],zero_guard_job=r['zero_guard_job'],minimum_probability=r['probability_range'][0],maximum_probability=r['probability_range'][1]))
 guardrows=[r for r in rows if r['target'] is None];inconclusive=[r for r in rows if r['status']=='INCONCLUSIVE'];cert=[r for r in rows if r['status']=='RELIABLY DETECTABLE'];statuscounts={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}
 lines=['RETROSPECTIVE REAL-SUPPORT POWER STUDY — unchanged V2; no manuscript rescoring.','',f"Completed {results['unique_trials']:,} unique fixed synthetic trials:2,000 per feasible positive point and10,000 per zero guard. All {len(guardrows)} guards and all effect positions are retained. The grid has612 slots; {len(feas['infeasible'])} infeasible cells received no draws and still occupy confidence-family slots. No sample extension, grid refinement, isotonic fit, interpolation or retuning occurred.",'','A section-effect difference is an extra sh–ch risk difference in the target context relative to its same-scribe peers. Each target C1–C5 is shifted separately. The common background effect is0 or+8 percentage points. Baselines are uniform, section-specific unequal, or availability-preserving. H/F remain alternate readings and were never pooled.','','Reliability requires the simultaneous exact Clopper–Pearson LOWER bound≥80%. UPPER<80% is below target; otherwise INCONCLUSIVE. These612 intervals jointly have at least95% coverage under the independent-trial simulation model; infeasible slots keep the family size conservative. The detection rule is unchanged V2 rawp≤.025 (conservative Holm2p≤.05).','','Status counts: '+json.dumps(statuscounts)+'.','',f"Zero guard results: {sum(r['status']=='GUARD PASS' for r in guardrows)}/{len(guardrows)} pass. Each guard is shared across the matching five target curves, not five independent repetitions. If a guard fails/is inconclusive, its curves cannot receive reliability certification; raw power estimates remain visible.",'','A compact summary below requires certified≥80% MARGINAL power in each reading and each of the three baseline architectures. It does not assert80% joint H-and-F detection probability. “Sustained” requires every larger jointly feasible tested grid point to qualify; points between grid values were not simulated.','','| Common background effect | Target | First certified tested difference across H/F and all baselines | First sustained certified tested difference | Largest jointly feasible tested difference |','|---|---|---|---|---|']
 for r in robust:lines.append(f"| {100*r['common_effect']:g} pp | {NAMES[r['target']]} | {pp(r['first_certified_tested_difference'])} | {pp(r['first_sustained_certified_tested_difference'])} | {pp(r['largest_jointly_feasible_tested_difference'])} |")
 lines+=['','All60 individual curves retain their own thresholds in CURVE-THRESHOLDS.json. An absent certified point means no tested magnitude met the criterion under that scenario, not impossibility at every larger untested effect. INCONCLUSIVE cells are retained in POWER-CELLS.csv and RESULTS.json; they are neither rounded up to reliable nor declared below target.','','| Reading | Architecture | Common | Target | Difference | Power [simultaneous CI] |','|---|---|---|---|---|---|']
 for r in inconclusive[:30]:lines.append(f"| {r['reading']} | {r['architecture']} | {100*r['common_effect']:g} pp | {r['target']} | {100*r['difference']:g} pp | {r['power']:.1%} [{r['CI'][0]:.1%},{r['CI'][1]:.1%}] |")
 if len(inconclusive)>30:lines+=['',f"This table shows the first30 of {len(inconclusive)} inconclusive cells; the CSV/JSON retain every one."]
 lines+=['','![H power curves](POWER-H.png)','','![F power curves](POWER-F.png)','','Infeasible cells:']
 lines+=['']
 for r in feas['infeasible']:lines.append(f"- {r['reading']} {r['architecture']}, common{100*r['common_effect']:g} pp, {r['target']} difference{100*r['difference']:g} pp; proposed probability range{r['probability_range']}. No clipping or replacement generator was used.")
 lines+=['','The figures connect measured grid points only as visual guides; their bands are simultaneous intervals. Diamonds denote reliable grid points and triangles denote inconclusive points. A probability boundary/infeasible point is not a zero-power observation. The PNGs and SVGs are standalone scientific figures.','','This study estimates operating characteristics conditional on unchanged real geometry and the specified synthetic generators. It is not a confidence bound on the actual manuscript’s unknown heterogeneity and does not convert the earlier no-detection result into proof of uniform strength. Baselines, background association, target position, folio imbalance and sparse contexts matter. Original context selection and exposed material remain. No new manuscript statistic, p-value, semantics or mechanism is inferred.','','PRESERVATION.json inventories all prior non-cache files. PROTOCOL.json and PHASES.jsonl freeze the grid, generator feasibility, support and results. Every synthetic hit/miss has a coordinate, seed, outcome hash and V2 statistic in trials/. POSTRUN-AUDIT.json records fixed first/middle/last checks per feasible cell and every zero-guard false flag, using independent scalar arithmetic. FINAL-VERIFICATION.json records final artifact hashes and preservation checks.']
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');core.verify();assert all(core.sha(R/n)==h for n,h in json.loads((R/'TRIAL-HASHES.json').read_text()).items());audit=json.loads((R/'POSTRUN-AUDIT.json').read_text())
 final=dict(status='COMPLETE_FIXED_POWER_STUDY_VERIFIED',unique_trials=results['unique_trials'],family_slots=612,positive_N=2000,guard_N=10000,status_counts=statuscounts,previous_noncache_files_unchanged=len(json.loads((R/'PRESERVATION.json').read_text())['hashes']),new_manuscript_scores=0,trial_extension_or_retuning=False,scalar_audit_checks=len(audit['checks']),artifact_hashes={str(p.relative_to(R)):core.sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'mpl-cache' not in p.parts and p.name!='FINAL-VERIFICATION.json'})
 (R/'FINAL-VERIFICATION.json').write_text(json.dumps(final,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(R/'REPORT.md'),statuses=statuscounts,guards=sum(r['status']=='GUARD PASS' for r in guardrows),thresholds=robust),indent=2),flush=True)
if __name__=='__main__':main()
