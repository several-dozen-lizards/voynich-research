from retrieve import *
b=json.loads((S/'sefaria-books.json').read_text(encoding='utf8'))['books']
chosen=[dict(x,arm='tanakh') for x in b if x['language']=='Hebrew' and x['versionTitle']=='Tanach with Text Only']
chosen += [dict(x,arm='medieval') for x in b if x['language']=='Hebrew' and x['title'].startswith('Mishneh Torah,') and x['versionTitle'] in ['Torat Emet 363','Torat Emet 370']]
for i,x in enumerate(chosen):x['local']=f"{x['arm']}/{i:03d}.json"
(S/'corpora-selection.json').write_text(json.dumps(chosen,indent=2),encoding='utf8')
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    rows=list(ex.map(lambda x:get(x['json_url'],x['local']),chosen))
(S/'corpora-retrieval.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps(dict(selected=len(chosen),success=sum('error' not in x for x in rows),failures=[x for x in rows if 'error' in x]),indent=2))
