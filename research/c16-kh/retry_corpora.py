from retrieve import *
rows=json.loads((S/'corpora-retrieval.json').read_text());failed=[x for x in rows if 'error' in x]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: retried=list(ex.map(lambda x:get(x['url'],x['path']),failed))
(S/'corpora-retry.json').write_text(json.dumps(retried,indent=2));print(json.dumps(dict(retried=len(retried),success=sum('error' not in x for x in retried),failures=[x for x in retried if 'error' in x]),indent=2))
