// The landing spot for the page events in assets/site.js. It stores nothing
// and reads nothing: the event IS the path (/t/home/tap/app-store/hero), and
// Cloudflare's own request log for the zone is what counts it, with country
// and device, and no cookie or identifier. scripts/site-events.py reads it.
//
// The event lives in the PATH, not a query string, because the free plan's
// analytics cannot see query strings (clientRequestQuery is denied).
//
// A Function rather than a missing file, because a missing file answers 404
// with the whole error page's bytes, and would bury real 404s in the counts.
// Only /t/* runs here; Pages keeps serving every other path as static files.
export const onRequest = () =>
  new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
