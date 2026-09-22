#!/usr/bin/env python3
"""Count the anonymous page events that assets/site.js sends to /t/<page>/<event>.

    python3 scripts/site-events.py                       # today (UTC)
    python3 scripts/site-events.py --since 2026-09-22 --until 2026-09-24 --country FI

Reads Cloudflare's request log for the zone, so it needs a token with Zone
Analytics Read: CLOUDFLARE_API_TOKEN in the environment, or in ../posty/.env.
The free plan limits each query to one day, so it walks day by day.

Counts are VISITORS (distinct addresses), not requests. The log is sampled
whenever the zone is busy, and a kept request is then weighted to stand for
several: one real page load came back as "6 views" on 2026-09-22. Counting
addresses ignores the weights. Sampling can still DROP an event, so a visitor
counts toward the total if any event of theirs survived, and each event's
count is a floor. Addresses are only counted, never printed.
"""
import argparse, collections, datetime as dt, json, os, pathlib, urllib.request

ZONE = '8bcbea4cdb1ae7595b92d048f5ebfe47'  # postmello.com


def token():
    if os.environ.get('CLOUDFLARE_API_TOKEN'):
        return os.environ['CLOUDFLARE_API_TOKEN']
    env = pathlib.Path(__file__).resolve().parents[2] / 'posty' / '.env'
    for line in env.read_text().splitlines():
        if line.startswith('CLOUDFLARE_API_TOKEN='):
            return line.split('=', 1)[1].strip().strip('"')
    raise SystemExit('CLOUDFLARE_API_TOKEN not set and not in ../posty/.env')


def day_rows(tok, day, country):
    extra = f', clientCountryName: "{country}"' if country else ''
    query = '''query($z: String!, $s: Time!, $e: Time!) { viewer { zones(filter: {zoneTag: $z}) {
      rows: httpRequestsAdaptiveGroups(limit: 5000, filter: {datetime_geq: $s, datetime_lt: $e,
        clientRequestPath_like: "/t/%%", requestSource: "eyeball"%s}) {
        count dimensions { clientRequestPath clientIP } } } } }''' % extra
    body = json.dumps({'query': query, 'variables': {
        'z': ZONE, 's': f'{day}T00:00:00Z', 'e': f'{day + dt.timedelta(days=1)}T00:00:00Z'}}).encode()
    request = urllib.request.Request('https://api.cloudflare.com/client/v4/graphql', data=body, headers={
        'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
    reply = json.load(urllib.request.urlopen(request))
    if reply.get('errors'):
        raise SystemExit(reply['errors'])
    return reply['data']['viewer']['zones'][0]['rows']


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    today = dt.datetime.now(dt.timezone.utc).date()
    parser.add_argument('--since', type=dt.date.fromisoformat, default=today)
    parser.add_argument('--until', type=dt.date.fromisoformat, default=today, help='inclusive')
    parser.add_argument('--country', help='two-letter code, e.g. FI')
    args = parser.parse_args()

    tok, seen, day = token(), collections.defaultdict(set), args.since
    while day <= args.until:
        for row in day_rows(tok, day, args.country):
            path, visitor = row['dimensions']['clientRequestPath'][3:], row['dimensions']['clientIP']
            seen[path].add(visitor)
            seen[path.split('/')[0] + '/*'].add(visitor)
        day += dt.timedelta(days=1)
    counts = {path: len(visitors) for path, visitors in seen.items()}

    pages = sorted({path.split('/')[0] for path in counts})
    print(f"{args.since} to {args.until}{' · ' + args.country if args.country else ''}")
    if not pages:
        print('no events')
    for page in pages:
        views = counts[f'{page}/*']
        print(f'\n{page}: {views} visitors')
        events = sorted(((path.split('/', 1)[1], n) for path, n in counts.items()
                         if path.startswith(page + '/') and path != f'{page}/*'),
                        key=lambda item: (item[0].split('/')[0], -item[1]))
        for event, n in events:
            share = f'{100 * n / views:3.0f}%' if views else '   -'
            print(f'  {n:6}  {share}  {event}')


if __name__ == '__main__':
    main()
