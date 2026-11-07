"""Actual-geometry no-wrap admission checks, using development sources only."""
from pathlib import Path
from unittest.mock import patch
import json
from core import save,sha,load_evt,panels
from sandbox import DATA
from source_contract import load_development_corpus,produce_from_development
from transfer_policy import SourceSupportError

ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/'FREEZE.json').exists()
    plan_path=ROOT/'SOURCE-ENTRYPOINT-PLAN-v2.json'
    if not plan_path.exists():
        files=['source_contract.py','registry.py','GENERATORS/__init__.py','transfer_policy.py','qualify_source_entrypoint.py',
               'test_source_contract.py','test_transfer_policy.py','core.py','LANGUAGE-SOURCE-SPLITS.json','EVA-GROUP-INVENTORIES.json',
               'SOURCE-COVERAGE-PLAN.json','UNKNOWN-AND-LENGTH-POLICY.json']
        files += [name+'-SOURCE-UNITS.json' for name in ('LATIN','ITALIAN','GERMAN','CZECH','OCCITAN')]
        save(plan_path,dict(tier='sandbox',scope='G1 for all5languages×10actual slot geometries; G2–G4 for admitted Latin cells only. Seed72001, default mechanism parameters; source selection development-only. Unsupported cells must reject before generator invocation. No reserve input or held score.',files={n:sha(ROOT/n) for n in files}))
    plan=json.loads(plan_path.read_text());assert all(sha(ROOT/n)==h for n,h in plan['files'].items())
    rows,_=load_evt(DATA/'text16e6.original.evt',DATA/'Davis-hands.original.csv')
    targets=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text());result=[]
    for language in ('Latin','Italian','German','Czech','Occitan'):
        corpus=load_development_corpus(ROOT,language)
        for key,cell in sorted(panels(rows).items()):
            cell_name='-'.join(key);geometry=[len(r['tokens']) for r in cell]
            families=('G1','G2','G3','G4') if language=='Latin' else ('G1',)
            for family in families:
                args=dict(family=family,params={},seed=72001,corpus=corpus,inventory=targets[cell_name],line_lengths=geometry)
                try:
                    generated=produce_from_development(**args)
                    assert [len(line) for line in generated['lines']]==geometry
                    receipt=generated['source_receipt'];assert receipt['partition']=='development' and receipt['source_wraps']==0
                    assert receipt['stop']-receipt['start']==sum(geometry)
                    result.append(dict(language=language,family=family,cell=cell_name,status='PASS',required_slots=sum(geometry),source_receipt=receipt))
                except SourceSupportError as error:
                    with patch('source_contract.produce',side_effect=AssertionError('invoked generator despite unsupported size')):
                        try:produce_from_development(**args)
                        except SourceSupportError:pass
                        else:raise AssertionError('unsupported source admitted')
                    result.append(dict(language=language,family=family,cell=cell_name,status='SOURCE_TOO_SHORT_PRE_GENERATOR',reason=str(error),required_slots=sum(geometry)))
    save(ROOT/'SOURCE-ENTRYPOINT-TRIALS.json',result)
    summary=dict(status='SOURCE_CONTRACT_VERIFIED',trials=len(result),passed=sum(r['status']=='PASS' for r in result),
                 short_source_rejections=sum(r['status']=='SOURCE_TOO_SHORT_PRE_GENERATOR' for r in result),
                 every_rejection_before_generator=True,reserve_used=False,held_scoring=False,H3='UNRESOLVED',plan_sha256=sha(plan_path))
    save(ROOT/'SOURCE-ENTRYPOINT-VERIFICATION.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
