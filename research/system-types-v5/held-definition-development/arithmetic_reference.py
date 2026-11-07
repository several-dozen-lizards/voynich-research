"""Synthetic-count arithmetic only. No corpus/generator adapters or held dispatch.

Table convention: rows = exposure/reference; columns = outcome yes/no.
This module qualifies arithmetic, not any H1/H2 event or sampling definition.
"""
from dataclasses import dataclass
from fractions import Fraction
import math

@dataclass(frozen=True)
class SyntheticTable:
    stratum:str
    a:int
    b:int
    c:int
    d:int

    def __post_init__(self):
        if not isinstance(self.stratum,str) or not self.stratum:raise ValueError('named synthetic stratum required')
        if any(type(x) is not int or x<0 for x in self.cells):raise ValueError('nonnegative integer cell counts required')

    @property
    def cells(self):return (self.a,self.b,self.c,self.d)

@dataclass(frozen=True)
class SyntheticFixture:
    fixture_id:str
    tables:tuple
    provenance:str='hand_written_synthetic_counts'

    def __post_init__(self):
        if not self.fixture_id or self.provenance not in ('hand_written_synthetic_counts','seeded_synthetic_counts'):raise ValueError('synthetic-count provenance required')
        if type(self.tables) is not tuple or any(not isinstance(t,SyntheticTable) for t in self.tables):raise TypeError('immutable synthetic tables required')
        if len({t.stratum for t in self.tables})!=len(self.tables):raise ValueError('duplicate stratum')

def _log_exact_ratio(value):
    """Avoid cancellation near one; never turn a nonunit exact ratio into a false zero."""
    if value==1:return 0.0
    delta=value.numerator-value.denominator
    if abs(delta)*2<=value.denominator:
        x=float(Fraction(delta,value.denominator))
        if x==0:return None
        return math.log1p(x)
    return math.log(value.numerator)-math.log(value.denominator)

def mh_reference(fixture):
    if not isinstance(fixture,SyntheticFixture):raise TypeError('synthetic fixture only; scientific scoring remains in locked held.py')
    numerator=Fraction(0);denominator=Fraction(0);ledger=[]
    for t in fixture.tables:
        a,b,c,d=t.cells;n=a+b+c+d
        if not n:reason='EMPTY'
        elif not(a+b) or not(c+d):reason='NO_EXPOSURE_CONTRAST'
        elif not(a+c) or not(b+d):reason='NO_OUTCOME_VARIATION'
        else:reason='INFORMATIVE'
        ledger.append(dict(stratum=t.stratum,status=reason,cells=list(t.cells)))
        if reason=='INFORMATIVE':
            numerator+=Fraction(a*d,n);denominator+=Fraction(b*c,n)
    value=None;ratio=None
    if not numerator and not denominator:status='NO_INFORMATION'
    elif not denominator:status='POSITIVE_INFINITY'
    elif not numerator:status='NEGATIVE_INFINITY'
    else:
        ratio=numerator/denominator;value=_log_exact_ratio(ratio)
        status='FINITE' if value is not None else 'NUMERIC_RANGE'
    return dict(fixture_id=fixture.fixture_id,scope='synthetic arithmetic, not a held statistic',status=status,log_or=value,
        exact_or=None if ratio is None else [str(ratio.numerator),str(ratio.denominator)],
        numerator=[str(numerator.numerator),str(numerator.denominator)],denominator=[str(denominator.numerator),str(denominator.denominator)],
        informative_strata=sum(r['status']=='INFORMATIVE' for r in ledger),strata=ledger,half_count_correction=False)

def availability_reference(aggregate,available):
    """Literal draft ratio of log effects; exact-null denominator is not rescued.

    Available tables must be a componentwise subset in the same table orientation.
    No availability classifier, contexts, words, positions or corpus data enter here.
    """
    if not isinstance(aggregate,SyntheticFixture) or not isinstance(available,SyntheticFixture):raise TypeError('synthetic fixtures only')
    total={t.stratum:t for t in aggregate.tables}
    for t in available.tables:
        if t.stratum not in total or any(x>y for x,y in zip(t.cells,total[t.stratum].cells)):
            raise ValueError('availability must be a componentwise subset of the same strata')
    all_result=mh_reference(aggregate);available_result=mh_reference(available)
    ratio=None;difference=None;ratio_status='NONFINITE_OR_UNSUPPORTED_EFFECT';interpretation=None
    if all_result['status']==available_result['status']=='FINITE':
        beta=all_result['log_or'];conditional=available_result['log_or'];difference=conditional-beta
        if all_result['exact_or']==['1','1']:ratio_status='ZERO_AGGREGATE_LOG_EFFECT'
        else:
            ratio=conditional/beta
            if not math.isfinite(ratio):ratio=None;ratio_status='NUMERIC_RANGE'
            else:
                opposite=conditional!=0 and ((beta<0)!=(conditional<0))
                ratio_status='FINITE';interpretation='DIRECTION_REVERSAL' if opposite else 'SAME_DIRECTION_OR_ZERO'
    return dict(scope='synthetic arithmetic; candidate H2 estimand not adopted',aggregate=all_result,available=available_result,
        log_effect_ratio=ratio,ratio_status=ratio_status,interpretation=interpretation,
        log_effect_difference_diagnostic=difference,difference_is_h2_replacement=False,
        epsilon_or_pseudocount_used=False)
