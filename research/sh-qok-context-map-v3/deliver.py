import analysis as a
import shutil
def fmt(x):return 'NA' if x is None else f'{x:.3g}'
def effect(row):
 ci=row.get('CI95_points');return f"{fmt(row.get('effect_points'))} [{fmt(ci[0])}, {fmt(ci[1])}]" if ci else 'NA'
def main():
 a.check_seals();A=a.json.loads((a.R/'PART-A.json').read_text());B=a.json.loads((a.R/'PART-B-TESTS.json').read_text());E=a.json.loads((a.R/'PART-B-ESTIMATES.json').read_text());Q=a.json.loads((a.R/'QUALIFICATION.json').read_text())
 ev,ledger=a.collect(True)
 with (a.R/'EVENTS.csv').open(encoding='utf-8') as f:rows=list(a.csv.DictReader(f))
 assert len(rows)==len(ledger)
 def direct(rr,available=False):
  strata=a.collections.defaultdict(lambda:[0,0,0,0])
  for r in rr:
   if r['exclusion_reason']:continue
   f=r['follower'];av=not f.startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
   assert av==(av or (f.startswith('qo') and not f.startswith('qok')))
   if available and not av:continue
   ns,nc,ys,yc=strata[r['folio'],r['family']];x=int(r['prefix']=='sh');y=int(f.startswith('qok'));strata[r['folio'],r['family']]=[ns+x,nc+1-x,ys+x*y,yc+(1-x)*y]
  num=den=0.
  for ns,nc,ys,yc in strata.values():
   if ns and nc:w=ns*nc/(ns+nc);num+=w*(ys/ns-yc/nc);den+=w
  return 100*num/den if den else None
 checks=[]
 for key,r in E.items():
  if 'aggregate' not in r:continue
  rr=[v for v in rows if v['context']==r['context'] and v['reading']==r['reading']]
  for av,n in [(False,'aggregate'),(True,'available')]:
   got=direct(rr,av);want=r[n]['effect_points'];assert got is None and want is None or abs(got-want)<1e-10;checks.append(key+'-'+n)
 original_w=a.json.loads((a.R/'SUPPORT.json').read_text());assert all(not original_w[k]['gate'] and original_w[k]['W']==0 for k in A)
 lines=['RETROSPECTIVE — all material exposed or uncertified (v100/v102).']
 for k,r in A.items():lines.append(f"{k}: {r['status']} — effect {effect(r['estimate'])} pts, Holm p {fmt(r['holm_p'])}")
 lines+=['','Amendment v3.1 was authorized and hashed before its primary support computation. Part A uses attempt C’s folio × ending exact engine on available followers. H/F are alternate readings, scored separately. This is neither prospective confirmation nor a meaning or mechanism claim.','','Context map: all descriptive. Effects and folio-bootstrap 95% CIs in percentage points.','','| Context | Reading | All events | Available events | Aggregate effect [CI] | Available effect [CI] | Discordant strata / supported pages |','|---|---|---:|---:|---|---|---|']
 names={'C1':'2 · Bath (selected discovery)','C2':'2 · Botanical (exposed retest)','C3':'2 · Rose obverse (uncertified)','C4':'3 · Starred (selected discovery)','C5':'3 · Botanical (exposed)','C6':'1 · Botanical / A (exposed)','C7':'1 · Recipes / A (uncertified)','C8-4':'4 · Astronomy P','C8-5':'5 · Botanical'}
 for c in names:
  for co in ['H','F']:
   r=E[c+'-'+co]
   if 'aggregate' not in r:lines.append(f"| {names[c]} | {co} | {r['support']['eligible_origins']} | — | COUNTS ONLY | — | {r['support']['supported_strata']} / {r['support']['supported_pages']} |")
   else:
    s=r['aggregate']['support'];lines.append(f"| {names[c]} | {co} | {r['aggregate']['events']} | {r['available']['events']} | {effect(r['aggregate'])} | {effect(r['available'])} | {s['supported_strata']} / {s['supported_pages']} |")
 lines+=['','Between-context REML summaries, C1–C5 (descriptive; B-Q2 failed qualification).']
 for co in ['H','F']:
  r=B['B-Q2-'+co];m=r['descriptive_tests']['primary']['random_effects'];ci=m.get('Q_profile_CI95')
  lines.append(f"{co}: τ² {fmt(m.get('tau2'))} [{', '.join(fmt(x) for x in ci) if ci else 'NA'}], I² {fmt(100*m['I2'])+'%' if 'I2' in m else 'NA'}; {r['status']}. τ² units are squared probability (×10,000 for squared percentage points).")
 lines+=['','Part B tests','','| Test | Reading | Status | Effect [CI] or descriptive Q | Holm p |','|---|---|---|---|---|']
 for k,r in B.items():
  val=effect(r['estimate']) if 'estimate' in r else fmt(r['descriptive_tests']['primary'].get('Q'));lines.append(f"| {k[:-2]} | {k[-1]} | {r['status']} | {val} | {fmt(r['holm_p'])} |")
 lines+=['','The starred cell passes both H and F: the sh→qok association there survives this availability condition. Its effect is about 1.16–1.17 times the aggregate effect, so blocking alone does not explain that retrospective association. P1 lacks a both-reading headline because F missed qualification, even though H passes and both descriptive effects remain positive. Bath and Currier A remain inference-blocked; they are not negative results.','','Scribe-2 heterogeneity sensitivities (all unqualified descriptive diagnostics, no Holm claim):','','| Reading | Contexts | Q | Diagnostic permutation p | τ² [Q-profile CI] | I² |','|---|---|---|---|---|---|']
 for co in ['H','F']:
  for name in ['scribe2_with_C1','scribe2_without_C1']:
   r=B['B-Q2-'+co]['descriptive_tests'][name];m=r['random_effects'];ci=m.get('Q_profile_CI95');lines.append(f"| {co} | {', '.join(r['contexts'])} | {fmt(r.get('Q'))} | {fmt(r.get('p'))} | {fmt(m.get('tau2'))} [{', '.join(fmt(x) for x in ci) if ci else 'NA'}] | {fmt(100*m['I2'])+'%' if 'I2' in m else 'NA'} |")
 lines+=['','Real-support qualification summary (200 trials per scenario):','','| Cell | Largest required-null upper Wilson bound | Positive lower Wilson bound | Result |','|---|---|---|---|']
 for k,r in Q['A_and_BQ1'].items():
  controls=r['controls'];nu=max(v['wilson95'][1] for v in controls if v.get('role','null')=='null');po=next(v['wilson95'][0] for v in controls if v['scenario']=='positive');lines.append(f"| {k} | {100*nu:.4f}% | {100*po:.2f}% | {r['status']} |")
 lines+=['','Four false flags in 200 gives an upper Wilson bound of 5.0287%, narrowly above the frozen 5% gate. Such a miss blocks qualification; it does not prove that the underlying method has a false-positive rate above 5%. No additional trials or threshold changes were used to rescue any cell.']
 lines+=['','Availability and surviving share: descriptive, with paired folio draws for numerator and denominator.','','| Cell | Reading | Aggregate effect [CI] | Available effect [CI] | Share [CI] | Strict q/o/d/y/a effect [CI] |','|---|---|---|---|---|---|']
 for k,r in A.items():
  share=r['surviving_share'];ci=share['CI95'];lines.append(f"| {k[:-2]} | {k[-1]} | {effect(r['aggregate'])} | {effect(r['estimate'])} | {fmt(share['share'])} [{fmt(ci[0])}, {fmt(ci[1])}] | {effect(r['strict_sensitivity'])} |")
 lines+=['','PASS requires support, null qualification, adequate positive-control power, positive effect and Holm p≤.05. UNDERPOWERED retains its score without a passing headline. Null qualification failures block inference. A Part A headline needs both readings. Holm families are three Part A cells per reading, and two Part B questions per reading; blocked slots occupy p=1 internally and are reported NA.','','A.1b adding qo-but-not-qok leaves availability identical for every event. The strict opening variant is descriptive. Surviving-share ratios can exceed one, change sign or become unstable when the aggregate denominator is near zero. Interpret its CI alongside the aggregate CI; invalid zero-denominator bootstrap draws are counted explicitly.','','The paired exact-body W engine remains an unchanged sensitivity outside Holm: all six cells W=0, zero contributing pages, UNSUPPORTED. It cannot rescue or overturn the amended primary. Its narrower matching population differs from attempt C. Initial support and all pair groups remain in the parent audit directory.','','B-Q2 failed qualification in both readings. Its H upper Wilson bounds were 7.05% under homogeneous null and 8.96% under homogeneous +8 points; F bounds were 7.05% and 7.69%, with four undefined homogeneous-positive trials. Heterogeneous +12-point power was 22.0% H / 11.5% F, descriptive only. The main B-Q2 calculation and the scribe-2 sensitivities are unqualified diagnostics. They cannot establish either heterogeneity or its absence. C1/C4 selection can inflate apparent heterogeneity, and broad τ² intervals remain inconclusive.','','A/Q1 controls used 200 trials per scenario on actual geometry. Part A retains all six required scenarios. B-Q1 uses attempt C’s original five scenario gates; an additional availability-only stress control is retained as a diagnostic. Frozen seeds, every miss/false flag and all outcome hashes remain in the parent audit directory. The interrupted controls resumed only missing jobs, with cached geometry and unchanged arithmetic verified against retained trials.','','Whole-folio heterogeneity permutations stay within scribe and preserve context counts. Every shuffle recomputes MH effects and cluster delta-method variances. Undefined shuffle statistics cause abstention. REML and Q-profile use these cluster variances; displayed effect CIs use 4,999 folio bootstrap samples. These numerical choices were frozen before controls and outcomes.','','Currier A results apply to these samples and this contrast. A pass would support a cross-variety association, not prove a scribe-independent habit. Unsupported and underpowered cells are not negatives. Nothing here distinguishes junction spelling from grammar among available followers or assigns a semantic explanation.','','Reserved Virgo/Libra/Scorpio/Sagittarius folios were filtered before v3.1 tokenization. f73r/v contain no eligible H/F P units, so no such events enter C5. C8 astronomy uses Davis’s literal Section Astronomy/Astrology; the initial preflight’s narrower label match was corrected before amended support.','','The first engineering toy fixture accidentally allowed zero-variance permutations; its assertion failure was retained and its toy numerator corrected from .040 to .041. The production method was unchanged. Engineering then passed 516 exact-distribution oracle cases, support replay and the Q calculation check.','','PROTOCOL.json contains the original spec, amendment and phase seals. COVERAGE-REPLAY.json reproduces all attempt C P1 counts/exclusions. SUPPORT.json is amended primary support; AVAILABILITY.json and EVENTS.csv preserve event flags and exclusions. VERIFICATION.json contains independent effect recalculations and file hashes. Source code, phase hashes, original v3 support, controls and failures are retained in the parent audit directory.']
 (a.R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 D=a.R/'delivery';D.mkdir(exist_ok=True)
 for n in ['COVERAGE-REPLAY.json','QUALIFICATION.json','PART-A.json','PART-B-ESTIMATES.json','PART-B-TESTS.json','EVENTS.csv','REPORT.md']:shutil.copy2(a.R/n,D/n)
 availability=dict(rule='available iff follower does not open ch/sh/cth/ckh/cph/cfh',A1b_identical=True,events=[{k:v[k] for k in ['reading','context','folio','line','position','origin','follower','follower_class','available','outcome','exclusion_reason']} for v in ledger])
 (D/'AVAILABILITY.json').write_text(a.json.dumps(availability,indent=2),encoding='utf-8');shutil.copy2(a.R/'SUPPORT-v3.1.json',D/'SUPPORT.json')
 (D/'PROTOCOL.json').write_text(a.json.dumps(dict(original=a.json.loads((a.R/'PROTOCOL.json').read_text()),amendment=a.json.loads((a.R/'AMENDMENT-v3.1.json').read_text()),resume=a.json.loads((a.R/'RESUME-v3.1.json').read_text()),phase_seals=[a.json.loads(s) for s in (a.R/'PHASES.jsonl').read_text().splitlines()]),indent=2,ensure_ascii=False),encoding='utf-8')
 verification=dict(status='PASS_NUMERICAL_AND_PROVENANCE_CHECKS; STATISTICAL QUALIFICATION FAILURES RETAINED',coverage_replay='PASS',independently_recomputed_MH_effects=checks,ledger_rows=len(ledger),A1b_identity=True,W_sensitivity_zero=True,phase_seals_unchanged=True,engineering=a.json.loads((a.R/'ENGINEERING-v3.1.json').read_text()),delivery_hashes={p.name:a.sha(p) for p in D.iterdir() if p.is_file() and p.name!='VERIFICATION.json'},audit_directory=str(a.R))
 (D/'VERIFICATION.json').write_text(a.json.dumps(verification,indent=2),encoding='utf-8');a.save('VERIFICATION.json',verification);print(D/'REPORT.md')
if __name__=='__main__':main()
