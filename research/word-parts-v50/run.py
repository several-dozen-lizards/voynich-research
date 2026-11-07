from pathlib import Path
import importlib.util,json,hashlib,collections,re,html
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('old',R.parent/'section-controls-v49/analyze.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def feats(w):
 out={'word:'+w}
 for n in range(1,len(w)+1):
  out.add('prefix:'+w[:n]);out.add('suffix:'+w[-n:])
  for i in range(1,len(w)-n):out.add('internal:'+w[i:i+n])
 return out
old.feats=feats
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 frozen=json.loads((R/'FREEZE.json').read_text())
 for p,h in frozen.items():assert digest(R/p)==h,p
 rows,events,features,shared=old.build()
 inventory=collections.defaultdict(lambda:collections.Counter())
 for e in events:
  for f in e['features']:inventory[f][e['tr']]+=1
 (R/'INVENTORY.json').write_text(json.dumps({f:dict(c)|{'screen_eligible':f in set(features)} for f,c in sorted(inventory.items())}),encoding='utf8')
 # Reuse unchanged v49 panel, support, permutation and exception rules.
 old.R=R;old.main()
 targets=[('2','B','Balneological','Botanical','prefix:qo'),('2','B','Botanical','Balneological','internal:od'),('1','A','Recipes','Botanical','internal:ke'),('1','A','Recipes','Botanical','suffix:eol')]
 audit=[]
 for hand,lang,a,b,feature in targets:
  pool=[e for e in events if e['hand']==hand and e['language']==lang and e['format']=='P' and e['pos']=='interior' and e['section'] in (a,b)]
  fs=collections.defaultdict(set)
  for e in pool:fs[e['folio']].add(e['section'])
  pool=[e for e in pool if len(fs[e['folio']])==1]
  # Fold assignment has no access to feature counts; H/F and all surfaces stay together.
  fold={}
  for sec in (a,b):
   folios=sorted({e['folio'] for e in pool if e['section']==sec},key=lambda f:hashlib.sha256(('v50:'+f).encode()).hexdigest())
   for i,f in enumerate(folios):fold[f]=i%3
  kind,part=feature.split(':')
  def family(w):
   if kind=='prefix':return w[len(part):]
   if kind=='suffix':return w[:-len(part)]
   i=w.find(part,1);return w[:i]+'|'+w[i+len(part):]
  def delta(es,ban=set(),familyban=set()):
   by=collections.defaultdict(list)
   for e in es:
    if e['w'] in ban or (feature in e['features'] and family(e['w']) in familyban):continue
    by[(e['section'],e['folio'])].append(feature in e['features'])
   rates={s:[sum(v)/len(v) for (sec,f),v in by.items() if sec==s] for s in (a,b)}
   valid=min(map(len,rates.values()))>=2
   return {'difference_pp':100*(sum(rates[a])/len(rates[a])-sum(rates[b])/len(rates[b])) if valid else None,'folios':{s:len(v) for s,v in rates.items()}}
  for tr in ('H','F'):
   es=[e for e in pool if e['tr']==tr];concentration={}
   for sec in (a,b):
    hits=[e for e in es if e['section']==sec and feature in e['features']];wc=collections.Counter(e['w'] for e in hits);fc=collections.Counter(family(e['w']) for e in hits)
    concentration[sec]={'hits':len(hits),'word_types':len(wc),'families':len(fc),'top1_share':sum(n for w,n in wc.most_common(1))/max(1,len(hits)),'top5_share':sum(n for w,n in wc.most_common(5))/max(1,len(hits)),'top_words':wc.most_common(10),'family_effective_count':len(hits)**2/sum(n*n for n in fc.values()) if fc else 0}
   folds=[]
   for k in range(3):
    train=[e for e in es if fold[e['folio']]!=k];test=[e for e in es if fold[e['folio']]==k]
    top=collections.Counter(e['w'] for e in train if feature in e['features']).most_common(5)
    fam=collections.Counter(family(e['w']) for e in train if feature in e['features']).most_common(5)
    folds.append({'fold':k,'test_folios':sorted({e['folio'] for e in test}),'train':delta(train),'heldout':delta(test),'heldout_without_train_top5_words':delta(test,{w for w,n in top}),'heldout_without_train_top5_families':delta(test,familyban={f for f,n in fam}),'removed_words':top})
   audit.append({'hand':hand,'variety':lang,'feature':feature,'higher_section':a,'comparison_section':b,'tr':tr,'concentration':concentration,'folds':folds})
 (R/'FAMILY-AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
 result=json.loads((R/'RESULTS.json').read_text());summary={'observed_features':len(inventory),'screened_features':len(features),'candidate_contrasts':len(result['candidates']),'exceptions':len(result['exceptions'])}
 print(json.dumps(summary));(R/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
 body='<h1>Word parts and family concentration — v50</h1><p>All observed contiguous EVA prefixes, suffixes, strict internal strings and whole words. No syllable or meaning inference. H/F are alternate readings. Same v49 controls and multiplicity correction, now a larger search family.</p><p>Three-fold folio tests are retrospective stability checks: these folios were already exposed in v49. No fresh confirmatory holdout is claimed. Top-five removal uses training folds only. Denominators are recomputed after removal. Families remove the focal sequence; internal families retain both flanks, using its first internal occurrence.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre>'
 body+='<h2>Four focal signals</h2><table><tr><th>Feature / reading</th><th>Higher section</th><th>Types / effective families</th><th>Top 5 share</th><th>Held-out differences (pp)</th><th>After removing training top 5 words</th></tr>'
 for r in audit:
  c=r['concentration'][r['higher_section']]
  fmt=lambda x:'NA' if x is None else f'{x:+.2f}'
  body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [r['feature']+' / '+r['tr'],r['higher_section'],f"{c['word_types']} / {c['family_effective_count']:.1f}",f"{c['top5_share']:.1%}",', '.join(fmt(f['heldout']['difference_pp']) for f in r['folds']),', '.join(fmt(f['heldout_without_train_top5_words']['difference_pp']) for f in r['folds'])])+'</tr>'
 body+='</table><h2>Full retained evidence</h2><p><a href="INVENTORY.json">Every observed feature, including sparse forms</a> · <a href="RESULTS.json">All tests and exceptions</a> · <a href="FAMILY-AUDIT.json">Word concentration, families, every fold and removals</a> · <a href="PROTOCOL.json">Frozen protocol</a></p><p>Historical grammar comparison remains unqualified: no independent prose/instruction/notation role labels are available. Casebooks are later than the fifteenth-century comparison sought. Distributional similarity cannot by itself identify an annotation grammar.</p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Voynich v50</title><style>body{font:17px system-ui;max-width:1150px;margin:40px auto;padding:20px;background:#f6f3eb;color:#192f30}td,th{padding:12px;border-bottom:1px solid #bbb;text-align:left}a{color:#176658}p{line-height:1.6}</style>'+body,encoding='utf8')
