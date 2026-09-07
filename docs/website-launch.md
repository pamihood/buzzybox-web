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
