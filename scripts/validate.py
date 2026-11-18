import json,pathlib,urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
for kind in ('jobs','opportunities','events'):
 rows=json.loads((root/'data'/f'{kind}.json').read_text())
 assert isinstance(rows,list),kind
 ids=set()
 for r in rows:
  assert isinstance(r,dict) and r.get('id') and r.get('title'),r
  assert r['id'] not in ids,r['id'];ids.add(r['id'])
  if r.get('url'):assert urllib.parse.urlsplit(r['url']).scheme=='https',r['url']
 print(kind,len(rows))
