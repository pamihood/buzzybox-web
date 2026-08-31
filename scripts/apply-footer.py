#!/usr/bin/env python3
"""Replace the <footer> block on every page with the grouped footer.

One source of truth for the site's sign-off, so the next link cannot land on
five pages and miss the sixth (which is how Help and Privacy drifted apart in
the first place).
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root, not scripts/

# page -> (prefix for root-level files, href for the blog index)
# index.html is NOT in this map (2026-08-23). The homepage was rebuilt on its
# own design system and carries its own footer - a three-column brand/links/
# newsletter block that has nothing in common with the shared one. Running this
# script over it would replace that footer with the legal pages' version and
# silently undo the redesign. If the rest of the site is ever brought onto the
# new system, this map is where the homepage comes back.
PAGES = {
    "support.html": ("", "blog/"),
    "privacy.html": ("", "blog/"),
    "terms.html": ("", "blog/"),
    "safety.html": ("", "blog/"),
    # 404 is served at ANY depth, so its links must be root-absolute.
    "404.html": ("/", "/blog/"),
    "blog/index.html": ("../", "./"),
    "blog/why-i-built-postmello/index.html": ("../../", "../"),
    "blog/designing-a-desk-not-an-app/index.html": ("../../", "../"),
    # Added 2026-08-31. All three carried a hand-kept copy of this footer and
    # were simply missing from the map - which is the drift the script exists
    # to stop, and it had already happened: a tagline change reached nine
    # pages and missed these. reset and confirmed are root-absolute for the
    # same reason 404 is; they are auth landing pages and may be served from
    # a path this file cannot predict.
    "parents.html": ("", "blog/"),
    "reset.html": ("/", "/blog/"),
    "confirmed.html": ("/", "/blog/"),
}

FOOTER = """  <footer>
    <p class="signoff">
      <img class="signoff-name" src="{p}assets/wordmark.png" alt="Postmello" width="1100" height="215" />
      <span class="signoff-line">A quiet place for letters.</span>
    </p>
    <nav class="foot-groups" aria-label="Footer">
      <div class="foot-group">
        <p class="foot-label">Explore</p>
        <a href="{blog}">Blog</a>
        <a href="{p}support.html">Help</a>
      </div>
      <div class="foot-group">
        <p class="foot-label">Trust</p>
        <a href="{p}safety.html">Safety</a>
        <a href="{p}parents.html">For parents</a>
        <a href="{p}privacy.html">Privacy Policy</a>
        <a href="{p}terms.html">Terms</a>
      </div>
      <div class="foot-group">
        <p class="foot-label">Contact</p>
        <a href="mailto:support@postmello.com">support@postmello.com</a>
      </div>
    </nav>
    <span class="fine">© 2026 Postmello</span>
  </footer>"""

# <footer\b[^>]*> rather than <footer>: parents.html carried
# class="site-foot" - inert, styled nowhere, but enough to make the old
# pattern miss the page and the script exit rather than write it.
pattern = re.compile(r"[ \t]*<footer\b[^>]*>.*?</footer>", re.S)

for rel, (prefix, blog) in PAGES.items():
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    new = FOOTER.format(p=prefix, blog=blog)
    html, n = pattern.subn(lambda _m: new, html, count=1)
    if n != 1:
        raise SystemExit(f"!! {rel}: expected one <footer>, replaced {n}")
    path.write_text(html, encoding="utf-8")
    print(f"[footer] {rel}")
