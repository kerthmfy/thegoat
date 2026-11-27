// Optional: my own tiny proxy for live Letterboxd updates.
//
// Browsers won't let my site read letterboxd.com directly, so the Films section
// asks a proxy. Public proxies work but can be slow or go down. This Cloudflare
// Worker (free) does the same job, only ever fetches MY feed, and caches it for
// 5 minutes so Letterboxd isn't hit on every visit.
//
// Setup (about 5 minutes):
//   1. Sign up at dash.cloudflare.com → Workers & Pages → Create → "Hello World" worker.
//   2. Replace its code with this file → Deploy.
//   3. Copy the worker's address (like https://letterboxd-feed.YOURNAME.workers.dev)
//      into MY_PROXY in index.html (search for MY_PROXY).

const FEED = "https://letterboxd.com/kerthfyadao/rss/";

export default {
  async fetch() {
    const upstream = await fetch(FEED, {
      headers: { "User-Agent": "Mozilla/5.0 (personal website film list)" },
      cf: { cacheTtl: 300, cacheEverything: true },
    });
    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Access-Control-Allow-Origin": "*",   // lets any page read it; it only serves my public feed
        "Cache-Control": "public, max-age=300",
      },
    });
  },
};
