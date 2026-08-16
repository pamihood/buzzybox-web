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
- **Postmello is not "an iPad app".** It is *coming first to iPad*.
- **"Collection" is the public noun, matching the app** (Revision 2 reversed
  the earlier "world" rule). It belongs in the supporting sentence and in the
  business-model column, not in an emotional headline — the collections
  heading names the desk, which is the object in the pictures. No prices,
  locks or buy controls in the desk grid; the money has its own section.
- **"One letter at a time." is the footer sign-off, not the H1.**

## TODO

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
