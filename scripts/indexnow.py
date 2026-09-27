#!/usr/bin/env python3
"""Tell Bing and the other IndexNow engines (Yandex, Seznam, Naver, Yep) which
pages changed, so a deploy is read within hours instead of whenever a crawler
next comes round. Bing's index also feeds Copilot and ChatGPT search. Google
does not take IndexNow: for Google, use Search Console, URL inspection, then
Request indexing.

    python3 scripts/indexnow.py                             # list every sitemap URL
    python3 scripts/indexnow.py --since 2026-09-27          # lastmod on or after
    python3 scripts/indexnow.py --since 2026-09-27 --send   # submit them

The URLs come from sitemap.xml, so they are exactly the indexable pages. A
sitemap entry without a lastmod is a page still waiting for its first commit
date, which makes it new, so --since includes it.

Run it AFTER the push is live. An engine fetches https://postmello.com/<KEY>.txt
to check that the site itself is asking, so the key file has to be deployed
first; --send checks that before submitting. The key is public by design,
which is why it is committed, and why the file at the root must never be
deleted as junk (check-site.py fails without it).
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "postmello.com"
KEY = "701511ec7ea649356a52d2b4ea14fac7"
KEY_URL = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
# Cloudflare's Browser Integrity Check answers urllib's default User-Agent
# ("Python-urllib/3.x") with a 403, error 1010, so the key-file check would
# fail on a live file. Any honest name gets through.
UA = {"User-Agent": "postmello-indexnow/1.0 (+https://postmello.com/)"}
ANSWERS = {
    200: "OK: submitted",
    202: "Accepted: the engine will verify the key file, then read the URLs",
    400: "Bad request: the body is malformed",
    403: "Forbidden: the key file did not match the key",
    422: "Unprocessable: a URL is not on the host, or the key location is wrong",
    429: "Too many requests: wait and try again later",
}


def sitemap_urls(since):
    tree = ET.parse(ROOT / "sitemap.xml")
    for url in tree.getroot().findall("s:url", NS):
        loc = url.findtext("s:loc", namespaces=NS).strip()
        lastmod = url.findtext("s:lastmod", namespaces=NS)
        if since is None or lastmod is None or lastmod.strip()[:10] >= since:
            yield loc


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", type=lambda s: datetime.date.fromisoformat(s).isoformat(),
                    help="only pages whose sitemap lastmod is on or after this date (YYYY-MM-DD)")
    ap.add_argument("--send", action="store_true", help="submit; without it, only list")
    args = ap.parse_args()

    if (ROOT / f"{KEY}.txt").read_text(encoding="utf-8").strip() != KEY:
        sys.exit(f"{KEY}.txt does not hold the key in scripts/indexnow.py")
    urls = list(sitemap_urls(args.since))
    if not urls:
        sys.exit("No sitemap URL matches; nothing to submit.")
    print("\n".join(urls))
    if not args.send:
        print(f"\n{len(urls)} URLs. Dry run: add --send to submit them.")
        return

    try:
        live = urllib.request.urlopen(urllib.request.Request(KEY_URL, headers=UA), timeout=20).read().decode().strip()
    except urllib.error.URLError as error:
        live = f"unreachable ({error})"
    if live != KEY:
        sys.exit(f"\n{KEY_URL} is not live yet ({live[:60]}): push, wait for the deploy, then send.")

    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_URL, "urlList": urls}).encode()
    request = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                     headers={**UA, "Content-Type": "application/json; charset=utf-8"})
    try:
        status = urllib.request.urlopen(request, timeout=30).status
    except urllib.error.HTTPError as error:
        status = error.code
    print(f"\n{len(urls)} URLs -> IndexNow: {status} {ANSWERS.get(status, '')}")
    sys.exit(0 if status in (200, 202) else 1)


if __name__ == "__main__":
    main()
