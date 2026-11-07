import sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.train import LanguageModel,prepare,ROOT,torch
torch.set_num_threads(2)

class ModelTests(unittest.TestCase):
    def setUp(self):self.config=json.loads((ROOT/'configs/phase4.json').read_text())

    def test_maximum_vocabulary_models_stay_under_cap(self):
        for arch in ['lstm','transformer']:
            model=LanguageModel(4099,arch,True,self.config)
            self.assertLessEqual(model.count,5_000_000)

    def test_future_content_and_future_layout_cannot_change_past_prediction(self):
        for arch in ['lstm','transformer']:
            torch.manual_seed(81);model=LanguageModel(40,arch,True,self.config).eval()
            x=torch.randint(3,40,(2,12));events=torch.zeros_like(x)
            with torch.no_grad():a=model(x,events)
            changed=x.clone();changed[:,7:]=torch.randint(3,40,(2,5));events[:,7:]=7
            with torch.no_grad():b=model(changed,events)
            self.assertTrue(torch.allclose(a[:,:7],b[:,:7],atol=1e-6))

    def test_train_only_vocabulary_and_causal_boundary_flags(self):
        rows=[dict(folio='f1r',line_id='a',text_eva='ab',is_para_start=True,currier_lang='A'),
              dict(folio='f1r',line_id='b',text_eva='cd',is_para_start=False,currier_lang='A'),
              dict(folio='f2r',line_id='c',text_eva='ab',is_para_start=False,currier_lang=None),
              dict(folio='f3r',line_id='d',text_eva='zzz',is_para_start=False,currier_lang='B')]
        split={'f1r':'train','f2r':'validation','f3r':'test'}
        p=prepare('ZL_running','T1',self.config,rows=rows,split=split)
        self.assertNotIn('z',p['vocabulary'])
        self.assertEqual(p['oov']['test']['unknown'],3)
        self.assertEqual(p['tensors']['train'][0,2,:5].tolist(),[5,0,0,3,0])
        self.assertEqual(p['metadata'][0]['length'],5)

if __name__=='__main__':unittest.main()
