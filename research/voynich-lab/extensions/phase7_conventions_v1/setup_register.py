from common import *
import shutil,ast
def main():
    assert not (R/'REGISTRATION.json').exists()
    # Metadata only. Do not import target strings or feature extractors here.
    layout=json.loads((OLD/'LAYOUT.json').read_text());available={page(r['folio']) for r in layout};hids=set()
    with (LAB/'data/voynich/LSI_H_running.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):hids.add(page(row['folio']))
    common=sorted(available&hids,key=lambda p:(leaf(p),p));dump(R/'COMMON_PAGES.json',common);eligible=sorted({leaf(p) for p in common})
    phy={};sheet=0
    def add(q,pairs):
        nonlocal sheet
        for j,(a,b) in enumerate(pairs):
            sheet+=1
            for l,other in [(a,b),(b,a)]:phy[str(l)]=dict(leaf=l,conjugate=other,quire=q,sheet=f'q{q:02d}s{j+1}',sheet_index=j,quire_index=q-1,source=f'https://www.voynich.nu/q{q:02d}/index.html',missing=l in [12,59,60,61,62,63,64,74,91,92,97,98,109,110])
    for q in range(1,8):
        a=(q-1)*8+1;add(q,[(a+i,a+7-i) for i in range(4)])
    for q,pairs in [(8,[(57,66),(58,65),(59,64),(60,63),(61,62)]),(9,[(67,68)]),(10,[(69,70)]),(11,[(71,72)]),(12,[(73,74)]),(13,[(75,84),(76,83),(77,82),(78,81),(79,80)]),(14,[(85,86)]),(15,[(87,90),(88,89)]),(16,[(91,92)]),(17,[(93,96),(94,95)]),(18,[(97,98)]),(19,[(99,102),(100,101)]),(20,[(103,116),(104,115),(105,114),(106,113),(107,112),(108,111),(109,110)])]:add(q,pairs)
    assert len(phy)==116 and all(str(l) in phy and not phy[str(l)]['missing'] for l in eligible)
    dump(R/'PHYSICAL.json',phy);shuffled=eligible[:];random.Random(1729).shuffle(shuffled);dump(R/'FOLDS.json',{str(l):i%5 for i,l in enumerate(shuffled)})
    shutil.copyfile(LAB/'configs/phase3.json',R/'phase3.json');shutil.copyfile(OLD/'reference/noise_model.json',R/'noise_model.json') if (OLD/'reference/noise_model.json').exists() else shutil.copyfile(LAB/'runs/phase5-c2f38fa45d6b/noise_model.json',R/'noise_model.json')
    source=R.parent/'prior_work_v1';java=next((source/'raw/mzattera').rglob('SlotAlphabet.java'));folder=R/'raw/mzattera';folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(java,folder/'SlotAlphabet.java')
    for p in (source/'raw/mzattera').rglob('*LICENSE*'):
        if p.is_file():shutil.copyfile(p,folder/p.name)
    adapter=(source/'slots.py').read_text(encoding='utf8').replace('from .common import EXT','from common import R as EXT');(R/'slots_adapter.py').write_text(adapter,encoding='utf8')
    shutil.copyfile(source/'THIRD_PARTY_NOTICES.md',R/'THIRD_PARTY_NOTICES.md')
    # The user revised the primary test to be order-agnostic. Secondary source limitations remain explicit.
    orders=[dict(id='current_binding',status='ADMITTED_SENSITIVITY_ONLY',citation='https://www.voynich.nu/layout.html',kind='current_binding',primary=False),dict(id='Bunn2010_Pelling2022_Q20_center_fragment',status='ADMITTED_FRAGMENT_SENSITIVITY_ONLY',citation='https://ciphermysteries.com/2022/12/20/quire-20-order-from-chaos-part-1-evidence',pages=['f111r','f111v','f108r','f108v'],note='Four-page proposed center only; below10-pair minimum, not a whole-book order.'),dict(id='Pelling2022_Q20_subquires',status='NO_UNIQUE_PAGE_SEQUENCE',citation='https://ciphermysteries.com/2022/12/20/quire-20-order-from-chaos-part-1-evidence',note='Proposed partition plus missing bifolio; do not invent within-partition ordering.'),dict(id='Pelling2006_Q13',status='PRIMARY_ORIENTATION_UNVERIFIED',citation='https://ciphermysteries.com/2010/06/15/the-four-main-voynich-ghosts',secondary_pointer='https://voynich.kiltau.com/bifolio/bM2',note='Secondary display has leaf order76,77,79,84,78,81,75,80,82,83; original orientation/page sequence not verified. No guessed numerical run.'),dict(id='Layfield_Davis2026_singulions_and_Q13_variant',status='PRIMARY_SOURCE_UNAVAILABLE',citation='https://doi.org/10.4000/16k0a',note='Publisher full text bot challenge. Secondary descriptions are not accepted as primary-order verification; source images are named by current nesting position. No inferred total reading order.'),dict(id='Zandbergen_Q9_refolding',status='NO_UNIQUE_PAGE_SEQUENCE',citation='https://www.voynich.nu/extra/sp_origin.html',note='Unused cuts/rebinding hypothesis does not specify a complete page sequence.'),dict(id='Pelling2022_Q20_follow_f106_with_f104',status='PARTIAL_PRECEDENCE_ONLY',citation='https://ciphermysteries.com/2022/12/22/quire-20-order-from-chaos-part-2-suggestions',pages=['f106v','f104r'],note='Proposed adjacency only; below10-pair minimum.'),dict(id='VoynichViews2015_Q13',status='PRIMARY_PAGE_SEQUENCE_NOT_RETRIEVED',citation='https://voynichviews.wordpress.com/2015/10/10/voynich-manuscript-re-ordering-the-folios-in-quire-13/',note='Identified through published cross-reference. No invented order.' )]
    dump(R/'ORDER_REGISTRY.json',orders)
    refs=[OLD/'common.py',OLD/'LAYOUT.json',OLD/'plaintext/C1.txt',OLD/'plaintext/C2.txt',OLD/'author/naibbe.py',OLD/'author/naibbe_tables.csv',LAB/'data/voynich/ZL_running.csv',LAB/'data/voynich/LSI_H_running.csv',LAB/'src/metrics.py',LAB/'src/tokenize.py',LAB/'src/noise.py',LAB/'src/phase3.py']
    original={}
    for folder in [OLD,R.parent/'c12_terminal_v1',R.parent/'c12_partial_v1']:
        for name in ['REGISTRATION.json','STATUS.json','VERIFICATION.json','REPORT.md','FAMILY_TERMINAL.json']:
            p=folder/name
            if p.exists():original[str(p.relative_to(LAB))]=sha(p)
    holds={}
    for folder in ['c16-kh','c16-kh-scorer-v2','c16-kh-scorer-v3']:
        for p in (LAB.parent/folder).glob('*'):
            if p.is_file() and any(t in p.name.upper() for t in ['STATUS','QUALIFICATION','REGISTRATION']):holds[str(p)]=sha(p)
    dump(R/'INPUT_SNAPSHOT.json',dict(reference_hashes={str(Path('..')/'..'/p.relative_to(LAB)):sha(p) for p in refs},preserved_originals=original,C16_holds=holds,metadata_only_before_gate=True))
    config=dict(k=list(range(1,13)),seeds=SEEDS,folds=5,components=20,covariance='tied',n_init=3,max_iter=500,tol=.0001,reg_covar=.001,permutations=1999,gate_exact_k_and_ARI=.8,passing_seeds=4,calibration_datasets=140)
    dump(R/'CONFIG.json',config)
    for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    frozen={str(p.relative_to(R)):sha(p) for p in list(R.glob('*.py'))+list(R.glob('*.md'))+list(R.glob('*.json'))+list((R/'sources').glob('*'))+list((R/'raw').rglob('*')) if p.is_file()};frozen.update(json.loads((R/'INPUT_SNAPSHOT.json').read_text())['reference_hashes'])
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_CONTROL_GENERATION_AND_MIXTURE_FITTING',files=frozen,target_text_feature_extraction=False,target_mixture_fits=0,real_analysis_gate='ALL_CALIBRATION_CELLS_PASS',codicology_primary='ORDER_AGNOSTIC',secondary_orders='source-limited hypotheses; no chosen order'))
    print(json.dumps(dict(status='REGISTERED',physical_pages=len(common),physical_leaves=len(eligible),calibration_datasets=140,target_text_features=0)))
if __name__=='__main__':main()
