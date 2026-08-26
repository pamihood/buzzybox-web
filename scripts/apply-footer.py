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
}

FOOTER = """  <footer>
    <p class="signoff">
      <img class="signoff-name" src="{p}assets/wordmark.png" alt="Postmello" width="1095" height="174" />
      <span class="signoff-line">Letters at your own pace.</span>
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

pattern = re.compile(r"[ \t]*<footer>.*?</footer>", re.S)

for rel, (prefix, blog) in PAGES.items():
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    new = FOOTER.format(p=prefix, blog=blog)
    html, n = pattern.subn(lambda _m: new, html, count=1)
    if n != 1:
        raise SystemExit(f"!! {rel}: expected one <footer>, replaced {n}")
    path.write_text(html, encoding="utf-8")
    print(f"[footer] {rel}")
