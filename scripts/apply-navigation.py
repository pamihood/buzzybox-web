#!/usr/bin/env python3
"""Apply the homepage navigation to supporting pages without changing their content."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent.parent
PAGES = ['support.html', 'privacy.html', 'terms.html', 'safety.html', 'parents.html', '404.html', 'confirmed.html', 'reset.html', 'blog/index.html'] + [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'blog').glob('*/index.html'))]
HEADER = '<header class="site-head"><a class="site-brand" href="/" aria-label="Postmello home"><img src="/assets/mark.png" width="42" height="42" alt=""><img class="name" src="/assets/wordmark.png" width="1100" height="215" alt="Postmello"></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-navigation" aria-label="Open menu" hidden><span class="menu-icon" aria-hidden="true"><span></span><span></span><span></span></span></button><nav id="main-navigation" aria-label="Main navigation"><a href="/#experience">The experience</a><a href="/#collections">Collections</a><a href="/#parents">For parents</a><a href="/#pricing">Free to start</a><a href="/blog/">Our story ↗</a></nav></header>'
for rel in PAGES:
    p = ROOT / rel
    html, count = re.subn(r'<header\b[^>]*>.*?</header>', lambda _: HEADER, p.read_text(), count=1, flags=re.S)
    if count != 1: raise SystemExit(f'{rel}: expected one header')
    if '/assets/site.js' not in html:
        html = html.replace('</head>', '<script src="/assets/site.js" defer></script>\n</head>')
    p.write_text(html)
    print(f'[navigation] {rel}')
