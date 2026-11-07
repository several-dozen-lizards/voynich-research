"""Primary source-backed entrypoint: development-only, contiguous, same-work source windows."""
from dataclasses import dataclass
from pathlib import Path
import json
from core import sha,canonical_hash
from transfer_policy import source_runs,sample_window,SourceSupportError
from registry import produce

@dataclass(frozen=True)
class DevelopmentCorpus:
    language:str
    runs:tuple
    development_sha256:str
    partition:str='development'

def load_development_corpus(root,language,partition='development'):
    if partition!='development':raise SourceSupportError('reserve/calibration cannot supply generation or fitting corpus')
    root=Path(root);name=language.upper()+'-SOURCE-UNITS.json'
    frozen=json.loads((root/'SOURCE-COVERAGE-PLAN.json').read_text())['files']
    for input_name in (name,'LANGUAGE-SOURCE-SPLITS.json'):
        if sha(root/input_name)!=frozen[input_name]:raise SourceSupportError('registered source input changed; new source cut required')
    units=json.loads((root/name).read_text())
    selected=json.loads((root/'LANGUAGE-SOURCE-SPLITS.json').read_text())[language]['development']['units']
    if set(selected)-{u['unit'] for u in units}:raise SourceSupportError('unregistered source unit')
    runs=source_runs(units,selected,language)
    immutable=tuple((r['work'],tuple(r['units']),tuple(r['tokens'])) for r in runs)
    return DevelopmentCorpus(language,immutable,canonical_hash(immutable))

def produce_from_development(family,params,seed,corpus=None,inventory=None,line_lengths=None,line_count=100):
    if family in ('G5','G6'):
        return produce(family,params,seed,inventory=inventory,line_lengths=line_lengths,line_count=line_count)
    if not isinstance(corpus,DevelopmentCorpus) or corpus.partition!='development':
        raise SourceSupportError('verified development corpus required')
    if not line_lengths:raise ValueError('original-slot geometry required')
    if 'source_start' in params:raise SourceSupportError('source start is sampled by the registered policy, not fitted')
    runs=[dict(work=w,units=list(ids),tokens=list(tokens)) for w,ids,tokens in corpus.runs]
    window=sample_window(runs,sum(line_lengths),seed)
    result=produce(family,dict(params,source_start=0),seed,source_words=window['tokens'],inventory=inventory,line_lengths=line_lengths)
    result['source_receipt']=dict(partition='development',language=corpus.language,development_sha256=corpus.development_sha256,
                                  work=window['work'],source_units=window['source_units'],start=window['start'],stop=window['stop'],source_wraps=0)
    return result
