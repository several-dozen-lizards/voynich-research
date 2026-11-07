"""Necessary information bound for the declared independent-band exact-order control."""
from fractions import Fraction
from math import factorial
class NotAdmitted(ValueError):pass

def check(lengths,alpha=Fraction(1,100)):
    if not lengths or any(type(n) is not int or n<1 for n in lengths):raise NotAdmitted('positive band cardinalities required')
    floor=Fraction(1)
    for n in lengths:floor*=Fraction(min(2*n,factorial(n)),factorial(n))
    if floor>=alpha:raise NotAdmitted('ideal dihedral shuffle tail floor '+str(floor)+' cannot clear alpha '+str(alpha))
    return dict(ideal_tail_floor=str(floor),necessary_bound_pass=True,sufficient_power_claim=False)
if __name__=='__main__':
    assert check([12])['necessary_bound_pass'];assert check([6,6])['necessary_bound_pass']
    try:check([4,4,4])
    except NotAdmitted as exc:assert '1/27' in str(exc)
    else:raise AssertionError('underpowered geometry admitted')
    print('geometry necessary-bound checks PASS; no sufficient-power claim')
