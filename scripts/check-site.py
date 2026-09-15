#!/usr/bin/env python3
"""Check public page links, assets, metadata, and selected-site invariants."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re, sys, hashlib
ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted([*ROOT.glob('*.html'), *(ROOT/'blog').rglob('*.html'), ROOT/'letter/index.html'])
ALIASES = {'how-it-works', 'desks', 'membership', 'grandparents', 'safety', 'request-an-invite'}
errors = []
class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.ids=set(); self.refs=[]; self.meta={}; self.feed(html)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: errors.append('duplicate ID: '+a['id'])
            self.ids.add(a['id'])
        if tag=='meta': self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        for key in ('src','href','data-image'):
            if key in a: self.refs.append((key,a[key]))
parsed={p:Page(p.read_text()) for p in PAGES}
def resolve(page, ref):
    url=urlsplit(ref)
    if url.scheme or url.netloc or ref.startswith(('data:', 'javascript:')): return None
    if any(x in ref for x in ('${','{{')): return None
    path=unquote(url.path)
    target=(ROOT/path.lstrip('/') if path.startswith('/') else page.parent/path) if path else page
    if target.is_dir(): target=target/'index.html'
    if not target.exists() and not target.suffix and target.with_suffix('.html').exists(): target=target.with_suffix('.html')
    return target.resolve(), unquote(url.fragment)
for p,doc in parsed.items():
    for kind,ref in doc.refs:
        result=resolve(p,ref)
        if result is None: continue
        target,fragment=result
        if not target.exists(): errors.append(f'{p.relative_to(ROOT)}: missing {kind} {ref}'); continue
        if fragment and target in parsed and fragment not in parsed[target].ids:
            if not (target==ROOT/'index.html' and fragment in ALIASES): errors.append(f'{p.relative_to(ROOT)}: missing anchor {ref}')
for css in [ROOT/'home.css',ROOT/'styles.css',ROOT/'assets/blog.css']:
    text=css.read_text()
    clean=re.sub(r'/\*.*?\*/','',text,flags=re.S)
    if clean.count('{')!=clean.count('}'): errors.append(f'{css.name}: unbalanced braces')
    for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)',clean):
        result=resolve(css,ref)
        if result and not result[0].exists(): errors.append(f'{css.name}: missing image {ref}')
    digest=hashlib.md5(css.read_bytes()).hexdigest()[:8]
    for p in PAGES:
        for _,ref in parsed[p].refs:
            if css.name+'?' in ref and 'v='+digest not in ref: errors.append(f'{p.name}: stale CSS version')
for rel in ['404.html','confirmed.html','reset.html','letter/index.html']:
    if 'noindex' not in parsed[ROOT/rel].meta.get('robots',''): errors.append(rel+': missing noindex')
if parsed[ROOT/'letter/index.html'].meta.get('referrer')!='no-referrer': errors.append('Private letter missing no-referrer')
if 'noindex' in parsed[ROOT/'index.html'].meta.get('robots',''): errors.append('Homepage still marked as exploration')
if (ROOT/'_concepts').exists(): errors.append('Exploration directory still present')
if '_concepts/' in (ROOT/'index.html').read_text(): errors.append('Homepage contains review links')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'[site] {len(PAGES)} pages: links, assets, IDs, CSS versions, and privacy metadata passed')
