# Postmello website

Static marketing + legal site for [Postmello](https://buzzybox.app), the cozy iPad app for handwritten letters.

Served via **GitHub Pages** at the apex domain `buzzybox.app`.

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing page |
| `privacy.html` | Privacy Policy (App Store privacy URL) |
| `support.html` | Help / contact (App Store support URL — filename kept for the store listing, nav reads "Help") |
| `terms.html` | Terms of Use |

## Editing

Plain HTML + one stylesheet (`styles.css`). No build step. Edit and push to `main`; GitHub Pages redeploys automatically.

Artwork in `assets/` is exported from the app project (app icon, splash scene, paper/envelope textures).

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
- **"World" in copy, "collection" in the catalog.** No prices, locks or buy
  controls in the worlds grid; the money is explained in its own section.
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

`CNAME` pins the site to `buzzybox.app`. DNS is managed at Namecheap (see the apex A/AAAA records pointing at GitHub Pages).
