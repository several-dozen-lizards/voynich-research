"""Geometry-only implementation of the existing v4 wrap rule. No ratings/text loader."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import hashlib,json
P=Path(__file__).parent;ROOT=P.parents[1]
G=ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json';RULE=ROOT/'image-context-v4/PROTOCOL-NOTES.md';SPEC=ROOT/'sh-qok-image-context-v4/PROTOCOL.json'
def wrap(width,widths):
    ws=sorted(Fraction(str(w)) for w in widths)
    if not ws or any(w<=0 for w in ws):raise ValueError('positive geometry widths required')
    n=len(ws);median=ws[n//2] if n%2 else (ws[n//2-1]+ws[n//2])/2
    return Fraction(str(width))*20<=median*17,median

def main():
    geo=json.loads(G.read_text(encoding='utf-8'));groups=defaultdict(list);rows=geo['lines'];ids=[r['shared_line_id'] for r in rows];assert len(ids)==len(set(ids))==1145
    for r in rows:
        assert r['folio'] not in {'f72v1','f72v2','f73r','f73v'}
        assert Fraction(str(r['line_width']))==Fraction(str(r['box'][2]));groups[(r['task_id'],r['block_id'])].append(r)
    output=[];gaps=[]
    for (task,block),rs in groups.items():
        if sorted(r['line_number'] for r in rs)!=list(range(1,len(rs)+1)):gaps.append(dict(task_id=task,block_id=block,ordinals=[r['line_number'] for r in rs]))
        for r in rs:
            flag,median=wrap(r['line_width'],[z['line_width'] for z in rs]);output.append(dict(shared_line_id=r['shared_line_id'],folio=r['folio'],task_id=task,block_id=block,line_number=r['line_number'],line_width=r['line_width'],block_median_width=str(median),wrapped=flag,length_bin='short' if flag else 'normal'))
    tests=[wrap(85,[100,100,85])[0],not wrap(86,[100,100,86])[0],wrap(85,[90,110])[0],not wrap(1,[1])[0]];assert all(tests)
    out=dict(status='DERIVED_FROM_BLIND_GEOMETRY',rule='line_width <= 17/20 * within-block median line width; equality is wrapped',owner='v4 blind registration',source_sha256=hashlib.sha256(G.read_bytes()).hexdigest(),rule_owner_sha256=hashlib.sha256(RULE.read_bytes()).hexdigest(),original_spec_sha256=hashlib.sha256(SPEC.read_bytes()).hexdigest(),lines=len(output),blocks=len(groups),short=sum(r['wrapped'] for r in output),normal=sum(not r['wrapped'] for r in output),noncontiguous_blocks=gaps,labels_joined=False,text_loaded=False,rows=sorted(output,key=lambda r:r['shared_line_id']))
    (P/'WRAP-FLAGS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
if __name__=='__main__':main()
