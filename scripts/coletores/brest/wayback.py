#!/usr/bin/env python3
"""Recuperar as seis sementes russas pelo Wayback, sem alterar acervo publicado."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from coletar import PoliteFetch,DEFAULT_OUTPUT,initial_sources,process,save_report,atomic_json,immutable,sha,canonical

IDS={'iskra-primeira-sessao','iskra-27-dez','iskra-jan-11','iskra-fase-2','iskra-jan-31','iskra-mar-1'}
CDX='https://web.archive.org/cdx/search/cdx'


class Wayback(PoliteFetch):
    def __init__(self,output):
        super().__init__(delay=3,timeout=30)
        self.output=output;self.captures={};self.acquisitions={}

    def index(self):
        response=self.session.get(CDX,params={'url':'iskra-research.org/USSR/Brest/*','output':'json','filter':'statuscode:200','collapse':'urlkey','fl':'timestamp,original','limit':1000},timeout=(12,35))
        response.raise_for_status();rows=response.json()
        if not rows or rows[0]!=['timestamp','original']:raise ValueError('Índice CDX inesperado')
        relative=Path('wayback/indexes')/(sha(response.content)+'.json');immutable(self.output/relative,response.content)
        for stamp,original in rows[1:]:
            if urlparse(original).hostname!='iskra-research.org' or not re.fullmatch(r'\d{14}',stamp):continue
            key=urlparse(original).path
            if key not in self.captures or stamp>self.captures[key]['timestamp']:
                self.captures[key]={'timestamp':stamp,'original':original,'cdx_snapshot':str(relative)}
        atomic_json(self.output/'wayback/index-latest.json',{'retrieved_at':datetime.now(timezone.utc).isoformat(),'snapshot':str(relative),'rows':len(rows)-1,'selection':'Most recent among CDX rows collapsed by URL key; not asserted latest available capture.'})

    def get(self,url):
        capture=self.captures.get(urlparse(url).path)
        if not capture:raise ValueError('Nenhuma captura localizada no resultado CDX; não significa inexistência no arquivo')
        requested=f"https://web.archive.org/web/{capture['timestamp']}id_/{capture['original']}"
        self.pause('web.archive.org')
        with self.session.get(requested,timeout=(12,40),stream=True) as response:
            response.raise_for_status()
            match=re.fullmatch(r'/web/(\d{14})(?:id_)?/(https?://.+)',urlparse(response.url).path)
            if urlparse(response.url).hostname!='web.archive.org' or not match:raise ValueError('URL de captura final inesperada')
            original=match[2]
            if urlparse(original).hostname!='iskra-research.org' or urlparse(original).path!=urlparse(url).path:raise ValueError('Captura não corresponde à fonte selecionada')
            chunks=[];size=0
            for chunk in response.iter_content(65536):
                size+=len(chunk)
                if size>25*1024*1024:raise ValueError('Captura acima de 25 MiB')
                chunks.append(chunk)
            blob=b''.join(chunks);soup=BeautifulSoup(blob,'html.parser');main=soup.select_one('#mainContent')
            if main is None or len(re.findall(r'[А-Яа-яЁё]',main.get_text()))<100:raise ValueError('Captura sem corpo russo identificável')
            self.final_urls[canonical(url)]=original
            self.acquisitions[url]={'provider':'Wayback Machine','requested_capture':requested,'archive_url':response.url,'capture_timestamp':match[1],'captured_original_url':original,'cdx_snapshot':capture['cdx_snapshot'],'raw_sha256':sha(blob),'http_status':response.status_code,'original_live_access':'Earlier collector attempts failed at robots.txt; archived copy acquired independently.'}
            return blob,'text/html'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);args=parser.parse_args()
    fetcher=Wayback(args.output);fetcher.index();records=[]
    for source in initial_sources():
        if source['id'] not in IDS:continue
        # process preserva metadados anteriores e snapshots por hash.
        row=process(source,fetcher,args.output,refresh=True)
        if source['url'] in fetcher.acquisitions:
            row['wayback']=fetcher.acquisitions[source['url']]
            atomic_json(args.output/'meta'/source['grupo']/(source['id']+'.json'),row)
        records.append(row);save_report(args.output,records,[])
        print(source['id'],row['estado_aquisicao'],row.get('erro',row.get('bytes')),flush=True)
    atomic_json(args.output/'wayback/result.json',{'sources':len(records),'recovered':sum(r.get('estado_aquisicao')=='FOUND_HTML_UNREVIEWED' for r in records),'records':records})


if __name__=='__main__':main()
