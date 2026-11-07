from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protocol=dict(date='2026-10-23',scope='Reader image audit, not expert palaeographic adjudication or a sound/name test. Preserve g/m/y and word-boundary alternatives.',focal_loci=['f70v1.S2.6','f39r.P.4','f103r.P.35','f45v.P.6','f83r.P.5','f67v1.Y.3','f66r.W.1','f69r.R.2'],selection='First5 are anchor and already recorded cheg/chem disputes; last3 broaden samehand4 comparison to agreed ypcheg and cheg/cheim or cheg/chey alternatives. All were exposed in v87. No claim of blind discovery.',controls='On each focal page use nearest preceding and nearest following H complete tokens ending m as positive graphic comparators, in source order, preserving actual line position. Also inspect neighbouring line/label endings visible in each crop, without changing source readings. Missing control remains missing; no cross-hand pooling.',inspection='Inspect native-resolution crops with whole word and adjoining context, not only isolated shapes. Describe loop count, vertical/descending strokes, connections, nearby sign variation and available image clarity. Do not infer stroke order or ligature segmentation from static ink. Distinguish allograph candidate, distinct-sign candidate, positional convention candidate and unresolved.',position='Classify each occurrence as single-word unit, first/interior/final source token and paragraph/radial/individual-label format. Final token on circular/radial text is not automatically physical line margin; record separately. Single-word labels are not independent evidence for line-end convention.',corpus_diagnostic='Descriptive H final-g tokens across atlas; F counterpart only at shared source locus with exactly matching token slots and identical whole-word prefix before final character. Retain unalignable/disagreeing prefixes and missing F. Counts diagnose transcription alternatives, not real glyph equivalence. No significance test or broad script normalisation.',preservation='Do not overwrite H/K/V/U anchor agreement with elsewhere F m readings. No global g-to-m merge and no new rarity rescore in this audit. No historical names or sounds fitted.')
save('PROTOCOL.json',protocol);save('PRE-IMAGE-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]})
rows=json.loads(S.read_text());byloc=collections.defaultdict(list)
for x in rows:byloc[x[8]].append(x)
packet={};controls=[]
for loc in protocol['focal_loci']:
 a=byloc[loc];packet[loc]=a;h=next(x for x in a if x[0]=='H');page=h[1];flat=[(x,j,w) for x in rows if x[0]=='H' and x[1]==page for j,w in enumerate(x[9])]
 focal=[i for i,(x,j,w) in enumerate(flat) if x[8]==loc and w and w.endswith('g')]
 if not focal:continue
 at=focal[-1]
 for direction,inds in [('before',range(at-1,-1,-1)),('after',range(at+1,len(flat)))]:
  chosen=next(((x,j,w) for i in inds for x,j,w in [flat[i]] if w and w.endswith('m')),None)
  if chosen:
   x,j,w=chosen;controls.append(dict(focal=loc,direction=direction,control_locus=x[8],index=j,word=w,raw=x[10],alternates=byloc[x[8]]))
  else:controls.append(dict(focal=loc,direction=direction,status='no same-page H m-ending control'))
save('FOCAL-READINGS.json',packet);save('CONTROL-PACKET.json',controls)
diag=[]
for x in rows:
 if x[0]!='H':continue
 for j,w in enumerate(x[9]):
  if not w or not w.endswith('g'):continue
  fs=[f for f in byloc[x[8]] if f[0]=='F'];f=fs[0] if fs else None;fw=f[9][j] if f and len(f[9])==len(x[9]) else None
  diag.append(dict(locator=x[8],page=x[1],hand=x[3],format=x[5],index=j,H_word=w,H_source_position='single' if len(x[9])==1 else 'final' if j==len(x[9])-1 else 'first' if j==0 else 'interior',F_word=fw,F_status='missing' if f is None else 'different slot count' if len(f[9])!=len(x[9]) else 'same prefix' if fw and fw[:-1]==w[:-1] else 'prefix differs/unknown',F_raw=f[10] if f else None,H_raw=x[10]))
save('CORPUS-G-DIAGNOSTIC.json',diag)
print(json.dumps(dict(focal_loci=list(packet),controls=[{k:v for k,v in x.items() if k!='alternates'} for x in controls],H_final_g_tokens=len(diag),H_positions=dict(collections.Counter(x['H_source_position'] for x in diag)),F_same_prefix_endings=dict(collections.Counter(x['F_word'][-1] for x in diag if x['F_status']=='same prefix'))),indent=2))
