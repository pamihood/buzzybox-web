# Buzzybox website

Static marketing + legal site for [Buzzybox](https://buzzybox.app), the cozy iPad app for handwritten letters.

Served via **GitHub Pages** at the apex domain `buzzybox.app`.

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing page |
| `privacy.html` | Privacy Policy (App Store privacy URL) |
| `support.html` | Support / contact (App Store support URL) |
| `terms.html` | Terms of Use |

## Editing

Plain HTML + one stylesheet (`styles.css`). No build step. Edit and push to `main`; GitHub Pages redeploys automatically.

Artwork in `assets/` is exported from the app project (app icon, splash scene, paper/envelope textures).

## Custom domain

`CNAME` pins the site to `buzzybox.app`. DNS is managed at Namecheap (see the apex A/AAAA records pointing at GitHub Pages).
