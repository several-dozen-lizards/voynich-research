"""Copy-first C12 extension; original phases and C16 families are read-only."""
from pathlib import Path
import os,shutil,json,hashlib,csv
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[1];I=ROOT/'instrument';OLD=LAB/'runs/phase5-c2f38fa45d6b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    assert not (ROOT/'INPUT_SNAPSHOT.json').exists()
    for sub in ['src','configs']:
        shutil.copytree(LAB/sub,I/sub,ignore=shutil.ignore_patterns('__pycache__'))
    (I/'data/raw').mkdir(parents=True,exist_ok=True);shutil.copyfile(LAB/'data/raw/hildegard_1903_ocr.txt',I/'data/raw/hildegard_1903_ocr.txt')
    ref=ROOT/'reference';ref.mkdir(exist_ok=True)
    for name in ['growth_and_lengths_extended.json','master_metrics_extended.csv','line_position_gain.csv','shorthand_sweep.csv','shorthand_sweep_model_runs.csv','noise_model.json']:
        shutil.copyfile(OLD/name,ref/name)
    shutil.copyfile(LAB/'data/controls/C1/clean.csv',ref/'C1-layout.csv');shutil.copyfile(OLD/'FREEZE.json',ref/'OLD_FREEZE.json')
    oldfreeze=json.loads((ref/'OLD_FREEZE.json').read_text());required=['src/train.py','src/tokenize.py','src/phase3.py','src/encoders/__init__.py','src/noise.py','src/parse_ivtff.py','src/metrics.py']
    for name in required:assert sha(I/name)==oldfreeze[name.replace('/','\\')],name
    for code in ['SW04']+[f'SW{i:02d}' for i in range(9,18)]:
        folder=ref/code;folder.mkdir()
        for name in ['clean.csv','noise.csv','encoder.json']:shutil.copyfile(OLD/'sweep'/code/name,folder/name)
        for version in ['clean','noise']:
            for pos in [0,1]:
                for seed in [1729,1733,1741,1753,1777]:
                    name=f'{code}-{version}-p{pos}-s{seed}';(ref/'jobs'/name).mkdir(parents=True)
                    for f in ['config.json','metrics.json']:shutil.copyfile(OLD/'sweep'/name/f,ref/'jobs'/name/f)
    original={}
    for sub in ['src','configs','report']:
        for p in (LAB/sub).rglob('*'):
            if p.is_file() and '__pycache__' not in str(p):original[str(p.relative_to(LAB))]=sha(p)
    for c in ['C5','C12']:
        for p in (LAB/'data/controls'/c).glob('*'):
            if p.is_file():original[str(p.relative_to(LAB))]=sha(p)
    dump(ROOT/'INPUT_SNAPSHOT.json',dict(original_lab_hashes=original,reference_hashes={str(p.relative_to(ROOT)):sha(p) for p in list(ref.rglob('*'))+list((I/'src').rglob('*.py'))+list((I/'configs').glob('*.json'))+[I/'data/raw/hildegard_1903_ocr.txt'] if p.is_file()},new_manuscript_instrument_runs=0))
    print(json.dumps(dict(snapshot_files=len(original),old_endpoint_jobs=200,source_instrument_matches_old_freeze=True)))
if __name__=='__main__':main()
