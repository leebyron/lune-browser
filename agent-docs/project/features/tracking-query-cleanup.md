# Tracking parameters in opened and copied links

[Issue #43](https://github.com/leebyron/lune-browser/issues/43) adds query cleanup before top-level HTTP(S) GET navigation and on browser URL copy. A same-origin internal redirect gives the destination the cleaned query and commits the cleaned URL in the tab. The browser applies cleanup before starting a service-worker loader. The network path covers reused redirect loaders and navigational prefetch. It also cleans outgoing referrer URLs after Chromium applies its referrer policy. A same-document History API update keeps its URL and state. Copy Page URL and a whole-address copy in the floating editor clean the clipboard after such an update. Copy Link Address cleans a link before it has been opened. A partial address selection copies the selected text.

The Helium 0.22.2 integration candidate also applies cleanup to the initial HTTP(S) GET for new downloads from an HTML `download` link or **Save Link As**. This happens before Chromium starts the request or offers it to a service worker. Range requests and interrupted-download resumes use Chromium's existing paths.

The signed input composition and validation results are recorded in the [build evidence](../builds/2026-11-18-tracking-parameter-removal.json).

## Rules and consent

The build extracts the compatible `removeparam` rules and exceptions from the bundled uBlock Origin privacy, core and unbreak lists. It also bundles a verified Helium snapshot of URL Tracking Protection for use before any update and whenever updates are off. A validated download replaces that snapshot and is combined with the original core rules. The bundled snapshot was fetched from Helium on November 18, 2026. Its upstream last-modified date is November 14 and its SHA-256 is `02f98af853e7a79012a2e481f810f4d8a4ab976f57175942ab7764e6a0dfc2c1`. Lune fetches [AdGuard/uBO URL Tracking Protection](https://github.com/uBlockOrigin/uAssets/blob/master/filters/privacy-removeparam.txt) directly from the configured Helium service. It resolves the public file through the filter-list catalog and accepts only the expected asset from the same origin. Requests carry no cookies, authentication credentials, browsing URLs or referrer.

The existing **Update privacy filter lists through Helium** choice governs native refresh and use of the downloaded rules. Lune can refresh with uBlock Origin disabled. Lune checks for updates when consent is granted, then once a day after a successful check. Failed requests, malformed catalogs and unsupported rules leave the last valid list in use and retry after an hour. The parser rejects an entire refresh that contains an active include, unknown condition, or unsupported removal selector. This preserves exceptions that an incomplete parse could otherwise miss. An identical response advances the saved check timestamp. Loaded network contexts receive updates only when the effective list or the cleanup setting changes. A valid snapshot is available at launch before any download. Revoking consent or changing the service origin stops the in-flight fetch and switches to the bundled rules until the new consent or origin supplies a valid snapshot. uBlock Origin runs its own filtering and updater.

Settings → Privacy and security → **Remove tracking parameters** contains the default-on toggle and the excluded-domain list. The toggle and exclusions apply to native request, referrer and clipboard cleanup. A domain entry covers that host and its subdomains. The Setup Privacy step exposes the same toggle. uBlock Origin continues to apply its own enabled lists. The native matcher uses domain, path and value scopes and exceptions from the list. It preserves recognized signed and OAuth URLs. In the Helium 0.22.2 integration candidate, the same filter rules apply to campaign parameters such as `utm_source` in requests, referrers and copied URLs.

## Test cases

Use a local HTTP server to check request targets, referrers and the committed address separately. Cover the first request, redirects, new tabs, reload, navigational prefetch, and copies after both History API methods. The service-worker fixture checks the URL seen by the worker, the committed address, and the request received by the server when the worker forwards a direct navigation or a redirect target. Form POSTs and frame and resource request targets retain their queries. Test offline behavior with the extension disabled and test the existing filter updater through a loopback catalog.

| Example | Expected |
| --- | --- |
| `https://youtu.be/<video>?si=lune-test&t=30` | Remove `si` and keep the video and 30-second seek. |
| `https://open.spotify.com/track/<id>?si=lune-test` | Remove `si` and keep the track. |
| `https://www.instagram.com/p/<post>/?igsh=lune-test` | Remove `igsh` and keep the post. |
| `https://www.amazon.com/s?k=notebook&s=price-asc-rank` | Keep the search and sort query. |
| `https://example.com/?si=keep&item=42&utm_source=newsletter` | Keep `si` and `item`. The bundled snapshot matches and removes `utm_source`. |
| `https://uploadnow.io/share?utm_source=service` | Preserve the parameter under the bundled snapshot’s share-link exception. |

## Request coverage compared with uBlock Origin

```sh
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --request-coverage --report LUNE.json
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --request-coverage --with-ublock --disabled --report UBLOCK.json
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --request-coverage --cold-external --report COLD-LUNE.json
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --request-coverage --cold-external --with-ublock --disabled --report COLD-UBLOCK.json
```

Both modes sent `/ordinary?keep=1` on an already-running browser. After the page added `fbclid` through `pushState`, Lune sent `/history?keep=1` in the `Referer` header of the next same-origin request. The uBlock-only profile sent `/history?keep=1&fbclid=referrer`. Both modes cleaned a same-origin Speculation Rules prefetch target when prefetch was allowed in uBlock's settings.

The cold check uses Launch Services to deliver an external URL on startup in a fresh profile on native hardware. Lune sent `/cold?keep=1` as its first request. The uBlock-only profile sent `/cold?keep=1&fbclid=cold` as its first request. These checks inspect the HTTP requests received by the fixture server. The cold Launch Services check ran on Apple silicon. The Intel bundle requires native execution for Launch Services to open it.

An existing-profile comparison first verified that uBlock was active and that an external URL opened in a new tab in the running browser. Both modes removed `fbclid` in that case. After quitting and reopening the visible macOS app with the same profile through Launch Services, the first external request kept `fbclid` on all three uBlock-only launches and dropped it on all three Lune-only launches. A second external URL after the first relaunch was cleaned in both modes.

The referrer probe also used a same-origin page that supplied a tracked `referrer` through `fetch()` without changing the page URL. Lune removed `fbclid` from that header. uBlock-only kept it. A cross-origin request under Chromium's default policy sent only the origin in both modes. An explicit `unsafe-url` policy sent the full path in both modes, and Lune removed the tracker. Both modes honored `no-referrer`.

The native **Copy Link Address** menu wrote a URL without `fbclid` in Lune-only mode. In uBlock-only mode, a preceding navigation confirmed that uBlock was active, then the same menu copied the full URL. The link target was never requested in either mode.

The Amazon product URL comparison used the same matcher and two rule sets. The original small bundle removed `ref_`. The now-bundled Helium list also removed `pd_rd_i`, `pd_rd_r`, `pd_rd_w`, `pd_rd_wg`, `pf_rd_p`, `pf_rd_r`, and `th`. The list leaves `content-id` in the URL. The matcher checks each top-level query field at each navigation hop. It leaves URLs embedded in parameter values intact.

## Validation

```sh
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --report REPORT.json --clipboard
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --report REFRESH.json --refresh-rules SAVED_LIST.txt --setup-consent next
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --report PRIVACY.json --privacy-controls
python3 scripts/check-clean-link-loading.py BUILD_OUTPUT --report DOWNLOADS.json --download-requests
```

The first command checks request targets, the committed URL, referrers and copy with extensions disabled. Add `--disabled` to exercise the native opt-out. The second serves a saved Helium list through a loopback-only catalog. Pass `--setup-consent defaults` to verify the first download and clean copy with Use Defaults, which also enables uBlock Origin. Omit the option to run the full fixture with consent granted in Settings. The fixture checks that Lune fetches only after consent, updates rules without restarting, rejects malformed lists and foreign asset URLs, uses its saved rules after a restart, and sends no cookies, authentication or referrer.

The Privacy controls fixture starts with list updates and extensions disabled. It checks a rule from the bundled Helium snapshot, then uses Settings to toggle cleanup and add and remove a domain exclusion. It verifies the address, the copied URL and the request referrer, and checks that the exclusion survives restart.

The downloads fixture disables extensions and checks that both navigation to an attachment and an HTML `download` link save the file and send only `keep=1` on the first request. It checks signed links, domain exclusion, the cleanup toggle and a referrer containing campaign tags.

To check the floating editor on macOS, use the console on a test page to run `history.pushState(null, '', '?item=7&fbclid=push')`. Press Cmd+L and Cmd+C and paste into a text editor. The pasted address should keep `item=7`. Select just `fbclid=push` in the address bar and copy again to check literal text selection. The page should retain the URL set by `pushState`.

The saved Helium snapshot used in development has SHA-256 `02f98af853e7a79012a2e481f810f4d8a4ab976f57175942ab7764e6a0dfc2c1`.

The Apple silicon and x86_64 previews passed bundled cleanup, the native opt-out, both Setup paths, the Settings consent flow, and packaged UI and Settings smoke checks. The Intel preview ran under Rosetta on Apple silicon. The full fixtures with uBlock disabled covered a refreshed list, last-valid rules after malformed or foreign responses, cached startup while offline, and requests without credentials or a referrer. Nine focused C++ tests and seven website tests passed.

The Apple silicon package also fetched the production catalog and saved the live Helium list with extensions disabled. The fetched snapshot contained 182,538 bytes and matched the saved fixture SHA-256.

| Preview | Execution | Framework SHA-256 |
| --- | --- | --- |
| arm64 | Apple silicon | `4eab9215271640d16d7e8de74d4be0382cf295d756b9142c8db1356dbbac64af` |
| x86_64 | Rosetta on Apple silicon | `6d392a17e62735ab6713293333e47f8dcaf7b983d8893e01b2bd49d9d3f049bc` |

Zero-fuzz preparation with the floating editor change matched all 35 affected and generated paths, including the eight files restored to their pre-feature extension content. The preparation log SHA-256 is `aa64bc4ac19e7e020b5df21ba5a8ef62d10815cd02ff1afc5a88117653467603`. On the updated Apple silicon preview, Cmd+C cleaned the whole address after `pushState`, Edit → Copy copied a literal partial selection, and opting out restored ordinary whole-address copying. The framework SHA-256 is `e0cf191e0761c1ccfaa9f883e686b1e759b3f7b391f00bbc4d7ee16d770e2423`.

The parser hardening passed nine focused C++ tests, including the bundled rules and the saved Helium snapshot. The Apple silicon refresh fixture measured two cleanup updates for an identical list on the previous preview and zero on the hardened preview. It verified live rule changes, rejection of an unsupported option, active include and legacy prefix selector, and retention of the last valid list across an offline restart. It also verified that switching cleanup off still updates the network context when only bundled rules are active. Zero-fuzz preparation matched all 35 affected and generated files. The preparation log SHA-256 is `4321437b9ebc698d2797a826cbcf32271d413089f316c40156f4a417d597ed8b`. The hardened Apple silicon framework SHA-256 is `6b70aa6ab526b3bcf4b3f8c058eb942697d12eeec3f01f93f35467cfbc45c2bd`.

The service-worker regression failed on the preceding preview and passed on Apple silicon and x86_64 under Rosetta. Both builds passed with cleanup enabled and opted out. The fixture verified worker-generated responses, a direct navigation forwarded by the worker, and a network redirect into worker scope. Zero-fuzz preparation matched all 36 affected and generated paths. The preparation log SHA-256 is `3f44ac8b0dfd4ee0c484a95c5bbbbebb1acadbc46de1c6354cdd37944698c480`. The first cold Launch Services run timed out on both previews. The rerun on the same updated Apple silicon package sent the clean URL with Lune-only cleanup and kept `fbclid` with uBlock alone. All 20 packaged reruns and nine focused C++ cases passed on the earlier service-worker review packages.

| Service-worker preview | Framework SHA-256 |
| --- | --- |
| arm64 | `f60e2fa80c9e2d76a0c96cddd395c21e133e79a4650d551782714aa07540c2fa` |
| x86_64 | `8e44494e81aea5323dccab5d912830a575ebb2f23a8af7a742e4774805b2b0dd` |

The Apple silicon Privacy Settings preview passed 12 packaged checks, including offline bundled rules, the tracking toggle, domain exclusions across navigation, copy, and referrers, persistence through restart, both Setup paths, live list refresh and rejection, cold external launch, and packaged Settings smoke. Eleven focused C++ cases passed. Zero-fuzz preparation and the final corrections matched all 56 affected and generated paths. The preview framework SHA-256 is `af95ce11c6489fe20be9c79e09f3862779f580ac4da6d9503d9f4bae98567736`.

The Apple silicon spacing revision passed the domain exclusion fixture and rendered a 12 px gap with no divider between the description and the Domain field. Its `resources.pak` SHA-256 is `d1abaae6095ae47e3466b4453932b77fcbebd91564e2b3026e912aee003770ea`.

The follow-up preview passed the same domain exclusion fixture and confirmed that the Excluded domains heading matches the font size, weight and color of the setting label above it. Its `resources.pak` SHA-256 is `e1f3ae5452116f8a1580c402e3ef53e72890a61e0aaa02ed932505f7841bf28c`.
