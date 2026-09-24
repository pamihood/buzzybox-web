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
- The hero is the desk film: `assets/site/desk-loop-960.mp4` (phones) and
  `desk-loop-1440.mp4`, the site film without its brand card and end card, playing
  muted as the page opens. Its recipe is `web_loop.sh` in posty's
  `_local/marketing/product-film/_recipe/`. The six desks are shown further down
  as a plain grid (`*-grid.webp`, 800x600), not as a switcher.
- "Not on your iPad?" (`[data-send-link]` in `index.html`, its script in
  `assets/site.js`): the closing section's form that emails a visitor the App
  Store link, for the phones the ads bring to an iPad-only app. The hero carries
  only one line pointing at it; on a phone that line is the hero's button and
  both App Store badges are hidden (an iPhone cannot install Postmello). It posts to posty's `ipad-link` edge function
  (Turnstile-gated, keeps no address, one email per address per day); on
  localhost it uses Cloudflare's always-pass test key and `/mock/ipad-link`.
  A headless browser cannot pass the real check on postmello.com (Cloudflare
  shows "Verify you are human" and refuses a scripted tick), so prove a change
  there with a human send; proven so on 2026-09-22.
- `assets/origin-writing.webp`: the "How it began" photo, Patrick's daughter
  writing at lunch. Framed below the chin, written names blurred; the recipe and
  boxes are in posty's `_local/marketing/carousel/` (README, "Website 'How it
  began' photo"). Any photo of a child here follows the same rules. Patrick
  approved reusing it (2026-09-23) in the Why I Built Postmello essay and, as a
  2:1 band of the hand and the page, on that essay's blog card
  (`assets/blog/why-i-built-postmello-card.webp`).
- `assets/site.js`: desk choices, header behavior, mobile navigation, old anchor aliases.
- `press.html` and `assets/press/`: the press kit at `/press`, linked from the
  footer. "About Postmello" is the site's own sentences (homepage and the Three
  Kinds of Quiet essay), so change the homepage first and carry it over; the
  story is Patrick's voice. The solo-build angle lives only here, and no photo of
  a child goes on it. Film files are named length, shape, sound
  (`postmello-long-16x9-no-music.mp4`), matching the finished set in posty's
  `_local/marketing/films/`; the short 4:3 film is the homepage's own
  `assets/site/desk-loop-1440.mp4`.
- Patrick's portrait (`assets/press/patrick-amihood-*.webp`, full-size `.jpg`
  for press) is a square crop of `~/Documents/me/misc/me.png`. It appears at the
  homepage's "How it began" signature, on every essay's byline and closing author
  card (`AUTHOR_CARD` in `scripts/render-blog.py`), and on the press page.
- `assets/instagram/`: the prints in the homepage's Instagram section, 3:4 WebP at
  900×1200, served from here so the page loads nothing from Instagram. The section is
  hand-maintained in `index.html`; the comment above the prints says how to add a post.
- `styles.css`: blog, support, legal, parental-consent, and account pages. The last
  section applies the selected design to their existing reading and form layouts.
- `blog/*/index.md`: maintained article prose. `blog/posts.json` owns ordering,
  descriptions, selected figures, related links, each essay's `published` and
  `updated` dates (set by hand, so a typo fix does not move them; the byline shows
  month and year, "Updated" only for a revision in a later month, and each page
  carries them as article times and schema.org data), and which essays the index
  lists: `featured`, each with a 2:1 `card` image (Why I Built Postmello and
  Three Kinds of Quiet since 2026-09-23, because nine at once read as homework).
  The other seven are unlisted but live, in the sitemap, and every essay's Keep
  reading points at the featured two. `scripts/render-blog.py` renders the nine
  articles and index; `assets/blog.css` adds reading details. Three Kinds of
  Quiet's picture (`assets/blog/three-kinds-of-quiet.webp`) is rendered from
  posty's `samples/app-store/compose/blog-three-kinds-of-quiet.html` (the App
  Store screenshots' wall, grain and object shadow and their cut-out art),
  by headless Chrome at 900x450 CSS px, device scale 2.
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
- `brand.json` owns the tagline, the App Store URL and the Instagram URL.
  `scripts/apply-brand.py` updates the homepage's marked elements, the press
  kit's App Store links, and the private letter viewer's fallback link; `scripts/apply-footer.py` reads the Instagram URL too.
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

## Hosting

Cloudflare Pages project `postmello-web` serves postmello.com and www. Pushes to
`main` deploy automatically. The GitHub Pages workflow is a deliberate standby
and holds the domain claim; keep `.github/workflows/pages.yml`, `CNAME`, and
`.nojekyll` together.

The selected website went live on 2026-09-15, after Apple approved 1.0 (build
95) for manual release. The App Store badges point at the listing's Apple id
`6806487006` (`brand.json`); the link answers 404 until the version is released
in App Store Connect and resolves as-is once it is. A work-in-progress branch may
prefix its save commits with `[CF-Pages-Skip]` to avoid preview deployments.
Bring such a branch to `main` with a merge commit, never a fast-forward, and
keep that token out of the merge commit's message entirely, body included. On
2026-09-15 the merge commit and the notes commit after it both quoted the
token while explaining this rule; the GitHub Pages standby deployed in 21
seconds, production still served the old site three minutes later, a commit
whose message never mentions the token was pushed, and the new site was live
about forty seconds after that (214 seconds after the first push). Cloudflare's
deployment list was not readable from that session, so whether the first push
built at all is unknown. A message that never mentions the token is the safe
rule either way.
Archive tags preserve the original and all explorations.

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
