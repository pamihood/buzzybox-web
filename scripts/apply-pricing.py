#!/usr/bin/env python3
"""Write the plans-block prices in index.html from the app repo's pricing.json.

pricing.json is THE ground truth for every Postmello price (adopted 2026-08-17
with the Family subscription revision); this script is how the website obeys
it. Edit the JSON first, then run this — never hand-edit a number in
index.html. Each rewritable line carries a data-price marker, so the
replacement is exact and idempotent:

    <span class="amount" data-price="membership">$14.99</span>

Keys: free, membership, membership_was, membership_founding,
membership_plus, membership_plus_was, membership_plus_founding, collections,
collections_discount (the member percentage — "50%" — from
collections.member_discount, added 2026-08-24 with the collections-for-
everyone revision: collections sell on every tier and the member benefit is
the discount), collections_shelf (how many a household SHOWS at once - it
sits in the FAQ since 2026-08-31, not the commerce panel; this script rewrites
the element wherever it lives, and refuses to run if it is gone), from
collections.max_active_per_household, added 2026-08-27). The two "-terms" spans
this once wrote are gone: the monthly-equivalent line went when the cards
switched to feature lists, and the founding annotation left the Membership
card on 2026-08-18 (the promise it stood in for is a hand-written line beneath
the whole pricing block).

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
    """One key per data-price element on the page.

    REWRITTEN 2026-08-23 with the homepage redesign. The old build put a whole
    price line in one element ("<s>$19.99</s> $14.99/year"); the new plan card
    sets the figure, the "/ year" suffix and the struck price at three
    different sizes, so each is its own leaf element and this map writes leaves
    rather than markup. The rule that produced the old shape is unchanged and
    still the reason the strike is allowed at all: the struck figure is the
    genuine post-founding regular price (pricing.json price_per_year), never an
    invented was-price.

    The two founding-only keys write an EMPTY STRING once the founding window
    closes, and home.css hides an empty .was and an empty .note--founding. That
    is what makes closing the window a pricing.json edit plus one run of this
    script, with no hand-editing of the page on the day the price moves."""
    plans = pricing["plans"]
    fam, plus = plans["membership"], plans["membership_plus"]

    # Both paid tiers carry a founding price as of 2026-08-23, so the strike and
    # its caption are generated the same way for each rather than hand-written
    # for one of them. A tier with no founding_price_per_year simply has
    # selling == regular and empties both of its founding elements.
    def tier(plan):
        now, later = selling_price(pricing, plan), plan["price_per_year"]
        founding = now != later
        return (money(now),
                money(later) if founding else "",
                # "yours to keep." overpromised: the founding rate is tied to
                # the subscription staying alive, not to the account forever.
                # (Patrick, 2026-08-31.)
                "Founding rate stays while your Membership remains active."
                if founding else "")

    fam_now, fam_was, fam_note = tier(fam)
    plus_now, plus_was, plus_note = tier(plus)
    return {
        "free": "Free",
        "membership": fam_now,
        "membership_was": fam_was,
        "membership_founding": fam_note,
        "membership_plus": plus_now,
        "membership_plus_was": plus_was,
        "membership_plus_founding": plus_note,
        # The bare figures for the Collections panel (2026-08-24, the
        # collections-for-everyone revision): every tier buys, members save.
        # The sentence around them ("From … · Members save …") is
        # hand-written in the panel; these slots hold only the two numbers
        # that must not drift — the base "from" price and the member
        # discount percentage.
        "collections": money(pricing["collections"]["price_from"]),
        "collections_discount":
            f"{round(pricing['collections']['member_discount'] * 100)}%",
        # THE SHELF CAP, on the site for the first time on 2026-08-27. A
        # household owns every collection it buys, permanently and through a
        # lapse — but it SHOWS up to this many at once, because everything on
        # a desk is wholly on device and that is what makes the offline
        # guarantee true. A commerce panel that says "Yours for good" and
        # nothing else leaves a buyer to discover the cap after paying.
        # Generated rather than typed for the obvious reason: it is a number
        # that can change, and the website was the copy most likely to be
        # forgotten when it did.
        "collections_shelf": str(pricing["collections"]["max_active_per_household"]),
        # The monthly equivalent came OUT (2026-08-18). The spec allows it as
        # supporting copy and it was never the lead, but on a card whose
        # headline is now a promise rather than a number, a second money
        # figure competes with the price line for no gain. The desk count took
        # its slot instead: it is the fact a large household needs and the
        # headline no longer carries it.
        #
        # "Early price, yours to keep" survives the spec's suggested copy on
        # purpose. The spec forgot the founding discount, and a struck $19.99
        # with nothing explaining it is worse than no strike at all.
        # One job now: explain the strike. The spec's card table moved the
        # desk count back into the headline and "Renews yearly" into the
        # feature list, which leaves this line saying the only thing neither
        # of those can — that the struck price is not a first-year teaser.
        # When founding_window closes, selling == regular, the strike drops,
        # and this line empties itself.
        # No membership-terms key any more: the founding annotation left the
        # card on 2026-08-18 and the promise it stood in for is a hand-written
        # line beneath the whole pricing block. Nothing generated explains the
        # strike now, and nothing needs to — a crossed-out number beside a
        # lower one is self-evident.
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
        ("data-plan-name", "dt|h3", expected_names(pricing)),
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
