#!/usr/bin/env python3
"""Public ATS API collector. Add company board tokens to config/sources.json."""
import datetime as dt, hashlib, json, pathlib, urllib.request, urllib.parse, html, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
TODAY=dt.datetime.now(dt.timezone.utc).date().isoformat()
HEADERS={'User-Agent':'BioMedicalVisualizationCareers/0.1 (+public job index)','Accept':'application/json'}
KEYWORDS=('medical illustrat','scientific illustrat','biomedical visual','medical visual','anatomical artist','medical animat','scientific visual','surgical simul','medical 3d','healthcare 3d','medical graphics','medical artist','biomedical animat','medical imaging visual')
def get(url):
 req=urllib.request.Request(url,headers=HEADERS)
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()[:400]
def match(title,desc):return any(k in (title+' '+desc).lower() for k in KEYWORDS)
def ident(url):return hashlib.sha256(url.encode()).hexdigest()[:16]
def item(title,org,url,loc,desc,source):
 return {'id':'j-'+ident(url),'title':title,'org':org,'category':'의료 시각화 개발' if any(x in title.lower() for x in ('developer','engineer','software')) else '의료 일러스트','type':'확인 필요','location':loc or '미기재','desc':desc,'tags':[source],'url':url,'first_seen':TODAY,'last_checked':TODAY,'status':'확인 필요'}
def main():
 config=json.loads((ROOT/'config/sources.json').read_text());old={x['id']:x for x in json.loads((ROOT/'data/jobs.json').read_text())};found={};fail=[];successful=0
 for provider in ('greenhouse','lever'):
  for entry in config.get(provider,[]):
   token=entry['token'];org=entry.get('name',token)
   try:
    if provider=='greenhouse':
     rows=get('https://boards-api.greenhouse.io/v1/boards/'+urllib.parse.quote(token)+'/jobs?content=true').get('jobs',[])
     for j in rows:
      title=j.get('title','');desc=clean(j.get('content',''))
      if not match(title,desc):continue
      url=j.get('absolute_url');
      if url:found['j-'+ident(url)]=item(title,org,url,j.get('location',{}).get('name',''),desc,'Greenhouse')
    else:
     rows=get('https://api.lever.co/v0/postings/'+urllib.parse.quote(token)+'?mode=json')
     for j in rows:
      title=j.get('text','');desc=clean(j.get('descriptionPlain',''))
      if not match(title,desc):continue
      url=j.get('hostedUrl');
      if url:found['j-'+ident(url)]=item(title,org,url,j.get('categories',{}).get('location',''),desc,'Lever')
    successful+=1
   except Exception as exc:fail.append(f'{provider}/{token}: {exc}')
 # Never wipe previously collected jobs if source APIs fail.
 if fail:print('WARN: '+ '; '.join(fail),file=sys.stderr)
 if successful==0 and (config.get('greenhouse') or config.get('lever')):sys.exit('All configured sources failed; preserving previous data')
 for key,j in found.items():
  if key in old:j['first_seen']=old[key].get('first_seen',TODAY)
 # Preserve previous entries when some sources fail, but do not claim they remain open.
 if fail:
  for key,j in old.items():
   if key not in found:j['status']='확인 필요';found[key]=j
 output=sorted(found.values(),key=lambda x:(x['org'],x['title']))
 (ROOT/'data/jobs.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 print(f'Collected {len(output)} relevant jobs from {successful} source boards; errors: {len(fail)}')
if __name__=='__main__':main()
