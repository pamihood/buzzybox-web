#!/usr/bin/env python3
"""Give every page the same head furniture: the webfonts, canonical, absolute
og:image/og:url, twitter card, apple-touch-icon; and the homepage its
schema.org structured data.

og:image and og:url MUST be absolute — a scraper fetching the page has no base
to resolve "assets/app-desk.jpg" against, so the homepage has been unfurling
with no picture at all. They are also the only absolute origins in the markup,
which is what makes the postmello.com move a single grep.
"""
import json
import re
import pathlib
from html import unescape   # not `import html`: the loops below name a variable html

ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root, not scripts/
ORIGIN = "https://postmello.com"          # flip here at the domain move
# Versioned by content: Slack, iMessage, X and Facebook cache a preview image by
# URL for hours to days, so a new card at the old URL kept unfurling as the old
# card. A hash in the query makes a changed card a new URL; the file itself
# is untouched, and the query is ignored by Pages.
import hashlib
CARD_HASH = hashlib.md5((ROOT / "assets" / "og-card.jpg").read_bytes()).hexdigest()[:8]
CARD = f"{ORIGIN}/assets/og-card.jpg?v={CARD_HASH}"

# The selected design uses Lora and DM Sans; code examples retain Courier Prime.
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '{i}<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '{i}<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Courier+Prime:wght@400;700&amp;family=DM+Sans:wght@400;500;600;700&amp;'
    'family=Lora:ital,wght@0,400;0,500;1,400;1,500&amp;display=swap" />'
)

# Public and account pages share fonts. Private letters keep local-only assets.
FONT_PAGES = [
    "index.html",
    "support.html", "press.html", "privacy.html", "terms.html", "safety.html",
    "404.html", "parents.html", "confirmed.html", "reset.html", "blog/index.html",
] + [str(p.relative_to(ROOT)) for p in sorted((ROOT / "blog").glob("*/index.html"))]

# page -> (canonical path, asset prefix)
#
# Paths are EXTENSIONLESS. The host 308-redirects /x.html to /x, so naming the
# .html form here pointed every canonical and og:url at a URL that immediately
# redirects -- the page telling crawlers one thing and the server another.
# Both forms still resolve, so old links (the App Store privacy and support
# URLs among them) keep working.
PAGES = {
    "index.html": ("/", ""),
    "support.html": ("/support", ""),
    "press.html": ("/press", ""),
    "privacy.html": ("/privacy", ""),
    "terms.html": ("/terms", ""),
    "safety.html": ("/safety", ""),
    "parents.html": ("/parents", ""),
    "blog/index.html": ("/blog/", "../"),
}
PAGES.update({
    str(p.relative_to(ROOT)): (f"/blog/{p.parent.name}/", "../../")
    for p in sorted((ROOT / "blog").glob("*/index.html"))
})


def ensure(html, probe, tag, anchor):
    """Insert `tag` before the stylesheet link if `probe` isn't already there."""
    if probe in html:
        return html, False
    return html.replace(anchor, tag + "\n" + anchor, 1), True


def stylesheet_anchor(html):
    """The page's OWN stylesheet link — never the Google Fonts one, which also
    matches `rel="stylesheet"` and sits above it once this has run.

    Matches home.css as well as styles.css since 2026-08-23: the homepage is
    the one page on its own sheet, and without this the search returned None
    and the script died on it with an AttributeError."""
    return re.search(r'[ \t]*<link rel="stylesheet" href="[^"]*(?:styles|home)\.css[^"]*"[^>]*>',
                     html).group(0)


for rel in FONT_PAGES:
    f = ROOT / rel
    html = f.read_text(encoding="utf-8")
    anchor = stylesheet_anchor(html)
    indent = " " * (len(anchor) - len(anchor.lstrip()))
    html = re.sub(r'<link\b[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*', '', html)
    html = html.replace(anchor, indent + FONTS.format(i=indent) + "\n" + anchor, 1)
    f.write_text(html, encoding="utf-8")
    print(f"[font] {rel}: Lora, DM Sans, Courier Prime")

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

    # og:url and canonical carry the origin AND the path, so they have to be
    # REPLACED when either changes. ensure() only inserts, which is why the
    # .html canonicals sat stale after the host started redirecting them, and
    # why the "single grep" in the docstring was not actually true for these
    # two. Same replace-then-fall-back-to-insert shape as og:image above.
    for pattern, tag, probe, label in [
        (r'<meta property="og:url" content="[^"]*"',
         f'<meta property="og:url" content="{ORIGIN}{path}"',
         'property="og:url"', "og:url"),
        (r'<link rel="canonical" href="[^"]*"',
         f'<link rel="canonical" href="{ORIGIN}{path}"',
         'rel="canonical"', "canonical"),
    ]:
        html, n = re.subn(pattern, tag, html)
        if n:
            added.append(label)
        else:
            html, ok = ensure(html, probe, f"{indent}{tag} />", anchor)
            added += [label] if ok else []

    for probe, tag in [
        ('property="og:site_name"', '<meta property="og:site_name" content="Postmello" />'),
        ('name="twitter:card"', '<meta name="twitter:card" content="summary_large_image" />'),
        ('rel="apple-touch-icon"', f'<link rel="apple-touch-icon" href="{prefix}assets/app-icon.png" />'),
    ]:
        html, ok = ensure(html, probe, indent + tag, anchor)
        if ok:
            added.append(probe.split('"')[1])

    f.write_text(html, encoding="utf-8")
    print(f"[meta] {rel:48} {'+ ' + ', '.join(added) if added else '(already complete)'}")


# The homepage's schema.org graph: the company, the site and the app, saying in
# machine terms what the page says in prose. Google takes the site name and logo
# in results from the Organization and WebSite nodes on the home page, and search
# engines and AI answers learn from the app node that Postmello is a free iPhone
# and iPad app. Every link comes from ORIGIN or brand.json, so the App Store URL
# is still typed in exactly one place, and the app's description IS the page's
# meta description, so the two cannot drift. Each essay's BlogPosting names the
# same Organization by its @id (scripts/render-blog.py).
#
# Google shows an app rich result only for a page with a visible rating or
# review. This page has neither and must never invent one, so Search Console
# lists the app as missing "aggregateRating" or "review". That is expected: it
# costs the star snippet, nothing about indexing.
BRAND = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
LD_PAGE = "index.html"


def homepage_graph(description):
    org = {"@id": f"{ORIGIN}/#organization"}
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", **org, "name": "Postmello", "legalName": "Postmello LLC",
             "url": f"{ORIGIN}/", "logo": f"{ORIGIN}/assets/mark.png", "email": "hello@postmello.com",
             "founder": {"@type": "Person", "name": "Patrick Amihood", "url": f"{ORIGIN}/press#founder"},
             "sameAs": [BRAND["instagram_url"]]},
            {"@type": "WebSite", "@id": f"{ORIGIN}/#website", "name": "Postmello",
             "url": f"{ORIGIN}/", "publisher": org},
            {"@type": "MobileApplication", "@id": f"{ORIGIN}/#app", "name": "Postmello",
             "description": description, "operatingSystem": "iOS, iPadOS",
             "applicationCategory": "LifestyleApplication",   # the App Store category
             "installUrl": BRAND["app_store_url"], "sameAs": BRAND["app_store_url"],
             "image": f"{ORIGIN}/assets/app-icon.png",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
             "publisher": org},
        ],
    }


f = ROOT / LD_PAGE
html = f.read_text(encoding="utf-8")
description = unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))
ld = json.dumps(homepage_graph(description), ensure_ascii=False).replace("</", "<\\/")
tag = f'<script type="application/ld+json">{ld}</script>'
# Replace in place, else add it last in <head>: the font links above are removed
# and re-added before the stylesheet on every run, so anchoring there would move
# this block on the second run.
html, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: tag, html, count=1, flags=re.S)
if not n:
    html = html.replace("</head>", tag + "\n</head>", 1)
f.write_text(html, encoding="utf-8")
print(f"[ld]   {LD_PAGE}: Organization, WebSite, MobileApplication")
