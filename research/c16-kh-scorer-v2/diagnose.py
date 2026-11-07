"""Explain failure on training examples only, without any manuscript scoring."""
import importlib.util,json,math
from preserve import R
from register import dump
spec=importlib.util.spec_from_file_location('unmodified_legacy_diagnosis',R/'inputs/legacy_core.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def main():
    results=[]
    for arm in ['tanakh','medieval']:
        data=json.loads((R/'inputs'/f'{arm}.json').read_text());lm=old.LM(data['train']);a=b='novel-context'
        finite=sum(math.exp(lm.logp(a,b,c)) for c in list(lm.u)+[old.UNK]);expanded=finite+sum(math.exp(lm.logp(a,b,'distinct-unseen-'+str(i))) for i in range(100))
        sample=data['train'][:100];wins=sum(lm.score([old.UNK]*len(s))>lm.score(s) for s in sample)
        results.append(dict(arm=arm,legacy_hapax_mass=lm.unkp,legacy_unigram_weight=lm.weights[0],legacy_unknown_word_probability=math.exp(lm.logp(a,b,old.UNK)),legacy_unseen_context_finite_event_mass=finite,legacy_mass_after_100_distinct_unseen_strings=expanded,training_examples=100,all_UNKNOWN_beats_training_example=wins,not_heldout_qualification=True))
    dump(R/'DIAGNOSIS.json',dict(findings=results,causes=['Hapax probability substituted for the published one-sentence UNKNOWN treatment.','Every unseen surface string gets full aggregate OOV mass rather than one canonical event.','Unseen histories are not canonicalized, and missing higher-order contexts lose conditional probability mass.','EOS is included as an extra denominator slot, subsidizing short unknown lines.','The same defective word score participates in key fitting, so re-ranking old decoded text alone is insufficient.'],published_source='https://aclanthology.org/C14-1218/ section 3',ZL_scored=False))
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
