from pathlib import Path
import ast,collections,hashlib,json,math,re
R=Path(__file__).resolve().parent
tree=ast.parse((R/'extract.py').read_text(encoding='utf8'))
ns={'json':json}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='panels'],type_ignores=[]),'extract.py','exec'),ns)
events=json.loads((R.parent/'fp-boundary-transfer-reed-v102/PROSE-EVENTS.json').read_text(encoding='utf8'))
lookup={(x['tr'],x['loc'],x['index']):x for x in events}
cells_checked=panels_checked=0
for name in ['TRAINING-RESULTS.json','TEST-RESULTS.json']:
    for p in ns['panels'](R/name):
        panels_checked+=1;page_cells=collections.defaultdict(list)
        for cell in p['cells']:
            cells_checked+=1;counts=[]
            for side,op in [('opening_events',True),('continuation_events',False)]:
                nA=nB=0
                for loc,idx,w in cell[side]:
                    x=lookup[(p['transcriber'],loc,idx)]
                    assert x['word']==w and x['opening']==op and x['split']==p['split']
                    assert x['page']==cell['key'][0] and idx==cell['key'][5]
                    inds=[i for i,ch in enumerate(w) if ch in 'ktfp'];assert len(inds)==1
                    j=inds[0];assert w[:j]+'_'+w[j+1:]==cell['key'][4]
                    assert not re.search('cth|ckh|cph|cfh',w)
                    if p['view']=='exact_line_length':assert x['n']==cell['key'][6]
                    if p['view']=='shared_structure':assert x['paired_structure']
                    if w[j] in p['A']:nA+=1
                    else:assert w[j] in p['B'];nB+=1
                counts.extend([nA,nB])
            assert counts==cell['counts']
            a,b,c,d=counts
            informative=bool(a+b and c+d and a+c and b+d)
            assert informative==(cell['status']=='informative')
            if informative:
                gap=a/(a+b)-c/(c+d);wt=(a+b)*(c+d)/(a+b+c+d)
                assert math.isclose(gap,cell['estimate']['gap'],abs_tol=1e-12)
                page_cells[cell['key'][0]].append((gap,wt))
        gaps=[sum(g*w for g,w in es)/sum(w for _,w in es) for es in page_cells.values()]
        assert len(gaps)==p['eligible_pages']
        if gaps:assert math.isclose(sum(gaps)/len(gaps),p['gap'],abs_tol=1e-12)
        else:assert p['gap'] is None
        assert sum(g>0 for g in gaps)==p['positive_pages']

raw=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
examples=json.loads((R/'INFORMATIVE-EXAMPLES.json').read_text(encoding='utf8'))
locs={z[0] for x in examples for side in ['opening_events','continuation_events'] for z in x[side]}
source=[];previous={}
for line in raw.read_text(encoding='latin1').splitlines():
    m=re.match(r'^<([^;]+);([HF])>',line)
    if not m:continue
    loc,tr=m.groups();pg=loc.split('.')[0]
    if loc in locs:source.append({'locator':loc,'transcriber':tr,'raw':line,'preceding_source_record':previous.get((tr,pg))})
    if '.P' in loc:previous[(tr,pg)]=line
(R/'SOURCE-EXCERPTS.json').write_text(json.dumps(source,indent=2),encoding='utf8')
result={'all_panels_recomputed':panels_checked,'all_cells_recounted':cells_checked,'all_counts_frames_positions_and_page_gaps_agree':True,
        'source_excerpt_records':len(source),'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
        'inputs_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in json.loads((R/'INPUT-FREEZE.json').read_text()).items())}
assert result['inputs_unchanged']
(R/'INDEPENDENT-VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
