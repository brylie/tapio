# ADR 0001: Replace bespoke crawler with Cloudflare Browser Rendering /crawl endpoint

## Status

Proposed

## Date

2026-03-12

## Context

Tapio includes a custom-built async web crawler (`BaseCrawler` in `tapio/crawler/crawler.py`) that uses httpx and BeautifulSoup to fetch HTML pages, follow links to a configurable depth, manage concurrency via asyncio semaphores, and save results to disk. A separate `CrawlerRunner` (`tapio/crawler/runner.py`) orchestrates crawl execution, and a `Parser` (`tapio/parser/parser.py`) converts the saved HTML to Markdown using XPath selectors and html2text.

This bespoke crawler requires us to maintain:

- Async HTTP fetching with configurable timeouts and redirects
- Recursive link discovery, extraction, and domain filtering
- Depth-limited traversal with visited-URL deduplication
- Concurrency control (semaphore-based throttling)
- Rate limiting (configurable delay between requests)
- HTML file storage with URL-to-filepath mapping
- Content-type filtering

Cloudflare announced the Browser Rendering `/crawl` endpoint (open beta, March 2026) which provides all of this functionality — and more — via a single REST API call. The endpoint supports headless browser rendering, returns content in HTML/Markdown/JSON formats, handles sitemap and link discovery, supports incremental crawling, and respects robots.txt by default.

Our project crawls 5 Finnish government websites (migri, te_palvelut, kela, vero, dvv) to build a RAG knowledge base. The crawling needs are straightforward and well within the capabilities of the Cloudflare endpoint.

## Decision

Replace the bespoke `BaseCrawler` and `CrawlerRunner` with a new implementation that wraps the Cloudflare Browser Rendering `/crawl` REST API.

### What changes

1. **Remove** `BaseCrawler` class (`tapio/crawler/crawler.py`) — the entire custom crawling logic
2. **Rewrite** `CrawlerRunner` (`tapio/crawler/runner.py`) as a Cloudflare `/crawl` API client with:
   - Job initiation (POST)
   - Async polling for completion (GET with `?limit=1`)
   - Paginated result retrieval (GET with `cursor`)
   - Graceful handling of all terminal statuses
3. **Update** `CrawlerConfig` model (`tapio/config/config_models.py`) to reflect Cloudflare parameters:
   - Remove: `delay_between_requests`, `max_concurrent` (handled by Cloudflare)
   - Keep: `max_depth` (maps to `depth`)
   - Add: `limit`, `render`, `source`, `formats`, `include_patterns`, `exclude_patterns`, `max_age`
4. **Update** site configurations (`tapio/config/site_configs.yaml`) with Cloudflare-appropriate defaults
5. **Update** the `crawl` CLI command (`tapio/cli.py`) for the async polling workflow
6. **Authenticate** via environment variables: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`

### What stays the same

- CLI interface and command signatures
- Site configuration structure (base_url, description, parser_config)
- Downstream pipeline: parse → vectorize → RAG app
- Parser module (still useful for targeted XPath content extraction if needed)

## Consequences

### Positive

- **Less code to maintain** — Removes ~300 lines of async crawling logic (link following, concurrency, rate limiting, HTML storage)
- **Better crawling capabilities** — Headless browser rendering for JS-heavy sites, sitemap discovery, incremental crawling, pattern-based URL filtering
- **robots.txt compliance by default** — The Cloudflare crawler identifies itself as a bot and respects directives automatically
- **Markdown output** — Cloudflare can return Markdown directly, potentially simplifying or eliminating the parse step for some use cases
- **Caching and incremental crawls** — `maxAge` and `modifiedSince` parameters reduce redundant crawling

### Negative

- **External service dependency** — Crawling now depends on Cloudflare's API availability and account limits
- **API token management** — Requires a Cloudflare account and API token with Browser Rendering permissions
- **Cost** — `render: true` crawls consume headless browser time (billed per Cloudflare pricing). `render: false` is free during beta but will be billed later
- **Less control** — Cannot customize HTTP request headers, cookies, or retry logic as granularly as with our own client (though the API does support `setExtraHTTPHeaders`, `authenticate`, and cookie options)
- **Async polling** — Crawl jobs are asynchronous; the CLI must poll for completion rather than stream results in real-time
- **Free plan limits** — Workers Free plan is capped at 10 minutes of browser time per day

### Risks

- **Beta status** — The `/crawl` endpoint is in open beta. API surface may change
- **Bot protection** — Target sites using Cloudflare Bot Management or WAF may block the crawler. This is the same risk our current crawler faces, but worth noting
- **Content quality difference** — Cloudflare returns full-page Markdown, while our parser extracts targeted content areas via XPath. Quality comparison needed during implementation

## Alternatives considered

### 1. Keep the bespoke crawler and improve it

Continue maintaining `BaseCrawler` with incremental improvements (sitemap support, better JS handling via Playwright, etc.). Rejected because this increases our maintenance burden for functionality that Cloudflare provides out of the box.

### 2. Use Scrapy or another crawling framework

Replace our custom code with an established Python crawling framework. Rejected because this still requires us to maintain crawling infrastructure, handle JS rendering separately, and manage concurrency — the same problems Cloudflare solves with less code.

### 3. Use Cloudflare Workers with Browser Rendering bindings

Deploy a Cloudflare Worker that uses the Browser Rendering bindings directly for more control. Rejected for this phase — the REST API `/crawl` endpoint is simpler to integrate and sufficient for our needs. Could revisit if we need fine-grained control later.

## References

- [Cloudflare /crawl endpoint documentation](https://developers.cloudflare.com/browser-rendering/rest-api/crawl-endpoint/)
- [Browser Rendering REST API setup](https://developers.cloudflare.com/browser-rendering/rest-api/)
- [Cloudflare Blog: Crawl entire websites with a single API call (March 10, 2026)](https://blog.cloudflare.com/)
- Related issue: [issues/replace-crawler-with-cloudflare.md](../../issues/replace-crawler-with-cloudflare.md)
