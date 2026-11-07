from pathlib import Path
import collections,datetime,hashlib,html,json,re,zipfile
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def digest(b):return hashlib.sha256(b).hexdigest()
prior=load(P/'exposure-history-v101/SCAN-FREEZE.json');paths=collections.defaultdict(list)
for s in prior['session_prefixes']:
 with Path(s['path']).open('rb') as f:b=f.read(s['bytes'])
 assert digest(b)==s['sha256']
 for line_num,line in enumerate(b.splitlines(),1):
  if b'attachments' not in line and b'.zip' not in line:continue
  try:d=json.loads(line)
  except json.JSONDecodeError:continue
  q=d.get('payload',{})
  if d.get('type')!='response_item' or q.get('type')!='message' or q.get('role')!='user':continue
  text='\n'.join(x.get('text','') for x in q.get('content',[]) if isinstance(x,dict))
  patterns=[r'C:[/\\]Users[/\\]lewis[/\\]\.codex[/\\]attachments[/\\][0-9a-f-]+[/\\]Pasted text\.txt',r'C:[/\\]Users[/\\]lewis[/\\]Downloads[/\\]claude[-A-Za-z0-9_ .]*\.zip']
  for pat in patterns:
   for m in re.finditer(pat,text,re.I):paths[str(Path(m.group()))].append(dict(thread_id=s['id'],history_line=line_num,timestamp=d.get('timestamp')))
protocol={'scope':'Follow explicitly attached Claude pasted-text histories and named Claude ZIP packages from the eight fixed v101 histories. No general Downloads or attachment-directory content scan; no external account access.',
 'freeze':'Freeze attachment byte hashes, availability, and historical attachment references before reading text or ZIP members for reserve evidence. Preserve missing files. Deduplicate identical text by content hash, not by name.',
 'read_only':'Never execute archive scripts or extract files. Inspect text-like ZIP members at <=2MiB/member and <=32MiB/archive; record every skipped entry. No binaries, model fits, source order statistics, new inference or power.',
 'evidence':'Search source text for reserve/custody terms and actual page/locus mentions. Exact locator matches support explicit textual reference, not proof every token was viewed. Page mentions do not imply all lines inspected. Reported manuscript findings are inherited claims, not reproduced results. Reserve phrases require review of subject, chronology, candidate IDs and custody; vocabulary unseen and synthetic test data are not manuscript reserves.',
 'units':'Map explicit exact locators to the 1783 v101 reading-loci by locator only; such a mention does NOT specify H or F unless supported in context. Keep H/F and hands separate and mark reading applicability unspecified. Do not assign evidence to missing F or silently resolve f73 hand conflict.',
 'gate':'No true reserve admitted automatically. Power and scoring stay CLOSED unless a credible protected passage list and exposure/custody history are established. Keep all v97/v98 failed gates and unrun v98 banks. Local saved attachments cannot certify the rest of an external Claude conversation.',
 'limits':'Bounded provenance audit only. No claim all possible external files or conversations were exhausted; missing and size-limited material remain gaps.'}
inventory=[];payloads={}
for p,refs in sorted(paths.items()):
 path=Path(p);rec=dict(path=p,refs=refs,exists=path.is_file())
 if rec['exists']:
  data=path.read_bytes();rec.update(bytes=len(data),sha256=digest(data));payloads[p]=data
 inventory.append(rec)
freeze=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol=protocol,script_sha256=digest(Path(__file__).read_bytes()),v101_history_freeze_sha256=digest((P/'exposure-history-v101/SCAN-FREEZE.json').read_bytes()),attachments=inventory)
if (R/'FREEZE.json').exists():raise RuntimeError('Preserve completed attachment audit; later source changes need a new attempt')
save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
texts=[];archives=[]
for p,b in payloads.items():
 if p.lower().endswith('.txt'):
  txt=b.decode('utf-8-sig',errors='replace');texts.append(dict(source=p,member=None,sha256=digest(b),text=txt))
 else:
  import io
  selected=0
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   for info in z.infolist():
    reason=None
    if info.is_dir():reason='directory'
    elif Path(info.filename).suffix.lower() not in ('.txt','.md','.py','.json','.csv','.toml','.yaml','.yml','.log'):reason='not selected text format'
    elif info.file_size>2*1024**2:reason='member exceeds frozen 2MiB cap'
    elif selected+info.file_size>32*1024**2:reason='archive exceeds frozen 32MiB text cap'
    rec=dict(archive=p,member=info.filename,uncompressed_bytes=info.file_size,read=reason is None,reason=reason)
    if reason is None:
     mb=z.read(info);selected+=len(mb);rec['sha256']=digest(mb)
     texts.append(dict(source=p,member=info.filename,sha256=digest(mb),text=mb.decode('utf-8-sig',errors='replace')))
    archives.append(rec)
save('ARCHIVE-MEMBERS.json',archives)
reserve=re.compile(r'untouched|unseen|hold[ -]?out|held[ -]?out|reserv(?:e|ed)|blind(?:ed)?|sequester|never (?:seen|used|inspect)|not (?:seen|used|inspect)',re.I)
pages=re.compile(r'\bf\d+[rv]\d*\b');locators=re.compile(r'\bf\d+[rv]\d*\.[A-Z][A-Za-z0-9]*\.[A-Za-z0-9]+\b')
seen=set();units=[];hits=[];mentions=[]
for t in texts:
 duplicate=t['sha256'] in seen;seen.add(t['sha256']);unit=dict(source=t['source'],member=t['member'],sha256=t['sha256'],characters=len(t['text']),duplicate_content=duplicate);units.append(unit)
 if duplicate:continue
 for i,line in enumerate(t['text'].splitlines(),1):
  ls=sorted(set(locators.findall(line)));pg=sorted(set(pages.findall(line)))
  if ls or pg:mentions.append(dict(source=t['source'],member=t['member'],line=i,locators=ls,pages=pg,excerpt=line[:2500],reading_applicability='unspecified unless resolved by manual context'))
  if reserve.search(line):hits.append(dict(source=t['source'],member=t['member'],line=i,excerpt=line[:5000]))
save('TEXT-UNITS.json',units);save('RESERVE-LEADS.json',hits);save('PASSAGE-MENTIONS.json',mentions)
ledger=load(P/'exposure-history-v101/LOCUS-EXPOSURE-REVIEWED.json');mapped=[]
index=collections.defaultdict(list)
for m in mentions:
 for loc in m['locators']:index[loc].append(dict(source=m['source'],member=m['member'],line=m['line']))
for x in ledger:
 y={k:x[k] for k in ['reading','page','numbered_folio','section','hand','variety','format','locus']}
 y['exact_locator_mentions']=index.get(x['locus'],[]);y['applicability']='Locator reference only; reading unspecified, not an H/F outcome or claim of separate inspection.';y['reserve_admitted']=False;mapped.append(y)
save('LOCUS-MENTION-MAP.json',mapped)
summary=[];groups=collections.defaultdict(list)
for x in mapped:groups[(x['section'],x['hand'],x['variety'],x['format'],x['reading'])].append(x)
for key,rr in sorted(groups.items()):summary.append(dict(zip(['section','hand','variety','format','reading'],key),loci=len(rr),loci_with_reading_unspecified_locator_reference=sum(bool(x['exact_locator_mentions']) for x in rr),reserve_admitted=0))
save('STRATA.json',summary)
old=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert old['status']=='FAIL' and old['robustness_banks_not_run']==[2,3]
for x in inventory:
 if x['exists']:assert digest(Path(x['path']).read_bytes())==x['sha256']
save('CHECKS.json',dict(frozen_input_hashes='PASS',mapped_loci=len(mapped),strata=len(summary),H_F_hand_format_separation='PASS',archive_execution='NONE',extraction='NONE',new_order_score='NOT COMPUTED',power='NOT RUN',v98='FAIL unchanged; banks2/3 unrun',reserve_status='PENDING DOCUMENTARY REVIEW; NOT ADMITTED'))
print(json.dumps(dict(attachments=len(inventory),available=sum(x['exists'] for x in inventory),text_units=len(units),unique_contents=len(seen),reserve_leads=len(hits),passage_reference_lines=len(mentions),archive_entries=len(archives))))
