# Website suggestions from search providers

Observed November 10, 2026 while reviewing issue [#23](https://github.com/leebyron/lune-browser/issues/23). This is endpoint research, separate from owner acceptance of the browser candidate. Provider behavior can vary with query, locale, client, cookies and time.

## Finding

Some autocomplete services return explicit website destinations. Google's configured Chrome endpoint returned `https://www.wikipedia.org/`, `https://github.com/` and `https://www.amazon.com/` for `wikipedia`, `github` and `amazon`, respectively, each marked `NAVIGATION` in `google:suggesttype`. The other successful configured endpoints returned query text only for these samples. A search index containing a website does not imply that its autocomplete endpoint exposes that site's URL.

The browser candidate already accepts explicit navigation matches in both menus. A loopback fixture verifies parsing, display and activation; live Google behavior was also verified in the rebuilt native candidate: Cmd-T displayed Wikipedia and wikipedia.com as Top hit rows below the typed search, and keyboard activation opened `https://www.wikipedia.org/`. A query suggestion saying `wikipedia website` remains a search, because no destination was supplied. The browser must not turn a brand name into a guessed domain.

## Direct endpoint probes

The probe used the prepared browser's eight engine definitions, public queries `wikipedia`, `github` and `amazon`, `en-US` where the template accepts a language, a Chrome user agent and no cookies. One request per query per endpoint; no retries after rate limiting. Raw responses and timestamps are retained locally in `.work/search-suggestions/navigation-probes.json`.

| Provider | Observed response for all three queries | Interpretation |
| --- | --- | --- |
| [Google](https://www.google.com/complete/search?client=chrome&q=wikipedia) | Query strings plus a website URL marked `NAVIGATION` | Explicit destinations available through the existing parser |
| [DuckDuckGo](https://duckduckgo.com/ac/?q=wikipedia&type=list) | Eight query strings; no destination metadata | Configured endpoint does not supply website hits in this sample |
| [Bing](https://www.bing.com/osjson.aspx?query=wikipedia&language=en-US) | Query strings and relevance scores; no navigation types or URLs | No website destinations in this sample |
| [Startpage](https://www.startpage.com/osuggestions?q=wikipedia) | Ten query strings | No website destinations in this sample |
| [Ecosia](https://ac.ecosia.org?q=wikipedia&mkt=en-US&type=list&language=en-US) | Eight query strings | No website destinations in this sample |
| [Kagi](https://kagisuggest.com/api/autosuggest?q=wikipedia) | Ten query strings | No website destinations in this unauthenticated sample; earlier empty responses are not a permanent limit |
| [Qwant](https://api.qwant.com/api/suggest/?q=wikipedia) | Object with `data.items` containing query text, `suggestType: 0`, and empty `special` | No website destinations in this sample; its configured response also differs from Chromium's expected top-level array and needs separate compatibility work |
| [Brave](https://search.brave.com/api/suggest?q=wikipedia&rich=true&rich_verticals=true) | HTTP 429 | Live capability remains unverified; no retry or rate-limit bypass |

DuckDuckGo's alternate response without `type=list` was also probed. It returned objects containing only `phrase` for these samples, with no explicit URL or navigation flag. Changing to that format alone would not supply the missing website destinations.

## Parser and API boundaries

The pinned Chromium `components/omnibox/browser/search_suggestion_parser.cc` reads `google:suggesttype` to distinguish navigation from query results. Its OpenSearch fourth array of query URLs is explicitly disregarded; a string looking like a URL alone is not a universal navigation contract. The Command-T adapter accepts `kNavsuggest` and `kNavsuggestPersonalized`, and retains the engine-provided destination. This source inspection is distinct from the live response observations above. The pinned `brave_search_suggestion_parser.cc` handles its richer object format as query/entity/calculator suggestions and never appends navigation results. That is an additional client-side limit: even a richer live Brave response would need a verified destination contract and parser support before it could become a website hit. The 429 responses prevent confirming such a contract here.

Brave has a separate authenticated [Autosuggest API](https://api-dashboard.search.brave.com/app/documentation/suggest/get-started) with optional entity metadata, and a separate [Web Search API](https://api-dashboard.search.brave.com/api-reference/web/search/get) returning ranked results and URLs. Those contracts do not establish what its unauthenticated browser endpoint returns. Full search APIs introduce provider credentials, plan limits and per-request cost decisions; they are not a general replacement to invoke on every keystroke.

## Follow-up

Keep engine-supplied website hits wherever available, preserving the selected engine and the existing consent setting. Keep the existing navigation fixture so future filtering changes cannot silently discard website hits; live Google verification passed on the local Apple silicon candidate. Treat Qwant response compatibility as a separate fix. Broader website coverage would need an explicit product choice: local history/bookmarks, a maintained local popular-site catalogue, or a separately configured provider API. No catalogue, cross-provider fallback, paid API, result-page scraping or guessed-domain behavior is implemented by this research.
