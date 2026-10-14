"""Deterministic HTML data extraction and export utilities."""
import csv
import json
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_html(html,base_url='',max_items=300):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup(['script','style','noscript','svg']): node.decompose()
    title=soup.title.get_text(' ',strip=True) if soup.title else ''
    headings=[{'level':int(n.name[1]),'text':n.get_text(' ',strip=True)} for n in soup.select('h1,h2,h3,h4,h5,h6') if n.get_text(' ',strip=True)][:max_items]
    links=[]
    for a in soup.select('a[href]')[:max_items]:
        href=urljoin(base_url,a.get('href',''))
        if href.startswith(('http://','https://')): links.append({'text':a.get_text(' ',strip=True)[:200],'url':href})
    tables=[]
    for table in soup.select('table')[:30]:
        rows=[]
        for tr in table.select('tr')[:max_items]:
            rows.append([td.get_text(' ',strip=True) for td in tr.select('th,td')])
        if rows: tables.append(rows)
    return {'url':base_url,'title':title,'headings':headings,'links':links,'tables':tables,'text':soup.get_text(' ',strip=True)[:50000]}

def export_records(records,path,fmt=None):
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    fmt=(fmt or target.suffix.lstrip('.')).lower()
    if fmt=='json': target.write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
    elif fmt=='csv':
        fields=sorted({k for record in records for k in record}) if records else []
        with target.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for r in records: writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
    else: raise ValueError('Supported formats: json, csv')
    return str(target)
