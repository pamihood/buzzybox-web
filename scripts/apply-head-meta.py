#!/usr/bin/env python3
"""Give every page the same head furniture: the webfonts, canonical, absolute
og:image/og:url, twitter card, apple-touch-icon.

og:image and og:url MUST be absolute — a scraper fetching the page has no base
to resolve "assets/app-desk.jpg" against, so the homepage has been unfurling
with no picture at all. They are also the only absolute origins in the markup,
which is what makes the postmello.com move a single grep.
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root, not scripts/
ORIGIN = "https://buzzybox.app"          # flip here at the domain move
CARD = f"{ORIGIN}/assets/og-card.jpg"

# Rubik for the mark, Nunito for the voice, DM Mono for the apparatus.
# Families must be listed ALPHABETICALLY or the css2 API 400s. Nunito is
# requested as a range so one variable file covers 450 through 800; the other
# two are single weights, which ship as smaller static instances.
# display=swap: the fallback stack renders immediately and is replaced when the
# webfont lands, so a slow CDN costs a reflow rather than invisible text.
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '{i}<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '{i}<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=DM+Mono:wght@500&amp;family=Nunito:wght@400..800&amp;'
    'family=Rubik:wght@600&amp;display=swap" />'
)

# Every page takes the fonts, including 404 (which takes nothing else — it is
# noindex and served at any depth, so canonical and og:url are meaningless).
FONT_PAGES = [
    "index.html", "support.html", "privacy.html", "terms.html", "safety.html",
    "404.html", "blog/index.html",
    "blog/why-i-built-postmello/index.html",
    "blog/designing-a-desk-not-an-app/index.html",
]

# page -> (canonical path, asset prefix)
PAGES = {
    "index.html": ("/", ""),
    "support.html": ("/support.html", ""),
    "privacy.html": ("/privacy.html", ""),
    "terms.html": ("/terms.html", ""),
    "safety.html": ("/safety.html", ""),
    "blog/index.html": ("/blog/", "../"),
    "blog/why-i-built-postmello/index.html": ("/blog/why-i-built-postmello/", "../../"),
    "blog/designing-a-desk-not-an-app/index.html": ("/blog/designing-a-desk-not-an-app/", "../../"),
}


def ensure(html, probe, tag, anchor):
    """Insert `tag` before the stylesheet link if `probe` isn't already there."""
    if probe in html:
        return html, False
    return html.replace(anchor, tag + "\n" + anchor, 1), True


def stylesheet_anchor(html):
    """The site's OWN stylesheet link — never the Google Fonts one, which also
    matches `rel="stylesheet"` and sits above it once this has run."""
    return re.search(r'[ \t]*<link rel="stylesheet" href="[^"]*styles\.css[^"]*"[^>]*>',
                     html).group(0)


for rel in FONT_PAGES:
    f = ROOT / rel
    html = f.read_text(encoding="utf-8")
    anchor = stylesheet_anchor(html)
    indent = " " * (len(anchor) - len(anchor.lstrip()))
    if "fonts.googleapis.com" in html:
        print(f"[font] {rel:48} (already linked)")
        continue
    html = html.replace(anchor, indent + FONTS.format(i=indent) + "\n" + anchor, 1)
    f.write_text(html, encoding="utf-8")
    print(f"[font] {rel:48} + Rubik, Nunito, DM Mono")

for rel, (path, prefix) in PAGES.items():
    f = ROOT / rel
    html = f.read_text(encoding="utf-8")
    anchor = stylesheet_anchor(html)
    indent = " " * (len(anchor) - len(anchor.lstrip()))
    added = []

    # og:image — replace a relative one rather than adding a second.
    html, n = re.subn(r'<meta property="og:image" content="[^"]*"',
                      f'<meta property="og:image" content="{CARD}"', html)
    if n:
        added.append("og:image=abs")
    else:
        html, ok = ensure(html, 'property="og:image"',
                          f'{indent}<meta property="og:image" content="{CARD}" />', anchor)
        added += ["og:image"] if ok else []

    for probe, tag in [
        ('property="og:url"', f'<meta property="og:url" content="{ORIGIN}{path}" />'),
        ('property="og:site_name"', '<meta property="og:site_name" content="Postmello" />'),
        ('name="twitter:card"', '<meta name="twitter:card" content="summary_large_image" />'),
        ('rel="canonical"', f'<link rel="canonical" href="{ORIGIN}{path}" />'),
        ('rel="apple-touch-icon"', f'<link rel="apple-touch-icon" href="{prefix}assets/app-icon.png" />'),
    ]:
        html, ok = ensure(html, probe, indent + tag, anchor)
        if ok:
            added.append(probe.split('"')[1])

    f.write_text(html, encoding="utf-8")
    print(f"[meta] {rel:48} {'+ ' + ', '.join(added) if added else '(already complete)'}")
