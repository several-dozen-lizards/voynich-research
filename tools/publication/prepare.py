"""Build a copy-first, hash-accounted research publication snapshot.

No experiment, model fitting, held-out scoring, or live service is started.
The inventory is an explicit input; excluded contents are not silently copied.
"""
import collections, csv, gzip, hashlib, html, io, json, re, shutil, time, sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
OUT = ROOT / 'github-export' / 'voynich-research'
INV = json.loads((TOOLS/'inventory.json').read_text(encoding='utf-8'))
TEXT = {'.md','.txt','.json','.jsonl','.csv','.tsv','.py','.mjs','.js','.html','.css','.yml','.yaml','.toml','.ini','.cfg','.xml','.bib','.ris','.log','.r','.sh','.ps1','.bat','.properties','.sha256'}
RUNTIME = {'.runtime','.analysis-runtime','.analysis-cache','.dependency-cache','.matplotlib-cache','.venv','venv','node_modules','__pycache__','runtime','.cache'}
PRIVATE = {'private','vault','registrar-only','rater-only','rater-a','rater-b','packets','sealed','human-registration','fresh-reserves'}
THIRD_PARTY = {'sources','upstream','corpora'}
SECRET = re.compile(rb'(?:\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}|\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
URL = re.compile(r'https?://[^\s<>"\x27`\\\]\[{}|]+')

def classify(rel):
    p=Path(rel); parts=[x.lower() for x in p.parts]; ext=p.suffix.lower(); name=p.name.lower()
    if any(x.startswith('.') or x in RUNTIME for x in parts): return 'dependency-or-cache'
    if any(x in PRIVATE for x in parts): return 'custody-or-blinding-review'
    metadata=bool(re.search(r'^(?:sources?|source[-_](?:manifest|audit|provenance|retrieval|notes|receipts)|license|copying|notice|manifest|acquisition|retrieval|verification|audit|readme|provenance|sha256|findings|metadata|qa|checks?)(?:[._-]|$)',name)) and ext in {'.md','.txt','.json','.csv'}
    if any(x in THIRD_PARTY for x in parts[:-1]) and not metadata: return 'third-party-source-review'
    if 'raw' in parts[:-1] and not metadata and not rel.startswith('image-context-v4/ratings/'): return 'third-party-source-review'
    if rel.startswith(('voynich-lab/data/voynich/','voynich-lab/data/known/')) and not metadata: return 'third-party-source-review'
    if ext in {'.pt','.pth','.pkl','.pickle','.npz','.npy','.safetensors','.bin','.onnx'}: return 'model-or-binary-data'
    if ext in {'.zip','.gz','.tar','.7z','.rar'}: return 'nested-archive-review'
    if ext in {'.pdf','.jpg','.jpeg','.tif','.tiff','.webp','.ttf','.otf','.woff','.woff2'}: return 'third-party-media-review'
    if ext=='.png' and '/report/' not in rel and '/results/' not in rel and not name.startswith(('power-','power_')): return 'third-party-media-review'
    if ext not in TEXT | {'.png','.svg'} and name not in {'license','copying','makefile','dockerfile','requirements','notice'}: return 'unclassified-review'
    return 'publish'

def link(rel): return quote(rel, safe='/._-')
def write(rel,text):
    p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8',newline='\n')

def copy_one(r):
    rel=r['path']; src=ROOT/rel; reason=classify(rel); urls=set()
    row={'original_path':rel,'bytes':r.get('bytes',0),'disposition':reason,'published_path':'','sha256':'','git_blob':'','snapshot_stat_changed':False}
    if reason!='publish': return row,urls
    try:
        before=src.stat()
        dstrel='research/'+rel
        if before.st_size>1_000_000: dstrel+='.gz'
        dst=OUT/dstrel; dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():
            try:
                source_hash=hashlib.sha256(); restored_hash=hashlib.sha256(); chunks=[]; tail=b''; secret=False
                with src.open('rb') as incoming:
                    for chunk in iter(lambda:incoming.read(1024*1024),b''):
                        source_hash.update(chunk)
                        if SECRET.search(tail+chunk): secret=True
                        tail=chunk[-256:]
                        if before.st_size<=10_000_000 and src.suffix.lower() in TEXT: chunks.append(chunk)
                with (gzip.open(dst,'rb') if dstrel.endswith('.gz') else dst.open('rb')) as restored:
                    for chunk in iter(lambda:restored.read(1024*1024),b''): restored_hash.update(chunk)
                if not secret and source_hash.digest()==restored_hash.digest():
                    data_hash=hashlib.sha256(); git_hash=hashlib.sha1(b'blob '+str(dst.stat().st_size).encode()+b'\0')
                    with dst.open('rb') as saved:
                        for chunk in iter(lambda:saved.read(1024*1024),b''): data_hash.update(chunk); git_hash.update(chunk)
                    after=src.stat()
                    if before.st_size!=after.st_size or before.st_mtime_ns!=after.st_mtime_ns: raise RuntimeError('file changed during reuse')
                    row.update(sha256=source_hash.hexdigest(),bytes=before.st_size,published_path=dstrel,published_bytes=dst.stat().st_size,published_sha256=data_hash.hexdigest(),git_blob=git_hash.hexdigest(),source_mtime_ns=before.st_mtime_ns,snapshot_stat_changed=(before.st_size!=r.get('bytes') or ('mtime_ns' in r and before.st_mtime_ns!=r['mtime_ns'])))
                    if chunks:
                        for url in URL.findall(b''.join(chunks).decode('utf-8',errors='replace')):
                            url=url.rstrip('.,;:)')
                            try:
                                host=urlsplit(url).hostname or ''
                                if host and host not in {'localhost','127.0.0.1','0.0.0.0'} and not any(x in url.lower() for x in ['access_token=','api_key=','token=','password=']): urls.add(url)
                            except ValueError: pass
                    return row,urls
            except (OSError,EOFError,gzip.BadGzipFile): pass
        original_hash=hashlib.sha256(); size=0; chunks=[]; tail=b''; secret=False
        with src.open('rb') as incoming, dst.open('wb') as raw_out:
            outgoing=gzip.GzipFile(filename='',mode='wb',fileobj=raw_out,compresslevel=6,mtime=0) if dstrel.endswith('.gz') else raw_out
            try:
                for chunk in iter(lambda:incoming.read(1024*1024),b''):
                    original_hash.update(chunk); size+=len(chunk); outgoing.write(chunk)
                    if SECRET.search(tail+chunk): secret=True
                    tail=chunk[-256:]
                    if before.st_size<=10_000_000 and src.suffix.lower() in TEXT: chunks.append(chunk)
            finally:
                if outgoing is not raw_out: outgoing.close()
        after=src.stat()
        if before.st_size!=after.st_size or before.st_mtime_ns!=after.st_mtime_ns: raise RuntimeError('file changed during copy')
        row['snapshot_stat_changed']=(size!=r.get('bytes') or ('mtime_ns' in r and before.st_mtime_ns!=r['mtime_ns']))
        if secret:
            dst.unlink(); row['disposition']='credential-pattern-review'; return row,urls
        data_hash=hashlib.sha256(); git_hash=hashlib.sha1(b'blob '+str(dst.stat().st_size).encode()+b'\0')
        with dst.open('rb') as published:
            for chunk in iter(lambda:published.read(1024*1024),b''): data_hash.update(chunk); git_hash.update(chunk)
        row.update(sha256=original_hash.hexdigest(),bytes=size,published_path=dstrel,published_bytes=dst.stat().st_size,published_sha256=data_hash.hexdigest(),git_blob=git_hash.hexdigest(),source_mtime_ns=before.st_mtime_ns)
        if chunks:
            for url in URL.findall(b''.join(chunks).decode('utf-8',errors='replace')):
                url=url.rstrip('.,;:)')
                try:
                    host=urlsplit(url).hostname or ''
                    if host and host not in {'localhost','127.0.0.1','0.0.0.0'} and not any(x in url.lower() for x in ['access_token=','api_key=','token=','password=']): urls.add(url)
                except ValueError: pass
    except Exception as e: row['disposition']='copy-error'; row['error']=str(e); row['published_path']=''
    return row,urls

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=[]; studies=collections.defaultdict(list); sources=collections.defaultdict(set); totals=collections.Counter(); errors=[]
    start=time.time()
    prior={}
    journal=TOOLS/'progress.jsonl'
    if journal.exists():
        for line in journal.read_text(encoding='utf-8').splitlines():
            try:
                saved=json.loads(line); prior[saved['row']['original_path']]=saved
            except (ValueError,KeyError): pass
    def resumable(r):
        saved=prior.get(r['path'])
        if saved and saved['row']['disposition']!='copy-error' and saved['row']['disposition']==classify(r['path']):
            row=saved['row']
            if not row['published_path']: return row,set(saved['urls'])
            stat=(ROOT/r['path']).stat()
            if stat.st_mtime_ns==row.get('source_mtime_ns') and stat.st_size==row['bytes'] and (OUT/row['published_path']).exists(): return row,set(saved['urls'])
        return copy_one(r)
    executor=ThreadPoolExecutor(max_workers=8)
    ordered=sorted(INV['files'],key=lambda r:r['path'])
    def bounded_results():
        for offset in range(0,len(ordered),256):
            yield from executor.map(resumable,ordered[offset:offset+256])
    results=bounded_results()
    progress=journal.open('a',encoding='utf-8')
    for n,(row,urls) in enumerate(results):
        rel=row['original_path']
        manifest.append(row); studies[rel.split('/')[0]].append(row); totals[row['disposition']]+=1
        for url in urls: sources[url].add(row['published_path'])
        progress.write(json.dumps({'row':row,'urls':sorted(urls)})+'\n')
        if n%256==0: progress.flush()
        if row['disposition']=='copy-error': errors.append(rel)
        if n%2000==0: print(json.dumps({'processed':n,'published':totals['publish'],'seconds':round(time.time()-start)}),flush=True)
    executor.shutdown()
    progress.close()
    finalize(manifest,sources)

def finalize(manifest,sources):
    studies=collections.defaultdict(list); totals=collections.Counter(); errors=[]
    for row in manifest:
        current=classify(row['original_path'])
        if not row['published_path'] and current=='publish' and row['disposition'] not in {'publish','credential-pattern-review'}:
            updated,found=copy_one({'path':row['original_path'],'bytes':row['bytes']})
            row.clear(); row.update(updated)
            for url in found: sources.setdefault(url,set()).add(row['published_path'])
        if row['published_path'] and current!='publish':
            p=(OUT/row['published_path']).resolve()
            if not p.is_relative_to(OUT.resolve()): raise RuntimeError('unsafe staged-path removal')
            p.unlink(missing_ok=True)
            row.update(disposition=current,published_path='',published_bytes=0,published_sha256='',git_blob='')
        studies[row['original_path'].split('/')[0]].append(row); totals[row['disposition']]+=1
        if row['disposition']=='copy-error': errors.append(row['original_path'])
    published_paths={r['published_path'] for r in manifest if r['published_path']}
    sources={url:set(paths)&published_paths for url,paths in sources.items() if set(paths)&published_paths}
    write('catalog/FILES.json',json.dumps(manifest,indent=2))
    buf=io.StringIO(newline=''); fields=['original_path','bytes','disposition','published_path','sha256','published_sha256','git_blob','snapshot_stat_changed']
    w=csv.DictWriter(buf,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(manifest); write('catalog/FILES.csv',buf.getvalue())
    source_rows=[{'url':u,'occurrences':sorted(ps)} for u,ps in sorted(sources.items())]
    write('catalog/SOURCE-LINKS.json',json.dumps(source_rows,indent=2))
    summary={'snapshot_date':'2026-11-07','assembly_finished_utc':datetime.now(timezone.utc).isoformat(),'scope':'Voynich workspace; Indus excluded by user','inventory_files':len(manifest),'studies':len(studies)-int('CURRENT-RESEARCH.txt' in studies),'dispositions':dict(totals),'published_bytes':sum(r.get('published_bytes',0) for r in manifest),'source_links':len(sources),'errors':errors,'source_stat_drift':sum(r['snapshot_stat_changed'] for r in manifest),'skipped_directories':INV['skipped_directories']}
    write('catalog/SNAPSHOT.json',json.dumps(summary,indent=2))
    if INV.get('assembly_cutoff_utc'):
        summary['inventory_cutoff_utc']=INV['assembly_cutoff_utc']
        write('catalog/SNAPSHOT.json',json.dumps(summary,indent=2))
    index=['# Study catalogue','','Paths retain the original workspace organization. Each study page links every copied report, check receipt, source record, protocol and script; the full file ledger also records material not published. Folder names and version numbers are historical identifiers, not a single global chronology.','', '| Study | Published files | Indexed exclusions | Browse |','|---|---:|---:|---|']
    source_index=['# Sources and provenance','','This is an index of retained local source records. It does not certify every quoted claim, license, URL, or transcription ancestry. Retrieval failures and corrections remain in their owning records. URLs were extracted from the archived text and have **not** all been revisited for this publication. The machine-readable [URL occurrence ledger](catalog/SOURCE-LINKS.json) records where each URL appeared; generated/example URLs can occur and are not automatically bibliographic citations.','']
    checks=['# Checks and verification','','These are historical check artifacts, copied without rerunning the experiments. A passing engineering check is not semantic validation. Read each protocol and result together; resource failures, invalid trials, reused sources, low power and unsupported panels retain their recorded limits.','']
    findings=['# Findings and reports','','The links below point to the retained owning reports, including negative and inconclusive results. The [historical chronology](research/CURRENT-RESEARCH.txt) is incomplete for later work; the lab extension and result reports remain separate owners.','']
    for study,rows in sorted(studies.items()):
        if study=='CURRENT-RESEARCH.txt': continue
        pub=[r for r in rows if r['published_path']]; excluded=[r for r in rows if not r['published_path']]
        doc='catalog/studies/'+study+'.md'
        index.append(f'| {study} | {len(pub)} | {len(excluded)} | [Study record]({link(doc)}) |')
        page=[f'# {study}','','Historical paths and bytes are preserved. Compression is indicated by `.gz` or `.xz`; uncompressed SHA-256 values are in the file ledger.','']
        buckets=collections.defaultdict(list)
        for r in pub:
            name=Path(r['original_path']).name.lower()
            if re.search(r'report|readme|decision|held-up|status|handoff|conclusion',name): bucket='Reports and findings'
            elif re.search(r'verif|check|audit|qualif|control|test|receipt|assert',name): bucket='Checks, controls and receipts'
            elif re.search(r'source|provenance|license|citation|bibliog|retrieval|reference',name): bucket='Sources and provenance'
            elif re.search(r'protocol|freeze|spec|registration|plan',name): bucket='Protocols and freezes'
            elif Path(name).suffix in {'.py','.mjs','.js','.sh','.ps1','.r'}: bucket='Code'
            else: bucket='Data and other artifacts'
            buckets[bucket].append(r)
        for bucket in ['Reports and findings','Checks, controls and receipts','Sources and provenance','Protocols and freezes','Code','Data and other artifacts']:
            rs=buckets[bucket]
            if not rs: continue
            page += ['## '+bucket,'']
            for r in rs:
                dest=r['published_path']; label=r['original_path'][len(study)+1:]
                page.append(f'- [{label}](../../{link(dest)})'+(' (gzip)' if dest.endswith('.gz') else ' (xz)' if dest.endswith('.xz') else ''))
            page.append('')
        if excluded:
            page += ['## Indexed exclusions','','See [the complete file ledger](../FILES.csv) for exact paths, sizes and reasons.','']
            page += [f'- {reason}: {count} files' for reason,count in sorted(collections.Counter(r['disposition'] for r in excluded).items())]
        if len(page)>350:
            chunks=[page[i:i+250] for i in range(0,len(page),250)]
            for i,chunk in enumerate(chunks,1):
                write(f'catalog/studies/{study}--{i:03d}.md',f'# {study}: catalogue part {i}\n\n[Study index]({study}.md)\n\n'+'\n'.join(chunk)+'\n')
            write(doc,f'# {study}\n\n{len(pub)} copied files; {len(excluded)} indexed exclusions. This catalogue is paginated for GitHub.\n\n'+'\n'.join(f'- [Part {i}]({study}--{i:03d}.md)' for i in range(1,len(chunks)+1))+'\n\n[Full file ledger](../FILES.csv)\n')
        else:
            write(doc,'\n'.join(page)+'\n')
        for bucket,target in [('Sources and provenance',source_index),('Checks, controls and receipts',checks),('Reports and findings',findings)]:
            rs=buckets[bucket]
            if rs:
                target += ['## '+study,'',f'[Full study record]({link(doc)})','']
                # Full lists are on each study page; these landing pages stay navigable.
                preferred=sorted(rs,key=lambda r:(len(Path(r['original_path']).parts),r['original_path']))[:8]
                target += [f'- [{r["original_path"]}]({link(r["published_path"])})' for r in preferred]; target.append('')
    write('STUDIES.md','\n'.join(index)+'\n'); write('SOURCES.md','\n'.join(source_index)+'\n'); write('CHECKS.md','\n'.join(checks)+'\n'); write('FINDINGS.md','\n'.join(findings)+'\n')
    # Derive a dated chronology without inventing ordering across independent arms.
    history=(ROOT/'CURRENT-RESEARCH.txt').read_text(encoding='utf-8')
    write('CHRONOLOGY.md','# Chronology and ownership\n\nThe [original running chronology](research/CURRENT-RESEARCH.txt) is preserved verbatim. It covers many early studies, but is not an up-to-date global status file. Later lab extension/result reports and freezes carry their own dates and ownership.\n\nSee [latest recorded work](LATEST.md), the [study catalogue](STUDIES.md), and each study’s registration and run records. Filesystem modification times are inventory metadata, not reliable experiment dates.\n')
    write('README.md',f'''# Voynich research archive

Research notes, experiments, code, checks, controls, findings, failures, and source records from the Voynich workspace, collected on 7 November 2026. This archive does not establish a decipherment, translation, language identification, or historical mechanism.

## Start here

- [Latest recorded work and limits](LATEST.md)
- [All {summary['studies']} study folders](STUDIES.md)
- [Browse by research theme](MAP.md)
- [Findings and owning reports](FINDINGS.md)
- [Checks, controls and verification](CHECKS.md)
- [Sources and provenance](SOURCES.md)
- [Chronology and ownership](CHRONOLOGY.md)
- [Coverage, omissions and publication policy](COVERAGE.md)
- [Reproduction and verification](REPRODUCING.md)
- [Archive integrity receipt](catalog/EXPORT-VERIFICATION.json)
- [Machine-readable file ledger](catalog/FILES.csv)

## What this collection contains

The snapshot inventories {len(manifest):,} files across the in-scope workspace. It copies {totals['publish']:,} publishable files into `research/`, preserving original paths and content. Each file is accounted for in the ledger; exclusions are visible, not silently discarded. Large text artifacts are losslessly compressed with gzip, or XZ for the largest table. Original and published checksums are recorded separately.

Reports retain unsuccessful controls, bugs and repairs, insufficient support, resource failures, negative findings and inconclusive results. A result is qualified only for the task and controls its owning protocol actually tested. Source/synthetic-control success does not itself open manuscript scoring, and structural correspondences do not establish semantics.

The small EVA continuation model is published separately at [voynich-experimental](https://github.com/several-dozen-lizards/voynich-experimental). It generates EVA text; it has no established translation ability. Model checkpoint copies are indexed here rather than duplicated.

## Scope

Voynich only. Indus work and the unrelated JNAIQ checkout are outside this snapshot. The archive gathers records present in this workspace; it does not claim to contain every past chat, external attachment, unretained experiment or earlier file version. See [coverage](COVERAGE.md) for the exact boundary.

Third-party corpora, raw manuscript transcriptions, imported source/media files, private/blinded packets and nested archives needing review remain indexed locally rather than being redistributed by default. See [rights and attribution](RIGHTS.md). No experiment was rerun and no closed research gate was reopened to create this archive.
''')
    write('COVERAGE.md','''# Coverage and exclusions

This is an inventory-backed snapshot of the local Voynich workspace. It is not a claim that all historical conversations and external attachments have been recovered.

Every file in the input inventory is assigned a disposition in `catalog/FILES.csv` and `catalog/FILES.json`. Published paths point to exact copies, or gzip/XZ streams retaining exact original bytes. Excluded entries retain their original path and byte count; no checksum is claimed for contents that were not read. The scanned-directory exclusions are listed in `catalog/SNAPSHOT.json`.

## Dispositions

- `publish`: code, reports, checks, protocols, source ledgers and result artifacts accepted by the documented selection rule and credential-pattern scan.
- `third-party-source-review`: imported corpora, raw transcriptions and source directories. Their provenance records elsewhere remain available. Public availability does not establish permission to redistribute.
- `third-party-media-review`: PDF, manuscript/source images and fonts requiring individual rights attribution/review.
- `custody-or-blinding-review`: paths designated private, vault, registrar-only, rater-only, packets, sealed or human-registration. Publication must not silently expose a reserve or invalidate independent registration.
- `model-or-binary-data`: model checkpoints and binary arrays. Existing published weights have a separate repository. Other weights/arrays remain local and indexed.
- `nested-archive-review`: compressed packages that could duplicate or conceal the above material. They remain indexed; any unpacked publishable originals are handled separately.
- `dependency-or-cache`: installed dependencies, caches and environment material.
- `unclassified-review`, `credential-pattern-review`, `copy-error`: unresolved material retained in the ledger rather than silently published.

Directory/name rules are conservative triage, not an individual legal or custody determination. A report can describe an excluded dataset without making that dataset available. `catalog/SNAPSHOT.json` records counts, source-stat changes, and errors. This archive does not certify historical blinding or restore an exposed holdout.

## Known gaps

The original running chronology is not current for all lab extensions. Historical references can name external attachments or older chats not retained here. Review all local source records before claiming exhaustive bibliography or successful reproduction. A URL extracted from code may be a template, example, or failed retrieval; it is not automatically a consulted source.

The archive copies the currently retained state. It does not reconstruct deleted files or invent Git history. The earlier source tree remains untouched. Original scripts may contain machine-specific paths or expect excluded datasets and will require the recorded source intake and environment.
''')
    write('RIGHTS.md','''# Rights and attribution

The repository was initialized by its owner with the Apache License 2.0, preserved in `LICENSE`. That license applies to the original code and documentation contributed to this repository. It does not relicense third-party sources, quoted material, transcriptions, or separately attributed works; their original rights and source-specific terms remain with their respective owners. Source ledgers record attribution and retrieval context; absence of a source license is not a permission grant.

Raw transcriptions, imported corpora, PDFs, source scans and fonts are indexed but held back by default. Locally authored reports and generated outputs can still contain quotations or excerpts; these retain their source attribution and do not convey rights to the underlying works. Inspect the owning source records before reuse or redistribution.

The source URL index records occurrences in archived text and is not a license audit. Missing/inaccessible sources and failed retrievals are preserved as such.
''')
    write('REPRODUCING.md','''# Reproduction and archive verification

This snapshot did not rerun historical analyses, retrain models, consume a statistical budget, or open a held-out scoring gate. Existing verification receipts are historical evidence, not freshly passing tests for this export.

Run `python tools/verify_archive.py` from the repository root to verify every copied research artifact against its manifest, including gzip/XZ integrity, original and published SHA-256, and Git blob identity. This uses Python's standard library and does not run research code.

Files larger than 1,000,000 bytes are stored with `.gz` appended; the largest table uses `.xz` to fit GitHub's individual-file limit. For reproduction, unpack them to a separate working copy with the original relative path. Use the original study's README, protocol, environment and source receipt. Many pipelines require external corpora, specific environments, or source intake that is intentionally not redistributed here. Do not treat a missing input as authorization to reacquire a closed reserve, alter a freeze, or score a withheld arm.

Older reports and scripts may retain links to a filename without the added `.gz`. The generated catalogue and manifest resolve the stored location. HTML reports and JavaScript dashboards are archival assets; GitHub's file viewer will not execute them. The archive's generated landing-page links are checked separately from every historical reference.

Check `catalog/SNAPSHOT.json` for observed changes between inventory and copy. Each copied file was checked for changes during its own read; this does not assert an atomic filesystem-wide snapshot of concurrent research.
''')
    (OUT/'tools').mkdir(exist_ok=True)
    shutil.copyfile(TOOLS/'verify_archive.py',OUT/'tools'/'verify_archive.py')
    print(json.dumps({k:v for k,v in summary.items() if k!='skipped_directories'},indent=2),flush=True)

if __name__=='__main__':
    if '--finalize' in sys.argv or '--supplement' in sys.argv:
        manifest=json.loads((OUT/'catalog/FILES.json').read_text(encoding='utf-8'))
        urls=json.loads((OUT/'catalog/SOURCE-LINKS.json').read_text(encoding='utf-8'))
        sources={r['url']:set(r['occurrences']) for r in urls}
        if '--supplement' in sys.argv:
            seen={r['original_path'] for r in manifest}
            extra=[r for r in INV['files'] if r['path'] not in seen]
            with ThreadPoolExecutor(max_workers=4) as executor:
                for row,found in executor.map(copy_one,extra):
                    manifest.append(row)
                    for url in found: sources.setdefault(url,set()).add(row['published_path'])
            print(json.dumps({'supplemental_files':len(extra)}),flush=True)
        finalize(manifest,sources)
    else: main()
