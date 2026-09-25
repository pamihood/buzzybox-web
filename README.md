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
  `_local/marketing/product-film/_recipe/`. In front of the film's lower-left
  corner sits an iPhone (`.film-phone`, a still): the picture says "iPhone and
  iPad" before the words do. It must NOT show the desk again (Patrick,
  2026-09-24: the film already did, and the desk is cramped on a phone). It
  shows a letter being made — the purple mountains, typed, with the sticker
  drawer open (`assets/site/iphone-letter-900.webp`, Patrick's own capture,
  turned a quarter counter-clockwise: iOS stores a sideways screen upright). Further down, two desks (Sandy Beach
  and Ember Peak, `desk-*-1200.webp`) are shown large and PLAIN: no caption, no
  mat, no device frame, just a soft edge. Refused on 2026-09-24: a photo print
  on a paper mat, an iPad frame (too strong) and the desk's own nameplate as the
  caption (it pulls the eye off the desk). Then every collection in a rail.
- The page's order since the iPhone + two-free-desks revision (branch
  `iphone-and-pricing`, 2026-09-24). The hero says **Kids can keep in touch
  without texting.** over the one line that says what the app does,
  **Write and draw digital letters with friends and family.** — keep that line
  verbatim. Straight after the film comes *How it began* — "She wanted a way
  to stay close to her friend." — because the headline is its story (Patrick,
  2026-09-24); its signature is "Dad & creator of Postmello" and nothing about
  past employers, and neither does the blog's author card (Patrick, 2026-09-24:
  it read as showing off). Only the press bio keeps that background.
  Then three promises, each in the site's own words:
  **creativity** — and the desk does not come again straight after the film
  (Patrick, 2026-09-24), so it opens on *A little wonder on every page*
  (Fairy Glen; "Papers, envelopes, stamps, and stickers in every collection";
  its pieces unlabelled), then *What kids make when there's room* (one real
  letter, the purple mountains), then *Their very own place. A desk that
  feels like them.* (two desks, large and plain, and "A desk in every
  collection"),
  then *Spark their imagination. So many worlds to choose from.* (every
  collection's icon in a rail that scrolls sideways — a finger or trackpad
  natively, a mouse by dragging or the arrows — in Patrick's order;
  `assets/collections/<key>.webp` are the app's own catalog icons; add a
  collection's icon there when it goes live). Each heading carries ONE value:
  the desk is IDENTITY (a child picks a desk for themselves, because it feels
  like them — not for friends, not for anyone else; Patrick, 2026-09-24), the
  collections are imagination and choice, so the desk line never says
  "choose". Refused: "So many possibilities" under the desks (it said the
  collections' thing twice), "For the people they love" (nobody picks a desk
  for someone else), "With their name on it" (a feature, not a value),
  "Whole little worlds" ("little" reads as for small children) and "Yours to
  keep" (keeping is not why anyone chooses a collection). Then
  **calm** — *Connected, not always on*; **safety** — *Their
  independence. Your boundaries.* (four facts; the safety page has the rest).
  Then pricing (**Two desks, free. Room to grow.** — true on every plan, which
  "Letters are free. Always." was not: a member pays), email friends,
  testimonials, FAQ, Instagram, and the close: **Letters, not texts.**
  (the brand line, `brand.json` `tagline`). The contrast is TEXTING, never phones
  (Postmello runs on one) and barely social media (the children it is for
  should not be on it); lead with what a child gains, and keep safety to plain
  facts. Section labels in tiny capitals are gone: a heading that says what its
  section is needs nothing above it; the few kept (Pricing, the FAQ, Instagram)
  are sentence case at body size. The three kinds of quiet live in the blog
  essay, not here. Neighbouring sections never share a background: they
  alternate warm and cool, light and deeper, with a rule at every seam.
- "Get the link by email" is RETIRED (2026-09-24). It emailed a visitor the App
  Store link, for the phones the ads brought to an iPad-only app; with the
  iPhone app every Apple device installs from the badge. `#get-the-link` is an
  alias for the hero, the privacy page no longer describes the form, and
  posty's `ipad-link` edge function has no caller once this ships.
- `assets/origin-writing.webp`: the "How it began" photo, Patrick's daughter
  writing a letter. Framed below the chin, written names blurred; the recipe and
  boxes are in posty's `_local/marketing/carousel/` (README, "Website 'How it
  began' photo"). Any photo of a child here follows the same rules. Patrick
  approved reusing it (2026-09-23) in the Why I Built Postmello essay and, as a
  2:1 band of the hand and the page, on that essay's blog card
  (`assets/blog/why-i-built-postmello-card.webp`).
- `assets/site.js`: the film, the collections rail's arrows, header behavior, mobile
  navigation, old anchor aliases, anonymous page events.
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
  Never caption or describe a picture of a child writing as being at lunch or at
  the lunch table (Patrick, 2026-09-24: a child should not draw at the lunch
  table) — the reel print says "Writing to a friend."; the origin photo's
  description names no meal either.
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
  plan names and counts, including founding-window copy. A desk count in prose
  is a `data-desk-count="<plan>"` span, written out as a word in the case the
  page already uses there ("Two desks, free." / "up to six desks").
- While `iphone-and-pricing` is unmerged, its prices come from posty's
  `pricing-and-onboarding` branch, not from posty's `main`: pass
  `--pricing ~/proj/posty-pricing/pricing.json` (or set `POSTY_PRICING_JSON`).
  The two branches ship together - merge both, then run the script against
  `../posty/pricing.json` as usual.
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
