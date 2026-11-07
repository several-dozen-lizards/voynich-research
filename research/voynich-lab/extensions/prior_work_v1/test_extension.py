import unittest
from collections import Counter
from .common import *
from .controls import macaronic,noisy_truth,naibbe_module,alphagram,strip_vowels
from .slots import pieces,decompose,SLOTS
from .mixtures import CharFeatures,fit_em,score,initialize_embeddings
import numpy as np
from src.noise import inject

class ExtensionTests(unittest.TestCase):
    def test_macaronic_uses_joint_spelling_and_known_origins(self):
        template=[dict(folio='f1r',line_id=str(i),text_eva='a b c d e',is_para_start=i%2==0) for i in range(6)]
        first=['latin']*30;second=['german']*30
        for grain in ['word','phrase','paragraph']:
            selected,truth=macaronic(first,second,template,grain)
            for r,t in zip(selected,truth):self.assertEqual([int(w=='german') for w in r['text_eva'].split()],t['word_sources'])

    def test_origin_trace_exactly_replays_noise_including_spaces(self):
        text='alpha beta gamma delta '*100;text=text.strip();sources=[0,1,0,1]*100
        rates=dict(substitution=.021595507891541885,insertion=.010565686968838526,deletion=.010565686968838526)
        a=random.Random(1729);b=random.Random(1729)
        expected,_,_=inject(text,rates,set(text)-{' '},a)
        actual,fractions=noisy_truth(text,sources,rates,set(text)-{' '},b)
        self.assertEqual(actual,expected);self.assertEqual(a.getstate(),b.getstate());self.assertEqual(len(fractions),len(actual.split()))

    def test_naibbe_author_tables_and_deck_counts(self):
        mod=naibbe_module(1729)
        for deck,n in [(False,52),(True,78)]:self.assertEqual(len(mod.create_card_deck(deck)),n)
        self.assertEqual(mod.placeholder_to_glyph['unigram_alpha_a'],'ol')
        self.assertEqual(mod.clean_line('W J K æ'),'uuicae')

    def test_slot_known_words_separable_and_lossless_fallback(self):
        self.assertEqual(len(SLOTS),12)
        for word in ['qokedy','daiin','chol','shedy']:self.assertEqual(decompose(word)[0],'REGULAR')
        self.assertEqual(decompose('qokedyqokedy')[0],'SEPARABLE')
        for word in ['abc','qokedy','daiin','chol','shedy','qokedyqokedy','\ufffd','\u05d0\u05b8\u05d1']:
            self.assertEqual(''.join(s for _,s in pieces(word)),word)

    def test_alphagrams_do_not_delete_word_slots_or_hebrew_matres(self):
        self.assertEqual(alphagram('caba','Latin'),'aabc')
        self.assertEqual(alphagram('ae','Latin',True),'\u2205')
        self.assertEqual(strip_vowels('\u05d5\u05b8\u05d9','Hebrew'),'\u05d5\u05d9')

    def test_character_alphabet_and_context_are_train_only(self):
        extractor=CharFeatures(['aaaa','abab']);x,lengths=extractor.transform(['zz'])
        self.assertNotIn('z',extractor.symbols);self.assertEqual(x.sum(),3);self.assertEqual(lengths[0],3)

    def test_em_penalized_objective_monotonic(self):
        texts=['aaaaabaaa','aaaaaaaba','bbbbbabb','bbbbbabbb']*10
        extractor=CharFeatures(texts);x,_=extractor.transform(texts);groups=np.array([str(i) for i in range(len(texts))])
        settings=config()['mixture'];embedding=initialize_embeddings(texts)
        fitted=fit_em(x,groups,embedding,2,1729,extractor.V,extractor.C,settings,False)
        self.assertTrue(np.all(np.diff(fitted['curve'])>=-1e-5))
        self.assertTrue(np.allclose(fitted['response'].sum(axis=1),1))

    def test_membership_coding_cannot_see_future_units(self):
        settings=config()['mixture'];extractor=CharFeatures(['aaaa','bbbb'])
        x,_=extractor.transform(['aaaa','bbbb']);embedding=initialize_embeddings(['aaaa','bbbb'])
        model=fit_em(x,np.array(['a','b']),embedding,2,1729,extractor.V,extractor.C,settings,False)
        a,ll_a=score(model,x,np.array(['same','same']),True,settings)
        changed,_=extractor.transform(['aaaa','aaaa']);b,ll_b=score(model,changed,np.array(['same','same']),True,settings)
        self.assertTrue(np.allclose(a[0],b[0]));self.assertAlmostEqual(ll_a[0],ll_b[0])

    def test_generated_sizes_origin_alignment_and_participant_split(self):
        reg=registry()
        for name,meta in reg.items():
            selected=corpus(name)
            if not meta['legacy'] and not meta.get('analysis_only') and not name.startswith('C17_') and name.endswith('_clean'):
                self.assertEqual(sum(len(r['text_eva'].split()) for r in selected),34509)
            if meta.get('truth_path'):
                truth={r['line_id']:r for r in json.loads((ROOT/meta['truth_path']).read_text())}
                for r in selected:self.assertEqual(len(r['text_eva'].split()),len(truth[r['line_id']]['word_sources']))
            if name.startswith('C17_'):
                by_participant={}
                for r in selected:
                    p=r['participant'];by_participant.setdefault(p,set()).add(meta['split'][r['folio']])
                self.assertTrue(all(len(v)==1 for v in by_participant.values()))

    def test_T4_preparation_denominator_is_original_source(self):
        from .neural import prepare
        cfg=json.loads((ROOT/'configs/phase4.json').read_text())
        selected=corpus('ZL_running');p=prepare('ZL_running','T4',cfg)
        self.assertEqual(sum(p['character_counts'].values()),sum(len(r['text_eva'].replace(' ','')) for r in selected))

if __name__=='__main__':unittest.main()
