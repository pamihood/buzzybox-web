# Selected Postmello website

The desk-and-letters exploration is the chosen design. It now lives in
`index.html`, `home.css`, and `assets/site/`. Supporting pages use `styles.css`
with the same fonts, palette, navigation, and footer.

## Publishing is on hold

Apple review is pending. The iPad download link must be confirmed after approval.
Update `brand.json` (`app_store_url`), run `python3 scripts/apply-brand.py`, and
verify the destination before publishing. The private letter viewer may receive
a `get_app_url` from the service; confirm that value alongside its local fallback.

This work is saved on `launch-badge-prototype`, not merged to `main`. The save
commit begins with `[CF-Pages-Skip]` to skip Cloudflare preview deployment.
Cloudflare and the GitHub Pages standby deploy on pushes to `main`; do not merge,
trigger a manual workflow, or deploy until launch is authorized.

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
3. Review the homepage, desk choices, mobile navigation, Membership Plus, FAQs,
   supporting pages, and account landing states locally.
4. Merge and deploy only after authorization.

## Blog integration — 2026-09-09

Patrick accepted the seven focused essays. They are integrated locally with
“tablet” in the prose, alongside new versions of both original articles. The
design article is now titled “A World Built for Childhood” and retains its
existing URL. The blog index groups the two overview articles ahead of the
seven closer looks; the overview links to all seven.

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
verbatim; the image is the unchanged homepage desk artwork (`assets/site/desk.png`),
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
