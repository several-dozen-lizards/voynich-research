from pathlib import Path
import json,hashlib
from datetime import datetime,timezone

R=Path(__file__).resolve().parent
def load(n):return json.loads((R/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    for n in ['VERIFICATION.json','EXACT-INTEGER-AUDIT.json','QUALIFICATION-AUDIT.json']:assert load(n)['status']=='PASS'
    text=(R/'REPORT.md').read_text(encoding='utf-8')
    assert '## Detailed control results' not in text
    q=load('QUALIFICATION.json')['results'];support=load('SUPPORT.json');secondary=load('SECONDARY.json');sens=load('SENSITIVITY.json');panels=load('PANELS.json')
    text+='\n## Detailed control results\n\nAll rejection flags use the conservative first Holm threshold .05/4. Wilson gates use all attempted trials, including abstentions. A null gate qualifies the finite end-to-end procedure here; it does not show calibration conditional on receiving a nondegenerate score.\n\n'
    text+='| Test | Cell | Scenario | Role | Flags / attempts | Wilson 95% | No p computed | Gate |\n|---|---|---|---|---:|---|---:|---|\n'
    for kind,cells in q.items():
        for cell,v in cells.items():
            for c in v['controls']:
                text+=f"| {kind} | {cell} | {c['scenario']} | {c['role']} | {c['flags']}/{c['trials']} | [{c['wilson95'][0]:.5f}, {c['wilson95'][1]:.5f}] | {c['not_tested']} | {c['gate'] if c['gate'] is not None else 'diagnostic only'} |\n"
    text+='\nH2 P1-F failed the additive null: 1/100 flags, Wilson upper 0.054486 > 0.05. Its positive control passed, but that cannot rescue failed null qualification. H1 P2-F additionally failed junction-only qualification (4/200; upper 0.050287), and both P2 readings had inadequate +15-point power. These failures remain recorded even though the earlier support gate already blocks both P2 manuscript tests.\n'
    text+='\n## Event exclusions\n\n| Cell | Unknown origin slots | Origin at line end | Following unknown |\n|---|---:|---:|---:|\n'
    for cell,s in support.items():
        ex=s['exclusions'];text+=f"| {cell} | {ex.get('unknown_origin',0)} | {ex.get('origin_at_end',0)} | {ex.get('following_unknown',0)} |\n"
    text+='\nAbsent exclusion keys in SUPPORT.json mean zero, not missing measurement.\n'
    text+='\n## Interpretation and execution receipts\n\n'
    text+='H1 passes the frozen two-reading primary rule: H +5.895 points [0.557, 11.554], F +6.414 [1.513, 11.285]; exact raw p 0.01360434 / 0.01031677; Holm-over-four adjusted p 0.04126710 in each reading. The two readings are not independent replications. The result concerns the specified mixture of non-bathing hand-2 pages; no post-outcome botanical-only or unsearched-subset test was added.\n\n'
    text+='P1 has 20 previously searched folios and six outside the listed sh→qok searches. P2 has seven previously searched folios and five outside those searches. P2 f65r/f73r/f73v have no P-unit coverage and remain in the declared lists. Neither combined panel is called untouched. No first-ever non-circular confirmation is claimed.\n\n'
    text+='H2 H has gain +0.00348252 bits/event (equal-folio average), raw sign-flip p 0.28462219 and Holm p 1.0: NO PASS. H2 F was not inferentially scored. H2 groups exact physical-page Folio identifiers, including separate recto/verso pages; it does not hold out an entire numbered leaf jointly as the old context-transfer extractor did. This limits the comparison with attempt B and may retain dependence between related pages. No grammar-versus-junction conclusion follows.\n\n'
    text+='The unchanged transported weak-score sensitivity produced no passing score in either P1 reading (raw p H 0.622867, F 0.685036; original factor-four p 1 in each). It tests the original far-context interaction with a sh/ch target, not H1’s adjacency effect or H2’s qok target, and cannot rescue either test.\n\n'
    text+='The original worker disappeared after 4,576 durably saved trials. RESUME.json records the event and file hash; only the remaining 424 predeclared jobs were run. All 5,000 trial keys and seeds are unique. No code, seed, quota or acceptance threshold changed.\n\n'
    text+='Independent verification passed: all 9,823 event/exclusion ledger rows; all primary/descriptive effects; primary bootstrap intervals; H2 fold separation and saved losses; exact H1 p-values recomputed using integer assignment counts; all 5,000 synthetic outcome hashes replayed; all 30 Wilson control gates recomputed; and all frozen hashes and phase order checked. See VERIFICATION.json, EXACT-INTEGER-AUDIT.json and QUALIFICATION-AUDIT.json.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    v=load('VERIFICATION.json');v['supplementary_audits']={n:dict(status=load(n)['status'],sha256=sha(R/n)) for n in ['EXACT-INTEGER-AUDIT.json','QUALIFICATION-AUDIT.json']}
    (R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
    files=[p for p in R.iterdir() if p.is_file() and p.name!='DELIVERY-MANIFEST.json']
    out=dict(utc=datetime.now(timezone.utc).isoformat(),status='COMPLETE_WITH_PRESERVED_SUPPORT_AND_QUALIFICATION_FAILURES',files={p.name:sha(p) for p in sorted(files)})
    (R/'DELIVERY-MANIFEST.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=out['status'],files=len(files),primary_two_reading_pass=True,verification='PASS')))

if __name__=='__main__':main()
