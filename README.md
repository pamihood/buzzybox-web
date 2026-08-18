# Postmello website

Static marketing + legal site for [Postmello](https://postmello.com), the cozy iPad app for handwritten letters.

Served via **GitHub Pages** at the apex domain `postmello.com`.

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
| `404.html` | Not-found page. **Root-absolute links only** — GitHub Pages serves it at any depth, so `assets/…` would resolve against the missing path and the page would arrive unstyled |
| `sitemap.xml`, `robots.txt` | Hand-maintained. Add the entry in the same commit that adds a page. `/letter/` is excluded from both: it is mail |

## Editing

Plain HTML + one stylesheet (`styles.css`). No build step. Edit and push to `main`; GitHub Pages redeploys automatically.

**Contact address: `support@postmello.com`** — Help, Privacy, Terms, Safety, 404
and every footer. Nothing on the site should carry a personal address.

**The footer is one block, repeated.** `scripts/apply-footer.py` rewrites the
`<footer>` on every page from a single template with per-page path prefixes; run
it rather than hand-editing nine copies, which is how Help and Privacy drifted
apart before.

**Prices are written, not typed.** `scripts/apply-pricing.py` rewrites the
plans-block price lines in `index.html` (keyed on their `data-price` markers)
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

`CNAME` pins the site to `postmello.com`, whose DNS is on **Cloudflare** (apex
A/AAAA plus a `www` CNAME, all DNS-only so GitHub issues the certificate).

`buzzybox.app` is the old home and now **404s**. GitHub Pages serves exactly one
custom domain and does not redirect the others — its DNS is still at Namecheap
pointing here, which is why it errors rather than failing to resolve. Nothing
depends on it; keep renewing it anyway so redirecting stays an option.
