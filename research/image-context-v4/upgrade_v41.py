"""Apply authorized picture-only amendment; retain the entire prior packet."""
from pathlib import Path
import shutil,json,hashlib,html,zipfile
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
 archive=R/'research-only/pre-v4.1';archive.mkdir(exist_ok=True)
 for n in ['MANUAL.md','PROTOCOL.json','PROTOCOL-NOTES.md','README.txt','STATUS.json','VERIFICATION.json','SHA256SUMS.json','prepare.py','tool-template.html','validate_ratings.py','verify.py','verify-tool.js','v4-rater-only.zip']:
  if not (archive/n).exists():shutil.copy2(R/n,archive/n)
 manual="""You'll be shown pages from an illustrated manuscript. You don't need to read the writing.

For each page, draw a box around every picture element and give it one category:

PL — Plant: roots, stems, leaves, flowers, seeds, whole plants, plant fragments.
VE — Vessel: jars, containers, pots, flasks.
FG — Figure / water: human figures, tubs, pools, pipes, tubes.
CE — Celestial / round: stars, sun, moon, rosettes, wheels, circular diagrams.
OT — Other: anything else drawn.

Don't judge what anything means. If you're unsure of a category, use OT and add a note.

Do not mark writing, writing blocks or writing lines.
Return one row per picture element (page, box, category, note). Mark every reviewed page complete, including pages with no picture elements.
"""
 (R/'MANUAL.md').write_text(manual,encoding='utf-8');shutil.copy2(R/'MANUAL.md',R/'rater-only/MANUAL.md')
 tasks=json.loads((R/'rater-only/TASKS.json').read_text())
 template=(R/'picture-tool-template.html').read_text(encoding='utf-8')
 (R/'rater-only/index.html').write_text(template.replace('__MANUAL__',html.escape(manual)).replace('__TASKS__',json.dumps(tasks)),encoding='utf-8')
 freeze=dict(version='v4.1',status='PICTURE_ONLY_PACKET_FROZEN_BEFORE_RATINGS',authority='AMENDMENT-v4.1-agreement-unit.md',amendment_sha256=sha(R/'AMENDMENT-v4.1-agreement-unit.md'),manual_sha256=sha(R/'MANUAL.md'),tool_sha256=sha(R/'rater-only/index.html'),tasks_sha256=sha(R/'rater-only/TASKS.json'),shared_line_geometry='Independent blind registrar; no rater writing boxes; registrar cannot see either picture-box set; freeze before applying picture ratings.',G6='Six-way per-registered-line kappa >=0.60 before OT merge; governs H-IMG',G2='PL/not-PL kappa >=0.60; governs H-PLANT',gate_timing='Two independent raters before adjudication',original_protocol_sha256=sha(archive/'PROTOCOL.json'),raters=0,registration='NOT RUN',agreement='NOT RUN',outcome_join='CLOSED')
 dump(R/'PROTOCOL-v4.1.json',freeze)
 status=json.loads((R/'STATUS.json').read_text());status.update(status='V4.1 PICTURE-ONLY PACKET READY; INDEPENDENT REGISTRAR AND TWO BLIND RATERS STILL REQUIRED',amendment='v4.1',agreement_rule='G6 and G2 pre-adjudication',writing_annotation_by_raters=False,shared_geometry='NOT RUN; registrar independent of both picture-box sets')
 dump(R/'STATUS.json',status)
 with zipfile.ZipFile(R/'v4-rater-only.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((R/'rater-only').rglob('*')):
   if p.is_file():z.write(p,p.relative_to(R/'rater-only'))
 (R/'README.txt').write_text('V4.1 PICTURE-ONLY RATER PACKET — 24 October 2026\n\nExtract v4-rater-only.zip and open index.html. Raters annotate picture elements only; mark each reviewed page complete, including pages with no pictures. Export JSON before closing; import to resume. Each independent rater receives a clean copy with only native images, anonymous canvas dimensions and the amended manual. No writing boxes, text, results or shared line geometry enter the rater packet.\n\n168 pages ready; 34 ambiguous/composite folios withheld; reserved zodiac excluded. Zero raters/ratings so far. Independently blind registration must supply one shared line geometry, without seeing either rater picture-box set. Each picture set then independently labels those lines using the two-height rule. G6 six-way and G2 PL/not-PL kappa are computed before OT merge and before adjudication, and govern H-IMG/H-PLANT separately. Unregistered blocks are dropped/listed, never invented rater disagreements.\n\nOriginal v4 packet and preparation scripts remain in research-only/pre-v4.1. prepare.py is historical; do not run it to rebuild v4.1. Rebuild with upgrade_v41.py. PROTOCOL-v4.1.json supersedes the original PROTOCOL.json on amended matters. Current verification uses verify_v41.py; validate_picture_ratings.py accepts v4.1 exports. The original pilot scorer/tool remain archived research-only; their plant-match endpoint differs from v4.1.\n\nNo ratings, shared geometry, agreement, support, controls, joins or scientific tests have been run. The v3.2 source question is separate; v103 remains parked. No more Rosettes leave-out grids.\n',encoding='utf-8')
 print(json.dumps(status,indent=2))
if __name__=='__main__':main()
