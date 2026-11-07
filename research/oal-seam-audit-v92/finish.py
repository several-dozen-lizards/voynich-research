from pathlib import Path
import hashlib,json
from html.parser import HTMLParser
P=Path(__file__).resolve().parent
s=(P/'report.html').read_text(encoding='utf-8')
lead='''<div style="background:#29404b;padding:20px"><b>Result: oal is not specific to astronomy.</b><p>H has three standalone oal tokens, at f17v.P.21 (botanical), f86v5.P.26 (Rose obverse), and f113r.P.3 (starred paragraphs). Of eight oal-initial tokens, only three are astronomy/astrology—and those are exactly the three oalch tokens. Additional oal-initial forms are botanical oaldary and starred-paragraph oaldar.</p><p>H oal anywhere:12 astronomy/astrology,12 botanical,12 starred paragraphs,1 baths,1 recipes,1 Rose obverse. Thus oal is widespread but not evenly distributed: astronomy has12/39 occurrences against8.05% of H readable tokens. These are descriptive ratios, not hand/format-controlled enrichment evidence.</p><p>The alch count87 is substring-bearing tokens, not87 standalone alch words: exact alch is absent in H. Astronomy contributes14/87, so the claim that sections receive alch in exact proportion to size is not established either.</p><p>At f39r.P.4, H reads okal!cheg, C reads okal.cheg, F/U read okal!chem. The tokenizer removes ! but retains dot boundaries. Literal oalcheg splits as oal + cheg, not oal + chem. The g/m variation must remain a separate transcription question.</p><p>F has3 standalone oal and5 initial occurrences, also outside astronomy; its astronomical coverage is only329 readable tokens versus2956 in H, so F's zero oalch is not independent evidence of absence. U/V support oalcheol and oalcheg at the known loci; H oalchdm has competing allchdm readings.</p><p>The proposed exclusive oal astronomy-marker prediction fails. The narrower oalch observation and a possible al|ch seam remain hypotheses. Neither the distribution nor a seam split establishes or refutes a Pleiades interpretation on its own.</p></div>'''
s=s.replace('<h2>Counts by reading</h2>',lead+'<h2>Counts by reading</h2>');(P/'report.html').write_text(s,encoding='utf-8')
class Check(HTMLParser):
 def handle_starttag(self,t,a):
  for k,v in a:
   if k=='href':assert (P/v).exists(),v
Check().feed(s)
assert s.count('<table')==s.count('</table>')
(P/'SHA256SUMS.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.iterdir() if f.is_file() and f.name!='SHA256SUMS.json'},indent=2),encoding='utf-8')
print('Findings added; links and table structure verified.')
