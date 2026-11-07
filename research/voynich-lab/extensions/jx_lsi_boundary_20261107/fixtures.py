"""Authored semantic and boundary fixtures, executed only after registration."""
from adapter import adapt,canonical,boundary_comparison

def execute():
    results=[]
    def check(name,predicate,actual):results.append(dict(name=name,passed=bool(predicate),actual=actual))
    def r(raw='',code='+P0',reader='H',page='f1r'):
        return dict(text_raw=raw,locus_code=code,transcriber=reader,folio=page)
    a=adapt([r('ab.cd','@P0'),r('ef.gh','*P0'),r('ij.kl','@P0')])
    check('layout_prefixes_never_certify_start',all(x['paragraph_start'] is None and x['paragraph_id'] is None for x in a),a)
    check('layout_does_not_break_safe_fragment',len({x['safe_fragment'] for x in a})==1,a)
    a=adapt([r('<%>ab.cd','@P0'),r('ef.gh','*P0'),r('ij.kl','@P0')])
    check('explicit_paragraph_not_restarted_by_layout',[x['line_index_in_paragraph'] for x in a]==[0,1,2] and len({x['paragraph_id'] for x in a})==1,a)
    a=adapt([r('ab.cd<$>','@P0'),r('ef.gh')])
    check('end_stops_fragment_without_inferred_start',a[0]['safe_fragment']!=a[1]['safe_fragment'] and a[1]['paragraph_start'] is None,a)
    a=adapt([r('<%>ab.cd'),r('ef.gh',reader='U'),r('ij.kl')])
    check('reader_state_isolated',a[1]['paragraph_id'] is None and a[2]['line_index_in_paragraph']==1,a)
    a=adapt([r('<%>ab.cd'),r('ef.gh',page='f1v')])
    check('page_state_isolated',a[1]['paragraph_id'] is None and a[0]['safe_fragment']!=a[1]['safe_fragment'],a)
    a=adapt([r('ab.cd'),r('xy','@La'),r('ef.gh')])
    check('nonparagraph_breaks_fragment',a[0]['safe_fragment']!=a[1]['safe_fragment'],a)
    a=adapt([r('ab.cd'),r('xy<->zz'),r('ef.gh')])
    check('drawing_breaks_fragment',len({x['safe_fragment'] for x in a})==3,a)
    x=canonical('ab!.[cd|ef],gh- {plant}',True)
    check('EVMT_comment_padding_first_alternative',x['literal']=='ab.cd,gh' and not x['paragraph_end'] and x['held'],x)
    x=canonical('ab.cd= {editorial}',True);y=canonical('ab.cd<$>')
    check('explicit_end_conversion',x==y,dict(original=x,ivtff=y))
    x=canonical('ab-{plant}cd-',True)
    check('internal_gap_is_barrier',x['held'] and x['hold_flags']['drawing'],x)
    x=canonical('ab.cd');y=canonical('ab.cd');z=boundary_comparison(x,y)
    check('identical_boundary_pair',z['status']=='ALIGNED' and len(z['shared'])==1 and not z['ZL_only'] and not z['H_only'],z)
    z=boundary_comparison(canonical('ab.cd.ef'),canonical('abcd.ef'))
    check('planted_join_detected',z['ZL_only']==[2] and z['H_only']==[] and z['shared']==[4],z)
    z=boundary_comparison(canonical('ab.cd'),canonical('ab.ce'))
    check('glyph_substitution_not_aligned',z['status']=='UNALIGNED_GLYPH_STREAM',z)
    z=boundary_comparison(canonical('ab.?d'),canonical('ab.cd'))
    check('unknown_is_held',z['status']=='HELD_SOURCE_UNCERTAINTY',z)
    return results
