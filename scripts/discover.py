#!/usr/bin/env python3
"""Retrieve candidate NASA footage (metadata only; no automatic rights inference)."""
import argparse,json,urllib.request,urllib.parse
def main():
    p=argparse.ArgumentParser()
    p.add_argument('query');p.add_argument('--year',type=int);p.add_argument('--limit',type=int,default=8)
    a=p.parse_args()
    if not 1<=a.limit<=20:p.error('limit must be 1–20')
    qs={'q':a.query,'media_type':'video','page_size':a.limit}
    if a.year:qs.update(year_start=a.year,year_end=a.year)
    def get(u):
        req=urllib.request.Request(u,headers={'User-Agent':'News-Clip-Video/1.0'})
        with urllib.request.urlopen(req,timeout=18) as f:return json.load(f)
    found=[]
    for item in get('https://images-api.nasa.gov/search?'+urllib.parse.urlencode(qs))['collection']['items'][:a.limit]:
        d=item['data'][0]; i=d['nasa_id']; token=urllib.parse.quote(i,safe='')
        found.append({'title':d['title'],'date':d.get('date_created'),'description':d.get('description','')[:400],
            'asset_id':i,'source':'https://images.nasa.gov/details-'+token,'asset_manifest':'https://images-api.nasa.gov/asset/'+token,
            'rights_reference':'https://www.nasa.gov/nasa-brand-center/images-and-media/','status':'candidate_needs_review'})
    print(json.dumps(found,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
