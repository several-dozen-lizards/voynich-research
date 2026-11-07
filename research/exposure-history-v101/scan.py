from pathlib import Path
import collections,datetime,hashlib,json,re
R=Path(__file__).resolve().parent;P=R.parent
def save(n,d):(R/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
ids=['01a160c2-56f0-7303-b3bf-ed8594c6ec40','01a16ab3-be61-74b2-95d2-d38c0ba2a642','01a16491-3972-7430-a33e-0da82c066bb4','01a16529-fd24-7d02-99e0-9a5bef58ed94','01a16601-47fd-7c73-aa74-e1137076d1d5','01a160c1-c17b-7c13-9255-3817d6dc0147','01a15c3d-56da-7f02-bc15-2522dc396abd','01a16ff2-0158-7b60-a624-317903618103']
sources=[]
for id in ids:
    paths=list(Path('C:/Users/lewis/.codex/sessions/2026/10').rglob('*'+id+'.jsonl'))
    assert len(paths)==1,(id,paths)
    b=paths[0].read_bytes();sources.append((id,paths[0],b))
protocol={'task':'Trace historical exposure of the 1783 reading-loci marked freshness_uncertified in v100. No newly computed target frequency, arrangement score, p-value, actual-layout power or rescoring.',
 'method':'Read existing relevant research chats and their source/program/result receipts. Freeze finite byte prefixes of eight local session histories because some are active and append-only. Preserve source hashes, offsets and message timestamps. Supplement with accessible ChatGPT snapshots; inaccessible reference-only assistant contents remain a gap.',
 'units':'H/F separate, exact source locus, hand, Currier variety and raw format. H/F overlap is not independent replication. Alternate image/text readings never silently replace missing F. Atlas metadata hand3 versus historical hand4 conflicts remain explicit.',
 'evidence_levels':'Availability != actual inspection != feature computation != neighbor/order computation. Exact-locus claims require a saved event/row or a verified source-selector plus matching metadata; page references alone support page-level exposure, never every line. Aggregate historical results may remain pooled; do not invent separate hand outcomes.',
 'freshness':'A fresh fitting split, untested new statistic, new hand or alternate transcription does not establish historical non-exposure. Conversely broad atlas availability alone does not demonstrate human inspection. No reserve admission without credible protected unit list and exposure/custody evidence. Absence of a local record cannot prove no external exposure.',
 'gates':'No candidate is automatically admitted by this audit. Power and scoring closed unless genuine reserve established, then separate frozen power qualification before scoring. Preserve v97/v98 failures and unrun v98 banks; do not rerun other chats or message them.',
 'scope':'Eight named local Codex research histories, current read_thread snapshots, two relevant ChatGPT chats, and specifically linked artifacts. Not all external Claude work, deleted records or inaccessible assistant content. This is a historical trace, not hypothesis confirmation.'}
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(json.dumps(protocol,sort_keys=True).encode()),'scanner_sha256':sha(Path(__file__).read_bytes()),'v100_ledger_sha256':sha((P/'untouched-passage-audit-v100/LOCUS-LEDGER.json').read_bytes()),'session_prefixes':[dict(id=id,path=str(p),bytes=len(b),sha256=sha(b)) for id,p,b in sources]}
if (R/'SCAN-FREEZE.json').exists():raise RuntimeError('Preserve original trace; use a new audit for later histories')
save('PROTOCOL.json',protocol);save('SCAN-FREEZE.json',freeze)
pattern=re.compile(r'astronom|astrolog|recipes|pharmaceut|rosett|rose obverse|f85r|f86v|f88|f89|f99|f100|f101|f102|f6[789]|f7[0-3]|section.profile|all_P|hold.?out|reserve|untouched',re.I)
out=[];index=[]
for id,p,b in sources:
    total=matched=0
    for line_num,line in enumerate(b.splitlines(),1):
        try:d=json.loads(line)
        except json.JSONDecodeError:continue
        q=d.get('payload',{})
        if d.get('type')!='response_item' or q.get('type')!='message' or q.get('role') not in ('assistant','user'):continue
        txt='\n'.join(x.get('text','') for x in q.get('content',[]) if isinstance(x,dict));total+=1
        if not pattern.search(txt):continue
        matched+=1
        out.append(dict(thread_id=id,path=str(p),jsonl_line=line_num,timestamp=d.get('timestamp'),role=q.get('role'),phase=q.get('phase'),text=txt,source_line_sha256=sha(line)))
    index.append(dict(thread_id=id,path=str(p),messages=total,matched_messages=matched,snapshot_bytes=len(b)))
save('HISTORY-EXCERPTS.json',out);save('HISTORY-COVERAGE.json',index)
print(json.dumps(dict(histories=len(sources),messages=sum(x['messages'] for x in index),matched=len(out))))
