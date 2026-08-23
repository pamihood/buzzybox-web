#!/usr/bin/env python3
"""Write the brand strings in index.html from brand.json.

Same shape as apply-pricing.py, and for the same reason: a string that appears
in more than one place stops being one string the moment somebody edits it in
only one of them. The tagline sat in the header, the hero headline and the
footer, and changing it meant remembering all three.

Each writable element carries a data-brand marker, so the replacement is exact
and idempotent:

    <span class="brand-sub" data-brand="tagline">A quiet place for letters.</span>

Keys: tagline, beta_cta. Anything in brand.json whose name starts with an
underscore is a note for a human and is skipped.

Usage:
    python3 scripts/apply-brand.py            # rewrite index.html in place
    python3 scripts/apply-brand.py --check    # exit 1 if the HTML disagrees
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand.json"
INDEX = ROOT / "index.html"

# The tags a brand string is allowed to live in. Narrow on purpose: a marker
# on something unexpected is a mistake worth failing on rather than rewriting.
TAGS = "span|p|h1|h2|a|button"


def normalize(text):
    """Collapse whitespace, so a hand-wrapped line still counts as equal."""
    return " ".join(text.split())


def main():
    ap = argparse.ArgumentParser(
        description="Sync index.html's brand strings with brand.json.")
    ap.add_argument("--check", action="store_true",
                    help="report disagreements and exit 1; write nothing")
    args = ap.parse_args()

    brand = json.loads(BRAND.read_text(encoding="utf-8"))
    expected = {k: v for k, v in brand.items() if not k.startswith("_")}

    html = INDEX.read_text(encoding="utf-8")
    disagreements = []
    written = 0

    for key, want in expected.items():
        pattern = re.compile(
            r'(<(?:' + TAGS + r')\b[^>]*data-brand="' + re.escape(key) + r'"[^>]*>)'
            r"(.*?)(</(?:" + TAGS + r")>)", re.S)
        found = list(pattern.finditer(html))
        if not found:
            raise SystemExit(f'!! index.html: no data-brand="{key}" element to write')
        # Rewrite every occurrence — the whole point is that there are several
        # and they must not drift. Walk backwards so earlier spans keep their
        # offsets as later ones are replaced.
        for match in reversed(found):
            have = normalize(match.group(2))
            if have == normalize(want):
                continue
            disagreements.append((key, have, want))
            html = html[: match.start(2)] + want + html[match.end(2):]
            written += 1

    if args.check:
        if disagreements:
            print(f"!! index.html disagrees with {BRAND.name}:")
            for key, have, want in disagreements:
                print(f'   data-brand="{key}"')
                print(f"     - {have}")
                print(f"     + {want}")
            sys.exit(1)
        parts = []
        for key in expected:
            marker = 'data-brand="' + key + '"'
            parts.append("%s x%d" % (key, html.count(marker)))
        print("[brand] index.html agrees with %s  (%s)"
              % (BRAND.name, ", ".join(parts)))
        return

    if disagreements:
        INDEX.write_text(html, encoding="utf-8")
        for key, _have, want in disagreements:
            print(f'[brand] data-brand="{key}" -> {want}')
    else:
        print("[brand] index.html already agrees; nothing written")


if __name__ == "__main__":
    main()
