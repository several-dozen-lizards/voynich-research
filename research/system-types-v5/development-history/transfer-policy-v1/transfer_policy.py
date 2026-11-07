"""Development-only transfer codebooks, barrier-preserving views, bounded source windows."""
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import json,random
from core import canonical_hash,group_rank_mapping

ROOT=Path(__file__).resolve().parent

class SourceSupportError(ValueError):pass

@dataclass(frozen=True)
class FrozenCodebook:
    entries:tuple
    training_scope:str
    training_sha256:str
    target_inventory_sha256:str

    @property
    def mapping(self):return dict(self.entries)

def fit_development_codebook(words,inventory,partition):
    if partition!='development':
        raise SourceSupportError('codebook fitting is development-only; calibration/reserve/diagnostic maps are forbidden')
    receipt=group_rank_mapping(words,inventory)
    return FrozenCodebook(tuple(sorted(receipt['mapping'].items())),partition,canonical_hash(words),canonical_hash(inventory))

def transfer_slots(words,book):
    """Never refits. One unknown unit makes the entire original word an opaque barrier."""
    if book.training_scope!='development':raise SourceSupportError('untrusted codebook provenance')
    mapping=book.mapping;out=[];events=[]
    for index,word in enumerate(words):
        if word is None:
            out.append(None);events.append(dict(slot=index,reason='source_unknown',units=[]));continue
        missing=sorted(set(word)-set(mapping))
        if missing:
            out.append(None);events.append(dict(slot=index,reason='unseen_unit',units=missing))
        else:out.append(''.join(mapping[u] for u in word))
    return dict(tokens=out,events=events,original_slots=len(words),supported_slots=sum(w is not None for w in out),
                primary_transfer_status='PASS' if not events else 'NOT_ESTIMABLE_FULL_TRANSFER',
                scope='barrier-preserving diagnostic view; not permission to run held statistics',
                codebook_training_sha256=book.training_sha256)

def source_runs(units,selected_ids,language):
    """Consecutive source units within one work; never bridge a missing unit or another work."""
    selected_ids=set(selected_ids);runs=[];current=[];ids=[];previous_work=None
    def finish():
        nonlocal current,ids,previous_work
        if ids:runs.append(dict(work=previous_work,units=ids,tokens=current))
        current=[];ids=[];previous_work=None
    for unit in units:
        if unit['unit'] not in selected_ids:finish();continue
        work='Occitan:'+unit['unit'] if language=='Occitan' else language+':primary-work'
        if previous_work is not None and work!=previous_work:finish()
        previous_work=work;ids.append(unit['unit']);current.extend(unit['words'])
    finish()
    return runs

def sample_window(runs,slots,seed):
    """Uniform over eligible start positions; counts source positions, not distinct word values."""
    if not isinstance(slots,int) or slots<1:raise ValueError('positive integer slot budget required')
    eligible=[(r,len(r['tokens'])-slots+1) for r in runs if len(r['tokens'])>=slots]
    total=sum(count for _,count in eligible)
    if not total:raise SourceSupportError('SOURCE_TOO_SHORT: no contiguous within-work run covers requested original slots')
    draw=random.Random(seed).randrange(total)
    for run,count in eligible:
        if draw<count:
            return dict(work=run['work'],source_units=run['units'],start=draw,stop=draw+slots,
                        tokens=run['tokens'][draw:draw+slots],source_wraps=0,selection='uniform over all eligible within-run starts')
        draw-=count
    raise AssertionError('start-position selection failed')

def build_policy():
    from core import save,sha
    path=ROOT/'UNKNOWN-AND-LENGTH-POLICY.json'
    policy=dict(version='unknown-and-source-length-v1',tier='sandbox policy settled; not claim FREEZE',
        evidence_boundary='Existing unknown-unit lists are already exposed. Decisions below follow representation/sampling requirements, not reserve-dependent frequency cutoffs; no reserve counts choose a fix.',
        fitting=dict(codebook='Development units/frequencies/position classes only. Calibration and reserve may not fit unit inventories, rank maps, spelling normalizers, abbreviation rules or generator rates.',
            read_vs_fit='Reserves may be read for this requested provenance/coverage diagnosis. Reading does not authorize fitting.',
            codebook_identity='Hash the exact selected development stream and target inventory. Hold mappings fixed across reserve views. Diagnostic whole-reserve representation maps are quarantined and cannot initialize claim fits.'),
        unknown=dict(primary='Any original unknown or out-of-development unit => full-transfer NOT_ESTIMABLE. Never interpret as a production-family elimination.',
            view='Retain every original word/line slot. A word containing any unseen unit becomes one None barrier; retain its raw written units/offsets in a separate provenance ledger.',
            adjacency='No dropping/repacking unknown words, joining neighbors across them, promoting later words to line-start, or using partial known letters as a complete word.',
            conversions='No accent stripping, NFC/NFD policy change, digit completion, mark merging, silent expansion, unknown-to-common-glyph assignment, reserve reranking or post hoc source additions in this cut.',
            conditional='Supported-slot diagnostics can be reported separately, with exact coverage and masks. Conditional held scoring requires its own later frozen estimand and support gate; it cannot certify full-source G2 survival.',
            improvement='Any inventory expansion must come from independently selected development data or a new externally justified alphabet/prior, with a new cut and a newly reserved test source. Current reserves are not recycled as new training.',
            semantics='Literal digits/signs/diacritics are identified by Unicode representation and provenance only; no automatic numeral, abbreviation or meaning is inferred.'),
        length=dict(primary_pool='Development only for fitting/generation. Calibration is for declared tuning/runtime/scale controls, reserve for evaluation. Do not merge partitions after observing shortages.',
            required_budget='Use original word slots, including unknown positions, not readable-word count alone. A fixed missingness mask can be applied only after allocating all original slots.',
            support='Need at least one contiguous same-work run covering the entire requested slot budget. Aggregate counts over different works or gaps are not enough.',
            selection='Uniform over all eligible start positions within the admitted development runs, without inspecting generated or reserve outcomes.',
            prohibited='No cyclic wrap, padding, within-manuscript reuse of source positions, stitching unrelated works, silently changing source or shortening only one candidate family.',
            allowed_repetition='Words already repeated in the original source remain repeated. Independent Monte Carlo draws may reuse the fixed development corpus; uncertainty is conditional on that corpus, not independent-corpus replication.',
            failure='SOURCE_TOO_SHORT / UNSUPPORTED_AT_SIZE before generator/model invocation. Never CANNOT_MIMIC_BASICS, ELIMINATED or a passing control.',
            comparison='A complete family comparison needs all preregistered candidates supported at the same declared geometry. A smaller common-size experiment is a separately frozen diagnostic, never a rescue of this cell.',
            generative_families='G5 native copy history and G6 reuse of their own table are mechanisms, not external source padding. Preserve G5 seed-line exclusion and native generation; stop/censor only at predeclared boundaries.',
            real_Latin='Native-page reserve remains a five-page control. Development vocabulary may pool explicitly listed earlier sources for codebook estimation, but generated source sequences may not stitch their manuscripts/pages without documented continuity.'),
        prior_exposure='Preserve earlier maps made from full reserve source distributions as diagnostic-only. Earlier Macer last40% mechanism controls overlap later calibration/reserve partitions; no historically untouched claim is made.',
        H3='UNRESOLVED',H1_H8_scoring='LOCKED',full_recovery='LOCKED')
    save(path,policy)
    save(ROOT/'TRANSFER-POLICY-DESIGN-SEAL.json',dict(tier='policy design, not claim freeze',policy_sha256=sha(path),implementation_sha256=sha(Path(__file__)),held_scoring=False))
    print('Unknown-unit and source-length policies specified without a reserve-trained repair.')

if __name__=='__main__':build_policy()
