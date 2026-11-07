"""User-authorized manual correction and segregated offline annotation packets."""
from pathlib import Path
import csv, hashlib, json, shutil, zipfile
from collections import defaultdict
import prepare as core

R=Path(__file__).resolve().parent
def archive(p):
    target=R/'private/hash-history'/core.sha(p)
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): shutil.copyfile(p,target)
def replace_json(name,value):
    p=R/name
    if p.exists():archive(p)
    core.save(name,value)

def main():
    if (R/'PACKET-SETUP.json').exists():raise SystemExit('Packets already sealed; do not overwrite.')
    manual=R/'MANUAL.md'
    old=manual.read_text(encoding='utf-8')
    sentence='Return one row per picture element (page, box, category, note) and one row per writing line (page, block, line number, box).'
    assert old.count(sentence)==1
    archive(manual)
    manual.write_text(old.replace(sentence,'Return one row per picture element (page, box, category, note).'),encoding='utf-8')
    core.save('MANUAL-CORRECTION.json',dict(authority='User instruction in this chat, 24 October 2026: Yes, picture-element rows only. Make that correction, hash the amended manual, and continue with the independent blind registration and rating setup.',
        old_final_sentence=sentence,new_final_sentence='Return one row per picture element (page, box, category, note).',manual_sha256=core.sha(manual),ratings_collected_before_correction=0))
    core.seal('user_authorized_picture_rows_only_manual_before_packet_release',['MANUAL.md','MANUAL-CORRECTION.json'])
    q=json.loads((R/'private/IMAGE-QUEUE.json').read_text(encoding='utf-8'))
    receipts={r['task_id']:r for r in json.loads((R/'private/IMAGE-RECEIPTS.json').read_text(encoding='utf-8'))}
    lines=json.loads((R/'private/LINE-REGISTRATION-QUEUE.json').read_text(encoding='utf-8'))
    bypage=defaultdict(list)
    for row in lines:bypage[row['folio']].append(row)
    tasks=[]
    for t in q['tasks']:
        assert t['folio'] not in core.RESERVED
        p=R/'private'/t['image']
        assert receipts[t['task_id']]['status']=='READY' and core.sha(p)==receipts[t['task_id']]['sha256']
        tasks.append(t)
    template=(R/'annotation-template.html').read_text(encoding='utf-8')
    manifests={}
    for role in ('registrar','rater-A','rater-B'):
        packet=R/'packets'/role
        (packet/'images').mkdir(parents=True)
        public=[]
        for t in tasks:
            shutil.copyfile(R/'private'/t['image'],packet/t['image'])
            row=dict(page_id=t['task_id'],image=t['image'],native_width=t['native_width'],native_height=t['native_height'])
            if role=='registrar':
                blocks=defaultdict(list)
                for source in bypage[t['folio']]: blocks[source['unit']].append(source)
                row['registration_sources']=dict(folio=t['folio'],canvas_id=t['canvas_id'],blocks=[dict(EVT_P_unit=unit,
                    H_source_line_count=sum('H' in s['readings'] for s in rows),F_source_line_count=sum('F' in s['readings'] for s in rows),
                    locus_headers=[dict(locus=s['locus'],readings=s['readings']) for s in rows]) for unit,rows in blocks.items()])
            public.append(row)
        config=dict(packet_id='visual-context-'+role+'-v4.1',role='registrar' if role=='registrar' else 'picture-rater',tasks=public,
                    manual=None if role=='registrar' else manual.read_text(encoding='utf-8'),manual_sha256=None if role=='registrar' else core.sha(manual))
        (packet/'index.html').write_text(template.replace('__CONFIG__',json.dumps(config,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
        if role=='registrar':
            shutil.copyfile(R/'REGISTRAR-CONTRACT.json',packet/'REGISTRAR-CONTRACT.json')
            instructions='Independent registrar only. Unzip and open index.html. Use only these unannotated pages and source locus headers/counts. Do not receive picture annotations, token transcriptions, event counts or project results. Record blocks and lines, their source crosswalks and count mismatches. Proposed mappings require validation before acceptance. Preserve every nonregistration and abstention. Export JSON to save; CSV is supplementary. Visible image text is unavoidable; do not transcribe it. Do not perform picture rating.\n'
        else:
            shutil.copyfile(manual,packet/'MANUAL.md')
            instructions='Independent picture rater only. Unzip and open index.html. Read MANUAL.md and annotate the page images independently. Do not view another participant\'s annotations, registrar files, transcriptions, project reports or chats. Return the exported JSON, preserving abstentions, notes and page-completion records. CSV is supplementary. A page with no picture elements still needs a completion record. Record identity, exposure and any page recognition. Never use both rater packets as the same person.\n'
        (packet/'READ-ME.txt').write_text(instructions,encoding='utf-8')
        hashes={str(p.relative_to(packet)).replace('\\','/'):core.sha(p) for p in packet.rglob('*') if p.is_file()}
        core.save(str((packet/'MANIFEST.json').relative_to(R)),dict(packet_id=config['packet_id'],role=config['role'],manual_sha256=config['manual_sha256'],files=hashes))
        target=R/'packets'/(role+'.zip')
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(packet.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(packet))
        manifests[role]=dict(path=str(target.relative_to(R)),sha256=core.sha(target),pages=len(public),role=config['role'])
    # A model runner sees one page and exact manual per isolated call, not HTML or registrar metadata.
    model=R/'packets/model-page-inputs'
    model.mkdir()
    for t in tasks:
        page=model/t['task_id'];page.mkdir()
        shutil.copyfile(manual,page/'MANUAL.md')
        shutil.copyfile(R/'private'/t['image'],page/'PAGE.jpg')
    core.save('private/MODEL-RUNNER-CONTRACT.json',dict(status='NOT DISPATCHED; NO ENFORCED ISOLATED RUNNER AVAILABLE',
        per_call_inputs=['One PAGE.jpg','Exact MANUAL.md as sole instruction prompt'],forbidden=['Inherited chat','Project memory','Any filesystem or tools beyond the two supplied inputs','Registrar geometry','Transcription','Results','Other rater responses'],
        independence='Two distinct rater runs; fresh isolated call for each page; record provider model exact version and input hashes.',
        note='Do not send READ-ME, manifests, this runner contract, or analyst files as model prompt content.'))
    preflight=json.loads((R/'PREFLIGHT.json').read_text(encoding='utf-8'))
    for issue in preflight['issues']:
        if issue['id']=='manual_return_sentence':issue.update(status='RESOLVED_BY_USER',detail='Manual final sentence now requests picture-element rows only; corrected and hashed before packet creation.')
    replace_json('PREFLIGHT.json',preflight)
    status=dict(status='SEGREGATED OFFLINE PACKETS READY; NO PARTICIPANT DISPATCH OR RATINGS',manual_sha256=core.sha(manual),
        ready_images=len(tasks),withheld_panels=len(q['withheld']),packets=manifests,manual_packaged=True,manual_released_to_raters=False,
        registrar_assigned=False,raters_assigned=False,ratings_collected=0,registration_completed=False,scientific_results=None,
        isolation='Offline packets separate the supplied inputs. They do not establish participant independence or model tool restrictions.',
        next_step='Assign an unexposed independent registrar and two unexposed independent picture raters; alternatively establish a restricted, stateless vision runner. Do not substitute this exposed analyst.')
    core.save('PACKET-SETUP.json',status)
    replace_json('DELIVERY.json',status)
    archive(R/'REPORT.md')
    (R/'REPORT.md').write_text(core.HEADER+'\n\n'+
        '\n'.join(f'H-IMG scribe{s}-{r}: PENDING — Q unavailable, Holm p unavailable' for s in (1,2,3) for r in ('H','F'))+
        '\n\nPENDING is a workflow state, not a scientific result. The user-authorized picture-only manual correction is hashed. '
        'Independent registrar and picture-rater packets are ready for controlled handoff. All 161 single-folio images are packaged; '
        '27 panels remain withheld. No participants have been assigned, no ratings collected, and no registration, agreement, support, controls, outcome join or tests completed. '
        'No available tool establishes the required restricted fresh vision-model sessions. See PACKET-SETUP.json and PREFLIGHT.json.\n',encoding='utf-8')
    core.seal('segregated_registration_and_picture_rating_packets',['PACKET-SETUP.json','DELIVERY.json','PREFLIGHT.json','REPORT.md','setup_packets.py','annotation-template.html','private/MODEL-RUNNER-CONTRACT.json']+[v['path'] for v in manifests.values()])
    verify_packets()
    core.verify()
    print(json.dumps(dict(manual_sha256=core.sha(manual),packets=manifests),indent=2))

def verify_packets():
    setup=json.loads((R/'PACKET-SETUP.json').read_text(encoding='utf-8'))
    for role,info in setup['packets'].items():
        target=R/info['path'];assert core.sha(target)==info['sha256']
        with zipfile.ZipFile(target) as z:
            manifest=json.loads(z.read('MANIFEST.json'))
            assert set(z.namelist())==set(manifest['files'])|{'MANIFEST.json'}
            for n,h in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
            html=z.read('index.html').decode('utf-8')
            config,_=json.JSONDecoder().raw_decode(html.split('const config=',1)[1])
            assert len(config['tasks'])==161
            if role!='registrar':
                assert z.read('MANUAL.md')==(R/'MANUAL.md').read_bytes()
                assert config['manual_sha256']==core.sha(R/'MANUAL.md')
                assert all(set(t)=={'page_id','image','native_width','native_height'} for t in config['tasks'])
                assert 'REGISTRAR-CONTRACT.json' not in z.namelist()
                assert not any(term in config['manual'] for term in ['qok','sh→','Holm','scribe'])
            else:assert config['manual'] is None and all('registration_sources' in t for t in config['tasks'])
    core.save('PACKET-VERIFICATION.json',dict(status='PASS',checks=['Zip allowlists and hashes','161 image tasks per packet','Exact corrected manual','No transcription or analytic fields in rater task data','Registrar receives no manual or picture judgments'],
        limitation='Packet checks do not prove human independence, actual input exposure, annotation accuracy, browser interaction, or enforce restricted model execution.'))

if __name__=='__main__':main()
