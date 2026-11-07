from pathlib import Path
import importlib.util,json,collections,difflib,html,hashlib
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('owner',P/'phrase-transfer-v62/run.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def show(ws):return ' · '.join(w if w is not None else '[?]' for w in ws)
groups=o.panels();f=o.load(P/'phrase-transfer-v62/FROZEN-CANDIDATES.json');records=[];ranks=[]
for base,phrase in [('2-B-Botanical','or aiin'),('1-A-Botanical','chol daiin')]:
 for split in ('train','test'):
  ix={tr:{r[6]:r for r in groups[base+'-'+tr][split]} for tr in ('H','F')}
  for loc in sorted(set(ix['H'])|set(ix['F'])):
   rr={tr:ix[tr].get(loc) for tr in ('H','F')};ns={tr:o.v.old.counts([rr[tr][7]],'interior','bigrams')[tuple(phrase.split())] if rr[tr] else 0 for tr in rr}
   if not any(ns.values()):continue
   h,ff=[rr[tr][7] if rr[tr] else [] for tr in ('H','F')]
   edits=[]
   for tag,a,b,c,d in difflib.SequenceMatcher(None,h,ff,autojunk=False).get_opcodes():
    if tag=='equal':continue
    hw,fw=h[a:b],ff[c:d]
    kind='uncertain reading' if None in hw+fw else 'boundary only' if ''.join(hw)==''.join(fw) else 'reading and/or boundary'
    edits.append({'H_index':[a,b],'F_index':[c,d],'H':hw,'F':fw,'kind':kind})
   records.append({'stratum':base,'phrase':phrase,'split':split,'locator':loc,'counts':ns,'H':h,'F':ff,'edits':edits,'count_agrees':ns['H']==ns['F']})
 for tr in ('H','F'):
  key=base+'-'+tr;i=list(groups).index(key)
  scores=o.v.test([r[7] for r in groups[key]['train']],62000+i)
  row=next((dict(x,rank=j+1) for j,x in enumerate(scores) if x['phrase']==phrase),None)
  ranks.append({'panel':key,'phrase':phrase,'training_score':row,'selected':any(x['phrase']==phrase for x in f[key]['candidates']),'top5':f[key]['candidates']})
save('LINES.json',records);save('SELECTION.json',ranks)
body='<h1>Phrase readings and selection — v63</h1><p>Descriptive audit of frozen v62 pairs; no new held-out significance tests. Dots separate parsed words, [?] preserves uncertain slots. Diff categories describe parsed text, not paleographic adjudication. All matching loci in either reading are retained, including unequal counts.</p>'
for rank in ranks:body+='<h2>'+rank['panel']+' / '+rank['phrase']+'</h2><pre>'+html.escape(json.dumps({k:v for k,v in rank.items() if k!='top5'},indent=2))+'</pre>'
for x in records:
 body+='<details><summary>'+html.escape(f"{x['split']} {x['locator']} — {x['phrase']} H={x['counts']['H']} F={x['counts']['F']}")+'</summary><p>H '+html.escape(show(x['H']))+'</p><p>F '+html.escape(show(x['F']))+'</p><pre>'+html.escape(json.dumps(x['edits'],indent=2))+'</pre></details>'
body+='<p><a href="LINES.json">All line receipts</a> · <a href="SELECTION.json">Training ranks and candidates</a></p>'
(R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Phrase readings v63</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}details{padding:12px;border-bottom:1px solid #bbb}pre{white-space:pre-wrap}p{line-height:1.7}</style>'+body,encoding='utf-8')
save('PROVENANCE.json',{str(p):o.sha(p) for p in [o.SOURCE,P/'phrase-transfer-v62/FREEZE.json',Path(__file__)]})
print(json.dumps({'lines':len(records),'ranks':[{k:v for k,v in x.items() if k!='top5'} for x in ranks],'test_disagreements':[x for x in records if x['split']=='test' and not x['count_agrees']]},indent=2))
