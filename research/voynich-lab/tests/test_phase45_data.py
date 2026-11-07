import sys,json,unittest,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.encoders import expansive
from src.extend_phase3 import manuscript,visible,read
from src.phase3 import ROOT
import xml.etree.ElementTree as ET

class ExtensionTests(unittest.TestCase):
    def test_C12_is_injective_at_every_registered_setting(self):
        config=json.loads((ROOT/'configs/phase3.json').read_text())
        for length in [2,3,4]:
            for rigidity in [0,.5,1]:
                words,meta=expansive(['periculum','solis','luna','atque','in','et','a']*5,random.Random(10),config,length,rigidity)
                codes=meta['codebook']
                self.assertEqual(len(codes),len(set(codes.values())))
                self.assertEqual({len(s) for s in codes.values()},{length})
                self.assertTrue(all(len(w)%length==0 for w in words))
                for slot in range(length):
                    observed=len({code[slot] for code in codes.values()})
                    self.assertEqual(observed,1 if slot in meta['shared_slots'] else len(codes))

    def test_diplomatic_choices_never_double_count_expansion(self):
        node=ET.fromstring('<w>co<choice><abbr>q<am>~</am></abbr><expan>qu<ex>e</ex></expan></choice></w>')
        self.assertEqual(visible(node),'coq~')

    def test_C13_preserves_authentic_source_line_records(self):
        rows,meta=manuscript()
        self.assertEqual(len(rows),2252)
        self.assertEqual(len({r['line_id'] for r in rows}),2252)
        self.assertEqual(len({r['folio'] for r in rows}),36)
        self.assertEqual(sum(len(r['text_eva'].split()) for r in rows),11056)
        self.assertTrue(all(r['image_coordinates'] and r['source_xml'] for r in rows))
        self.assertEqual(meta['license'],'CC0 1.0')
        self.assertTrue(all(r['is_para_start'] is None for r in rows))

    def test_C13_leaf_sides_never_cross_split(self):
        split=json.loads((ROOT/'configs/C13_page_split.json').read_text())
        leaf={}
        for page,group in split.items():
            key=page[:-1]
            if key in leaf:self.assertEqual(leaf[key],group)
            leaf[key]=group

    def test_entropy_table_has_requested_T1_T2_rows(self):
        rows=read(ROOT/'report/T1_T2_entropy_comparison.csv')
        self.assertEqual(len(rows),16)
        self.assertEqual({r['tokenization'] for r in rows},{'T1','T2'})
        self.assertIn('C12_clean',{r['corpus'] for r in rows})

if __name__=='__main__':unittest.main()
