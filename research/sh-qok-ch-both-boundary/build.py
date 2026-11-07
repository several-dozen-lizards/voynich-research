from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent
original=(P/'sh-qok-feasibility-boundary/run.py').read_text()
for mode,base,hi in [('ch',1320000,(134,141)),('both',1420000,(84,91))]:
 d=R/mode;d.mkdir(exist_ok=True)
 start=original.index("if sys.argv[1]=='freeze':")
 end=original.index("for p,h in json.loads",start)
 protocol=f'''if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh {mode} boundary synthetic controls only. No manuscript or H/F data.',generator='Same12page4targetbody7linebalanced structure,V576/7. Direct conditional mask generation: choose available ch count uniformly34..40 of336; sh count uniformly{hi[0]}..{hi[1]-1} of336. Sample positions uniformly within each prefix class. This deliberately conditions masks on prefix, NOT independent-mask rejection sampling; all masks precede qok outcomes. Fixed chx blockers preserve target support. Conditional mask construction is part of the selection challenge.',gate='Require80<=V<84,>=8pages,maxshare<=.25,.10<=f_ch<=.12 and {'.39<=f_sh<=.43' if mode=='ch' else '.25<=f_sh<=.27'}.200freshlayouts,cap200attempts; failed designs retained, never replaced. Seeds{base}+attempt; outcome seeds{base+5000000}+attempt.',outcomes='Independent nonorigin-qok nulls .2,.6 and additive page/line/position logits; no prefix calibration in nulls. Positive availablematched followers .10/f_ch and.25/f_sh for weightedgap.15. Existing exact reference null andBonferroni8 unchanged. Nullclass labels describe no direct qok choice dependence among available followers; masks themselves can induce dependence and the test must reject specificity if falsely promoted as controlled.',gates='All200needed. PositiveWilson95lower>=.80; eachnullupper<=.05. Anyfailedcell failsqualification. No postoutcome correction, rescoring or threshold change. Keep expected structural gap, every outcome, masks and failures.',limits='Prefix-conditioned mask selection may bias the unchanged reference null. This run tests that risk, not a proof of exchangeability. Artificial blockers and balanced overlap are not historical coverage. H/F stay separate; manuscript closed.'))
 save('FREEZE.json',{{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES}});print('Frozen');sys.exit()
'''
 code=original[:start]+protocol+original[end:]
 code=code.replace("P=R.parent;FILES=", "P=R.parent.parent;FILES=")
 code=code.replace('range(2000)','range(200)').replace('1280000+attempt',f'{base}+attempt').replace('6280000+attempt',f'{base+5000000}+attempt')
 code=code.replace('available=set(int(x) for x in rng.choice(672,168,replace=False))',f'''byclass={{0:[],1:[]}}
 for idx,(ri,pos) in enumerate(followers):byclass[int(rows[ri][1][pos-1].startswith('sh'))].append(idx)
 assert all(len(v)==336 for v in byclass.values())
 nc=int(rng.integers(34,41));ns=int(rng.integers({hi[0]},{hi[1]}))
 available=set(int(x) for x in rng.choice(byclass[0],nc,replace=False))|set(int(x) for x in rng.choice(byclass[1],ns,replace=False))''')
 code=code.replace("f[0]>=.1 and .25-1e-12<=f[1]<=.27",f".1<=f[0]<=.12 and {'.39<=f[1]<=.43' if mode=='ch' else '.25-1e-12<=f[1]<=.27'}")
 code=code.replace("assert abs(V-576/7)<1e-9 and abs(sum(f)-.5)<1e-12","assert abs(V-576/7)<1e-9 and abs(f[0]-nc/336)<1e-12 and abs(f[1]-ns/336)<1e-12")
 (d/'run.py').write_text(code,encoding='utf-8')
print('Built both candidates before outcomes.')
