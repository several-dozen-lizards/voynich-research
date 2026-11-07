from common import *
from plain_api import json_object
from workflow import box_ok

P=ROOT/'registration-pilot';audit=[]
for task in load(P/'PLAN.json')['tasks']:
    per={};errors={}
    for role in ['proposer-GLM','reviewer-GLM']:
        path=P/task['page']/role/'completion.json';content=load(path)['content']
        try:per[role]=json_object(content)
        except Exception as error:errors[role]=type(error).__name__
    a={r['task_id']:r for r in per.get('proposer-GLM',{}).get('rows',[])}
    b={r['task_id']:r for r in per.get('reviewer-GLM',{}).get('rows',[])}
    for tid in task['task_ids']:
        reasons=[];first=a.get(tid,{});second=b.get(tid,{})
        if errors:reasons.append('SECOND_PASS_SCHEMA_NONCOMPLIANT')
        if not first.get('physical_label_id'):reasons.append('PROPOSER_PHYSICAL_LABEL_ID_MISSING')
        if first.get('bbox') is None:reasons.append('PROPOSER_ABSTAINED')
        if not first.get('locus_identity_confirmed'):reasons.append('PROPOSER_IDENTITY_UNCONFIRMED')
        if not second.get('physical_label_id'):reasons.append('REVIEW_PHYSICAL_LABEL_ID_MISSING_OR_UNPARSED')
        audit.append(dict(task_id=tid,page=task['page'],status='UNREGISTERED',reasons=reasons,proposed_bbox=first.get('bbox'),
                          reviewer_schema_error=errors,accepted=False))
assert all(r['reasons'] for r in audit)
save(P/'AUDIT.json',dict(status='FAILED_REGISTRATION_PILOT',accepted=0,dropped=len(audit),rows=audit,
    analyst_QA='Nonblind engineering veto: f83r proposed upper/main paragraph blocks instead of the specified lower-left inscription units. No boxes admitted; analyst did not supply replacement geometry.',
    limitations='Two source-only stateless requests from one model family did not establish accurate geometry. Proposer-anchored review repeated incorrect coordinates.'))
save(P/'ACCEPTED.json',dict(status='NONE_ACCEPTED',rows=[],accepted=0))
print('Pilot rejected:',len(audit),'loci; zero accepted geometry')
