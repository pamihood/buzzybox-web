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

- **Does the assurance coda survive?** (`.assurance`, bottom of `index.html`).
  It was one run-on sentence; it is now two tiers — "Every contact is approved
  by an admin." as the claim, "No feeds. No ads. No strangers." as a quieter
  second line. That fixes how it *reads*, but not the open question: the coda
  still partly duplicates the `.pitch` section above it, where "away from the
  rush of messaging" already covers no-feeds. The approval line is definitely
  staying — it is the one claim a parent needs that no image can carry, and
  nothing else on the page makes it. The coda is the part to decide on.

## Custom domain

`CNAME` pins the site to `buzzybox.app`. DNS is managed at Namecheap (see the apex A/AAAA records pointing at GitHub Pages).
