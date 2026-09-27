#!/usr/bin/env python3
"""Count the anonymous page events that assets/site.js sends to /t/<page>/<event>.

    python3 scripts/site-events.py                                  # today so far
    python3 scripts/site-events.py --since "2026-09-28 08:00"        # since 8 am
    python3 scripts/site-events.py --since "2026-09-28 08:00" --ads --country US,GB,CA,AU,NZ,IE,DK --visits
    python3 scripts/site-events.py --log --since 2026-09-22 --until 2026-09-24 --country FI

Times are Pacific unless they carry an offset, and a bare --until date includes
that whole day. --ads keeps only Meta's in-app browsers (Instagram, Facebook,
Messenger, Threads), which is where every ad click lands. --visits adds one
line per visitor: when, where, what device, how long and how far down.

THE COUNT is Workers Analytics Engine (dataset postmello_site_events): from
2026-09-27, functions/t/[[path]].js writes one row per event, kept three
months. A visit there is one page load, grouped by the random number site.js
makes for it and keeps nowhere, so nothing links two visits. It needs
CLOUDFLARE_API_TOKEN (Account Analytics Read) and CLOUDFLARE_ACCOUNT_ID, in the
environment or in ../posty/.env. Every run checks the rows it got against the
dataset's own total, and the header says so if Analytics Engine ever samples.

--log reads the zone's request log instead: the only record of events before
the switch, kept about a week. Cloudflare SAMPLES that log as it stores it (on
2026-09-27 it held 37 of 59 page views), so every count from it is a floor, and
an event sent once, like an App Store tap, is kept or lost whole. There a
visitor is an address (an IPv6 /64, since one phone holds many) with one
browser, counted once it is sent a page or sends an event; a time mark implies
the ones before it; addresses are never printed. It needs Zone Analytics Read,
and the free plan limits each query to one day, so it walks a day at a time.

Left out, and counted in the header:
- Meta's own servers. When an ad is created or edited, Meta's review systems
  load the page with ordinary-looking browsers, run its script, scroll and tap
  links: 294 requests in 15 minutes on 2026-09-26, "from" the US, Ireland and
  Denmark, where Meta has data centres, all from 2a03:2880::/32 (AS32934).
- Crawlers and scanners: bot user agents, and the years-old "iPhone OS 13_2_3"
  string that scanners use.
- Probes (user agent PostmelloProbe), and every host but postmello.com, such as
  a check sent to postmello-web.pages.dev.
"""
import argparse, collections, datetime as dt, ipaddress, json, os, pathlib, re, urllib.error, urllib.request
from zoneinfo import ZoneInfo

ZONE = '8bcbea4cdb1ae7595b92d048f5ebfe47'  # postmello.com
DATASET = 'postmello_site_events'          # previews write postmello_site_events_preview
HOSTS = {'postmello.com', 'www.postmello.com'}
IN_APPS = {'Instagram', 'Facebook', 'Threads'}  # what functions/t/[[path]].js calls Meta's browsers
OLD_SCRIPT = 'a site.js older than visit numbers'
OLD_SCRIPT_TAPS = 'App Store taps among them'
PACIFIC = ZoneInfo('America/Los_Angeles')
SITE = pathlib.Path(__file__).resolve().parents[1]
LIMIT = 10000
COUNTED_LIMIT = 200000

# Meta's networks (AS32934). Ad review has only been seen on the first.
META = [ipaddress.ip_network(net) for net in (
    '2a03:2880::/32', '2620:0:1c00::/40', '2401:db00::/32', '31.13.24.0/21', '31.13.64.0/18',
    '45.64.40.0/22', '57.141.0.0/16', '57.144.0.0/14', '66.220.144.0/20', '69.63.176.0/20',
    '69.171.224.0/19', '74.119.76.0/22', '102.132.96.0/20', '103.4.96.0/22', '129.134.0.0/16',
    '157.240.0.0/16', '163.70.128.0/17', '173.252.64.0/18', '179.60.192.0/22',
    '185.60.216.0/22', '185.89.216.0/22', '204.15.20.0/22')]
CRAWLER = re.compile(r'bot|crawl|spider|slurp|facebookexternalhit|meta-external|curl|wget|python'
                     r'|go-http|headless|lighthouse|iPhone OS 13_2_3', re.I)
IN_APP = re.compile(r'Instagram|FBAN|FBAV|FB_IAB|FB4A|Barcelona')
TIMES = [10, 30, 60, 120, 300]


def setting(name):
    """A value from the environment, else from ../posty/.env."""
    if os.environ.get(name):
        return os.environ[name]
    for line in (SITE.parent / 'posty' / '.env').read_text().splitlines():
        if line.startswith(name + '='):
            return line.split('=', 1)[1].strip().strip('"')
    raise SystemExit(f'{name} not set and not in ../posty/.env')


def slug(value):
    """The name site.js gives a page or a section."""
    value = re.sub(r'\.html$', '', str(value).lower())
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')[:60]


def moment(text, end=False):
    """A time from the command line: Pacific unless it carries an offset. A bare
    date is the start of that day, or with end=True the end of it."""
    value = dt.datetime.fromisoformat(text)
    if end and len(text) == 10:
        value += dt.timedelta(days=1)
    return value if value.tzinfo else value.replace(tzinfo=PACIFIC)


def fetch(tok, start, end):
    """Every page and event request in [start, end), as Cloudflare logged them."""
    iso = lambda moment: moment.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    query = '''query($z: String!, $s: Time!, $e: Time!) { viewer { zones(filter: {zoneTag: $z}) {
      rows: httpRequestsAdaptiveGroups(limit: %d, filter: {datetime_geq: $s, datetime_lt: $e,
        requestSource: "eyeball", clientRequestPath_notlike: "/assets/%%"}) {
        count dimensions { datetimeMinute clientRequestPath clientIP clientCountryName userAgent
          edgeResponseStatus } } } } }''' % LIMIT
    body = json.dumps({'query': query, 'variables': {'z': ZONE, 's': iso(start), 'e': iso(end)}}).encode()
    request = urllib.request.Request('https://api.cloudflare.com/client/v4/graphql', data=body, headers={
        'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
    reply = json.load(urllib.request.urlopen(request))
    if reply.get('errors'):
        raise SystemExit(reply['errors'])
    rows = reply['data']['viewer']['zones'][0]['rows']
    if len(rows) == LIMIT:  # the cap trims silently: halve the window instead
        middle = start + (end - start) / 2
        return fetch(tok, start, middle) + fetch(tok, middle, end)
    return rows


def sql(query):
    """One Analytics Engine query, its rows as dicts."""
    account = setting('CLOUDFLARE_ACCOUNT_ID')
    request = urllib.request.Request(
        f'https://api.cloudflare.com/client/v4/accounts/{account}/analytics_engine/sql',
        data=f'{query} FORMAT JSON'.encode(),
        headers={'Authorization': f'Bearer {setting("CLOUDFLARE_API_TOKEN")}'})
    try:
        return json.load(urllib.request.urlopen(request))['data']
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Analytics Engine answered {error.code}: {error.read().decode()[:300]}')


def counted(start, end):
    """Every event Analytics Engine holds in [start, end), checked against its own total."""
    utc = lambda moment: moment.astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    window = (f"FROM {DATASET} WHERE timestamp >= toDateTime('{utc(start)}')"
              f" AND timestamp < toDateTime('{utc(end)}')")
    rows = sql('SELECT timestamp, _sample_interval AS weight, blob1 AS host, blob2 AS page, blob3 AS event,'
               ' blob4 AS load, blob5 AS country, blob6 AS device, blob7 AS app, blob8 AS who'
               f' {window} ORDER BY timestamp LIMIT {COUNTED_LIMIT}')
    total = int(sql(f'SELECT count() AS n {window}')[0]['n'])
    if len(rows) != total:
        raise SystemExit(f'Analytics Engine sent {len(rows)} of the {total} rows in that window: narrow it')
    return rows


def counting_began():
    """When Analytics Engine's first event landed, or None before there was one."""
    first = sql(f'SELECT min(timestamp) AS first FROM {DATASET}')[0]['first']
    began = dt.datetime.fromisoformat(first).replace(tzinfo=dt.timezone.utc)
    return began if began.year >= 2026 else None


def section_order():
    """Each page's sections in the order the page shows them, named as site.js names them."""
    order = {}
    for html in SITE.rglob('*.html'):
        relative = html.relative_to(SITE).as_posix()
        if relative.startswith(('_', 'scripts/', 'docs/')):
            continue
        path = '/' + relative.removesuffix('index.html')
        names = []
        for tag, attributes in re.findall(r'<(section|footer)\b([^>]*)>', html.read_text()):
            # site.js: the id, else a section's first class, else the footer's tag name
            named = re.search(r'\bid="([^"]+)"', attributes) \
                or (tag == 'section' and re.search(r'\bclass="([^"\s]+)', attributes))
            name = named.group(1) if named else 'footer' if tag == 'footer' else 'page'
            names.append(slug(re.sub(r'-section$', '', name)))
        order[slug(path) or 'home'] = names
    return order


def device(agent):
    kind = next((name for key, name in (('iPad', 'iPad'), ('iPhone', 'iPhone'), ('Android', 'Android'),
                 ('Macintosh', 'Mac'), ('Windows', 'Windows'), ('Linux', 'Linux')) if key in agent), 'other')
    app = 'Instagram' if 'Instagram' in agent else 'Threads' if 'Barcelona' in agent \
        else 'Facebook' if IN_APP.search(agent) else ''
    return f'{kind} · {app}' if app else kind


def new_visitor():
    return {'pages': set(), 'events': set(), 'first': None, 'weight': 1}


def from_log(rows, args, countries):
    """Visitors from the zone's sampled request log: an address with one browser."""
    left_out, visitors = collections.Counter(), collections.defaultdict(new_visitor)
    for row in rows:
        d = row['dimensions']
        address = ipaddress.ip_address(d['clientIP'])
        if any(address in net for net in META if net.version == address.version):
            left_out["Meta's own servers"] += row['count']
            continue
        if CRAWLER.search(d['userAgent']):
            left_out['crawlers and scanners'] += row['count']
            continue
        if countries and d['clientCountryName'] not in countries:
            continue
        if args.ads and not IN_APP.search(d['userAgent']):
            continue
        path = d['clientRequestPath']
        if path.startswith('/t/'):
            page, _, event = path[3:].partition('/')
        elif re.fullmatch(r'/[^.]*|/.*\.html', path) and d['edgeResponseStatus'] in (200, 304):
            page, event = slug(path) or 'home', None
        else:
            continue
        net = ipaddress.ip_network(f'{address}/64', strict=False) if address.version == 6 else address
        visitor = visitors[(str(net), d['userAgent'])]
        visitor.update(country=d['clientCountryName'], device=device(d['userAgent']))
        visitor['first'] = min(filter(None, (visitor['first'], d['datetimeMinute'])))
        visitor['pages'].add(page)
        if event:
            visitor['events'].add((page, event))
    return visitors, left_out


def from_counted(rows, args, countries):
    """Visits from Analytics Engine: one per page load, every event in it."""
    why = {'meta': "Meta's own servers", 'bot': 'crawlers and scanners', 'probe': 'probes'}
    left_out, visits = collections.Counter(), collections.defaultdict(new_visitor)
    for row in rows:
        if row['host'] not in HOSTS:
            left_out['other hosts (pages.dev)'] += 1
            continue
        if row['who'] != 'person':
            left_out[why.get(row['who'], row['who'])] += 1
            continue
        if countries and row['country'] not in countries:
            continue
        if args.ads and row['app'] not in IN_APPS:
            continue
        if not row['load']:  # a site.js from before the number: no visit to put it in
            left_out[OLD_SCRIPT] += 1
            left_out[OLD_SCRIPT_TAPS] += row['event'].startswith('tap/app-store')
            continue
        visit = visits[row['load']]
        visit.update(country=row['country'],
                     device=row['device'] if row['app'] == 'other' else f"{row['device']} · {row['app']}")
        visit['weight'] = max(visit['weight'], int(row['weight']))
        visit['first'] = min(filter(None, (visit['first'], row['timestamp'].replace(' ', 'T') + 'Z')))
        visit['pages'].add(row['page'])
        visit['events'].add((row['page'], row['event']))
    return visits, left_out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--since', help='Pacific date or time, default today 00:00')
    parser.add_argument('--until', help='Pacific date (inclusive) or time, default now')
    parser.add_argument('--country', help='two-letter codes, comma-separated, e.g. US,GB,DK')
    parser.add_argument('--ads', action='store_true', help="only Meta's in-app browsers")
    parser.add_argument('--visits', action='store_true', help='one line per visitor')
    parser.add_argument('--log', action='store_true',
                        help="the zone's SAMPLED request log instead: before 2026-09-27, and floors")
    args = parser.parse_args()

    now = dt.datetime.now(PACIFIC)
    start = moment(args.since) if args.since else now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = min(moment(args.until, end=True), now) if args.until else now
    countries = {code.strip().upper() for code in args.country.split(',')} if args.country else None
    when = lambda moment: moment.astimezone(PACIFIC).strftime('%a %d %b %H:%M')

    if args.log:
        tok, rows, chunk = setting('CLOUDFLARE_API_TOKEN'), [], start
        while chunk < end:
            rows += fetch(tok, chunk, min(chunk + dt.timedelta(days=1), end))
            chunk += dt.timedelta(days=1)
        visitors, left_out = from_log(rows, args, countries)
        source, noun, unit = "the zone's request log, SAMPLED: every count is a floor", 'visitors', 'requests'
    else:
        visitors, left_out = from_counted(counted(start, end), args, countries)
        source, noun, unit = 'Analytics Engine: every event', 'visits', 'events'
    for visitor in visitors.values():  # staying 60 s means having stayed 10 s and 30 s
        for page, event in list(visitor['events']):
            if event.startswith('time/'):
                seconds = int(event[5:-1])
                visitor['events'] |= {(page, f'time/{mark}s') for mark in TIMES if mark < seconds}

    order = section_order()
    print(f"{when(start)} to {when(end)} Pacific"
          + (" · Meta ads (Instagram and Facebook in-app browsers)" if args.ads else '')
          + (f" · {', '.join(sorted(countries))}" if countries else '')
          + f"\nCounted from {source}.")
    if not args.log:
        began = counting_began()
        if began is None or began > start:
            print(f"Counting began {when(began) + ' Pacific' if began else 'with the first event'};"
                  " anything earlier is only in the sampled log (--log).")
        if any(v['weight'] > 1 for v in visitors.values()):
            print('Analytics Engine SAMPLED some of these: each kept visit counts as the visits it stands for.')
    stale_taps = left_out.pop(OLD_SCRIPT_TAPS, 0)
    if left_out:
        print('Left out: ' + ', '.join(f'{n} {unit if n != 1 else unit[:-1]} from {why}'
                                       for why, n in left_out.most_common()) + '.')
    if stale_taps:
        print(f'{stale_taps} of those were App Store taps, which the table below does not include.')
    if not visitors:
        print(f'no {noun}')
        return

    def reached(visitor, section):
        return any(event == f'seen/{section}' for _, event in visitor['events'])

    def longest(visitor):
        marks = [int(event[5:-1]) for _, event in visitor['events'] if event.startswith('time/')]
        return f'{max(marks)}s' if marks else '<10s'

    columns = [noun, *(['any event'] if args.log else []), *(f'{mark}s' for mark in TIMES[:3]),
               'pricing', 'App Store']
    tests = [lambda v: True, *([lambda v: bool(v['events'])] if args.log else []),
             *(lambda v, m=mark: any(e == f'time/{m}s' for _, e in v['events']) for mark in TIMES[:3]),
             lambda v: reached(v, 'pricing'),
             lambda v: any(e.startswith('tap/app-store') for _, e in v['events'])]
    weigh = lambda group, test=lambda v: True: sum(v['weight'] for v in group if test(v))
    by_country = collections.defaultdict(list)
    for visitor in visitors.values():
        by_country[visitor['country']].append(visitor)
    print('\n       ' + ''.join(f'{name:>11}' for name in columns))
    for country, group in sorted(by_country.items(), key=lambda item: -weigh(item[1])) + [('all', list(visitors.values()))]:
        print(f'  {country:5}' + ''.join(f'{weigh(group, test):11}' for test in tests))

    if args.visits:
        print()
        for visitor in sorted(visitors.values(), key=lambda v: v['first']):
            first = dt.datetime.fromisoformat(visitor['first'].replace('Z', '+00:00')).astimezone(PACIFIC)
            page = 'home' if 'home' in visitor['pages'] else min(visitor['pages'])
            seen = [s for s in order.get(page, []) if (page, f'seen/{s}') in visitor['events']]
            taps = sorted(e[4:] for _, e in visitor['events'] if e.startswith('tap/'))
            print(f"  {first:%a %H:%M}  {visitor['country']}  {visitor['device']:22} {'+'.join(sorted(visitor['pages'])):10}"
                  f" {longest(visitor):>5}  {f'down to {seen[-1]}' if seen else 'no section event'}"
                  f"{' · tapped ' + ', '.join(taps) if taps else ''}")

    for page in sorted({page for v in visitors.values() for page in v['pages']},
                       key=lambda page: -weigh(visitors.values(), lambda v: page in v['pages'])):
        here = [v for v in visitors.values() if page in v['pages']]
        counts = collections.Counter()
        for v in here:
            for p, event in v['events']:
                if p == page:
                    counts[event] += v['weight']
        sections = order.get(page, [])
        rank = lambda event: ({'view': 0, 'time': 1, 'seen': 2, 'tap': 3}.get(event.split('/')[0], 4),
                              int(event[5:-1]) if event.startswith('time/') else
                              sections.index(event[5:]) if event[5:] in sections else len(sections),
                              -counts[event], event)
        print(f'\n{page}: {weigh(here)} {noun}')
        for event in sorted(counts, key=rank):
            print(f'  {counts[event]:6}  {100 * counts[event] / weigh(here):3.0f}%  {event}')


if __name__ == '__main__':
    main()
