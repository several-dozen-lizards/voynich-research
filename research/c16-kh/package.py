"""Package and verify blind artifacts without opening the sealed key."""
from prepare import R,dump,sha,read
import json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
def main():
    blind=R/'blind';book=R/'outputs/01a17998-a0e6-7c80-9a3f-ea90fdb78854/ratings.xlsx';rs=read(blind/'ratings.csv');ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    assert len(rs)==200 and len({r['item_id'] for r in rs})==200
    assert all(not r[k] for r in rs for k in ['coherence_0_4','grammaticality_0_4','comments'])
    assert all(set(r['decoded_line'].split())=={'<UNK>'} for r in rs)
    with zipfile.ZipFile(book) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        tree=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={}
        for c in tree.findall('.//m:c',ns):
            v=c.find('m:v',ns);val=v.text if v is not None else ''
            if c.get('t')=='s':val=strings[int(val)]
            elif c.get('t')=='inlineStr':val=''.join(c.find('m:is',ns).itertext())
            cells[c.get('r')]=val
        for i,r in enumerate(rs,2):
            assert cells[f'A{i}']==r['item_id'];assert cells[f'B{i}']==r['decoded_line']
            assert all(cells.get(f'{col}{i}','')=='' for col in ['C','D','E'])
        assert not tree.findall('.//m:f',ns)
    packet=blind/'rater-only.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(blind/'ratings.csv','ratings.csv');z.write(book,'ratings.xlsx');z.write(blind/'INSTRUCTIONS.txt','INSTRUCTIONS.txt')
    receipt=json.loads((blind/'EXPORT_RECEIPT.json').read_text());assert sha(R/'sealed/key.zip')==receipt['key_sha256']
    dump(R/'STATUS.json',dict(status='STOPPED_AFTER_REGISTERED_RUN',automatic_analysis='COMPLETE',exact_replication=False,replication_qualification='NOT_ESTABLISHED',coherence_selection='FAILED_ALL_200_ITEMS_ALL_UNKNOWN',usable_human_coherence_test=False,self_ratings=0,retuned_after_results=False,variants=24,ZL_loci=5385,ZL_words=39026,C17_documents=38,C17_clean_words=10075,C17_size_mismatch=True,corpora=['tanakh_substitute_edition','public_domain_medieval_Mishneh_Torah'],blind_packet_sha256=sha(packet),sealed_key_sha256=receipt['key_sha256'],workbook_sha256=sha(book),frozen_input_and_algorithm_hashes='PASS',shared_lab_snapshot='CONCURRENT_CHANGES_RECORDED',translation_claims=False))
    dump(R/'PACKET_VERIFICATION.json',dict(items=200,unique_ids=200,rating_fields_empty=True,workbook_matches_csv=True,all_unknown_items=200,source_variant_columns_absent=True,key_not_in_packet=True,sealed_key_hash_unchanged=True,packet_sha256=sha(packet),workbook_sha256=sha(book),sealed_key_opened=False,visual_QA='synthetic_text_only'))
    (R/'blind/HOLD_NOTICE.txt').write_text('FAILED SELECTION: all 200 items contain only <UNK>. Preserved as the frozen-rule outcome; no human rating is recommended. No replacement or retuning was performed. The sealed key is separate.\n',encoding='utf8')
    print(json.dumps(dict(packet='blind/rater-only.zip',items=200,all_unknown_items=200,key_read=False,workbook_matches_csv=True)))
if __name__=='__main__':main()
