# Buzzybox website

Static marketing + legal site for [Buzzybox](https://buzzybox.app), the cozy iPad app for handwritten letters.

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
