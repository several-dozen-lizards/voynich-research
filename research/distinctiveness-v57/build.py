from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parent;P=R.parent
src=P/'word-parts-v50/RESULTS.json';x=json.loads(src.read_text());inv=json.loads((P/'word-parts-v50/INVENTORY.json').read_text());loc=json.loads((P/'wheel-parts-v51/MATCHED-COMPARISONS.json').read_text());mapping=json.loads((P/'wheel-parts-v51/LOCATION-MAP.json').read_text())
keys=['hand','language','format','position','section_a','section_b'];index={tuple(p[k] for k in ['transcription']+keys):p for p in x['results']};records=[];panels=[]
for key,h in index.items():
 if key[0]!='H':continue
 f=index.get(('F',)+key[1:])
 if not f:continue
 title=f"hand {h['hand']} / {h['language']} / {h['format']} / {h['position']} / {h['section_a']} vs {h['section_b']}";panels.append({'id':title,**{k:h[k] for k in keys},'H_support':{k:h[k] for k in ['folios_a','folios_b','words_a','words_b']},'F_support':{k:f[k] for k in ['folios_a','folios_b','words_a','words_b']}})
 fm={v['feature']:v for v in f['features']}
 for hv in h['features']:
  fv=fm[hv['feature']];dh=hv['difference_pp'];df=fv['difference_pp'];same=dh*df>0;passed=same and min(abs(dh),abs(df))>=2 and max(hv['p_family'],fv['p_family'])<=.05
  status='passes both readings' if passed else 'direction disagreement' if dh*df<0 else 'same direction, not qualified' if same else 'zero in one/both readings'
  records.append({'panel':title,'unit':hv['feature'],'section_a':h['section_a'],'section_b':h['section_b'],'favours':h['section_a'] if same and dh>0 else h['section_b'] if same else 'unresolved','H':hv,'F':fv,'status':status,'score':min(abs(dh),abs(df)) if same else 0})
rare=[{'unit':f,'H':v.get('H',0),'F':v.get('F',0),'status':'below pooled support screen; not tested'} for f,v in inv.items() if not v['screen_eligible']]
data={'panels':panels,'records':records,'rare':rare,'location_tests':loc,'ambiguous_locations':[{k:v[k] for k in ['page','description','zone','reason','status']}|{'unit':u} for u,v in mapping.items() if v['zone']=='ambiguous' or v['status']=='missing transcription'],'unsupported':x['unestimable'],'method':'Existing frozen v50 tests, not a rerun or new confirmation. Shared H/F loci, exact hand/Currier/rawformat/first-interior-last; equal numbered-folio weights. >=5 folios/100words per side; feature>=20 pooled occurrences/5folios. 1999 maxT permutations across3577features plus12panel correction. Positive requires >=2pp and adjustedp<=.05 both readings. Ranking within evidence class by smaller absolute H/F effect.','limits':'Conditional exploratory association; section-label exchangeability unverified. No semantic meaning, causality or held-out confirmation. H/F are not independent manuscripts. Other atlas readings remain descriptive, not covered by these corrected tests.'}
(R/'data.js').write_text('const DATA='+json.dumps(data,separators=(',',':'))+';',encoding='utf8');(R/'RESULTS.json').write_text(json.dumps(data,indent=2),encoding='utf8');(R/'PROVENANCE.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,P/'word-parts-v50/INVENTORY.json',P/'wheel-parts-v51/MATCHED-COMPARISONS.json',P/'wheel-parts-v51/LOCATION-MAP.json']},indent=2))
print(json.dumps({'ranked_contrasts':len(records),'passing':sum(r['status']=='passes both readings' for r in records),'rare_units':len(rare),'unsupported_panels':len(data['unsupported'])}))
