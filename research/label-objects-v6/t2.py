"""Frozen text-only T2 scheduling and exact statistical calibration.
No object or similarity judgments are manufactured here.
"""
from common import *
from collections import Counter
from scipy.stats import binom,binomtest

def schedule():
    pairs=read_csv(ROOT/'T2-MATCHED-PAIRS.csv');inventory={r['locus']:r for r in read_csv(ROOT/'LABEL-INVENTORY.csv')}
    features={(r['locus'],r['reading']):r for r in read_csv(ROOT/'FEATURES.csv')}
    ledger=load(ROOT/'T2-EXPOSURE-EXCLUSIONS.json');exposed={(r['pharma_page'],r['herbal_page']) for r in ledger['pairs']}
    known_sources={r['pharma_page'] for r in ledger['pairs']}
    _,source_rows=source();herbal={r['page']:r for r in source_rows if r['section']=='Botanical' and r['page'] not in RESERVED}
    occurrences={reading:{} for reading in ['H','F']}
    for r in source_rows:
        if r['page'] in herbal and r['reading'] in occurrences:
            occurrences[r['reading']].setdefault(r['page'],set()).update(w for w in r['words'] if w)
    from build import distance_one
    selected=[];rejected=Counter()
    for reading in ['H','F']:
        used_labels=set();used_words=set();used_herbal=set();used_physical_folios=set()
        candidates=sorted([r for r in pairs if r['reading']==reading],key=lambda r:(r['match']!='EXACT',digest('v61-T2:'+r['pair_id'])))
        for pair in candidates:
            locus=pair['pharma_locus'];meta=inventory[locus];feat=features[locus,reading];word=pair['pharma_word'];target=pair['herbal_page']
            reason=None
            if feat['eligible']!='True' or feat['word_count']!='1':reason='NOT_SINGLE_FULLY_READABLE_LABEL'
            elif (meta['page'],target) in exposed:reason='PREVIOUSLY_SHOWN_PAIR'
            elif meta['page'] in known_sources:reason='CONSERVATIVE_PREVIOUSLY_SHOWN_SOURCE_PAGE'
            elif locus in used_labels or word in used_words or target in used_herbal:reason='REUSED_LABEL_WORD_OR_HERBAL_PAGE'
            if reason:rejected[reading+':'+reason]+=1;continue
            # Same scribe and strict unmatched word criterion; no language-only fallback.
            pool=[]
            for page,h in herbal.items():
                if page==target or page in used_herbal or h['scribe']!=pair['herbal_scribe']:continue
                words=occurrences[reading].get(page,set())
                if word in words or any(min(len(word),len(w))>=5 and distance_one(word,w) for w in words):continue
                if (meta['page'],page) in exposed:continue
                pool.append(page)
            if not pool:rejected[reading+':NO_UNMATCHED_SAME_SCRIBE_DISTRACTOR']+=1;continue
            distractor=min(pool,key=lambda p:digest('v61-T2-distractor:'+pair['pair_id']+':'+p))
            matched_side='LEFT' if int(digest('v61-T2-side:'+pair['pair_id'])[-1],16)%2==0 else 'RIGHT'
            trial=dict(pair,pharma_page=meta['page'],pharma_folio=meta['folio'],distractor_page=distractor,matched_side=matched_side,
                status='AWAITING_DISTINCT_DRAWING_GEOMETRY_AND_EXHAUSTIVE_TEXT_MASKS',
                freshness='No source-page exposure in frozen earlier paired-image ledgers; not a claim of previously unseen text',
                physical_drawing_nonreuse='Must be verified before stimulus release; unresolved => exclude, never replace after a choice')
            selected.append(trial);used_labels.add(locus);used_words.add(word);used_herbal.update([target,distractor])
    write_csv(ROOT/'T2-TEXT-SCHEDULE.csv',list(selected[0]) if selected else ['pair_id'],selected)
    save(ROOT/'T2-SCHEDULE-FREEZE.json',dict(status='TEXT_SCHEDULE_FROZEN_BEFORE_SIMILARITY_CHOICES',
        scheduled=dict(Counter(r['reading'] for r in selected)),rejections=dict(rejected),
        schedule_sha256=sha(ROOT/'T2-TEXT-SCHEDULE.csv'),code_sha256=sha(Path(__file__)),
        conservative_source_exclusion=True,no_image_judgment=True,
        pending='Distinct physical drawings, all-writing masks, no-reuse validation and shuffled-match image schedule before any stimulus release'))

def calibration():
    results=[]
    for n in range(15,81):
        flags=[k for k in range(n+1) if binomtest(k,n,.5,alternative='greater').pvalue<=.05]
        actual=float(sum(binom.pmf(k,n,.5) for k in flags));power=float(sum(binom.pmf(k,n,.8) for k in flags))
        assert actual<=.05+1e-12
        results.append(dict(n=n,minimum_matched_to_pass=min(flags),exact_null_false_positive_rate=actual,power_if_true_choice_rate_80pct=power))
    save(ROOT/'controls/T2-BINOMIAL-CALIBRATION.json',dict(status='PASS_STATISTICAL_CALIBRATION_ONLY',results=results,
        image_shuffled_match_control='NOT_RUN_NO_VERIFIED_DRAWINGS_OR_MASKS',
        limitation='This is the exact independent-trial binomial model. It does not validate rater reliability, image leakage, plant attachment or trial independence.'))

if __name__=='__main__':schedule();calibration();print(load(ROOT/'T2-SCHEDULE-FREEZE.json')['scheduled'])
