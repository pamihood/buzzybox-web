#!/usr/bin/env python3
"""Apply the selected design's compact footer to public and account pages."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent.parent
PAGES = ['index.html', 'support.html', 'privacy.html', 'terms.html', 'safety.html', 'parents.html', '404.html', 'confirmed.html', 'reset.html', 'blog/index.html', 'blog/why-i-built-postmello/index.html', 'blog/designing-a-desk-not-an-app/index.html']
FOOTER = '<footer class="wrap footer site-footer"><nav aria-label="Footer"><a href="/privacy.html">Privacy</a><a href="/safety.html">Safety</a><a href="/terms.html">Terms</a><a href="/support.html">Support</a><a href="/blog/">Blog</a></nav><span>© 2026 Postmello</span></footer>'
for rel in PAGES:
    p = ROOT / rel
    html, count = re.subn(r'<footer\b[^>]*>.*?</footer>', lambda _: FOOTER, p.read_text(), count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{rel}: expected one footer')
    p.write_text(html)
    print(f'[footer] {rel}')
