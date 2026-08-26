# Postmello website

Static marketing + legal site for [Postmello](https://postmello.com), the cozy
app for handwritten letters.

**This README is the operating manual for the repo, not a strategy document.**
It exists because several pages here are *rewritten by scripts*, and a person
who edits the HTML without knowing that will have their work silently reverted
the next time someone runs one. (That is not hypothetical — it happened on
2026-08-25.) Everything below is either a mechanism you need to know before
editing, or a copy rule that is easy to break by accident.

Two standing rules about the README itself:

- **Never restate a number here.** Prices, plan limits and desk counts live in
  `../posty/pricing.json` and are written into the page by a script. Earlier
  versions of this file quoted figures, and every one of them went stale.
  Describe the mechanism; let the script own the value.
- It is **not served** — `_redirects` returns 404 for `/README.md`. It is a
  build-time input, like `brand.json`, and the repo is deployed wholesale.

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing page. On its own stylesheet — see **Two stylesheets** |
| `blog/index.html` | Blog index |
| `blog/<slug>/index.html` | One post per directory, so the URL is `/blog/<slug>/` with no server config |
| `safety.html` | Safety by design — how the product protects children, in plain English |
| `privacy.html` | Privacy Policy (App Store privacy URL) |
| `parents.html` | The under-13 consent explainer an adult is sent to |
| `support.html` | Help / contact (App Store support URL — filename kept for the store listing, nav reads "Help") |
| `terms.html` | Terms of Use |
| `confirmed.html` | Where an email-confirmation link lands. Root-absolute links only |
| `reset.html` | Where a password-reset link lands. Root-absolute links only |
| `letter/index.html` | The private page an email-lane friend reads a letter on. `noindex, nofollow`, `no-referrer`, robots-disallowed, kept out of the sitemap — **it is mail, not a page** |
| `404.html` | Not-found page. **Root-absolute links only** — the host serves it at any depth, so `assets/…` would resolve against the missing path and the page would arrive unstyled |
| `sitemap.xml`, `robots.txt` | Hand-maintained. Add the entry in the same commit that adds a page |
| `_headers`, `_redirects` | Cloudflare Pages config: security headers, long-cache for the two stylesheets, and 404s for the build-time files |

## Editing

Plain HTML, no build step. Edit and push to `main`; Cloudflare Pages redeploys
automatically.

**Two stylesheets since 2026-08-23.** `index.html` is on **`home.css`**; every
other page is on **`styles.css`**. They are independent on purpose: a homepage
change must not restyle the legal pages. Both now draw from the same type
system (see **Typography**), but they are still separate files with separate
component rules, and three scripts know about the split —
`apply-footer.py` does not touch `index.html` (the homepage has its own
three-column footer), `apply-head-meta.py` skips it for FONTS but still writes
its canonical and og tags, and `stamp-css-version.sh` hashes the two sheets
separately.

The homepage also carries ~150 lines of inline vanilla JS for the desk picker,
the stationery tabs, the FAQ accordion and filter, the mobile menu, and the
beta form. It is progressive: with the script blocked the page still reads top
to bottom.

## The four things a script owns

Run the script; never hand-edit its output. Three of them take `--check`, which
exits nonzero when the HTML disagrees — cheap to run before a commit.

**The footer is one block, repeated.** `scripts/apply-footer.py` rewrites the
`<footer>` on the eight non-homepage pages from one template, which is how Help
and Privacy stopped drifting apart. **Read this before running it:** the
template is the source of truth, so any footer improvement made by hand in a
page will be *destroyed* the next time the script runs. If you improve a
footer, improve `FOOTER` in the script. Three pages (`parents`, `confirmed`,
`reset`) are deliberately outside its `PAGES` map because they carry their own
variants; they must be updated by hand.

**The tagline is written, not typed.** It appears three times — header, hero
headline, footer — so it lives in `brand.json` and `scripts/apply-brand.py`
writes it into every element marked `data-brand="tagline"`. Same for the beta
CTA (`beta_cta`), which changes the day the beta ends. Edit the JSON, run the
script.

**Prices are written, not typed.** `scripts/apply-pricing.py` rewrites the
plan-card figures, names and desk counts in `index.html` (keyed on their
`data-price` / `data-plan-name` / `data-plan-desks` markers) from the app
repo's `../posty/pricing.json`, **the single ground truth for every Postmello
number**. A price change starts in that JSON. The plan limits are served from
`account_capabilities` and are meant to be retunable without a client release,
so the JSON is what you reconcile against — never a figure remembered from a
page.

**Head meta.** `scripts/apply-head-meta.py` owns the Google Fonts `<link>`, and
writes `canonical`, `og:url` and `og:image` on every page. Those three are
**absolute** everywhere: a scraper has no base to resolve a relative one
against, and a shared link once unfurled with no picture at all.

Two more, run by hand when their inputs change:

- `scripts/stamp-css-version.sh` appends `?v=<md5>` to every stylesheet link.
  The host serves CSS with a short max-age; `_headers` now sets a long
  immutable cache on the two sheets, which is safe *only because* this stamp
  changes the URL when the file changes. Run it after any CSS edit.
- `scripts/make-og-card.py` shoots `scripts/og-card.html` — a real page in the
  site's own fonts and tokens — in headless Chrome at 2x and downsamples to
  `assets/og-card.jpg` (1200×630). Rerun after any change to the H1, the hero
  capture, or the type system.

## Addresses

**Two addresses, on purpose** (settled 2026-08-25). Both are live mailboxes.

- **`hello@postmello.com` — the front door.** The homepage's "write to the
  creators directly", the private-beta ask, and the beta form's error message.
  It is the brand's voice: a person answers, and the page says so.
- **`support@postmello.com` — help and the record.** Help, Privacy, Terms,
  Safety, 404, every shared footer, and both App Store listing URLs. Anywhere
  someone needs an address because something must be *handled* rather than
  chatted about, including legal and reporting routes.

Nothing on the site should carry a personal address. The earlier rule that
support@ went everywhere is retired — it was written before the beta form
existed.

## Typography

**Lora is the voice. Plus Jakarta Sans is the interface. Courier Prime is the
apparatus.** All three load from Google Fonts (`apply-head-meta.py` owns the
`<link>`), and every stack keeps a system fallback so a blocked CDN degrades to
something reasonable rather than to Times New Roman. Both stylesheets request
the same three families, under different token names — `--font-serif` /
`--font-sans` / `--font-mono` in `home.css`, `--font-serif` / `--font-voice` /
`--font-apparatus` in `styles.css`.

**The wordmark is artwork, not type** (`assets/wordmark.png`). It used to be
Rubik 600, and `styles.css` still carries the tombstone comment explaining why
`--font-mark` is gone rather than remapped. Do not reintroduce a font for it:
the footer rule styles `.signoff-name` as an image, and a `<span>` cannot be
stretched the way the image is.

Sizes and weights live in the `--fs-*` tokens and the component rules; the
governing rule is that **the page is quiet because of whitespace, never because
the text is small or faint.** No accent colour is introduced anywhere beyond
the terracotta: the desks, stamps and stickers supply all the colour, and
everything else is warm paper and dark ink.

## Artwork

Artwork in `assets/` is exported from the app project (app icon, splash scene,
paper/envelope textures). Every PNG goes through
`pngquant --quality 60-88 --speed 1 --strip`, which is the difference between a
2MB block and a 600KB one.

**`assets/stationery/fairy-glen/` is one whole shipped pack, not a selection.**
The spread under the desk grid shows every active piece of the Fairy Glen
collection — nine papers, six envelopes, six stamps, ten stickers — and the
sentence beneath it counts them, so the folder and that sentence have to change
together. Sources are the app repo's `samples/collections/fairy_glen/`
(landscape papers only); the catalog is the authority on what is in the pack:

```sql
select s.type, s.name from stationery s
  join stationery_packs p on p.id = s.pack_id and p.type = s.type
 where p.collection_id = 'col_fairy_glen' and s.is_active order by 1, 2;
```

Sizes are chosen from the on-page display size at 2×: papers 560px JPEG q78,
envelopes 480px, stamps and stickers 180px.

**Blog posts keep their markdown source.** `blog/<slug>/index.md` is the prose
as written; `index.html` is the rendering of it. Edit the `.md` and bring the
change across — they are not generated from each other, so they can drift, and
the `.md` is the one a human wrote. `blog/why-i-built-postmello/index.md` is
Patrick's, verbatim; the HTML was diffed against it word by word.

Posts carry a **deck** (the article's own subtitle) and, where there is one, a
byline. Standalone bolded lines in the source become `<p class="post-beat">` —
a beat in the argument, not a heading.

## Copy rules

The landing page used to have a spec in the app repo (`docs/WEBSITE_SPEC.md`,
retired 2026-08-24). **The pages themselves are the copy source now**, and
these are the rules that are easiest to break by accident:

- **Kids, family and friends, household, approved friends.** Never "parents",
  "grown-ups" or "guardians" as generic labels in marketing copy — approval is
  stated in the passive ("Only approved email addresses can reply"). The legal
  pages are exempt; they say "parent or guardian" because that is the wording
  the law uses.
- **Friends, not contacts** (renamed in the app 2026-08-24). A person is a
  *friend*; "by email" describes a **lane**, never a noun — write "a friend
  reached by email", never "an email contact". The formal register of the
  legal pages may keep bare "approved contacts"; the plain-English pages may
  not.
- **The email lane goes BOTH ways** (since 2026-08-20). A friend reached by
  email receives letters as an email plus a private page, *and* their replies
  come back to the desk as typewritten letters. Never describe it as one-way.
- **The plans block names nobody, and counts instead** (2026-08-17). A desk
  owner can be a kid, a grandparent or a pen pal, so "a desk for your kid"
  shrank the product on the one screen where a visitor is deciding what it
  costs. The columns are a desk ladder, and collections span the row beneath
  them, because they apply on any plan rather than being another rung. Always
  "up to", never a bare figure and never "every".
- **The plans block may look like a plan view; it may not act like a shop.**
  Borrowed on purpose (2026-08-17): an aligned column ladder, one emphasised
  column, a `START HERE` tag on the free one, and prices. Still refused: buy
  buttons, ticks, shadows, and colour used as tier coding. Colour runs on one
  axis only — **free is the only block with chroma**; the paid tiers differ by
  a step of value, never of hue. The rule that outranks the rest here is that
  the free column must never lose the row.
- **Collections are sold to everyone** (2026-08-24). Every tier can buy them;
  members pay less. There is no "included collections" benefit any more. The
  figures come from the script — see above.
- **Nothing is sold to the child.** On the desk there are no prices, locks,
  countdowns, currencies or limited-time offers. A child *chooses*; the choice
  opens an adult's PIN gate, which is the only place a price appears; a
  declined choice leaves no trace to return to. The old "make a wish" mechanic
  was retired in the app on 2026-08-24 and is gone from this site — do not
  reintroduce it, and never write "ask a grown-up to buy this" (EU/UK pester
  power).
- **Postmello is not "an iPad app".** It is *coming first to iPad*.
- **"Collection" is the public noun, matching the app.** Capitalised as a
  product noun mid-sentence.
- **"One letter at a time." is the footer sign-off, not the H1.**

## TODO

- **Re-cast the friends in every screenshot** (Patrick, 2026-08-16; halved
  2026-08-17). The drawer cast is currently Iris, Theo, Grandma, Grandpa and
  Nana — five friends, four of them relatives. One change is left:
  **"Luna" replaces "Grandpa."** Four relatives and one friend under a heading
  about friends and family undersells the friend half, and Postmello is a
  pen-pal product before it is a family one. Keeping Grandma covers the
  relatives. So the row becomes **Iris, Theo, Luna, Grandma, Nana** —
  friend-forward, five drawers, no layout change. Touches
  `assets/drawer-grandpa.png` → `drawer-luna.png`, `assets/drawer-row.jpg`, and
  every screenshot with the drawer rail in it: `assets/app-desk.jpg` (hero),
  `assets/step-stamp.jpg`, and `assets/og-card.jpg` once the hero is re-shot.
  The alt strings that name the cast must change in the same commit. The seed
  that populates the rail is `marketing-desk-seed.sh` in the app repo; capture
  recipe and cast rules live in the app repo at `docs/MARKETING_SHOT.md`, which
  is where the canonical cast list should be updated too. Do it in the same
  pass as the step-panel re-shoot below — both need the same seeded device.

- **Re-shoot the three step panels before launch** (`assets/step-*.jpg`).
  The current set is good enough to iterate on and not good enough to ship:

  - **`step-writing.jpg` — the handwriting is fake, and the page is blank.**
    Those strokes were drawn by `idb ui swipe`, and every swipe is a straight
    segment, so each "word" is a polyline. Needs a letter actually written by
    hand — trackpad on the simulator, or Pencil on a device.
  - **The desks are under-dressed.** In the paper picker and the canvas the
    desk behind the content is nearly bare. A shipped shot should look lived
    in: mail in the mailbox, a draft or two on the surface, stickers placed on
    the letter. `marketing-desk-seed.sh` populates the drawer rail but not the
    desk surface.
  - The letter in `step-writing.jpg` has no stickers on it, which undersells
    the sticker packs entirely.

  The alt text on all three panels now describes what is actually in the
  frame, so **re-shooting means rewriting those three alt strings too.**
  Capture recipe, cast, device and aspect rules are in the app repo at
  `docs/MARKETING_SHOT.md`. Keep all three panels on one device — the 11-inch
  is 1.44 and the 13-inch is 4:3, and mixing them staggers the row — and trim
  the bottom 32px, which is where iOS draws the home indicator.

- **The Quiet Post Journal — parked, not dropped** (Patrick, 2026-08-23). The
  footer's third column shipped as a newsletter card for a parent-facing
  dispatch on "screen sanity, handwriting & literacy, and the art of slow
  correspondence". It came out because there was no list to post to and no
  endpoint to receive an address, and a signup box that accepts an email and
  quietly discards it is the one thing that must never happen. The slot is now
  the private-beta ask. To bring it back, in order: pick where addresses land,
  then restore the card — a `<form>` with a labelled email input and a Join
  button, all of which is in the git history at `86fb473^`. Two rules it has
  to keep: an accessible label for the input, and no claim about frequency the
  sending side cannot honour. (The `beta-request` function is now a working
  model for the receiving half.) The "Crafted for iPadOS · Calm Tech" foot row
  does NOT come back with it — it was a stray footnote carrying the for-iPad
  framing the positioning rule already refuses.

**Closed since the last revision of this file:** the beta-request backend is
deployed and verified end to end (Turnstile, row, notification email — first
real submission 2026-08-26); Cloudflare Turnstile shipped on the form, so the
"honeypot now, Turnstile if needed" item is done; and the six desks in the grid
are six distinct captures (`73d3246`).

## Hosting

The site is served by **Cloudflare Pages** — project `postmello-web`, connected
to this repo, deploying on push to `main`. `postmello.com` and `www` are both
proxied CNAMEs to `postmello-web.pages.dev`, and Cloudflare issues the
certificate.

**A GitHub Pages workflow (`.github/workflows/pages.yml`) still runs on the
same push, and that is deliberate.** It keeps a current standby copy and holds
the custom-domain claim on GitHub — which is precisely the thing whose absence
let a stranger take `buzzybox.app`. `pamihood.github.io/buzzybox-web/`
redirects to `postmello.com`, so there is no duplicate content. The `CNAME`
file and `.nojekyll` belong to that standby. **Do not delete any one of the
three on its own** — removing the workflow while keeping `CNAME` leaves a
stale standby, which is the worst of both.

Cloudflare Pages 308-redirects `/x.html` to `/x`. Both forms resolve and the
content is identical; `sitemap.xml`, the `canonical`/`og:url` tags, and the
site's own internal links all name the extensionless form, so nothing
advertises a URL the server redirects. Old `.html` links keep working — the App
Store privacy and support URLs among them.

`buzzybox.app` is the old home and no longer resolves at all. Its DNS was left
at Namecheap pointing at GitHub Pages after the site moved, and because GitHub
had released the hostname, a stranger claimed it and served their own site from
our domain (2026-08-20). The A records and the `www` CNAME were deleted the
same day. The Resend TXT and MX records were deliberately kept: they are the
idle email rollback lane, and unlike a hostname they cannot be claimed by
anyone else. Keep renewing the domain — letting it lapse hands the name away
for good — and know that redirecting it needs a Redirect Rule at a host that
can serve two domains, which is a thing DNS alone never did.
