"""LSI paragraph evidence and safe fragments; layout is not paragraph evidence."""
import re

P_TYPES={'P0','P1','Pc','Pr','Pt'}

def adapt(records):
    states={};out=[]
    for r in records:
        key=(r['folio'],r['transcriber']);s=states.setdefault(key,dict(fragment=-1,paragraph=None,index=None,blocked=True,serial=0))
        raw=r['text_raw'];is_p=r['locus_code'][1:] in P_TYPES
        start='<%>' in raw;end='<$>' in raw
        barrier=any(x in raw for x in ['<->','<~>']) or r.get('is_spurious',False) or r.get('has_missing_span',False) or r.get('has_uncertainty',False) or '\ufffd' in r.get('text_eva','')
        if not is_p:
            s['blocked']=True;s['paragraph']=None;s['index']=None
            continue
        if s['blocked'] or start or barrier:s['fragment']+=1
        if start:
            s['serial']+=1;s['paragraph']=f"{r['folio']}:{r['transcriber']}:explicit:{s['serial']}";s['index']=0
        elif s['paragraph'] is not None:s['index']+=1
        # A null start is unknown, not a certified continuation or a failed line.
        result=dict(r,paragraph_start=True if start else None,paragraph_end=True if end else None,
            paragraph_id=s['paragraph'],line_index_in_paragraph=s['index'],
            safe_fragment=f"{r['folio']}:{r['transcriber']}:{s['fragment']}",
            paragraph_evidence='explicit <%>' if start else 'UNKNOWN_START',
            layout_locator=r['locus_code'][0],barrier=barrier,
            context_policy='Unknown paragraph context retained for locus-local analysis; no inferred paragraph start')
        out.append(result)
        s['blocked']=end or barrier
        if end or barrier:s['paragraph']=None;s['index']=None
    return out

def strip_brace_comments(text):
    while '{' in text:
        text,n=re.subn(r'\{[^{}]*\}','',text)
        if not n:raise ValueError('Unbalanced original-source comments')
    return text

def first_alternative(text):
    while '[' in text:
        text,n=re.subn(r'\[([^\[\]]*)\]',lambda m:re.split(r'[:|]',m[1])[0],text)
        if not n:raise ValueError('Unbalanced alternatives')
    return text

def canonical(raw,original=False):
    """Literal EVA and exact dot/comma offsets. No edit alignment or glyph repair."""
    uncertain='[' in raw
    if original:
        s=re.sub(r'\s+','',strip_brace_comments(raw));ending=s.endswith('=')
        if s.endswith(('-','=')):s=s[:-1]
        drawing='-' in s
        s=s.replace('-','\ufffd')
    else:
        ending='<$>' in raw;drawing='<->' in raw or '<~>' in raw
        s=re.sub(r'<[-~]>','\ufffd',raw);s=re.sub(r'<[^>]*>','',s)
        s=s.replace('{','').replace('}','')
    s=first_alternative(s);s=re.sub(r'@\d{3};','\ufffd',s)
    s=s.replace('!','');s=re.sub(r'[?%*]+','\ufffd',s)
    s=re.sub(r'\s+','',s);s=re.sub(r'[^a-zA-Z.,\ufffd]','\ufffd',s)
    s=s.strip('.,')
    stream=[];boundaries=[]
    for c in s:
        if c in '.,':boundaries.append([len(stream),c])
        else:stream.append(c)
    return dict(literal=s,stream=''.join(stream),boundaries=boundaries,paragraph_end=ending,
        held=uncertain or drawing or '\ufffd' in s or not stream,
        hold_flags=dict(uncertainty=uncertain,drawing=drawing,unknown='\ufffd' in s,empty=not stream))

CLUSTERS=sorted(['ch','sh','cth','ckh','cph','cfh','ii','iii','in','iin','aiin','qo','ee'],key=lambda s:(-len(s),s))
def units(word):
    out=[];i=0
    while i<len(word):
        x=next((x for x in CLUSTERS if word.startswith(x,i)),word[i]);out.append(x);i+=len(x)
    return out

def boundary_comparison(a,b):
    """Only align identical glyph streams; altered glyph strings remain unaligned."""
    if a['held'] or b['held']:return dict(status='HELD_SOURCE_UNCERTAINTY')
    if a['stream']!=b['stream']:return dict(status='UNALIGNED_GLYPH_STREAM')
    stream=a['stream'];aa={p for p,c in a['boundaries'] if 0<p<len(stream)};bb={p for p,c in b['boundaries'] if 0<p<len(stream)}
    shared=sorted(aa&bb);mismatch=[]
    def junction(cuts,p):
        left=max([0]+[x for x in cuts if x<p]);right=min([len(stream)]+[x for x in cuts if x>p])
        return [units(stream[left:p])[-1],units(stream[p:right])[0]]
    for p in shared:
        x,y=junction(aa,p),junction(bb,p)
        mismatch.append(dict(offset=p,ZL=x,H=y,different=x!=y))
    return dict(status='ALIGNED',glyphs=len(stream),ZL_boundaries=sorted(aa),H_boundaries=sorted(bb),
        shared=shared,ZL_only=sorted(aa-bb),H_only=sorted(bb-aa),shared_junction_features=mismatch,
        boundary_type_differences=[dict(offset=p,ZL=[c for x,c in a['boundaries'] if x==p],H=[c for x,c in b['boundaries'] if x==p]) for p in shared if [c for x,c in a['boundaries'] if x==p]!=[c for x,c in b['boundaries'] if x==p]],
        caveat='Spacing-exclusive edges exist in only one parse by construction; they are not independent evidence of concentration or causation.')
