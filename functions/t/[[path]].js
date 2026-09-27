// The landing spot for the page events in assets/site.js: each event is one
// POST to /t/<page>/<event> (/t/home/tap/app-store/hero), answered with 204.
//
// The count is Workers Analytics Engine (binding EVENTS: dataset
// postmello_site_events in production, postmello_site_events_preview on
// preview deployments), read by scripts/site-events.py. Not the zone's request
// log: Cloudflare SAMPLES that as it stores it, so an event sent once, like an
// App Store tap, is kept or lost whole (on 2026-09-27 the log held 37 of 59
// page views). Analytics Engine keeps every event at this volume, and marks
// each row with its _sample_interval if it ever stops.
//
// A row, blob by blob (the report reads them by POSITION, so a new field goes
// on the end):
//   1 host  2 page  3 event  4 load  5 country  6 device  7 app  8 who
// and double1, the network's AS number. No address and no user agent is kept:
// the device, the app and who sent it (person, meta, bot or probe) are worked
// out here and the agent is dropped, so the report can leave out crawlers and
// Meta's ad review without storing anyone's details. `load` is the random
// number site.js makes for one page load and keeps nowhere, so one visit's
// events read together and nobody is recognised on the next.
//
// The event lives in the PATH because the zone log on the free plan cannot see
// query strings. A Function rather than a missing file, because a missing file
// answers 404 with the whole error page's bytes. Only /t/* runs here; Pages
// keeps serving every other path as static files. Nothing here may fail the
// response: a failed write is dropped.

const CRAWLER = /bot|crawl|spider|slurp|facebookexternalhit|meta-external|curl|wget|python|go-http|headless|lighthouse|iPhone OS 13_2_3/i;
const META = new Set([32934, 54115, 63293]);  // Meta's networks, where its ad review runs
const clip = (value, size = 100) => String(value || '').slice(0, size);

const device = agent => {
  const key = ['iPad', 'iPhone', 'Android', 'Macintosh', 'Windows', 'CrOS', 'Linux'].find(k => agent.includes(k));
  return { Macintosh: 'Mac', CrOS: 'ChromeOS' }[key] || key || 'other';
};

const app = agent =>
  agent.includes('Instagram') ? 'Instagram'
  : agent.includes('Barcelona') ? 'Threads'
  : /FBAN|FBAV|FB_IAB|FB4A/.test(agent) ? 'Facebook'
  : /Edg(e|A|iOS)?\//.test(agent) ? 'Edge'
  : agent.includes('SamsungBrowser') ? 'Samsung'
  : /Firefox|FxiOS/.test(agent) ? 'Firefox'
  : /Chrome|CriOS/.test(agent) ? 'Chrome'
  : agent.includes('Safari') ? 'Safari'
  : 'other';

const who = (agent, asn) =>
  agent.includes('PostmelloProbe') ? 'probe' : META.has(asn) ? 'meta' : CRAWLER.test(agent) ? 'bot' : 'person';

export const onRequest = ({ request, env }) => {
  try {
    if (request.method === 'POST' && env.EVENTS) {
      const url = new URL(request.url);
      const [page, ...event] = url.pathname.split('/').slice(2);
      const load = /^[0-9a-f]{16}$/.test(url.searchParams.get('l')) ? url.searchParams.get('l') : '';
      const agent = request.headers.get('User-Agent') || '';
      const asn = Number(request.cf?.asn) || 0;
      env.EVENTS.writeDataPoint({
        indexes: [load || clip(page, 96)],
        blobs: [url.hostname, page, event.join('/'), load, request.cf?.country,
                device(agent), app(agent), who(agent, asn)].map(value => clip(value)),
        doubles: [asn],
      });
    }
  } catch (_) {}
  return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
};
