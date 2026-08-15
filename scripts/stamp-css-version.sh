#!/usr/bin/env bash
# Stamp styles.css's content hash into every stylesheet link.
#
# GitHub Pages serves styles.css with cache-control: max-age=600, so for ten
# minutes after a deploy a returning visitor gets the NEW html and the OLD css.
# Any markup that depends on a new rule renders unstyled — which is how a
# centred note shipped looking left-aligned and full-width. The hash makes the
# stylesheet a different URL whenever its bytes change, so the two can never
# disagree. Run this after editing styles.css, before committing.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root, not scripts/
HASH=$(md5 -q styles.css | cut -c1-8)
for f in index.html support.html privacy.html terms.html safety.html 404.html blog/index.html blog/*/index.html; do
  [ -f "$f" ] || continue
  perl -pi -e "s{(href=\"[^\"]*styles\.css)(\?v=[a-f0-9]+)?\"}{\$1?v=$HASH\"}g" "$f"
done
echo "[css] stamped v=$HASH into $(grep -rl "styles.css?v=$HASH" --include='*.html' . | wc -l | tr -d ' ') pages"
