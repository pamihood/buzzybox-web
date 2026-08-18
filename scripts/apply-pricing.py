#!/usr/bin/env python3
"""Write the plans-block prices in index.html from the app repo's pricing.json.

pricing.json is THE ground truth for every Postmello price (adopted 2026-08-17
with the Family subscription revision); this script is how the website obeys
it. Edit the JSON first, then run this — never hand-edit a number in
index.html. Each rewritable line carries a data-price marker, so the
replacement is exact and idempotent:

    <p class="plan-price" data-price="family">$19.99/year</p>

Keys: free, family, family_plus, collections, founding-note (the whole
founding sentence, since its price is part of it).

Usage:
    python3 scripts/apply-pricing.py            # rewrite index.html in place
    python3 scripts/apply-pricing.py --check    # exit 1 if HTML disagrees; write nothing

pricing.json is found at ../posty/pricing.json by default; override with
--pricing PATH or the POSTY_PRICING_JSON environment variable (flag wins).
"""
import argparse
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root, not scripts/
DEFAULT_PRICING = ROOT.parent / "posty" / "pricing.json"
INDEX = ROOT / "index.html"


def money(amount):
    return f"${amount:.2f}"


def normalize(text):
    """Collapse whitespace so a hand-wrapped HTML line still counts as equal."""
    return " ".join(text.split())


def selling_price(pricing, plan):
    """What a subscriber PAYS today: the founding launch price while the
    window is open (2026-08-17: everyone subscribes; the founding benefit is
    this price, preserved for existing subscribers when the ASC price later
    rises), the regular price after."""
    if pricing["founding_window"]["active"] and "founding_price_per_year" in plan:
        return plan["founding_price_per_year"]
    return plan["price_per_year"]


def expected_lines(pricing):
    plans = pricing["plans"]
    return {
        "free": "Free",
        "family": f"{money(selling_price(pricing, plans['family']))}/year",
        "family_plus": f"{money(selling_price(pricing, plans['family_plus']))}/year",
        "collections": f"From {money(pricing['collections']['price_from'])}",
        "founding-note": (
            f"Founding price: {money(plans['family']['founding_price_per_year'])}/year "
            f"for households that join while Postmello is new — yours to keep "
            f"for as long as you stay subscribed. Later, Family is "
            f"{money(plans['family']['price_per_year'])}/year."
        ),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Sync index.html's plans-block prices with pricing.json.")
    ap.add_argument("--pricing", help="path to pricing.json "
                    "(default: $POSTY_PRICING_JSON, then ../posty/pricing.json)")
    ap.add_argument("--check", action="store_true",
                    help="report disagreements and exit 1; write nothing")
    args = ap.parse_args()

    pricing_path = pathlib.Path(
        args.pricing or os.environ.get("POSTY_PRICING_JSON") or DEFAULT_PRICING)
    pricing = json.loads(pricing_path.read_text(encoding="utf-8"))

    # The founding sentence may only be on the page while the window is open.
    # This script writes prices; taking the line OFF is a layout decision made
    # by hand — so refuse loudly instead of quietly leaving a stale offer up.
    if not pricing.get("founding_window", {}).get("active"):
        raise SystemExit(
            "!! founding_window is closed in pricing.json — remove the "
            "founding-note line from index.html by hand (and its data-price "
            "key here), then rerun.")

    html = INDEX.read_text(encoding="utf-8")
    disagreements = []
    for key, want in expected_lines(pricing).items():
        pat = re.compile(
            r'(<p class="[^"]+" data-price="' + re.escape(key) + r'">)'
            r"(.*?)(</p>)", re.S)
        m = pat.search(html)
        if not m:
            raise SystemExit(
                f'!! index.html: no data-price="{key}" line to rewrite')
        have = normalize(m.group(2))
        if have == normalize(want):
            continue
        disagreements.append((key, have, want))
        html = (html[: m.start(2)] + want + html[m.end(2):])

    if args.check:
        if disagreements:
            print(f"!! index.html disagrees with {pricing_path}:")
            for key, have, want in disagreements:
                print(f'   data-price="{key}"')
                print(f"     - {have}")
                print(f"     + {want}")
            sys.exit(1)
        print(f"[pricing] index.html agrees with {pricing_path}")
        return

    if disagreements:
        INDEX.write_text(html, encoding="utf-8")
        for key, _have, want in disagreements:
            print(f"[pricing] {key} -> {want}")
    else:
        print("[pricing] index.html already agrees; nothing written")


if __name__ == "__main__":
    main()
