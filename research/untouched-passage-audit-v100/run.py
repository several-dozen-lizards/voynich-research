from pathlib import Path
import collections, datetime, hashlib, html, json, re

R = Path(__file__).resolve().parent
P = R.parent
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n, x): (R/n).write_text(json.dumps(x, indent=2, ensure_ascii=False), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

protocol = {
 'question': 'Audit whether local passages can be certified untouched for a prospective sh- to qok- test. No source arrangement statistic or new power calculation before freshness admission.',
 'freeze_order': 'Freeze this protocol, code and evidence hashes before metadata inventory. Prior source outcomes have already been exposed; this does not retroactively blind them.',
 'scope': 'Every H/F atlas locus, separate section, exact hand, Currier variety and raw format. Validate coverage against the original source using locator/reading metadata only. Preserve single-reading loci and ambiguous hands.',
 'exposure_rule': 'The three v75 sections are directly target-exposed in ALL formats: shared rawP inferential tests, all rawP pooled target audit including unpaired rows, and separate non-P target inventory. A fresh fold, different hand, alternate transcription or omitted paired row cannot reverse this.',
 'other_passages': 'Other sections are unverified for target exposure. Whole-corpus atlas availability and word-part exploration are documented, but availability is not proof of human inspection or target scoring. Absent an auditable prior reserve or independent custody attestation, do not certify untouched. No target frequencies/neighbors/positions read to choose candidates.',
 'admission': 'Require passage identities fixed without target outcomes, verifiable exposure/custody history, no prior influence on this hypothesis, reading overlap and whole numbered-folio contamination review, exact hand/section/format metadata, then a separately frozen test and actual-layout power qualification. Uncertain freshness stays uncertified, not a demonstrated direct exposure.',
 'test_distinction': 'Adjacent ordering under a word-order shuffle and residual one-gap ordering under transition constraints are different hypotheses. A transition-preserving test fixes adjacent S/Q/N counts and cannot test their aggregate adjacent ordering. No substitution of one for the other.',
 'power_gate': 'If no certified candidate remains, power is NOT RUN for provenance failure, never recorded as zero or low power. Any future residual transition test retains the v97/v98 >=80% at weight1.5 and >=90% at weight2 gates per reading/hand/view, plus method/calibration qualification and a full predeclared prospective family. Adjacent effects require their own justified frozen scale and qualified power design; do not transplant gap tilts.',
 'preserve': 'v98 FAIL and unrun banks2/3; v97 failures; v99 diagnostic-only status. No easier target threshold promoted, no corpus score or rescore, no new inferential p-value. H/F are dependent alternate readings, not replication.',
 'limits': 'Bounded local documentary audit, not omniscience about collaborators or external sources. Lack of a reserve receipt is not proof every passage was viewed. No previously unseen external transcription or new manuscript material is obtained here.'
}
evidence = [
 'frequency-atlas-v48/rows.json', 'frequency-atlas-v48/source-manifest.json',
 'frequency-atlas-v48/build.py', 'complete-atlas-v56/build.py', 'complete-atlas-v56/SOURCE-MANIFEST.json',
 'word-parts-v50/PROTOCOL.json', 'word-parts-v50/VERIFICATION.json',
 'opening-order-audit-v75/PROTOCOL.json', 'opening-order-audit-v75/run.py',
 'opening-order-audit-v75/audit_claims.py', 'opening-order-audit-v75/PANEL-LEDGER.json',
 'opening-order-audit-v75/NON-P-FORMAT-INVENTORY.json',
 'sh-qok-context-transfer-v1/PROTOCOL.md', 'sh-qok-context-transfer-v2/PROTOCOL.md',
 'sh-qok-context-transfer-v2/SOURCE-COVERAGE-AUDIT.json',
 'transition-power-v97/PROTOCOL.json', 'transition-maxT-qual-v98/QUALIFICATION.json',
 'transition-cost-diagnostic-v99/VERIFICATION.json'
]
manifest = load(P/'frequency-atlas-v48/source-manifest.json')
raw_source = Path(next(k for k in manifest['sources'] if k.endswith('.evt')))
assert sha(raw_source) == manifest['sources'][str(raw_source)]
hashes = {n: sha(P/n) for n in evidence}
hashes[str(raw_source)] = sha(raw_source)
# Search only research protocol/readme records for a reserve receipt, not token arrays or outcome tables.
documents = sorted(p for d in P.iterdir() if d.is_dir() and d != R for p in d.iterdir()
                   if p.is_file() and (p.name.upper().startswith(('PROTOCOL', 'README')))
                   and p.suffix.lower() in ('.md', '.txt', '.json'))
for p in documents: hashes[str(p.relative_to(P))] = sha(p)
hashes['run.py'] = sha(Path(__file__))
freeze = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sha256': hashes}
if (R/'FREEZE.json').exists():
    assert load(R/'PROTOCOL.json') == protocol
    assert load(R/'FREEZE.json')['sha256'] == hashes
else:
    save('PROTOCOL.json', protocol)
    save('FREEZE.json', freeze)

rows = load(P/'frequency-atlas-v48/rows.json')
assert len(rows) == manifest['rows']
keys = [(r[0], r[6]) for r in rows]
original_keys = []
for line in raw_source.read_text(encoding='latin1').splitlines():
    m = re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>', line)
    if m and m[4] in ('H','F'): original_keys.append((m[4], '.'.join(m.group(i) for i in (1,2,3))))
assert collections.Counter(keys) == collections.Counter(original_keys)
assert len(keys) == len(set(keys))
direct_sections = {'Balneological', 'Botanical', 'Starred paragraphs'}
direct_folios = {re.match(r'f\d+', r[1])[0] for r in rows if r[2] in direct_sections}
groups = collections.defaultdict(list)
ledger = []
for r in rows:
    reading, page, section, hand, variety, fmt, locus = r[:7]  # never inspect r[7] tokens
    folio = re.match(r'f\d+', page)[0]
    status = 'direct_target_exposure' if section in direct_sections else 'freshness_uncertified'
    ledger.append(dict(reading=reading, page=page, numbered_folio=folio, section=section,
                       hand=hand, variety=variety, format=fmt, locus=locus, status=status,
                       overlaps_direct_numbered_folio=folio in direct_folios, certified_untouched=False))
    groups[(section,hand,variety,fmt,reading)].append(ledger[-1])
summary = []
for key, rr in sorted(groups.items()):
    section, hand, variety, fmt, reading = key
    other = {r[6] for r in rows if tuple(r[2:6]) == key[:4] and r[0] != reading}
    summary.append(dict(section=section, hand=hand, variety=variety, format=fmt, reading=reading,
        lines=len(rr), shared_loci=sum(x['locus'] in other for x in rr),
        single_reading_loci=sum(x['locus'] not in other for x in rr),
        pages=sorted({x['page'] for x in rr}), numbered_folios=sorted({x['numbered_folio'] for x in rr}),
        status=rr[0]['status'], certified_lines=0,
        overlaps_direct_numbered_folio=sum(x['overlaps_direct_numbered_folio'] for x in rr),
        power_status='NOT RUN: no certified untouched passages', score_status='NOT RUN'))
reserve_hits = []
for p in documents:
    for i, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
        if re.search(r'untouched|hold.?out|reserve|unseen|fresh confirm', line, re.I):
            reserve_hits.append(dict(file=str(p.relative_to(P)),line=i,text=line))
save('RESERVE-SEARCH.json', dict(documents=len(documents), hits=reserve_hits,
    interpretation='Search leads, not automatic certifications. No matching record reviewed establishes a protected H/F manuscript reserve.'))
old = load(P/'transition-maxT-qual-v98/QUALIFICATION.json')
assert old['status'] == 'FAIL' and old['robustness_banks_not_run'] == [2,3]
totals = {reading:dict(total=sum(x['reading']==reading for x in ledger),
    direct=sum(x['reading']==reading and x['status']=='direct_target_exposure' for x in ledger),
    uncertified=sum(x['reading']==reading and x['status']=='freshness_uncertified' for x in ledger), certified=0)
    for reading in ('H','F')}
save('LOCUS-LEDGER.json', ledger)
save('STRATA.json', summary)
save('RESULTS.json', dict(status='NO CERTIFIED UNTOUCHED LOCAL HOLDOUT', totals=totals,
    candidate_power='NOT RUN: freshness admission unmet, not a low-power finding',
    manuscript_scoring='NOT PERFORMED', v98_status=old['status'], robustness_banks_not_run=[2,3],
    reserve_document_search=len(documents), scope_limit=protocol['limits']))
# Verification uses only metadata and frozen bytes; no ordering statistic is evaluated.
assert sum(x['lines'] for x in summary) == len(ledger)
assert all(x['certified_lines']==0 for x in summary)
for n,h in hashes.items():
    p = Path(__file__) if n=='run.py' else (Path(n) if Path(n).is_absolute() else P/n)
    assert sha(p)==h, n
save('VERIFICATION.json', dict(source_locus_coverage='all original H/F loci reconciled',
    unique_reading_loci=len(keys), strata=len(summary), separate_readings_hands_formats='PASS',
    ledger_totals='PASS', frozen_hashes='PASS', source_ordering_statistic='NOT COMPUTED',
    candidate_power='NOT RUN: provenance gate', previous_failed_gate='FAIL unchanged',
    browser_visual_review='not performed'))
e = html.escape
def table(headers, records):
    return '<div class="scroll"><table><tr>'+''.join('<th>'+e(x)+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in rr)+'</tr>' for rr in records)+'</table></div>'
body = '<p>VOYNICH · PROVENANCE BEFORE POWER · v100</p><h1>Is there an untouched passage reserve?</h1><p><strong>No local H/F reserve can currently be certified from the audited receipts.</strong> This is a provenance stop, not a negative ordering result or a power estimate. v98 remains FAIL; no scoring or rescoring was performed.</p>'
body += table(['Reading','All loci','Direct target exposure','Freshness uncertified','Certified untouched'],[[k,v['total'],v['direct'],v['uncertified'],v['certified']] for k,v in totals.items()])
body += '<h2>What disqualifies the apparent reserves?</h2><p>v75 tested shared H/F paragraphs across all recorded hands in Bath, Botanical and Starred text. Its pooled audit also counted target pairs in every raw-P row, including single-reading exclusions. Its separate non-P inventory counted the same target in other formats of these sections. H and F cannot hold out one another; moving an exposed folio into a new split does not make it fresh.</p><p>The other sections have no direct target-exposure receipt established by this audit. They were included in the whole-source atlases and broad word-part exploration. That availability is not proof someone inspected every passage. Their status is therefore <strong>uncertified</strong>, not demonstrated untouched and not automatically demonstrated target-scored. The documentary search cannot establish what happened in external conversations.</p>'
body += '<h2>Power must follow freshness admission and precede scoring</h2><p>Zero candidates passed the freshness admission requirement, so actual candidate-layout power was NOT RUN. Nothing here asserts zero power. The targeted v99 powers apply to exposed bath/starred layouts and cannot certify different passages or an adjacent-order test.</p><p>First obtain a fixed source-unit list with a credible custody/exposure account; exclude direct exposure and audit whole-folio overlap. Then freeze adjacency versus residual-gap hypothesis, literal classes, endpoints/unknown rules, exact strata, effect scale, test family, calibration and power criteria. Read only the permitted invariant layout information for power; record every failed stratum before opening arrangement scores. Any admitted residual transition test retains the existing 80% at weight1.5 and 90% at weight2 requirements. An adjacent-order design needs its own qualified effect model. No gate is waived by this audit.</p><p>A transition-preserving null fixes adjacent S/Q/N edge counts. It can test residual gap structure, but cannot test the aggregate adjacent sh→qok excess that it conditions on. These are distinct questions.</p>'
body += '<h2>Every stratum, including unpaired and ambiguous material</h2>'+table(['Section','Hand','Variety','Format','Reading','Lines','Shared','Unpaired','Exposure status','Numbered folios'],[[x['section'],x['hand'],x['variety'],x['format'],x['reading'],x['lines'],x['shared_loci'],x['single_reading_loci'],x['status'],', '.join(x['numbered_folios'])] for x in summary])
body += '<p>H/F remain alternate readings, not independent replication. No new meaning, grammar or mechanism claim. New independent material or a credible documented reserve could change the admission decision; merely relabelling an exposed fold cannot.</p><p><a href="PROTOCOL.json">Frozen protocol</a> · <a href="FREEZE.json">Evidence and script hashes</a> · <a href="LOCUS-LEDGER.json">Every locus</a> · <a href="STRATA.json">All strata</a> · <a href="RESERVE-SEARCH.json">Bounded documentary search</a> · <a href="VERIFICATION.json">Verification</a> · <a href="../transition-maxT-qual-v98/report.html">Preserved failed v98</a></p><p>Numerical and source checks only; browser appearance unreviewed.</p>'
style = '<style>body{margin:auto;max-width:1400px;padding:28px;background:#f5f2e9;color:#203f35;font:16px/1.55 system-ui}h1{font-size:32px}h2{margin-top:30px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;padding:9px;border-bottom:1px solid #bbc9ba}a{color:inherit}</style>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Untouched passage audit · v100</title>'+style+'<main>'+body+'</main></html>',encoding='utf-8')
print(json.dumps(dict(totals=totals,strata=len(summary),documents=len(documents),reserve_search_hits=len(reserve_hits),power='NOT RUN',score='NOT RUN')))
