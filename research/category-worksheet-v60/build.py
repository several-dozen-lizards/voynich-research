from pathlib import Path
import collections, hashlib, html, json

R = Path(__file__).resolve().parent
P = R.parent
source = P / 'frequency-atlas-v48/rows.json'
rows = json.loads(source.read_text(encoding='utf-8'))
index = {(r[0], r[6]): r for r in rows}

# Explicitly chosen, already exposed examples. No search for a winning reading.
cohorts = [
 dict(id='bath', title='Bath-section pair', loci=['f75r.P.33','f75r.P.23'],
      selection='Two previously discussed qol chedy occurrences on one folio; the second has an unknown slot immediately before the pair. Not independent examples.',
      models=[
       dict(name='Preparation / application', mapping={'qol':'OPERATION?','chedy':'MATERIAL / PREPARATION?'},
            fits='The same adjacent pair can be rendered as an operation followed by its object in both lines.',
            breaks='Adjacency supplies no direction of action, ingredient identity, body target or application route. Calling chedy a poultice would add unsupported specificity.',
            test='On reserved same-stratum lines, ask whether qol neighbours form a constrained object-like set and whether those words also occupy other predicted material positions.'),
       dict(name='Catalogue / description', mapping={'qol':'ENTITY?','chedy':'ATTRIBUTE?'},
            fits='A recurring entity–attribute expression also accommodates the adjacent pair without an action.',
            breaks='No independently identified entity or property, and no established record boundary. This reading explains the same arrangement as the procedure model.',
            test='Check whether qol participates in parallel attribute lists or recurring entry positions, rather than only this selected pair.'),
       dict(name='Timing / condition', mapping={'qol':'TIME / CONDITION?','chedy':'STATE / EVENT?'},
            fits='A condition–event expression is compatible with the same two positions.',
            breaks='Neither token is anchored to a cycle, date, celestial object or conditional relation. Bath-section membership supplies none of those meanings.',
            test='Seek an independently registered temporal or diagram relation, then test the proposed role on reserved passages without relabelling the words.'),
      ]),
 dict(id='recipe', title='Operation or record field?', loci=['f88v.P1.2','f89r1.P1.4'],
      selection='Previously discussed qokeey daiin pair, plus an occurrence with daiin on both sides of qokeey. Section label “Recipes” is inherited metadata, not a decipherment.',
      models=[
       dict(name='Preparation / application', mapping={'qokeey':'OPERATION?','daiin':'MATERIAL?'},
            fits='The first line permits OPERATION–MATERIAL. The second permits MATERIAL–OPERATION–MATERIAL, a possible combination pattern.',
            breaks='The two flanking materials in the second line are the SAME written word. A two-different-ingredients story fails here unless supported by additional context. “Combine” is an illustrative verb, not an identified meaning.',
            test='Freeze the operation/object proposal and compare left and right neighbourhoods on reserved same-hand, same-variety, same-format lines; retain identical-object repetitions.'),
       dict(name='Catalogue / description', mapping={'qokeey':'ATTRIBUTE / FIELD?','daiin':'VALUE / ENTITY?'},
            fits='The second line permits VALUE–FIELD–VALUE; repeated values could be part of a record rather than a preparation.',
            breaks='There is no identified field boundary or value domain. A table-like interpretation needs evidence beyond a repeating word.',
            test='Test whether the proposed field occurs at stable record positions and whether adjacent values recur in parallel structures on other folios.'),
       dict(name='Timing / condition', mapping={'qokeey':'EVENT / RELATION?','daiin':'TIME / CONDITION?'},
            fits='The second line permits CONDITION–EVENT–CONDITION while keeping the same label for each daiin.',
            breaks='No evidence distinguishes a time from a material or record value. Repeated daiin cannot silently become two different dates or an invented “before/after” pair.',
            test='Require an independent temporal anchor or repeated conditional arrangement; do not infer a celestial meaning from these lines alone.'),
      ]),
 dict(id='botanical', title='Plant passage, several possible uses', loci=['f2v.P.8','f20v.P.2'],
      selection='Previously discussed cheol chol occurrences. The second line contains another chol later in the same source line.',
      models=[
       dict(name='Preparation / application', mapping={'cheol':'OPERATION?','chol':'MATERIAL?'},
            fits='Both pair occurrences permit OPERATION–MATERIAL; the later chol retains MATERIAL in the second line.',
            breaks='Neither a preparation nor a treatment target is identified. The extra material mention needs an explanation; the illustration-section label cannot provide it.',
            test='Look for repeatable relations between the later material mention and preceding operations on reserved botanical passages.'),
       dict(name='Catalogue / description', mapping={'cheol':'ENTITY / PART?','chol':'PROPERTY?'},
            fits='Both pairs permit ENTITY–PROPERTY. The later chol could repeat a property in another description.',
            breaks='Nothing here identifies a plant part or property. The second chol receives the same PROPERTY label, even though that may make the full line awkward.',
            test='Seek parallel descriptions where candidate entities change but property positions persist, with counterexamples retained.'),
       dict(name='Timing / condition', mapping={'cheol':'EVENT?','chol':'TIME / CONDITION?'},
            fits='Both pairs allow EVENT–CONDITION; the repeated chol would repeat that same proposed condition.',
            breaks='No calendar or celestial referent is established. Introducing a different time meaning for the later chol would be an extra assumption.',
            test='Ask whether the proposed condition appears in independently anchored timing contexts; preserve hand, variety and format differences rather than pooling them.'),
      ]),
 dict(id='celestial', title='Celestial-section counterweight', loci=['f67r1.P.2','f67r1.P.4'],
      selection='First H paragraph line on f67r1 containing sar, then its next paragraph-line recurrence on that page. Selected after inspection; not a blind test. Only sar is tentatively substituted.',
      models=[
       dict(name='Preparation / application', mapping={'sar':'OPERATION?'},
            fits='A repeated operation could in principle appear in explanatory text accompanying a diagram.',
            breaks='One repeated token supplies no object, preparation, route or recipe sequence. This passage provides no positive medicinal evidence.',
            test='Require recurring operation–object relationships in comparable passages before assigning any preparation meaning.'),
       dict(name='Catalogue / description', mapping={'sar':'ENTITY / FIELD?'},
            fits='A recurring entity or descriptive field is compatible with both appearances.',
            breaks='There is no identified referent or record structure. The same observation also accommodates a function word.',
            test='Use independently registered diagram labels or repeatable record positions; paragraph and ring formats must remain separate.'),
       dict(name='Timing / celestial reference', mapping={'sar':'TIME / CELESTIAL REFERENCE?'},
            fits='A celestial-reference proposal is worth retaining beside the alternatives because this source is catalogued in Astronomy/Astrology.',
            breaks='Section membership is the reason for proposing this model, not evidence that sar names a planet, sign or time. There is no such anchor in the displayed text.',
            test='Register an image/text relation independently, with disputed readings preserved, before testing an object or temporal assignment.'),
      ]),
]

for c in cohorts:
    c['passages'] = []
    for loc in c['loci']:
        readings = {}
        for tr in ('H','F'):
            r = index.get((tr,loc))
            assert r is not None, (tr,loc)
            # Neighbours are context, not joined text or inferred sentences.
            same = [v for v in rows if v[0]==tr and v[1]==r[1] and v[5]==r[5]]
            k = next(i for i,v in enumerate(same) if v[6]==loc)
            readings[tr] = dict(transcription=tr,page=r[1],section=r[2],hand=r[3],variety=r[4],format=r[5],locator=loc,tokens=r[7],
                                previous=({'locator':same[k-1][6],'tokens':same[k-1][7]} if k else None),
                                following=({'locator':same[k+1][6],'tokens':same[k+1][7]} if k+1<len(same) else None))
        h, f = readings['H']['tokens'], readings['F']['tokens']
        c['passages'].append(dict(locator=loc,readings=readings,agreement='Identical token sequence' if h==f else 'Different tokenization, spelling or unknown slots; source locus shared, token indices not aligned'))

data = dict(title='Competing category worksheet',status='Exploratory, authored hypotheses. No inferred meanings, semantic scores, winning interpretation or independent validation.',
            categories=['MATERIAL','OPERATION','PREPARED FORM','APPLICATION','PURPOSE / TARGET','TIME / CELESTIAL REFERENCE','RELATION / QUANTITY','ENTITY / ATTRIBUTE','UNKNOWN'],
            policy='Mappings are local to a cohort and hypothesis, explicit whole-token proposals; same token keeps its proposed category within that cohort/model. No affix-to-meaning assignment. Unknown slots remain barriers. Unmapped words remain unassigned.',
            nonsemantic='Form / discourse alternative: the recurrence may reflect grammatical, orthographic, copying, formulaic or other text-production constraints. A neutral repeated-slot representation fits by construction and predicts no ingredient, action or planet. It is a baseline, not a claimed explanation.',
            cohort_count=len(cohorts),passage_count=sum(len(c['passages']) for c in cohorts),cohorts=cohorts)
nullpath=P/'combination-null-v59/SUMMARY.json'
data['combination_test_snapshot']=json.loads(nullpath.read_text()) if nullpath.exists() else None
data['combination_test_caveat']='At worksheet build time v59 summary reports zero paired patterns passing both readings. These selected recurrences are therefore not established H/F-shared phrase-enrichment anchors. This does not establish absence of structure.'
(R/'WORKSHEET.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data.js').write_text('const WORKSHEET = '+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(R/'PROVENANCE.json').write_text(json.dumps({
    'sources':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,P/'frequency-atlas-v48/source-manifest.json',P/'contrast-context-v58/RESULTS.json',nullpath] if p.exists()},
    'selection':'Purposive exposed examples; no representative-sample or heldout claim. Celestial pair additionally selected by recurring sar in paragraph format.',
    'transcriptions':{'H':'Takahashi','F':'First Study Group'},
    'controls':'Metadata displayed, not a new controlled statistical test. Cross-cohort differences cannot establish semantic effects.',
    'interpretation':'Human-review worksheet; category names and fit/break assessments are authored conjectures. No automatic category inference or semantic gate claim.',
},indent=2),encoding='utf-8')
print(json.dumps({'cohorts':len(cohorts),'passages':data['passage_count'],'readings':2*data['passage_count']}))
