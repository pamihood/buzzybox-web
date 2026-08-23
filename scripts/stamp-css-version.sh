#!/usr/bin/env bash
# Stamp each stylesheet's content hash into the links that load it.
#
# The host serves CSS with a short max-age, so for a few minutes after a deploy
# a returning visitor gets the NEW html and the OLD css. Any markup that depends
# on a new rule renders unstyled — which is how a centred note shipped looking
# left-aligned and full-width. The hash makes the stylesheet a different URL
# whenever its bytes change, so the two can never disagree.
#
# TWO stylesheets since 2026-08-23: index.html is on home.css and every other
# page is on styles.css. They are hashed independently — a homepage-only change
# must not bust the cache for the legal pages, and vice versa.
#
# Run this after editing either stylesheet, before committing.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root, not scripts/

stamp() {                 # stamp <cssfile> <page>...
  local css="$1"; shift
  local hash; hash=$(md5 -q "$css" | cut -c1-8)
  local base; base=$(basename "$css" .css)
  local n=0
  for f in "$@"; do
    [ -f "$f" ] || continue
    perl -pi -e "s{(href=\"[^\"]*${base}\.css)(\?v=[a-f0-9]+)?\"}{\$1?v=${hash}\"}g" "$f"
    n=$((n+1))
  done
  echo "[css] ${base}.css v=${hash} -> ${n} page(s)"
}

stamp home.css index.html
stamp styles.css support.html privacy.html terms.html safety.html parents.html \
      confirmed.html reset.html 404.html blog/index.html blog/*/index.html
