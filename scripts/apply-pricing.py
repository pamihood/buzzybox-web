#!/usr/bin/env python3
"""Write the plans-block prices in index.html from the app repo's pricing.json.

pricing.json is THE ground truth for every Postmello price (adopted 2026-08-17
with the Family subscription revision); this script is how the website obeys
it. Edit the JSON first, then run this — never hand-edit a number in
index.html. Each rewritable line carries a data-price marker, so the
replacement is exact and idempotent:

    <p class="plan-price" data-price="family"><s>$19.99</s> $14.99/year</p>

Keys: free, family, family_plus, collections, plus the two terms spans
(family-terms, family_plus-terms) — they carry the monthly-equivalent
supporting copy the spec allows (never the lead; the price line stays
annual), so their numbers must be written, not typed. While the founding
window is open, Family renders the struck regular price beside the founding
selling price — honest by the site's own rule because the struck figure is
the genuine post-founding price (pricing.json price_per_year), and the
"Early price, yours to keep" terms suffix names what the strike means.

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


def monthly(amount_per_year):
    """The supporting monthly equivalent — never the lead."""
    return f"${amount_per_year / 12:.2f}"


def family_price_line(pricing, plan):
    """While founding is open: the genuine post-founding regular price,
    struck, beside the founding selling price. The strike is honest by the
    site's own rule only because price_per_year IS the documented later
    price; if that intent ever changes, pricing.json changes and this line
    follows."""
    now = selling_price(pricing, plan)
    later = plan["price_per_year"]
    if now != later:
        return f"<s>{money(later)}</s> {money(now)}/year"
    return f"{money(now)}/year"


def expected_lines(pricing):
    plans = pricing["plans"]
    fam, plus = plans["family"], plans["family_plus"]
    return {
        "free": "Free",
        "family": family_price_line(pricing, fam),
        "family_plus": family_price_line(pricing, plus),
        "collections": f"From {money(pricing['collections']['price_from'])}",
        "family-terms": (
            f"About {monthly(selling_price(pricing, fam))} a month · "
            f"Renews yearly · Early price, yours to keep"
            if selling_price(pricing, fam) != fam["price_per_year"]
            else f"About {monthly(selling_price(pricing, fam))} a month · Renews yearly"
        ),
        "family_plus-terms": (
            f"About {monthly(selling_price(pricing, plus))} a month · Renews yearly"
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

    # No founding-window gate: closing the window in pricing.json simply
    # makes selling == regular, which drops the strike and the "Early price"
    # suffix on the next run. (The old founding-note paragraph this script
    # once guarded was removed 2026-08-17 — "that join while Postmello is
    # new" read as if nobody was on it.)
    html = INDEX.read_text(encoding="utf-8")
    disagreements = []
    for key, want in expected_lines(pricing).items():
        pat = re.compile(
            r'(<(?:p|span)\b[^>]*data-price="' + re.escape(key) + r'"[^>]*>)'
            r"(.*?)(</(?:p|span)>)", re.S)
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
