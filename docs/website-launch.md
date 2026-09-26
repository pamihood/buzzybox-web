# Selected Postmello website

The desk-and-letters exploration is the chosen design. It now lives in
`index.html`, `home.css`, and `assets/site/`. Supporting pages use `styles.css`
with the same fonts, palette, navigation, and footer.

## Published 2026-09-15

Apple approved 1.0 (build 95) on 2026-09-15, manual release; App Store Connect
reads the version as Pending Developer Release. Patrick authorized pushing the
site the same day, ahead of the release, to see it on production.
`launch-badge-prototype` was merged into `main` with a merge commit, because
its save commits carry the `[CF-Pages-Skip]` prefix and a fast-forward would
have skipped the production build. The merge commit's own body then quoted
the token while saying so; whether Cloudflare skipped that push is unknown
(its deployment list was not readable), a commit whose message never mentions
the token followed, and the site was live at 16:18 UTC (README, "Hosting").

The App Store link, `https://apps.apple.com/app/id6806487006`, is the
listing's Apple id read from App Store Connect (`brand.json`, applied to both
homepage badges and the private letter viewer's fallback). It returns 404 until
the version is released and then resolves with no change to the site.

## Next push: iPhone (`iphone-and-pricing`)

The branch says "For iPhone and iPad", and since 2026-09-26 it carries the
collections-only pricing (below), as `main` does for iPad. Every claim must be
true the moment it goes live, so the branch is merged into `main` (= deployed)
only when the version carrying the iPhone app is RELEASED — not merely
accepted: the app uses manual release, so press Release first. The pricing
claims need two facts live by then, whichever push comes first: the free desk
count on the hosted server (posty migration `20260926100000`, Patrick's go)
and collections selling in App Store Connect at the site's "from" price, with
no subscription on sale. posty's `check-pricing-sync.py` passes against both
this branch and `main`.

`main` and this branch both rewrote the pricing copy on 2026-09-26, so the
merge conflicts where the two differ: `index.html` and `press.html` say iPhone
here and iPad there. Take this branch's side, then run the maintenance
commands in README.md (including `bash scripts/stamp-css-version.sh`) and
`python3 scripts/check-site.py`, and set `sitemap.xml`'s lastmod for every
page the merge changes. The branch's save commits carry `[CF-Pages-Skip]`, so
bring it in with a merge commit whose message never mentions that token
(README, "Hosting").

Before pushing, check the App Store badge on a real iPhone AND a real iPad.
There is ONE link, `https://apps.apple.com/app/id6806487006` — the listing
itself, with no platform or country in it, so it is not an iPad link. Apple
shows one listing for both devices, and it offers Get on an iPhone only once
the released build supports iPhone: posty's `main` has the iPhone layout
merged but switched off (builds ship iPad-only, 2026-09-24), so today an
iPhone opens the listing and cannot install. After the release: the listing
names iPhone, Get works on both, and nothing on the site changes.

## Archives

- `archive/pre-exploration-website` points to `84270d5`, the full website before
  exploration began. It includes the HTML, styles, scripts, and all assets.
- `archive/website-explorations` preserves every explored design and the final
  selected version immediately before promotion.

The archives are Git tags, not public website routes. To browse the original
without disturbing this checkout, create a detached worktree:

```sh
git worktree add --detach ../postmello-original archive/pre-exploration-website
```

Exploration files and review links were removed from the active site. Old shared
homepage anchors continue to resolve through aliases in `assets/site.js`.

## Before launch

1. Confirm Apple approval and update/verify the App Store link.
2. Run the maintenance commands in README.md and `python3 scripts/check-site.py`.
3. Review the homepage, desk choices, mobile navigation, pricing, FAQs,
   supporting pages, and account landing states locally.
4. Merge and deploy only after authorization.

## Collections-only pricing - 2026-09-26

Patrick dropped Membership for launch (posty `pricing.json` 2026-09-26a):
desks, friends, letters, replies and history are free, up to the free plan's
desk count, and collections are the only thing sold - bought once, yours to
keep. Both `main` (iPad) and `iphone-and-pricing` (iPhone and iPad) say so:
the hero, one free card, the collection price, the promise, the FAQ, the
press kit and the terms (only their now-false sentences changed). No page
shows a Membership, a founding rate or a price per year, and
`scripts/apply-pricing.py` renders only what `pricing.json` has on sale.

Push `main` only once every claim is true: the free desk count live on the
hosted server (posty migration `20260926100000`) and collections selling in
App Store Connect at the site's "from" price, with no subscription on sale.

## Blog integration — 2026-09-09

Patrick accepted the seven focused essays. They are integrated locally with
“tablet” in the prose, alongside new versions of both original articles. The
design article is now titled “A World Built for Childhood” and retains its
existing URL. The blog index lists the two overview articles ahead of the
seven closer looks, as one list; the overview links to all seven. Since
2026-09-15 (Patrick) the index has no intro line, no index-level byline and no
group headings, and the navigation label for it reads "Blog".

The why article combines the selected homepage's motivations with Patrick's
original summer/travel experiences: independent friendships before a smartphone,
creation, a personal space, optional immediacy, and room for older writers and
adults. “Roughly a hundred builds” follows Patrick's supplied scale, not a claim
that a particular build shipped. The audience research used Wait Until 8th's
official FAQ (https://www.waituntil8th.org/faqs), which distinguishes delaying a
smartphone from preventing communication. No endorsement or affiliation is implied.

The prose and blog inventory are maintained in `blog/`; run the renderer after
shared-page maintenance, as documented in README.md. Five articles have selected
existing imagery. Identity, reply-audience and the historical transition captures
remain possible enhancements; no placeholder or review-only image is published.
App/runtime asset provenance: `assets/blog/bee-at-home.png` comes from the bundled
bee-skep asset in posty; `space-with-a-view.jpg` comes from the established Baan Na
desk background, not the unpublished Ricefield Hut preview. Both are unchanged.

Patrick explicitly deferred pushing until App Store submission success. There
was no push, merge to main, hosting change, or automatic future deployment set up.

Validation: brand/pricing checks passed; the renderer's check confirms nine
articles and their index match the sources; site checks passed across 20 pages.
All nine article routes returned 200 locally. Metadata, sitemap coverage, all
seven overview links, accepted-source parity and tablet wording were checked.

Patrick subsequently approved **Why I Built Postmello**; the only subsequent
changes to its prose correct the founder's account: the older daughter's request
started Postmello, and both daughters used it and helped shape it. The homepage
origin and design overview now use that distinction too.
The design article is the overarching essay most readers should read.
Patrick's latest direction is to explain the overarching design of the app made
for children, grounded in the selected website copy, in simple and direct language.
The overview now leads with imagination, friendship and independence. Five short
sections explain the desk as the interface, whole worlds for expression, the bee,
real friendships and quiet. Technical mechanisms and the abstract argument about
power and responsibility are left out of the publication copy. The essay
links to all seven focused posts. Ann's existing homepage quote is reused
verbatim; the image is the unchanged homepage desk artwork (`assets/site/desk.webp`),
which includes a painted letter. No new testimonial, anecdote or outcome is invented.
Implementation research remains in the app repository's `docs/BLOG_SERIES_PLAN.md`.
Title, deck, description, image placement, index and related links were updated
together. Patrick approved the final design revision on 2026-09-09, completing
approval of all nine articles. Preserve the accepted prose. The earlier tablet
substitution's three “an tablet” errors were also corrected in the focused essays
and their source mirrors; no other changes were made to their approved prose.

The latest design revision preserves that structure and expands the quiet section
at Patrick's request. It introduces concentration, time to answer and freedom to
leave before the feature examples. The postal ritual provides time to prepare
something for a friend and a clear finish to the writer's turn; delivery remains
quick, while the next reply happens in its own time.
This approved version includes the daughter corrections.

On 2026-09-10, Patrick explicitly authorized committing and pushing the approved
website work, with no deployment. Save on `launch-badge-prototype` with the
`[CF-Pages-Skip]` commit prefix to suppress Cloudflare preview deployment.
GitHub Pages only runs on pushes to `main` or manual dispatch. Do not merge to
`main`, dispatch a workflow, or deploy; publication still requires authorization.
