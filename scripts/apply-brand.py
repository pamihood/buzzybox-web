#!/usr/bin/env python3
"""Write the brand strings in index.html from brand.json.

Same shape as apply-pricing.py, and for the same reason: a string that appears
in more than one place stops being one string the moment somebody edits it in
only one of them. The tagline sat in the header, the hero headline and the
footer, and changing it meant remembering all three.

Each writable element carries a data-brand marker, so the replacement is exact
and idempotent:

    <span class="brand-sub" data-brand="tagline">A quiet place for letters.</span>

A brand string can also be an ADDRESS rather than words. Those carry
data-brand-href and are written into the href instead of the element body:

    <a class="appstore-badge" data-brand-href="app_store_url" href="...">

That second form arrived with the App Store badge (2026-09-03). The badge is
Apple artwork that may not be relettered, so the thing that repeats across the
four call-to-action sites is no longer a LABEL but a LINK - and a link typed
four times drifts exactly the way the tagline did. A key may use either form or
both; it fails only when neither marker exists anywhere.

Keys: tagline, app_store_url. (beta_cta was the third until the private beta
ended - see the note in brand.json.) Anything in brand.json whose name starts
with an underscore is a note for a human and is skipped.

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
        # The href form. Note the marker is data-brand-HREF, which the pattern
        # above cannot match: it requires the quote immediately after
        # data-brand, so the two markers never collide on one key name.
        href_pattern = re.compile(
            r'(<(?:' + TAGS + r')\b[^>]*data-brand-href="' + re.escape(key)
            + r'"[^>]*\bhref=")([^"]*)(")')
        href_found = list(href_pattern.finditer(html))
        if not found and not href_found:
            raise SystemExit(
                f'!! index.html: no data-brand="{key}" or '
                f'data-brand-href="{key}" element to write')
        # Rewrite every occurrence — the whole point is that there are several
        # and they must not drift. Walk backwards so earlier spans keep their
        # offsets as later ones are replaced. Both marker kinds are collected
        # first and replaced in one descending pass, because they are offsets
        # into the SAME string and interleave in document order.
        for match in sorted(found + href_found,
                            key=lambda m: m.start(2), reverse=True):
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
            n = (html.count('data-brand="' + key + '"')
                 + html.count('data-brand-href="' + key + '"'))
            parts.append("%s x%d" % (key, n))
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
