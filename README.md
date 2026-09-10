# Postmello website

Static HTML/CSS website for Postmello. No build step or package installation is
required. The selected design is now the homepage; the other explorations are
archived in Git. See `docs/website-launch.md` for archives and the launch hold.

## Local preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/. The production files are served directly.

## Design and pages

- `index.html` and `home.css`: selected desk-and-letters homepage.
- `assets/site/`: the selected desk backdrop, wood texture, and full desk images.
- `assets/site.js`: desk choices, header behavior, mobile navigation, old anchor aliases.
- `styles.css`: blog, support, legal, parental-consent, and account pages. The last
  section applies the selected design to their existing reading and form layouts.
- `blog/*/index.md`: maintained article prose. `blog/posts.json` owns ordering,
  descriptions, selected figures and related links. `scripts/render-blog.py`
  renders the nine articles and index; `assets/blog.css` adds reading details.
- `letter/index.html`: private letter viewer with its own CSS and behavior. It
  stays noindex, no-referrer, and outside the sitemap. No marketing navigation or
  third-party font requests are added to this private surface.

Lora is the heading face, DM Sans the interface/body face, and Courier Prime is
reserved for technical or postal details. The red mailbox and yellow wordmark
are artwork. Use warm paper, quiet ink, and the app's assets for color.

The footer is deliberately compact, with no repeated logo. All public and account
pages share the navigation destinations and mobile hamburger behavior. The
homepage's transparent header scrolls away and returns after the hero; supporting
pages use a sticky paper header.

## Maintained sources

Do not hand-edit generated prices or duplicate the download URL.

- `../posty/pricing.json` is the sole pricing source. Never restate prices or desk
  counts in this README. `scripts/apply-pricing.py` updates all marked amounts,
  plan names, counts, and discounts, including founding-window copy.
- `brand.json` owns the tagline and App Store URL. `scripts/apply-brand.py` updates
  the homepage's marked elements and the private letter viewer's fallback link.
- `scripts/apply-navigation.py` owns supporting-page headers.
- `scripts/apply-footer.py` owns all public/account footers.
- `scripts/apply-head-meta.py` owns fonts, canonicals, and shared social metadata.
- `scripts/stamp-css-version.sh` versions both stylesheets and the shared script.

After changes, run:

```sh
python3 scripts/apply-brand.py
python3 scripts/apply-pricing.py
python3 scripts/apply-navigation.py
python3 scripts/apply-footer.py
python3 scripts/apply-head-meta.py
bash scripts/stamp-css-version.sh
python3 scripts/render-blog.py
python3 scripts/render-blog.py --check
python3 scripts/apply-brand.py --check
python3 scripts/apply-pricing.py --check
python3 scripts/check-site.py
```

Header/footer/metadata edits belong in their scripts so a later refresh doesn't
undo them. Preserve legal text and transactional scripts when restyling pages.
The app's Supabase-backed consent, confirmation, password-reset, and private
letter behavior must remain intact.

For a prose-only blog edit, run `python3 scripts/render-blog.py` followed by its
`--check` mode and `python3 scripts/check-site.py`. The renderer uses paragraphs,
headings, links, emphasis and strong text; it deliberately needs no package
installation. New posts need an inventory entry and a sitemap URL. The two
original URLs stay stable even when an article's title changes.

The accepted seven essays use “tablet” instead of “iPad” in their prose. Keep
actual platform availability specific on download and compatibility surfaces;
the editorial wording does not announce Android availability.

## Hosting and launch hold

Cloudflare Pages project `postmello-web` serves postmello.com and www. Pushes to
`main` deploy automatically. The GitHub Pages workflow is a deliberate standby
and holds the domain claim; keep `.github/workflows/pages.yml`, `CNAME`, and
`.nojekyll` together.

The selected website is waiting for Apple review and download-link verification.
Keep it on the working branch and prefix save commits with `[CF-Pages-Skip]` to
avoid preview deployments. Do not merge to main or trigger a manual deployment
until authorized. Archive tags preserve the original and all explorations.

`_headers` maintains security and immutable CSS caching. The cache versions must
be refreshed after stylesheet edits. `_redirects` excludes operational documents
from public routes. Existing App Store privacy/support `.html` URLs remain valid.

## Content rules

- Describe the implemented safety mechanisms, without inventing certification,
  privacy guarantees, or outcome claims. Parental approval is enforced server-side.
- Keep App Store badge artwork unchanged. Update its URL only from the approved listing.
- `hello@postmello.com` is the creator/front-door address; `support@postmello.com`
  is for support, legal, privacy, and reporting requests.
- Existing testimonials are real quotes. No fabricated awards, metrics, or endorsements.
- Keep purchased collections distinct from membership and preserve the pricing source.
- Preserve the blog's rationale and legal documents; visual changes should not rewrite them.
