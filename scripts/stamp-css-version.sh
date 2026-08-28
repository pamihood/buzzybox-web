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

# A stylesheet that does not PARSE still stamps fine, and the page then loads a
# sheet the browser silently drops rules from. That happened on 2026-08-27: an
# edit added prose after a comment's closing */ and before the rule it
# explained, so `.stationery-panels` was dropped and the box it sizes went on
# measuring itself against the wrong element. Nothing errored; the page just
# looked slightly wrong.
#
# Unbalanced /* */ and unbalanced braces are the two cheap tells, and both are
# exactly what a comment-heavy stylesheet gets wrong. Checked before stamping,
# because stamping a broken sheet is how it reaches the browser.
check_syntax() {
  local css="$1"
  local opens closes braces_o braces_c
  opens=$(grep -o '/\*' "$css" | wc -l | tr -d ' ')
  closes=$(grep -o '\*/' "$css" | wc -l | tr -d ' ')
  braces_o=$(grep -o '{' "$css" | wc -l | tr -d ' ')
  braces_c=$(grep -o '}' "$css" | wc -l | tr -d ' ')
  if [ "$opens" != "$closes" ]; then
    echo "!! $css: $opens '/*' against $closes '*/' - a comment is unbalanced," >&2
    echo "   which drops every rule until the parser recovers." >&2
    exit 1
  fi
  if [ "$braces_o" != "$braces_c" ]; then
    echo "!! $css: $braces_o '{' against $braces_c '}'" >&2
    exit 1
  fi
}

check_syntax home.css
check_syntax styles.css

stamp home.css index.html
stamp styles.css support.html privacy.html terms.html safety.html parents.html \
      confirmed.html reset.html 404.html blog/index.html blog/*/index.html
