from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 q=json.loads((R/'QUALIFICATION.json').read_text());result=json.loads((R/'RESULTS.json').read_text());assert all(not x['manuscript_scored'] for x in result['readings'].values())
 reasons={co:[c for c in r['controls'][:5] if c['nominal_size_alarm'] or c['status']!='CERTIFIED BELOW TOLERANCE'] for co,r in q['results'].items()}
 interpretation=dict(status='NOT QUALIFIED IN BOTH READINGS; MANUSCRIPT UNSCORED',numerical_zero_variance_handling='Passed: finite working variance in deterministic fixtures, all six old undefined synthetic assignments and the completed fresh run.',primary_failure='Required equal-effect section-baseline control triggers frozen nominal-size alarm in each reading. All practical-null upper bounds remain below5%, but the separate nominal-size condition fails.',blocking_controls=reasons,manuscript_statistics_computed=0,run_extended=False,retuned=False,power='Point-flag power for planted+.12 in C1 ranges47.9%..51.6%; descriptive, not a qualification gate.',inconclusive_distinction='Qualification failure is established by simultaneous lower bounds>.025 for the section-baseline null. Whether the manuscript has heterogeneous effects remains unresolved and unscored. Other control intervals straddling nominal retain that uncertainty; absence of a nominal alarm is not a proof of nominal calibration.')
 (R/'QUALIFICATION-INTERPRETATION.json').write_text(json.dumps(interpretation,indent=2),encoding='utf-8')
 report=(R/'REPORT.md').read_text(encoding='utf-8');first,rest=report.split('\n',1)
 front=['','Both readings failed the frozen nominal-calibration gate. All practical-null bounds cleared the separate5% tolerance; this does not override the nominal-size condition. No manuscript heterogeneity statistic, p, τ² or I² was computed.','','| Blocking control | Reading | Flags/N | Rejection rate | Simultaneous exact interval | Nominal target |','|---|---|---|---|---|---|']
 for co in ['H','F']:
  for c in reasons[co]:lo,hi=c['simultaneous_exact_CI95'];front.append(f"| {c['scenario']} | {co} | {c['flags']}/{c['n']} | {c['rate']:.3%} | [{lo:.3%}, {hi:.3%}] | 2.5% |")
 front+=['','In this control the expected effect is+.08 in every context, while context baseline probabilities differ. The lower bounds exceed2.5% in both readings, establishing a calibration problem at the predeclared nominal level for this candidate on this geometry. The problem is not a residual undefined statistic. No replacement rule, extra trials, altered baseline or guarded-flag fallback was used after seeing it.','','Planted+.12 power was only47.9%–51.6% across the four positive-control cells. Power was descriptive by design; it reinforces why a no-detection result would not establish a uniform rule. Here both manuscript readings remain unscored. The scientific heterogeneity question remains unresolved.','','The14 simultaneous intervals in the main table cover10 point-flag null rates and4 point-flag power rates. Supplementary guarded-power intervals in JSON are per-proportion descriptive intervals and are not included in that14-interval simultaneous family.','']
 lines=(first+'\n'+'\n'.join(front)+'\n'+rest.lstrip('\n')).splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|---') and i and lines[i-1].startswith('|'):lines[i]='|'+'---|'*(lines[i-1].count('|')-1)
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 v=json.loads((R/'VERIFICATION.json').read_text());v['presentation_note']='Added explicit gate-failure explanation, distinguished unresolved scientific inference and supplementary guarded intervals, and normalized Markdown table separators; no data/statistics/scoring rule changed.'
 v['artifact_hashes']={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'}
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(line)['hashes'].items():assert sha(R/n)==h
 (R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');assert all(sha(R/p)==h for p,h in v['artifact_hashes'].items());print(json.dumps(dict(prior_files_unchanged=len(preserved['hashes']),artifact_hashes_verified=len(v['artifact_hashes']),manuscript_statistics_computed=0,nominal_failures={co:[c['scenario'] for c in rr] for co,rr in reasons.items()}),indent=2))
if __name__=='__main__':main()
