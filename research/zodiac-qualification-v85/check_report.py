from pathlib import Path
from html.parser import HTMLParser
import json
P=Path(__file__).resolve().parent
class Check(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='href': assert (P/v).exists(),v
s=(P/'report.html').read_text(encoding='utf-8')
Check().feed(s)
assert s.count('<table')==s.count('</table>')
assert len((P/'replicates.jsonl').read_text().splitlines())==280
print('HTML parsed; local links verified; table tags balanced; 280 trials retained. No rendered-UI claim.')
