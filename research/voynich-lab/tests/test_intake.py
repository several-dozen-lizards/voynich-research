import random
import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.parse_ivtff import clean, logical_lines, parse, edit_distance, UNK

class IntakeTests(unittest.TestCase):
    def test_real_source_receipts_and_reported_distances(self):
        root = Path(__file__).resolve().parents[1]
        rows = parse(root/'data/raw/LSI_ivtff_0d.txt', 'LSI')
        zl = parse(root/'data/raw/ZL3b-n.txt', 'ZL')
        self.assertEqual(len(rows), 17344)
        self.assertEqual(len(zl), 5385)
        self.assertEqual(len({r['folio'] for r in zl}), 227)
        lookup = {(r['line_id'],r['transcriber']):r['text_eva'] for r in rows}
        with (root/'report/agreement_lines.csv').open(encoding='utf-8', newline='') as f:
            pairs = list(csv.DictReader(f))
        rng = random.Random(1729)
        for pair in rng.sample(pairs, 200):
            a = lookup[pair['line_id'],pair['transcriber_a']].replace(UNK,'\ue000')
            b = lookup[pair['line_id'],pair['transcriber_b']].replace(UNK,'\ue001')
            prev = list(range(len(b)+1))
            for i,x in enumerate(a,1):
                row = [i]
                for j,y in enumerate(b,1):
                    row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
                prev = row
            self.assertEqual(int(pair['distance']), prev[-1])

    def test_markup(self):
        self.assertEqual(clean('<%>q[o:a].{cth}y,???.@192;<!ignored><->dar<$>'), f'qo cthy {UNK} {UNK} dar')
        self.assertEqual(clean('ch!ol.%%%%'), f'chol {UNK}')
        self.assertEqual(clean('q[{cto}:@194;]y'), 'qctoy')

    def test_continuation(self):
        self.assertEqual(list(logical_lines('<f1r.1,@P0> qo/\n/kedy')), [(1, '<f1r.1,@P0> qokedy')])
        with self.assertRaises(ValueError):
            list(logical_lines('<f1r.1,@P0> qo/\nwrong'))

    def test_metadata_and_interlinear_paragraphs(self):
        fixture = '''#=IVTFF Eva- 1.5
<f1r> <! $I=H $H=2 $L=A>
<f1r.1,@P0;H> <%>qo
<f1r.1,@P0;F> qo
<f1r.2,+P0;H> dar<$>
<f1r.2,+P0;F> dar<$>
<f1v> <! $I=Z>
<f1v.1,@Ls;H> chol
'''
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            path = Path(tmp)/'sample.txt'
            path.write_text(fixture)
            rows = parse(path, 'LSI')
        self.assertEqual(rows[2]['line_index_in_paragraph'], 1)
        self.assertIsNone(rows[1]['line_index_in_paragraph'])
        self.assertIsNone(rows[0]['hand_scribe'])
        self.assertEqual(rows[0]['currier_hand'], '2')
        self.assertIsNone(rows[-1]['currier_lang'])
        self.assertTrue(rows[-1]['is_label'])

    def test_exact_edit_distance_against_independent_dynamic_program(self):
        rng = random.Random(1729)
        def reference(a,b):
            prev = list(range(len(b)+1))
            for i,x in enumerate(a,1):
                row = [i]
                for j,y in enumerate(b,1):
                    row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
                prev = row
            return prev[-1]
        for _ in range(500):
            a = ''.join(rng.choices('abc ', k=rng.randrange(50)))
            b = ''.join(rng.choices('abc ', k=rng.randrange(50)))
            self.assertEqual(edit_distance(a,b), reference(a,b))

if __name__ == '__main__':
    unittest.main()
