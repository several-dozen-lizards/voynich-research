from pathlib import Path
import json
import rate_model as m
R=Path(__file__).resolve().parent
rows=[]
for folio,section,label,N,Q in [('f1r','low','PL',10,1),('f1v','low','NO',90,9),('f2r','high','PL',100,90),('f2v','high','NO',10,9)]:
    rows.append(dict(folio=folio,section=section,label=label,N=N,Q=Q,hand='1',unknown_slots=0,wrap_bin='normal'))
r=m.fit(rows,'PL')
assert abs(r['OR']-1)<1e-12 and r['CI95']==[1.0,1.0] and r['undefined_draws']==0
missing=m.fit([rows[0],rows[3]],'PL')
assert missing['OR'] is None and missing['undefined_draws']==4999 and missing['CI95'] is None
record=dict(status='PASS_SYNTHETIC_BOOTSTRAP',section_confounding_adjusted_OR=1.0,bootstrap_draws_per_case=4999,full_stratum_reaggregation_checked=True,nonoverlap_withholds_interval=True,real_ratings_read=False)
(R/'BOOTSTRAP-QUALIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
