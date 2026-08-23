# Postmello website

Static marketing + legal site for [Postmello](https://postmello.com), the cozy iPad app for handwritten letters.

Served via **Cloudflare Pages** at the apex domain `postmello.com`.

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing page |
| `blog/index.html` | Blog index |
| `blog/<slug>/index.html` | One post per directory, so the URL is `/blog/<slug>/` with no server config |
| `safety.html` | Safety by design — how the product protects children, in plain English |
| `privacy.html` | Privacy Policy (App Store privacy URL) |
| `support.html` | Help / contact (App Store support URL — filename kept for the store listing, nav reads "Help") |
| `terms.html` | Terms of Use |
| `404.html` | Not-found page. **Root-absolute links only** — the host serves it at any depth, so `assets/…` would resolve against the missing path and the page would arrive unstyled |
| `sitemap.xml`, `robots.txt` | Hand-maintained. Add the entry in the same commit that adds a page. `/letter/` is excluded from both: it is mail |

## Editing

Plain HTML, no build step. Edit and push to `main`; Cloudflare Pages redeploys
automatically.

**TWO stylesheets since 2026-08-23.** `index.html` is on **`home.css`** — a
different design system (Fraunces / Plus Jakarta Sans / Courier Prime on
parchment, terracotta accent) that came in with the homepage redesign. Every
other page is still on **`styles.css`** (Rubik / Nunito / DM Mono). They are
independent on purpose: a homepage change must not restyle the legal pages.
Three scripts know about the split, and it is worth knowing why before editing
them — `apply-footer.py` no longer touches `index.html` (the homepage has its
own footer), `apply-head-meta.py` skips it for FONTS but still writes its
canonical and og tags, and `stamp-css-version.sh` hashes the two sheets
separately.

The homepage also carries ~90 lines of inline vanilla JS for the desk picker,
the stationery tabs, the FAQ accordion and filter, and the mobile menu. It is
progressive: with the script blocked the page still reads top to bottom.

**Contact address: `support@postmello.com`** — Help, Privacy, Terms, Safety, 404
and every footer. Nothing on the site should carry a personal address.

**The footer is one block, repeated.** `scripts/apply-footer.py` rewrites the
`<footer>` on every page from a single template with per-page path prefixes; run
it rather than hand-editing nine copies, which is how Help and Privacy drifted
apart before.

**Prices are written, not typed.** `scripts/apply-pricing.py` rewrites the
plan-card figures, names and desk counts in `index.html` (keyed on their
`data-price` / `data-plan-name` / `data-plan-desks` markers)
from the app repo's `../posty/pricing.json`, the single ground truth for every
Postmello number; `--check` exits nonzero when they disagree. A price change
starts in the JSON, then the script — see the pricing rules below.

**Share card**: `assets/og-card.jpg` (1200×630). `scripts/og-card.html` is the
source — a real page in the site's own fonts and tokens — and
`scripts/make-og-card.py` shoots it in headless Chrome at 2x and downsamples.
Rerun it after any change to the H1, the hero capture, or the type system.
`og:image`, `og:url` and `canonical` are **absolute** on every page (a scraper
has no base to resolve a relative one against, so a shared link unfurled with no
picture at all).

## Typography

**Rubik is the mark. Nunito is the voice. DM Mono is the apparatus.** All three
load from Google Fonts (`scripts/apply-head-meta.py` owns the `<link>`), and
every stack keeps its old system fallback so a blocked CDN degrades to what the
site looked like before rather than to Times New Roman.

- **Rubik 600** — the wordmark only, header and footer sign-off, uppercase,
  `0.025em` tracking, `--ink-mark` (#2C231D). Written `Postmello` in the markup
  and uppercased in CSS, so screen readers and copy-paste get the spoken name.
  Keeping it to those two places is what makes it read as a logo instead of a
  third font. The CDN request asks for `wght@600` — a real Semibold face, not a
  synthesised one — so changing the mark's weight means changing
  `scripts/apply-head-meta.py` **and** `scripts/og-card.html` too.
- **Nunito 450–800** — every heading and every sentence, hero to legal page.
  Display sizes need `letter-spacing: -0.025em`; Nunito goes loose when large.
- **DM Mono 500** — eyebrows, plan names, the badge, footer group labels, the
  blog byline, dates. Never a paragraph. **The face ships 300/400/500 only**, so
  apparatus text is 500 — asking for 600 gets a synthesised bold.

Sizes and weights live in the `--fs-*` tokens and the component rules; the
governing rule is that **the page is quiet because of whitespace, never because
the text is small or faint.** No accent colour is introduced anywhere: the desks,
stamps and stickers supply all the colour, and everything else is warm paper and
dark ink.

Artwork in `assets/` is exported from the app project (app icon, splash scene, paper/envelope textures).

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
envelopes 480px, stamps and stickers 180px. Every PNG goes through
`pngquant --quality 60-88 --speed 1 --strip`, which is the difference between a
2MB block and a 600KB one.

**Blog posts keep their markdown source.** `blog/<slug>/index.md` is the prose
as written; `index.html` is the rendering of it. Edit the `.md` and bring the
change across — they are not generated from each other, so they can drift, and
the `.md` is the one a human wrote. `blog/why-i-built-postmello/index.md` is
Patrick's, verbatim; the HTML was diffed against it word by word.

Posts carry a **deck** (the article's own subtitle) and, where there is one, a
byline. Standalone bolded lines in the source become `<p class="post-beat">` —
a beat in the argument, not a heading.

**The landing page has a spec.** Section order, the exact copy, the audience and
platform wording rules, and the acceptance list live in the app repo at
`docs/WEBSITE_SPEC.md` (applied 2026-08-14). The rules that are easiest to
break by accident:

- **Kids, family and friends, household, approved contacts.** Never "parents",
  "grown-ups" or "guardians" as generic labels in marketing copy — approval is
  stated in the passive ("Every contact is approved before letters can be
  exchanged"). The legal pages are exempt; they say "parent or guardian"
  because that is the wording the law uses.
- **The plans block names nobody, and counts instead** (2026-08-17). A desk
  owner can be a kid, a grandparent or a pen pal, so "a desk for your kid"
  shrank the product on the one screen where a visitor is deciding what it
  costs. The three columns are a desk ladder — **One desk / Up to 6 desks /
  Up to 12 desks** — and collections span the row beneath them, because they
  apply on any plan rather than being a fourth rung. Always "up to", never a
  bare figure and never "every": the counts are server-side
  (`account_capabilities`, starter 1 / family 6 / family_plus 12) and meant to
  be retunable without a client release, so check that table before editing a
  number here.
- **The plans block may look like a plan view; it may not act like a shop.**
  Borrowed on purpose (2026-08-17): an aligned three-column ladder, one
  emphasised column, a `START HERE` tag on the free one, and prices. Still
  refused: buy buttons, ticks, shadows, and colour used as tier coding. Colour
  runs on one axis only — **free is the only block with chroma**; Family and
  Plus differ by a step of value, never of hue. The one rule that outranks the
  rest here is that the free column must never lose the row.
- **Prices come from the app repo, never from this one** (revised 2026-08-17,
  evening — the annual model). `../posty/pricing.json` is the ground truth for
  every number; `scripts/apply-pricing.py` writes it into the plans block and
  `--check` fails when they disagree. Edit the JSON first, then run the script
  — never hand-edit a price in `index.html`. The ladder is annual-only
  ("everyone subscribes"): Family renders `~~$19.99~~ $14.99/year` — the
  struck figure is the **genuine post-founding regular price** (the same
  rule the very first strike stood on: a strike is honest only while the
  struck figure is the genuine later price; pricing.json's `price_per_year`
  is its source, and if that intent ever changes the strike follows in the
  same run of the script). Founding subscribers keep $14.99/year via an ASC
  preserve-price increase — no product involved. Family Plus is
  `$29.99/year` flat (one annual tier total, no `+`, no add-on framing).
  **There is no founding footnote** (Patrick: "that join while Postmello is
  new" made it sound like no one is on it) — the terms line's "Early price,
  yours to keep" carries the promise instead. The **monthly equivalent is
  supporting copy only**, exactly as the strategy spec allows: it lives in
  the terms line ("About $1.25 a month"), computed by the script, and never
  leads — the price line is always the yearly figure. Collections stay
  `From $0.99`, one-time — "from" stays true
  if collections ever tier. "No subscription to write letters" survives the
  pivot on purpose: the subscription only covers extra desks.
- **Postmello is not "an iPad app".** It is *coming first to iPad*.
- **"Collection" is the public noun, matching the app** (Revision 2 reversed
  the earlier "world" rule) — but on the homepage it enters exactly ONCE
  (2026-08-17): at the stationery spread's heading, "Every desk brings its own
  collection.", which states the desk-to-collection relationship beside the
  picture that defines it. Everything from the collections heading through
  the desk grid says DESK — the object in the pictures, the thing a visitor
  picks. Never open a sentence with "each collection" before that heading has
  run. No prices, locks or buy controls in the desk grid; the money has its
  own section.
- **"One letter at a time." is the footer sign-off, not the H1.**

## TODO

- **The Quiet Post Journal — parked, not dropped** (Patrick, 2026-08-23). The
  footer's third column shipped as a newsletter card for a parent-facing
  dispatch on "screen sanity, handwriting & literacy, and the art of slow
  correspondence". It came out because there is no list to post to and no
  endpoint to receive an address, and a signup box that accepts an email and
  quietly discards it is the one thing that must never happen. The slot is now
  the private-beta ask.

  To bring it back, in order: pick where addresses land (a real ESP, or a
  Supabase function writing to a table), then restore the card — a `<form>`
  with a labelled email input and a Join button, all of which is in the git
  history at `86fb473^`. Two rules it has to keep: an accessible label for the
  input, and no claim about frequency the sending side cannot honour. The
  "Crafted for iPadOS · Calm Tech" foot row does NOT come back with it — it was
  a stray footnote and it carried the for-iPad framing the positioning rule
  (§2) already refuses.

- **The beta form needs its backend deployed before it works.** The form is
  built and the page posts to
  `https://jbrxtkedjahpbzrqxeos.supabase.co/functions/v1/beta-request`, but
  nothing answers there yet. Until the app repo deploys `beta-request` and
  applies migration `20260823120000_someone_can_ask_to_be_let_in.sql`, every
  submission shows the error state — which at least names an address to write
  to, but is not a working form. Steps are on the matching item in the app
  repo's `docs/TODO.md`. **Do not announce the beta anywhere until a test
  submission comes back ok.**

- **Spam: honeypot now, Turnstile if needed.** The form carries a hidden
  `company` field that bots fill and humans never see; the function drops
  those and answers 200 so a bot learns nothing. If real spam arrives, the
  site is already behind Cloudflare, so Turnstile is a script tag plus a token
  check above the insert.

- **Re-cast the contacts in every screenshot** (Patrick, 2026-08-16; halved
  2026-08-17). The drawer cast is currently Iris, Theo, Grandma, Grandpa and
  Nana — five contacts, four of them relatives. One change is left:

  - ~~**"Mom" replaces "Nana."**~~ **Dropped 2026-08-17.** Its whole
    justification was the free plan including a desk for the account holder
    ("A desk for your kid — and one for you"), so that a picture somewhere on
    the site showed that person in a drawer. That feature is being reverted
    app-side and the copy is gone, so the re-cast has nothing left to
    illustrate. If the account holder's desk ever ships, reopen this — with
    the constraint that survived: the nameplate must be the answer to "what
    should Maya call you?", never a label like "Admin" or "Parent", which §1
    forbids on this site anyway.
  - **"Luna" replaces "Grandpa."** Four relatives and one friend under a
    heading about friends and family undersells the friend half, and Postmello
    is a pen-pal product before it is a family one. Keeping Grandma covers the
    relatives.

  So the row becomes **Iris, Theo, Luna, Grandma, Nana** — friend-forward,
  five drawers, no layout change. Touches `assets/drawer-grandpa.png` →
  `drawer-luna.png`, `assets/drawer-row.jpg`, and every screenshot with the drawer rail in it:
  `assets/app-desk.jpg` (hero), `assets/step-stamp.jpg`, and `assets/og-card.jpg`
  once the hero is re-shot. **Two alt strings name the cast** and must change
  in the same commit — `index.html` at the step-stamp figure and at
  `drawer-row.jpg`. The seed that populates the rail is
  `marketing-desk-seed.sh` in the app repo; capture recipe and cast rules live
  in the app repo at `docs/MARKETING_SHOT.md`, which is where the canonical
  cast list should be updated too. Do it in the same pass as the step-panel
  re-shoot below — both need the same seeded device.

- **Re-shoot the three step panels before launch** (`assets/step-*.jpg`).
  The current set is good enough to iterate on and not good enough to ship:

  - **`step-writing.jpg` — the handwriting is fake.** Those strokes were drawn
    by `idb ui swipe`, and every swipe is a straight segment, so each "word" is
    a polyline. It passes as a child's hand at 285px and falls apart the moment
    anyone looks closely or the image is shown larger. Needs a letter actually
    written by hand — trackpad on the simulator, or Pencil on a device.
  - **The desks are under-dressed.** In the paper picker and the canvas the
    desk behind the content is nearly bare. A shipped shot should look lived
    in: mail in the mailbox, a draft or two on the surface, stickers placed on
    the letter — closer to how a real desk looks after a week of use than to a
    freshly seeded one. `marketing-desk-seed.sh` populates the drawer rail but
    not the desk surface.
  - The letter in `step-writing.jpg` also has no stickers on it, which
    undersells the sticker packs entirely.

  Capture recipe, cast, device and aspect rules are in the app repo at
  `docs/MARKETING_SHOT.md`. Keep all three panels on one device — the 11-inch
  is 1.44 and the 13-inch is 4:3, and mixing them staggers the row — and trim
  the bottom 32px, which is where iOS draws the home indicator.

- **Two of the six worlds are the same two desks twice.** Only four desk styles
  have ever been captured from the app, so Honey Cottage and Storybook repeat
  in slots 5 and 6. At the old three-across size this passed; at ~580px each it
  does not. Fix is capture time, not a file copy — the concept renders in the
  app repo are not the app, and this site presents captures as captures. Recipe
  and cast in the app repo's `docs/MARKETING_SHOT.md`; tracked in its
  `docs/TODO.md`. Swapping the last two `<figure>`s is the whole integration.

## Custom domain

The site is served by **Cloudflare Pages** — project `postmello-web`, connected
to this repo, deploying on push to `main`. `postmello.com` and `www` are both
proxied CNAMEs to `postmello-web.pages.dev`, and Cloudflare issues the
certificate. The `CNAME` file is a GitHub Pages leftover, kept while that stays
claimed as a one-DNS-change rollback; it does nothing here.

Cloudflare Pages 308-redirects `/x.html` to `/x`. Both forms resolve and the
content is identical; `sitemap.xml` and the `canonical`/`og:url` tags name the
extensionless form to match, so nothing advertises a URL the server redirects.
Old `.html` links keep working — the App Store privacy and support URLs among
them.

`buzzybox.app` is the old home and no longer resolves at all. Its DNS was left
at Namecheap pointing at GitHub Pages after the site moved, and because GitHub
had released the hostname, a stranger claimed it and served their own site from
our domain (2026-08-20). The A records and the `www` CNAME were deleted the same
day. The Resend TXT and MX records were deliberately kept: they are the idle
email rollback lane, and unlike a hostname they cannot be claimed by anyone
else. Keep renewing the domain — letting it lapse hands the name away for good —
and know that redirecting it needs a Redirect Rule at a host that can serve two
domains, which is a thing DNS alone never did.
