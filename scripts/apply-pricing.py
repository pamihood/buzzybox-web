#!/usr/bin/env python3
"""Sync the homepage's marked prices, plan name, and desk counts with pricing.json.

The app's ../posty/pricing.json is the source of truth. Since its 2026-09-26
collections-only revision, Postmello sells one kind of thing: a collection,
bought once and kept, "from" collections.price_from. Desks, friends, letters,
replies and history are free, up to plans.free.max_desks in one account. The
two membership tiers are still in the file, marked "on_sale": false, because
grants hold them - and the site must never offer them. So only what is on
sale is rendered, and the run fails when the homepage marks or names a plan
that is not.

Each marker is rewritten wherever it occurs:

  data-plan-name="free"           the plan's public_name, verbatim
  data-plan-desks="free"          "Up to 6 desks" (lower case where the page has it so)
  data-desk-count="free"          the count as a word ("six"), in the page's case
  data-price="free"               "$0"
  data-price="collections"        collections.price_from - the page says "from"
  data-price="collections_shelf"  collections.max_active_per_household

Any other marker fails the run (a retired discount, an off-sale plan's price
or founding rate: a page still offering what is no longer sold), and so does a
dollar amount typed outside a data-price marker. Use --check to validate
without writing; --pricing PATH or POSTY_PRICING_JSON can override the source.
"""
import argparse
import json
import os
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root, not scripts/
DEFAULT_PRICING = ROOT.parent / "posty" / "pricing.json"
INDEX = ROOT / "index.html"

ATTRS = ("data-price", "data-plan-name", "data-plan-desks", "data-desk-count")
# A marker is a leaf: one of these tags, holding text and nothing else.
# Groups: 1 opening tag, 2 tag name, 3 attribute, 4 key, 5 text, 6 closing tag.
MARKER = re.compile(
    r'(<(p|span|dt|dd|strong|h3|li)\b[^>]*?\b(' + "|".join(ATTRS) + r')="([^"]*)"[^>]*>)'
    r"(.*?)(</\2>)", re.S)
ANY_MARKER = re.compile(r"\b(" + "|".join(ATTRS) + r')="([^"]*)"')

NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "ten", "eleven", "twelve"]

# Meta tags whose content a visitor meets (search results, link previews).
META_SHOWN = {"description", "og:title", "og:description",
              "twitter:title", "twitter:description"}


def money(amount):
    return f"${amount:.2f}"


def normalize(text):
    """Collapse whitespace so a hand-wrapped HTML line still counts as equal."""
    return " ".join(text.split())


def on_sale(plan):
    """Free carries no flag and is on sale by definition. Since 2026-09-26 the
    membership tiers carry "on_sale": false: held by grants, sold to nobody."""
    return plan.get("on_sale", True) is not False


def in_page_case(text, current):
    """The words are pricing.json's; the case is the page's. A marker that
    opens a sentence or a line keeps its capital, one mid-sentence stays lower
    case ("Up to 6 desks" on a card, "up to six desks" in an answer)."""
    if current[:1].islower():
        return text[:1].lower() + text[1:]
    return text[:1].upper() + text[1:]


def count_word(n):
    return NUMBER_WORDS[n] if 0 <= n < len(NUMBER_WORDS) else str(n)


def desks_line(n):
    """The desk count on a card. One desk says what it is; more is a ceiling:
    max_desks is a server-side capability (account_capabilities), retunable
    without a release, and "up to" is what keeps that honest. A numeral, like
    every other figure on the card."""
    return "1 desk" if n == 1 else f"Up to {n} desks"


def renderers(pricing):
    """{(attribute, key): current text -> wanted text} for every marker the
    homepage may carry. A plan off sale gets none, so a marker naming it is
    reported instead of rendered."""
    free = pricing["plans"]["free"]
    n = free["max_desks"]
    coll = pricing["collections"]
    price_from = coll.get("price_from", coll["price"])
    shelf = str(coll["max_active_per_household"])
    return {
        ("data-plan-name", "free"): lambda cur: free["public_name"],
        ("data-plan-desks", "free"): lambda cur: in_page_case(desks_line(n), cur),
        ("data-desk-count", "free"): lambda cur: in_page_case(count_word(n), cur),
        ("data-price", "free"): lambda cur: "$0",
        ("data-price", "collections"): lambda cur: money(price_from),
        ("data-price", "collections_shelf"): lambda cur: shelf,
    }


class VisibleText(HTMLParser):
    """The words a visitor can meet: text outside <script> and <style>, the
    attributes that are shown or read aloud, and the page's description."""
    SKIP = {"script", "style"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0
        self.feed(html)
        self.close()
        self.text = normalize(" ".join(self.parts))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self._skip += 1
        for name in ("alt", "title", "aria-label", "placeholder"):
            if a.get(name):
                self.parts.append(a[name])
        if tag == "meta" and (a.get("name") or a.get("property")) in META_SHOWN:
            self.parts.append(a.get("content") or "")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def off_sale_names(pricing):
    """Each off-sale plan's public name and its short form ("Postmello
    Membership Plus", "Membership Plus", ...), longest first."""
    names = set()
    for plan in pricing["plans"].values():
        if not on_sale(plan):
            names.add(plan["public_name"])
            names.add(plan["public_name"].removeprefix("Postmello "))
    return sorted(names, key=len, reverse=True)


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


def page_problems(html, pricing, seen):
    """What no rewrite can fix: the page offering, or failing to mark, what
    pricing.json says. Reported in page order."""
    problems = []
    if ("data-price", "collections") not in seen:
        problems.append('no data-price="collections" element: the one thing '
                        "sold must carry its price")
    if not {("data-plan-desks", "free"), ("data-desk-count", "free")} & seen:
        problems.append('no data-plan-desks="free" or data-desk-count="free" '
                        "element: the free desk count must be marked, not typed")

    names = off_sale_names(pricing)
    if names:
        said = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")s?\b", re.I)
        hits = {}
        for m in said.finditer(VisibleText(html).text):
            hits.setdefault(m.group(0).lower(), m.group(0))
        for hit in hits.values():
            problems.append(f'the page says "{hit}", and pricing.json has that '
                            "plan off sale: the site must not offer it")

    # Every dollar amount is a marker's. Blank the data-price markers, and
    # whatever figure is left was typed by hand.
    blanked = MARKER.sub(
        lambda m: m.group(1) + m.group(6) if m.group(3) == "data-price" else m.group(0),
        html)
    for m in re.finditer(r".{0,30}\$\s?\d[\d.,]*.{0,12}", VisibleText(blanked).text):
        problems.append(f'a price typed by hand ("...{m.group(0).strip()}..."): '
                        "wrap it in a data-price marker")
    return problems


def main():
    ap = argparse.ArgumentParser(
        description="Sync index.html's marked prices and desk counts with pricing.json.")
    ap.add_argument("--pricing", help="path to pricing.json "
                    "(default: $POSTY_PRICING_JSON, then ../posty/pricing.json)")
    ap.add_argument("--check", action="store_true",
                    help="report disagreements and exit 1; write nothing")
    args = ap.parse_args()

    pricing_path = pathlib.Path(
        args.pricing or os.environ.get("POSTY_PRICING_JSON") or DEFAULT_PRICING)
    pricing = json.loads(pricing_path.read_text(encoding="utf-8"))

    sold = [key for key, plan in pricing["plans"].items() if on_sale(plan)]
    if sold != ["free"]:
        raise SystemExit(
            f"!! {pricing_path} puts {sold} on sale. This page renders the free "
            "plan and collections only; a plan that is sold needs its card and "
            "its price written into index.html, and a renderer here, first.")

    render = renderers(pricing)
    # Longest first, so "membership_plus_context" belongs to membership_plus.
    off_sale = sorted((key for key in pricing["plans"] if key not in sold),
                      key=len, reverse=True)
    html = INDEX.read_text(encoding="utf-8")
    disagreements, marker_problems, seen = [], [], set()

    matches = list(MARKER.finditer(html))
    if len(matches) != len(ANY_MARKER.findall(html)):
        marker_problems.append(
            "a marker sits on a tag this script does not rewrite, or inside "
            "another marker: use p, span, dt, dd, strong, h3 or li, holding text only")
    for m in reversed(matches):
        attr, key, text = m.group(3), m.group(4), m.group(5)
        rule = render.get((attr, key))
        if rule is None:
            plan = next((k for k in off_sale if key == k or key.startswith(k + "_")), None)
            why = (f"belongs to {plan}, which pricing.json has off sale" if plan
                   else "is not a marker this script renders")
            marker_problems.append(f'{attr}="{key}" {why}: remove it, and its copy')
            continue
        if "<" in text:
            marker_problems.append(f'{attr}="{key}" wraps markup; a marker holds text only')
            continue
        seen.add((attr, key))
        have = normalize(text)
        want = rule(have)
        if have != want:
            disagreements.append((f'{attr}="{key}"', have, want))
            html = html[:m.start(5)] + want + html[m.end(5):]
    disagreements.reverse()
    marker_problems.reverse()

    problems = marker_problems + page_problems(html, pricing, seen)
    shelf_problems = check_shelf_copies(pricing, pricing_path)

    if args.check:
        if disagreements or problems or shelf_problems:
            if disagreements:
                print(f"!! index.html disagrees with {pricing_path}:")
                for key, have, want in disagreements:
                    print(f"   {key}")
                    print(f"     - {have}")
                    print(f"     + {want}")
            for problem in problems:
                print(f"!! index.html: {problem}")
            for problem in shelf_problems:
                print(f"!! {problem}")
            sys.exit(1)
        print(f"[pricing] index.html agrees with {pricing_path}")
        return

    if problems:
        for problem in problems:
            print(f"!! index.html: {problem}")
        sys.exit("!! nothing written: fix the page, then run this again")

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
