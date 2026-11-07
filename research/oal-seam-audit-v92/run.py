from pathlib import Path
import json,hashlib,collections,time,html
P=Path(__file__).resolve().parent; S=P.parent/'complete-atlas-v56/ROWS.json'
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
save('PRE-SEARCH-FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'code_sha256':sha(Path(__file__)),'input_sha256':sha(S),'scope':'Exposed descriptive claims only; no confirmatory test or semantic inference. Separate18 readings, hand,section,raw format. Literal oal whole,initial including whole,noninitial and substring; oalch nested subset. No g/m substitution, joining or token repair. alch seam at al|ch; standalone component attestation descriptive only. No invented definition for quoted0.68 similarity.'})
rows=json.loads(S.read_text()); codes=sorted({r[0] for r in rows}); counts=[];events=[];loci=set();vocab=collections.defaultdict(collections.Counter);local=collections.defaultdict(collections.Counter)
for r in rows:
    vocab[r[0]].update(w for w in r[9] if w);local[(r[0],r[2],r[3],r[5])].update(w for w in r[9] if w)
groups=collections.defaultdict(list)
for r in rows:groups[(r[0],r[2],r[3],r[5])].append(r)
for (code,section,hand,fmt),rr in groups.items():
    words=[w for r in rr for w in r[9] if w]
    counts.append(dict(reading=code,section=section,hand=hand,format=fmt,tokens=len(words),oal_whole=sum(w=='oal' for w in words),oal_initial=sum(w.startswith('oal') for w in words),oal_noninitial=sum('oal' in w and not w.startswith('oal') for w in words),oal_any=sum('oal' in w for w in words),oalch_any=sum('oalch' in w for w in words),alch_any=sum('alch' in w for w in words)))
for r in rows:
    for j,w in enumerate(r[9]):
        if not w or not ('oal' in w or 'alch' in w):continue
        e=dict(reading=r[0],page=r[1],section=r[2],hand=r[3],format=r[5],locator=r[8],token_index=j,word=w,raw=r[10],context=r[9][max(0,j-2):j+3],oal_whole=w=='oal',oal_initial=w.startswith('oal'),oal_any='oal' in w,oalch_any='oalch' in w)
        if 'alch' in w:
            i=w.index('alch')+2;left,right=w[:i],w[i:]; lc=local[(r[0],r[2],r[3],r[5])]
            e['seam']=dict(left=left,right=right,left_global=vocab[r[0]][left],right_global=vocab[r[0]][right],left_same_stratum=lc[left],right_same_stratum=lc[right])
        events.append(e);loci.add(r[8])
save('COUNTS.json',counts);save('EVENTS.json',events)
save('ALTERNATES.json',{l:[dict(reading=r[0],tokens=r[9],raw=r[10]) for r in rows if r[8]==l] for l in sorted(loci)})
summary=[]
for c in codes:
    cc=[x for x in counts if x['reading']==c];ee=[e for e in events if e['reading']==c and e['oal_any']]
    totals={k:sum(x[k] for x in cc) for k in ['tokens','oal_whole','oal_initial','oal_noninitial','oal_any','oalch_any','alch_any']}
    sections={s:{k:sum(x[k] for x in cc if x['section']==s) for k in totals} for s in sorted({x['section'] for x in cc})}
    summary.append(dict(reading=c,**totals,sections=sections,oal_words=dict(collections.Counter(e['word'] for e in ee))))
save('SUMMARY.json',summary)
for c in codes:assert sum(x['oal_any'] for x in counts if x['reading']==c)==sum(e['oal_any'] for e in events if e['reading']==c)
h=['<!doctype html><meta charset="utf-8"><title>oal and the al|ch seam · v92</title><style>body{font:17px/1.55 system-ui;max-width:1200px;margin:auto;padding:32px;background:#11202a;color:#e7eeee}a{color:#99d4ef}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #51636c;padding:8px;text-align:left}h1,h2{color:#a8e1c9}</style><h1>oal distribution and literal al|ch splits</h1><p>Descriptive audit of exposed claims. Transcriptions are alternative readings, not independent replications. No morphology, sound values or star identifications assigned.</p><h2>Counts by reading</h2><p>Initial includes the whole word; noninitial excludes initial matches. All counts are token occurrences, not distinct word types. Unknown/uncertain atlas tokens remain excluded rather than repaired.</p><table><tr><th>Reading</th><th>Tokens</th><th>oal whole</th><th>oal initial</th><th>oal noninitial</th><th>oal anywhere</th><th>oalch anywhere</th></tr>']
for s in summary:h.append('<tr>'+''.join('<td>'+str(s[k])+'</td>' for k in ['reading','tokens','oal_whole','oal_initial','oal_noninitial','oal_any','oalch_any'])+'</tr>')
h+=['</table><h2>Section denominators: H, F, U, V separately</h2><table><tr><th>Reading / section</th><th>Tokens</th><th>Whole</th><th>Initial</th><th>Noninitial</th><th>Any / 10k tokens</th><th>oalch</th></tr>']
for s in summary:
    if s['reading'] not in ['H','F','U','V']:continue
    for section,t in s['sections'].items():h.append('<tr>'+''.join('<td>'+str(x)+'</td>' for x in [s['reading']+' / '+section,t['tokens'],t['oal_whole'],t['oal_initial'],t['oal_noninitial'],f'{t["oal_any"]} / {10000*t["oal_any"]/max(1,t["tokens"]):.2f}',t['oalch_any']])+'</tr>')
h+=['</table><h2>Every oal occurrence in H/F/U/V</h2><table><tr><th>Reading / locus</th><th>Section / hand / format</th><th>Word</th><th>Neighboring tokens</th><th>Literal split and component counts</th></tr>']
for e in events:
    if not e['oal_any'] or e['reading'] not in ['H','F','U','V']:continue
    h.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [e['reading']+' '+e['locator'],[e['section'],e['hand'],e['format']],e['word'],e['context'],e.get('seam','')])+'</tr>')
h+=['</table><h2>Interpretation limits</h2><p>Possible al|ch components being independently attested does not establish a historical word boundary. Frequent strings can form such splits by chance. The quoted similarity0.68 lacks a named metric, weighting, sample and comparison strata, so it is not reproduced here. Literal cheg is not chem: g/m alternatives must remain separate source readings.</p><p>Section concentration cannot by itself establish a prefix meaning or a Pleiades mansion. A rare combination of otherwise widespread components can still have a distinct use; neither frequency outcome decides its semantics. Hand and format denominators are retained in the complete counts, without pooling unsupported comparisons.</p><p><a href="SUMMARY.json">All summaries</a> · <a href="COUNTS.json">Hand/section/format counts</a> · <a href="EVENTS.json">Every event and seam component count</a> · <a href="ALTERNATES.json">All available readings at every matched locus</a> · <a href="PRE-SEARCH-FREEZE.json">Rules and hashes</a></p>']
(P/'report.html').write_text('\n'.join(h),encoding='utf-8')
print(json.dumps([s for s in summary if s['reading'] in ['H','F','U','V']],indent=2))
