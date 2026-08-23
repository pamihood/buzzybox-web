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
ORIGIN = "https://postmello.com"          # flip here at the domain move
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
# `confirmed` and `reset` are here for the same reason 404 is: they take the
# fonts and nothing else. Both are noindex transactional landings that a
# Supabase redirect drops someone on once, so a canonical URL and an og:card
# would be describing a page nobody links to.
#
# index.html came OFF this list on 2026-08-23. The homepage was rebuilt on its
# own design system and loads Fraunces / Plus Jakarta Sans / Courier Prime;
# this script writes the SHARED trio (Rubik, Nunito, DM Mono), so leaving the
# homepage here would have added a second, contradictory font link. It stays in
# PAGES below, because canonical, og:url and the share card are site-wide facts
# that have nothing to do with which stylesheet a page loads.
FONT_PAGES = [
    "support.html", "privacy.html", "terms.html", "safety.html",
    "404.html", "parents.html", "confirmed.html", "reset.html", "blog/index.html",
    "blog/why-i-built-postmello/index.html",
    "blog/designing-a-desk-not-an-app/index.html",
]

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
    "privacy.html": ("/privacy", ""),
    "terms.html": ("/terms", ""),
    "safety.html": ("/safety", ""),
    "parents.html": ("/parents", ""),
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
