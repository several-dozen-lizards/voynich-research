"""Assemble only independently returned geometry and pictures; no text join."""
from pathlib import Path
from collections import Counter
import csv,json,hashlib
import continue_blind_cohort as runner
import prepare as core
from setup_packets import archive,replace_json

def main():
    manifest=json.loads((runner.RUNS/'MANIFEST.json').read_text(encoding='utf-8'))
    state=json.loads((runner.RUNS/'RUN-STATE.json').read_text(encoding='utf-8'))
    assert state['status']=='COMPLETE','Never label a partial cohort complete.'
    registration=[];picture_rows={'rater-A':[],'rater-B':[]};failed=[];models=Counter()
    for page in manifest:
        page_record=dict(page=page['page_id'],folio=page['folio'],raster_width=page['raster_width'],raster_height=page['raster_height'],
                         native_width=page['native_width'],native_height=page['native_height'],native_transform=page['native_transform'])
        for role in runner.ROLES:
            folder=Path(page['roles'][role]['control'])
            receipt=json.loads((folder/'RECEIPT.json').read_text(encoding='utf-8'))
            assert receipt['model_identifier']==runner.MODEL and receipt['credential_removed']
            models[receipt['model_identifier']]+=1
            if receipt['status']!='COMPLETED_VALIDATED':
                failed.append(dict(page=page['page_id'],folio=page['folio'],role=role,receipt=str(folder/'RECEIPT.json'),status=receipt['status']))
                if role=='registrar':page_record.update(status='EXECUTION_OR_GEOMETRY_FAILURE',accepted_geometry=[],dropped_blocks=[],accepted_lines=0)
                continue
            validation=receipt['validation']
            if role=='registrar':
                page_record.update(validation)
                page_record.update(receipt_sha256=core.sha(folder/'RECEIPT.json'),raw_response_sha256=core.sha(folder/'FINAL.json'))
            else:
                for row in validation['rows']:
                    picture_rows[role].append(dict(page=page['page_id'],folio=page['folio'],element=row['element'],
                        box_json=json.dumps(row['box']),native_box_json=json.dumps(row['native_box']),coordinate_system='jpeg_raster_xywh',
                        category=row['category'],note=row['note'],model=receipt['model_identifier'],cli_version=receipt['cli_version'],
                        thread_id=receipt['thread_id'],source_response_sha256=core.sha(folder/'FINAL.json')))
        registration.append(page_record)
    source_queue=json.loads((core.R/'private/IMAGE-QUEUE.json').read_text(encoding='utf-8'))
    output_registration=dict(status='ANNOTATION_COHORT_COMPLETE; NO AGREEMENT OR TEXT JOIN',
        design='v4 + v4.1 + picture-only manual correction + v4.2 with explicit timing exception; corrected engineering transport.',
        pages=registration,first_page_excluded=dict(page='page-001',status='UNREGISTERED_RETAINED',receipt='FIRST-BLIND-PAGE.json',
            reason='Coordinate discrepancy, registrar abstention, and unexposed selected model identity. Not retried or silently repaired.'),
        withheld_panels=source_queue['withheld'],failed_calls=failed,
        accepted_registered_lines=sum(p.get('accepted_lines',0) for p in registration),
        model_identifiers=dict(models),server_revision='Not exposed; no dated immutable snapshot offered for the explicit public model identifier.',
        no_outcomes_accessed=True)
    core.save('REGISTRATION.json',output_registration)
    fieldnames=['page','folio','element','box_json','native_box_json','coordinate_system','category','note','model','cli_version','thread_id','source_response_sha256']
    for role,name in [('rater-A','RATER-A.csv'),('rater-B','RATER-B.csv')]:
        with (core.R/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader();w.writerows(picture_rows[role])
    summary=dict(status='REMAINING 160 PAGES ATTEMPTED; REGISTRATION AND PICTURE RATINGS COLLECTED',
        pages=160,planned_calls=480,recorded_calls=sum(models.values()),failed_calls=len(failed),
        accepted_registered_lines=output_registration['accepted_registered_lines'],
        picture_elements={r:len(rows) for r,rows in picture_rows.items()},
        model=runner.MODEL,reasoning_effort=runner.EFFORT,cli_version=runner.VERSION,
        server_revision='Not exposed; explicit public model identifier, binary hash and catalog hash recorded in COHORT-V2-FREEZE.json.',
        first_page_failure_preserved=True,withheld_panels=len(source_queue['withheld']),
        agreement=None,support=None,synthetic_qualification=None,outcome_join=None,scientific_tests=None)
    core.save('COHORT-V2-RESULTS.json',summary)
    delivery=json.loads((core.R/'DELIVERY.json').read_text(encoding='utf-8'))
    delivery.update(status=summary['status'],remaining_pages=0,cohort_result='COHORT-V2-RESULTS.json',
        registration_completed=True,ratings_collected=sum(summary['picture_elements'].values()),
        accepted_source_lines=summary['accepted_registered_lines'],scientific_results=None,
        next_step='Agreement gates and prescribed adjudication only; no text join until agreement, outcome-blind support and synthetic qualification phases are satisfied.')
    replace_json('DELIVERY.json',delivery)
    report=core.R/'REPORT.md';archive(report)
    report.write_text(report.read_text(encoding='utf-8')+'\nCorrected cohort completed: '+json.dumps(summary,ensure_ascii=False)+
        '\nThese are annotation/execution counts, not independent accuracy confirmation or a text–image finding. The first-page failed attempt and all subsequent failures remain preserved.\n',encoding='utf-8')
    core.seal('registered_geometry_and_actual_picture_ratings_assembled_before_agreement',[
        'REGISTRATION.json','RATER-A.csv','RATER-B.csv','COHORT-V2-RESULTS.json','DELIVERY.json','REPORT.md','collect_blind_cohort.py'])
    # Phase chain verification remains applicable; the original preparation-only
    # assertion that no rater files exist is intentionally not used after real ratings.
    chain=(core.R/'PHASES.jsonl').read_bytes().splitlines(keepends=True);prior=b''
    for raw in chain:
        phase=json.loads(raw)
        assert phase['previous_log_sha256']==(hashlib.sha256(prior).hexdigest() if prior else None)
        for name,h in phase['files'].items():
            p=core.R/name;old=core.R/'private/hash-history'/h
            assert core.sha(p)==h or (old.exists() and core.sha(old)==h),name
        prior+=raw
    core.save('COHORT-V2-VERIFICATION.json',dict(status='PASS',phase_chain_valid=True,
        actual_receipts=480,first_page_failure_preserved=True,
        no_source_join_or_scientific_test=True,
        limitation='Verifies provenance, execution separation, coordinate contracts and source-count/order checks; it does not establish pixel accuracy or rater reliability.'))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
