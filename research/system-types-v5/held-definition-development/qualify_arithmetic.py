"""Synthetic engineering controls only; never imports a corpus or production generator."""
from pathlib import Path
import json,hashlib,unittest,io,random,math,sys
from decimal import Decimal,localcontext
from arithmetic_reference import SyntheticTable as T,SyntheticFixture as F,mh_reference,availability_reference
from test_arithmetic_reference import ArithmeticTests,fixture

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(HERE/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')

def main():
    assert not (ROOT/'FREEZE.json').exists()
    plan_path=HERE/'REFERENCE-PLAN.json'
    if not plan_path.exists():save(plan_path.name,dict(tier='synthetic arithmetic qualification; NOT claim FREEZE',
        files={p.name:sha(p) for p in [HERE/'arithmetic_reference.py',HERE/'test_arithmetic_reference.py',Path(__file__)]},
        held_owner_sha256=sha(ROOT/'held.py'),fixture_seed=92001,decimal_precision=80,oracle_cases=250,
        oracle='Independent Decimal weighted cross-product sums and Decimal natural logarithm; no Fraction code reused.',
        scope='No manuscript, real-source or G1-G6 output counts; no H1-H8 targets or recovery.',
        formula_source='https://www.statsmodels.org/stable/_modules/statsmodels/stats/contingency_tables.html#StratifiedTable.oddsratio_pooled',
        uncertainty='Not implemented; iid table variance is not assumed valid for dependent manuscript events.',H3='UNRESOLVED',held_scoring=False))
    plan=json.loads(plan_path.read_text());assert all(sha(HERE/n)==h for n,h in plan['files'].items())
    assert sha(ROOT/'held.py')==plan['held_owner_sha256']
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArithmeticTests))
    (HERE/'TEST-LOG.txt').write_text(stream.getvalue(),encoding='utf-8');assert tests.wasSuccessful(),stream.getvalue()
    rng=random.Random(plan['fixture_seed']);records=[]
    for i in range(plan['oracle_cases']):
        tables=[tuple(rng.randrange(1,101) for _ in range(4)) for j in range(rng.randrange(1,9))]
        f=F(f'seeded-{i:03d}',tuple(T(str(j),*row) for j,row in enumerate(tables)),provenance='seeded_synthetic_counts')
        actual=mh_reference(f)
        with localcontext() as context:
            context.prec=plan['decimal_precision'];top=Decimal(0);bottom=Decimal(0)
            for row in tables:
                a,b,c,d=map(Decimal,row);n=a+b+c+d;top+=a*d/n;bottom+=b*c/n
            expected=float((top/bottom).ln())
        error=abs(actual['log_or']-expected)
        assert math.isclose(actual['log_or'],expected,rel_tol=1e-12,abs_tol=1e-13),(i,actual,expected)
        records.append(dict(fixture_id=f.fixture_id,tables=tables,actual_log_or=actual['log_or'],decimal_log_or=expected,absolute_error=error))
    save('DECIMAL-ORACLE.json',records)
    examples=dict(single_table=mh_reference(fixture((8,2,4,6))),
        two_separated_strata_with_finite_pool=mh_reference(fixture((0,3,4,0),(5,0,0,6))),
        ratio_distinction=availability_reference(fixture((10,10,5,10)),fixture((4,1,1,2))),
        exact_null_denominator=availability_reference(fixture((10,10,10,10)),fixture((4,1,1,1))))
    save('SYNTHETIC-EXAMPLES.json',examples)
    # Gate checks assert refusal only; no statistic is computed.
    sys.path.insert(0,str(ROOT))
    from held import score,ClaimLocked
    for root in (ROOT,HERE):
        try:score(root,'H1',[])
        except ClaimLocked:pass
        else:raise AssertionError('scientific score gate opened')
    result=dict(status='SYNTHETIC_LOG_ODDS_ARITHMETIC_QUALIFIED_CLAIM_LOCKED',engineering_tests=tests.testsRun,errors=len(tests.errors),failures=len(tests.failures),
        decimal_oracle_cases=len(records),maximum_absolute_oracle_error=max(r['absolute_error'] for r in records),
        statsmodels_execution='NOT_RUN: package absent; official formula inspected, no package installed',
        support_policy='No pseudocounts; noninformative strata retained in ledger; separation extended-tagged; exact-null log denominator undefined.',
        H2_estimand='Literal ratio of log effects is a candidate definition, not adopted or given manuscript targets.',
        uncertainty_qualified=False,event_builder_implemented=False,manuscript_counts_used=False,generator_output_counts_used=False,fresh_reserve_bodies_parsed=0,
        H3='UNRESOLVED',held_scoring=False,recovery_executed=False,plan_sha256=sha(plan_path),held_owner_unchanged=True)
    save('RESULTS.json',result);print(json.dumps(result))

if __name__=='__main__':main()
