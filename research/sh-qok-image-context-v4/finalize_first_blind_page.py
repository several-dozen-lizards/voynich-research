"""Preserve actual blind first-page responses; no source join or agreement gate."""
import csv,json,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import prepare as core
import isolated_cli as cli
from setup_packets import archive,replace_json

all_runs={}
for role in ['registrar','rater-A','rater-B']:
    folder=core.R/'private/cli-runs'/(role+'-page-001')
    receipt=json.loads((folder/'RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['status']=='COMPLETED_NO_TOOL_CALLS' and receipt['credential_copy_removed']
    home=cli.BASE/'control'/('runtime-'+role)
    assert not (home/'auth.json').exists()
    events=[json.loads(s) for s in (folder/'EVENTS.jsonl').read_text(encoding='utf-8').splitlines()]
    thread=next(e['thread_id'] for e in events if e.get('type')=='thread.started')
    warnings=[e['item']['message'] for e in events if e.get('item',{}).get('type')=='error']
    all_runs[role]=dict(status=receipt['status'],thread_id=thread,raw_final_sha256=core.sha(folder/'FINAL.txt'),
        tool_events=receipt['observed_tool_events'],credential_copy_removed=True,
        cli_version='0.164.0-alpha.11.1',model='CLI runtime default; selected model identifier and server revision were not exposed in retained events/logs.',
        model_provenance_complete=False,startup_warnings=warnings,
        note='Unknown model identity is retained explicitly; do not invent a version from bundled catalog priority.')
    if role=='registrar':continue
    raw=(folder/'FINAL.txt').read_text(encoding='utf-8')
    assert 'left, top, right, bottom' in raw
    actual=Image.open(cli.BASE/role/'page-001/PAGE.jpg').size
    rows=[]
    for line in raw.splitlines():
        m=re.fullmatch(r'\|\s*1\s*\|\s*\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)\s*\|\s*(PL|VE|FG|CE|OT)\s*\|\s*(.*?)\s*\|',line)
        if not m:continue
        left,top,right,bottom=map(int,m.groups()[:4])
        assert 0<=left<right<=actual[0] and 0<=top<bottom<=actual[1]
        rows.append(dict(page='page-001',element=len(rows)+1,x=left,y=top,width=right-left,height=bottom-top,
            coordinate_system='JPEG raster xywh',category=m[5],note=m[6],rater=role,
            original_box_ltrb=json.dumps([left,top,right,bottom]),source_response_sha256=core.sha(folder/'FINAL.txt')))
    assert len(rows)==sum(bool(re.match(r'^\|\s*1\s*\|',line)) for line in raw.splitlines())>0
    out=folder/'PICTURE-ELEMENTS.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    all_runs[role].update(elements=len(rows),raster_dimensions=actual,
        categories={c:sum(r['category']==c for r in rows) for c in ['PL','VE','FG','CE','OT']},
        parsing='Deterministic lossless conversion of explicitly declared LTRB boxes to XYWH; notes/categories unchanged.',
        parsed_csv_sha256=core.sha(out))

geometry=json.loads((core.R/'private/cli-runs/registrar-page-001/GEOMETRY-VALIDATION.json').read_text(encoding='utf-8'))
status=dict(status='V4.2 FROZEN; HOLD LIFTED; ISOLATION QUALIFIED; FIRST INDEPENDENT PAGE CALLS COMPLETE',
    utc=datetime.now(timezone.utc).isoformat(),v4_2_freeze='V4.2-FREEZE.json',
    timing_exception='Pre-v4.2 registration exists in another folder; explicitly retained and authorized. No such registration was reused here.',
    isolation_qualification='ISOLATION-QUALIFICATION.json',
    accepted_source_lines=0,registrar_status='UNREGISTERED; abstention and coordinate discrepancy retained',
    actual_calls=all_runs,cohort_single_image_pages=161,pages_with_completed_calls=1,
    remaining_single_image_pages=160,withheld_panel_pages=27,
    agreement=None,support=None,qualification=None,outcome_join=None,scientific_results=None,
    model_provenance='First calls used CLI default; exact model identifier not exposed. Must resolve explicit model recording before using model ratings for a protocol-compliant final analysis.',
    transport_issue='Registrar was supplied native canvas dimensions and returned them as JPEG dimensions. Actual JPEG is 1282x1800; response reported 2676x3756. Do not override or silently convert its abstaining source mapping.',
    next_step='Before subsequent pages, freeze a corrected geometry transport that supplies actual JPEG raster dimensions separately from native canvas dimensions and records the selected model explicitly. Preserve this first-page attempt. Use new fresh sessions, and qualify each new folder boundary.',
    interpretation='The requested independent work has started. This is an execution and annotation receipt, not a manuscript test result.')
core.save('FIRST-BLIND-PAGE.json',status)
delivery=json.loads((core.R/'DELIVERY.json').read_text(encoding='utf-8'))
delivery.update(status=status['status'],hold='LIFTED by direct user instruction; V4.2-FREEZE.json',
    hard_filesystem_isolation_certified='MXC role-specific profile passed own-read, cross-role-denial and outside-denial checks; minimal runtime system access retained.',
    registrar_assigned=True,raters_assigned=True,cli_inference_sessions_launched=3,
    ratings_collected=sum(v.get('elements',0) for v in all_runs.values()),rating_pages_completed_per_rater=1,
    registration_completed=False,accepted_source_lines=0,scientific_results=None,
    current_receipt='FIRST-BLIND-PAGE.json',next_step=status['next_step'])
replace_json('DELIVERY.json',delivery)
report=core.R/'REPORT.md';archive(report)
text=report.read_text(encoding='utf-8')
text+='\nCurrent status superseding the earlier hold: the user explicitly froze v4.2 with the timing exception and lifted the hold. MXC permission profiles passed role-specific canary reads: own page readable; outside and other-role reads denied. Three memory-disabled, independently authenticated fresh CLI calls have completed for page-001, with no tool events in their recorded inference traces. Each picture rater returned 20 elements; responses are sealed independently.\n'
text+='\nThe registrar abstained and returned a coordinate-system discrepancy; zero source lines from page-001 are accepted. This is not evidence that the manuscript lacks line-level support. No agreement gate, support computation, synthetic qualification, outcome join, or inferential test has run. The first-page model identifier was not exposed in the retained runtime metadata; preserve that provenance gap. Correct and freeze subsequent geometry transport and explicit model recording before advancing the cohort. No first-page abstention or failure has been erased or reclassified as a pass.\n'
report.write_text(text,encoding='utf-8')
paths=['FIRST-BLIND-PAGE.json','DELIVERY.json','REPORT.md','finalize_first_blind_page.py','read_runtime_model.py','private/RUNTIME-MODEL-AUDIT.json',
       'ISOLATION-BOUNDARY-PROBE.json','ISOLATION-BOUNDARY-PROBE-elevated.json','ISOLATION-BOUNDARY-PROBE-mxc.json','ISOLATION-BOUNDARY-PROBE-mxc-inline.json',
       'private/cli-runs/rater-A-page-001/PICTURE-ELEMENTS.csv','private/cli-runs/rater-B-page-001/PICTURE-ELEMENTS.csv']
core.seal('first_blind_page_complete_failures_retained_no_scientific_scoring',paths)
core.verify()
print(json.dumps(dict(status=status['status'],elements={r:v.get('elements') for r,v in all_runs.items()},accepted_source_lines=0)))
