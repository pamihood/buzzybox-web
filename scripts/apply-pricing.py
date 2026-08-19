#!/usr/bin/env python3
"""Write the plans-block prices in index.html from the app repo's pricing.json.

pricing.json is THE ground truth for every Postmello price (adopted 2026-08-17
with the Family subscription revision); this script is how the website obeys
it. Edit the JSON first, then run this — never hand-edit a number in
index.html. Each rewritable line carries a data-price marker, so the
replacement is exact and idempotent:

    <p class="plan-price" data-price="membership"><s>$19.99</s> $14.99/year</p>

Keys: free, membership, membership_plus, collections, plus the two terms spans
(membership-terms, membership_plus-terms) — they carry the monthly-equivalent
supporting copy the spec allows (never the lead; the price line stays
annual), so their numbers must be written, not typed.

Since the 2026-08-18 Membership revision this script also owns two things
that used to be typed by hand, both because they had drifted: the plan NAMES
(data-plan-name="<key>", written from public_name — the rename from Family to
Membership is exactly the kind of change that survives in one file and not
another) and the DESK COUNTS (data-plan-desks="<key>", written from
max_desks). The plan keys stay `family`/`family_plus` in the markup for the
RENAMED 2026-08-18 from family/family_plus: the identifiers now match the
public names, because nothing outside the repo was holding the old ones.

While the founding
window is open, Membership renders the struck regular price beside the founding
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


def membership_price_line(pricing, plan):
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


def desks_line(plan, key):
    """The desk count, in the block's own voice. Free says what it IS; the
    paid tiers say "up to", because the number is a server-side capability
    (account_capabilities) that is meant to be retunable without a release,
    and "up to" is what keeps that honest."""
    n = plan["max_desks"]
    if key == "free":
        return "One desk" if n == 1 else f"{n} desks"
    return f"Up to {n} desk" + ("" if n == 1 else "s")


def expected_lines(pricing):
    plans = pricing["plans"]
    fam, plus = plans["membership"], plans["membership_plus"]
    return {
        "free": "Free",
        "membership": membership_price_line(pricing, fam),
        "membership_plus": membership_price_line(pricing, plus),
        "collections": f"From {money(pricing['collections']['price_from'])}",
        "membership-terms": (
            f"About {monthly(selling_price(pricing, fam))} a month · "
            f"Renews yearly · Early price, yours to keep"
            if selling_price(pricing, fam) != fam["price_per_year"]
            else f"About {monthly(selling_price(pricing, fam))} a month · Renews yearly"
        ),
        "membership_plus-terms": (
            f"About {monthly(selling_price(pricing, plus))} a month · Renews yearly"
        ),
    }


def expected_names(pricing):
    return {key: plan["public_name"] for key, plan in pricing["plans"].items()}


def expected_desks(pricing):
    return {key: desks_line(plan, key) for key, plan in pricing["plans"].items()}


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
    # (attribute, tag alternation, expected map) — one rewrite rule each.
    for attr, tags, expected in (
        ("data-price", "p|span", expected_lines(pricing)),
        ("data-plan-name", "dt", expected_names(pricing)),
        ("data-plan-desks", "strong", expected_desks(pricing)),
    ):
        for key, want in expected.items():
            pat = re.compile(
                r'(<(?:' + tags + r')\b[^>]*' + attr + r'="' + re.escape(key) + r'"[^>]*>)'
                r"(.*?)(</(?:" + tags + r")>)", re.S)
            m = pat.search(html)
            if not m:
                raise SystemExit(
                    f'!! index.html: no {attr}="{key}" element to rewrite')
            have = normalize(m.group(2))
            if have == normalize(want):
                continue
            disagreements.append((f'{attr}="{key}"', have, want))
            html = (html[: m.start(2)] + want + html[m.end(2):])

    if args.check:
        if disagreements:
            print(f"!! index.html disagrees with {pricing_path}:")
            for key, have, want in disagreements:
                print(f"   {key}")
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
