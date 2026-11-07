from pathlib import Path
import json,html
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def main():
 data={n:json.loads((W/f).read_text()) for n,f in [('pages','PAGES.json'),('units','EVT-STRUCTURE.json'),('candidates','GEOMETRY-CANDIDATES.json')]}
 template=(R/'tool-template.html').read_text(encoding='utf-8')
 (W/'index.html').write_text(template.replace('__DATA__',json.dumps(data)),encoding='utf-8')
 (W/'REGISTRAR-MANUAL.txt').write_text('Independent writing registrar only. Do not consult picture-rater files, outcomes, text readings, project chat, effect summaries or inferential reports. Inspect source pixels; verify every writing region and line. Automated rectangles are provisional and may contain drawings or miss writing. Correct, split, merge or replace them using geometry only. Select a P unit only when identity/order is unambiguous. Exact line count is necessary, not sufficient. H/F counts are separate. If a block count disagrees, retain visible lines and abstain; never remove visible rows to force a match. Preserve all ambiguities and every unregistered block. Native x,y,width,height rectangles; number physical lines top to bottom. Source P-unit headers/counts are provided without transcription bodies. Include unmapped writing blocks with unit=null and reason. Mark a page reviewed only after inspecting all writing blocks; unfinished pages remain unreviewed. No image category coding. Export JSON before closing; Python register.py validates and performs the count checks. Never certify blindness unless true.\n',encoding='utf-8')
 print(W/'index.html')
if __name__=='__main__':main()
