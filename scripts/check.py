"""Validate generated pages, local links, anchors and CV publication coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
root=Path(__file__).resolve().parents[1]/'site'
class Page(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.ids=set(); self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1': self.h1+=1
        if 'id' in a: self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a: self.links.append(a[key])
pages={}
for file in root.rglob('*.html'):
    p=Page(); p.feed(file.read_text()); pages[file.resolve()]=p
errors=[]
for file,p in pages.items():
    if p.h1!=1: errors.append(f'{file}: {p.h1} h1 elements')
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        target=((root/unquote(u.path).lstrip('/')).resolve() if u.path.startswith('/') else (file.parent/unquote(u.path)).resolve()) if u.path else file
        if not target.exists(): errors.append(f'{file.name}: missing {link}')
        elif u.fragment and target in pages and u.fragment not in pages[target].ids: errors.append(f'{file.name}: missing anchor {link}')
projects=json.loads((root.parent/'projects.json').read_text())
assert sorted(i for p in projects for i in p['papers'])==list(range(17))
assert not errors, '\n'.join(errors)
print(f'PASS: {len(pages)} HTML pages; all local assets, links and anchors; all 17 papers mapped exactly once across {len(projects)} projects.')
