import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.surprise import fold_splits,leaf_key,score_rows
from src.fingerprint import chunks
from src.probes import representations,fit_probe
from src.train import torch,np

class AnalysisTests(unittest.TestCase):
    def test_crossfit_test_leaves_are_never_train_or_validation(self):
        rows=[dict(folio=f'f{i}{side}') for i in range(1,21) for side in ['r','v']]
        splits=fold_splits(rows)
        for split in splits:
            parts={part:{leaf_key(p) for p,v in split.items() if v==part} for part in ['train','validation','test']}
            self.assertFalse(parts['test']&parts['train']);self.assertFalse(parts['test']&parts['validation'])
        for r in rows:self.assertEqual(sum(s[r['folio']]=='test' for s in splits),1)

    def test_classifier_chunks_are_disjoint_and_small_remainder_excluded(self):
        rows=[dict(line_id=str(i),text_eva=' '.join(['ab']*100)) for i in range(53)]
        result=chunks(rows)
        self.assertEqual(len(result),2)
        self.assertFalse({r['line_id'] for r in result[0][1]}&{r['line_id'] for r in result[1][1]})

    def test_clean_noise_chunks_share_source_boundaries(self):
        clean=[dict(line_id=str(i),text_eva=' '.join(['ab']*100)) for i in range(60)]
        noise=[dict(line_id=str(i),text_eva=' '.join(['ab']*110)) for i in range(60)]
        membership=lambda rows,template:{r['line_id']:block for block,rs in chunks(rows,template) for r in rs}
        self.assertNotEqual(membership(clean,None),membership(noise,None))
        self.assertEqual(membership(clean,clean),membership(noise,clean))

    def test_probe_representation_sees_last_symbol_without_metadata(self):
        class FakeModel(torch.nn.Module):
            with_position=False
            def __init__(self):super().__init__();self.dummy=torch.nn.Parameter(torch.zeros(1))
            def forward(self,x,events,return_hidden=False):
                self.assertion=bool((events==0).all())
                return torch.zeros(*x.shape,5),x.float().unsqueeze(-1)
        model=FakeModel()
        config=dict(context_length=8,batch_size=2,embedding_dim=1)
        spec=dict(vocabulary=['<PAD>','<UNK>','<BOS>','a','b'],tokenization='T1',bpe_merges=None)
        f=representations(model,[dict(text_eva='ab')],spec,config)
        self.assertAlmostEqual(f[0,0],3.0);self.assertTrue(model.assertion)

    def test_probe_majority_comes_from_training_not_test(self):
        x=np.array([[0],[1],[0],[1],[0],[1],[0],[1],[0],[1],[0],[1]],dtype=float)
        y=['A','B']*6;groups=['train']*6+['validation']*2+['test']*4
        result=fit_probe(x,y,groups,[.1,1])
        self.assertEqual(result['test'],4);self.assertEqual(result['majority_baseline'],.5)
        self.assertEqual(result['accuracy'],1.0)

    def test_token_surprisal_reconciles_with_word_scores_and_literal_escape(self):
        class UniformModel(torch.nn.Module):
            def __init__(self):super().__init__();self.dummy=torch.nn.Parameter(torch.zeros(1))
            def forward(self,x,events):return torch.zeros(*x.shape,7)
        from src.train import ROOT
        config=json.loads((ROOT/'configs/phase4.json').read_text())
        prepared=dict(name='ZL_running',scheme='T1',vocabulary=['<PAD>','<UNK>','<BOS>','a','b','c',' '],merges=None)
        rows=[dict(folio='f1r',line_id='test',text_eva='az b',is_para_start=None,is_label=True,currier_lang=None)]
        tokens=[];words,lines=score_rows(UniformModel(),prepared,rows,config,independent_lines=True,token_sink=tokens)
        self.assertEqual(len(words),2)
        self.assertAlmostEqual(sum(r['bits'] for r in words),sum(r['total_bits'] for r in tokens if r['word_index'] is not None),places=5)
        self.assertEqual(sum(r['literal_escape_bits'] for r in tokens),40)
        self.assertTrue(all(r['is_label'] for r in words))

if __name__=='__main__':unittest.main()
