from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while True:
   block=f.read(1024*1024)
   if not block:break
   h.update(block)
 return h.hexdigest()
def main():
 data=json.loads((R/'RESULTS.json').read_text());rows=data['rows'];grid=[.04,.08,.12,.16,.20,.24,.28,.32,.40,.48];summaries=[]
 for co in ['H','F']:
  for b in [0.,.08]:
   for target in ['C1','C2','C3','C4','C5']:
    points=[]
    for delta in grid:
     rr=[r for r in rows if r['reading']==co and r['common_effect']==b and r['target']==target and r['difference']==delta];assert len(rr)==3;points.append(dict(difference=delta,jointly_feasible=all(r['feasible'] for r in rr),all_architectures_certified=all(r['status']=='RELIABLY DETECTABLE' for r in rr)))
    cert=[p['difference'] for p in points if p['all_architectures_certified']];sustained=[p['difference'] for i,p in enumerate(points) if p['all_architectures_certified'] and all(q['all_architectures_certified'] for q in points[i:] if q['jointly_feasible'])];summaries.append(dict(reading=co,common_effect=b,target=target,first_certified_tested_difference=min(cert) if cert else None,first_sustained_certified_tested_difference=min(sustained) if sustained else None,largest_jointly_feasible_tested_difference=max(p['difference'] for p in points if p['jointly_feasible']),points=points,derivation='Presentation-only per-reading intersection of the same frozen simultaneous-bound criteria, without pooling readings or changing a cell classification.'))
 (R/'PER-READING-THRESHOLDS.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
 names={'C1':'Scribe2 Bath','C2':'Scribe2 Botanical','C3':'Scribe2 Rose','C4':'Scribe3 Starred','C5':'Scribe3 Botanical'}
 def display(co,b,t):
  r=next(x for x in summaries if x['reading']==co and x['common_effect']==b and x['target']==t);d=r['first_sustained_certified_tested_difference'];return f'+{100*d:g} pp' if d is not None else 'Not certified'
 first,rest=(R/'REPORT.md').read_text(encoding='utf-8').split('\n',1);front=['','The first sustained certified tested differences below meet the80% lower-bound criterion across all three baseline architectures, separately within each reading. They are grid points, not interpolated minimum detectable effects. All larger jointly feasible tested points also qualify.','','| Target context | H, common0 | F, common0 | H, common+8 | F, common+8 |','|---|---|---|---|---|']
 for t in names:front.append(f"| {t} · {names[t]} | {display('H',0.,t)} | {display('F',0.,t)} | {display('H',.08,t)} | {display('F',.08,t)} |")
 at12=[r for r in rows if r['target'] is not None and r['difference']==.12];assert len(at12)==60 and all(r['status']=='BELOW 80% TARGET' for r in at12)
 front+=['',f"Every +12-point scenario was below the80% target: power estimates ranged{min(r['power'] for r in at12):.2%}–{max(r['power'] for r in at12):.2%}. This is a conditional sensitivity result, not a bound on true manuscript heterogeneity.",'','C5 on the+8-point background has no cross-baseline certification in F within the jointly feasible grid. Its uniform-baseline+40-point estimate is82.45%, but the simultaneous interval78.90%–85.65% straddles80%; +48 is infeasible in the unequal and availability-preserving scenarios. Each individual curve is retained; “not certified” does not mean detection is impossible.','','All12 zero guards passed;18 power cells remain INCONCLUSIVE, and3 cells are INFEASIBLE. No additional trials or probability clipping was used. The charts were visually inspected with H/F separate; PNG and SVG exports retain the full curves and simultaneous intervals.','']
 lines=(first+'\n'+'\n'.join(front)+'\n'+rest.lstrip('\n')).splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|---') and i and lines[i-1].startswith('|'):lines[i]='|'+'---|'*(lines[i-1].count('|')-1)
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(line)['hashes'].items():assert sha(R/n)==h
 ver=json.loads((R/'FINAL-VERIFICATION.json').read_text());ver['figures_visually_inspected']=['POWER-H.png','POWER-F.png'];ver['presentation_note']='Added per-reading intersections of the same certified grid cells and explicit inconclusive-boundary interpretation; no trial, grid point, detection rule or classification changed.';ver['artifact_hashes']={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'mpl-cache' not in p.parts and p.name!='FINAL-VERIFICATION.json'};(R/'FINAL-VERIFICATION.json').write_text(json.dumps(ver,indent=2),encoding='utf-8');assert all(sha(R/p)==h for p,h in ver['artifact_hashes'].items());print(json.dumps(dict(reading_thresholds=[{k:v for k,v in s.items() if k not in ['points','derivation']} for s in summaries],prior_files_preserved=len(preserved['hashes']),artifact_hashes_verified=len(ver['artifact_hashes'])),indent=2))
if __name__=='__main__':main()
