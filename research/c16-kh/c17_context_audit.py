"""Namespace repeated control words by writer; do not collide local symbol maps."""
from prepare import R,table,dump
from run import consistency
from collections import defaultdict
import gzip,json
def main():
    output=[];pooled=[]
    for arm in ['tanakh','medieval']:
      for version in ['clean','noise']:
        groups=defaultdict(lambda:defaultdict(list))
        with gzip.open(R/'results'/arm/f'C17-{version}-tokens.jsonl.gz','rt',encoding='utf8') as f:
            for line in f:
                r=json.loads(line);groups[r['variant'],r['writer']][r['source_word']].append((r['page'],r['line_id'],r['selected']))
        combined=defaultdict(dict)
        for (variant,writer),words in groups.items():
            output.append(dict(arm=arm,source='C17',version=version,variant=variant,writer=writer,size_mismatch=True,word_namespace='writer-local',**consistency(words)))
            combined[variant].update({(writer,w):obs for w,obs in words.items()})
        for variant,words in combined.items():pooled.append(dict(arm=arm,source='C17',version=version,variant=variant,size_mismatch=True,word_namespace='writer-local',**consistency(words)))
    table(R/'C17-writer-context-consistency.csv',output);table(R/'C17-context-consistency-scoped.csv',pooled)
    dump(R/'C17_CONTEXT_AUDIT.json',dict(status='CORRECTED_REPORTING_SCOPE',reason='Per-document injective alphabets make cross-writer relabeled-string collisions uninterpretable. Namespace word identities by writer before pooling context pairs.',legacy_cross_writer_agreements='Do not interpret C17 cross-context rows in original per-arm tables; use scoped tables instead.',fit_decode_rank_blind_selection_changed=False,writer_rows=len(output),pooled_rows=len(pooled)))
    print(json.dumps(dict(writer_rows=len(output),pooled_rows=len(pooled),rankings_changed=False)))
if __name__=='__main__':main()
