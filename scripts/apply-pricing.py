#!/usr/bin/env python3
"""Sync the homepage's marked prices, plan names, desk counts, and discounts.

The app's ../posty/pricing.json is the source of truth. All occurrences of each
marker are updated, including repeated member discounts. Founding annotations
empty themselves when the founding window closes. Use --check to validate
without writing; --pricing PATH or POSTY_PRICING_JSON can override the source.
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


# The markers whose desk count lands MID-SENTENCE rather than at the head of
# its own line. Membership Plus is not a card; it is a disclosure row reading
# "Membership Plus supports up to 12 desks." — and a capital U inside that
# clause is a typo the page cannot fix at its end, because this script owns
# the string. The card markers (free, membership) each open a line of their
# own and keep the capital. Add a key here if a count ever moves into prose.
MIDSENTENCE_DESKS = {"membership_plus"}


def desks_line(plan, key):
    """The desk count, in the block's own voice. Free says what it IS; the
    paid tiers say "up to", because the number is a server-side capability
    (account_capabilities) that is meant to be retunable without a release,
    and "up to" is what keeps that honest.

    Case follows the SLOT, not the tier: see MIDSENTENCE_DESKS above."""
    n = plan["max_desks"]
    if key == "free":
        # Numeral, like every other figure in the block. "One desk" was the
        # odd one out the moment the paid cards started saying "Up to 4".
        return f"{n} desk" + ("" if n == 1 else "s")
    lead = "up to" if key in MIDSENTENCE_DESKS else "Up to"
    return f"{lead} {n} desk" + ("" if n == 1 else "s")


def expected_lines(pricing):
    """Leaf values used by the selected homepage; keep founding copy conditional."""
    fam = pricing["plans"]["membership"]
    plus = pricing["plans"]["membership_plus"]
    founding = pricing["founding_window"]["active"]
    return {
        "free": "$0",
        "membership": money(selling_price(pricing, fam)),
        "membership_context": f"Founding rate · Regularly {money(fam['price_per_year'])}/year" if founding else "",
        "membership_founding": "Founding rate stays while subscribed." if founding else "",
        "membership_more": f"Need more than {fam['max_desks']} desks?",
        "membership_plus": money(selling_price(pricing, plus)),
        "membership_plus_context": f" at the founding rate (regularly {money(plus['price_per_year'])}/year)" if founding else "",
        "collections": money(pricing["collections"]["price_from"]),
        "collections_discount": f"{round(pricing['collections']['member_discount'] * 100)}%",
        "collections_shelf": str(pricing["collections"]["max_active_per_household"]),
    }


def expected_names(pricing):
    """Card eyebrows: public_name, verbatim.

    They were briefly stripped to "Free" / "Membership" / "Membership Plus" on
    the theory that the brand is already established by this scroll depth.
    Patrick put it back (2026-08-18): these are the PRODUCT names, they are
    what the App Store sheet and the app say, and a plan view is where a
    reader decides what to buy — the one place worth spending the word.
    Verbatim also means one rule, with no special case for Free."""
    return {key: plan["public_name"] for key, plan in pricing["plans"].items()}


def expected_desks(pricing):
    return {key: desks_line(plan, key) for key, plan in pricing["plans"].items()}


SHELF_COPIES = [
    # (path relative to the app repo root, regex with one capture group, what it is)
    ("Buzzybox/Buzzybox/Services/PackEntitlementStore.swift",
     r"static let maxActiveCollections\s*=\s*(\d+)",
     "the client's shelf cap"),
]


def check_shelf_copies(pricing, pricing_path):
    """pricing.json is the ground truth; the app HAND-COPIES this one number.

    Every other figure this script writes exists in pricing.json and nowhere
    else, so "edit the JSON, run the script" is the whole contract. The shelf
    cap is different: `collections.max_active_per_household` is also written
    out as a Swift constant and, since 2026-08-26, enforced inside the
    `activate_pack` RPC - three copies of one number, and changing the JSON
    alone would leave a site advertising a cap the app does not keep.

    So --check reads the Swift constant back and fails on a mismatch. It is a
    cross-repo check on purpose: this script already reaches into the app repo
    for pricing.json, and the drift it is guarding against is exactly the kind
    nobody notices until a household is told it can show eight and can't.

    NOT checked here, and deliberately: the SERVER copy. The number sits in an
    `activate_pack` body, and migrations are immutable, so the newest
    definition is the only one that counts - reading the migration trail
    under-reports, and reading the live function needs the network and a
    token, which a pre-commit check must not require. Verify that one against
    the live database when the cap changes.

    Returns a list of human-readable problems; empty means agreement (or that
    the app repo is not next to this one, which is not an error - the website
    still builds fine on a machine that only has the website)."""
    want = int(pricing["collections"]["max_active_per_household"])
    root = pricing_path.resolve().parent
    problems = []
    for rel, pattern, what in SHELF_COPIES:
        f = root / rel
        if not f.exists():
            continue
        m = re.search(pattern, f.read_text(encoding="utf-8"))
        if not m:
            problems.append(f"{rel}: could not find {what} "
                            f"(pattern {pattern!r}) - has it been renamed?")
        elif int(m.group(1)) != want:
            problems.append(
                f"{rel}: {what} is {m.group(1)}, pricing.json says {want}. "
                f"One of the two is wrong, and the website now prints the "
                f"pricing.json figure to the public.")
    return problems


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
        # h3 joined the alternation with the 2026-08-23 redesign: the plan
        # NAME is a heading on the new card, not a <dt> in a <dl>.
        ("data-price", "p|span|dt|strong|h3", expected_lines(pricing)),
        ("data-plan-name", "p|span|dt|h3", expected_names(pricing)),
        ("data-plan-desks", "h3|span|strong", expected_desks(pricing)),
    ):
        for key, want in expected.items():
            pat = re.compile(
                r'(<(?:' + tags + r')\b[^>]*' + attr + r'="' + re.escape(key) + r'"[^>]*>)'
                r"(.*?)(</(?:" + tags + r")>)", re.S)
            matches = list(pat.finditer(html))
            if not matches:
                raise SystemExit(f'!! index.html: no {attr}="{key}" element to rewrite')
            for m in reversed(matches):
                have = normalize(m.group(2))
                if have == normalize(want):
                    continue
                disagreements.append((f'{attr}="{key}"', have, want))
                html = html[:m.start(2)] + want + html[m.end(2):]

    shelf_problems = check_shelf_copies(pricing, pricing_path)

    if args.check:
        if disagreements or shelf_problems:
            if disagreements:
                print(f"!! index.html disagrees with {pricing_path}:")
                for key, have, want in disagreements:
                    print(f"   {key}")
                    print(f"     - {have}")
                    print(f"     + {want}")
            for problem in shelf_problems:
                print(f"!! {problem}")
            sys.exit(1)
        print(f"[pricing] index.html agrees with {pricing_path}")
        return

    for problem in shelf_problems:
        print(f"!! {problem}")

    if disagreements:
        INDEX.write_text(html, encoding="utf-8")
        for key, _have, want in disagreements:
            print(f"[pricing] {key} -> {want}")
    else:
        print("[pricing] index.html already agrees; nothing written")


if __name__ == "__main__":
    main()
