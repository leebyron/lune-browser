# Privacy policy source review

November 14, 2026. The owner requested a policy draft and generated page for local
review, then accepted the result and authorized publication on the same date. The canonical text is
[legal/privacy.md](../../legal/privacy.md); the [website instructions](../../website/README.md)
describe building `/privacy`. The owner confirmed on November 14, 2026 that `privacy@lune.computer` is
configured. The policy now links it as the private contact address. Mailbox
provider, access and retention still need confirmation.

## Source basis and limits

Reviewed the main development lock selecting macOS
`956bc5a32fbdc7cdf89ee1ba5946683a6f69d71f` and core
`f7d3113d2a0b271fc57d354e058b0ddc3c60ab71`, including the prepared source in the
existing `.work/older-tabs-arrangement/platform/build/src`. No source copy was made. Setup now has a focused privacy-link patch selected for future builds. The published release remains 26.1114.1;
the revised Services/one-time installer flow is future-build behavior. This
draft does not claim a new packaged-browser network capture or legal approval.

| Topic | Evidence | Draft treatment |
| --- | --- | --- |
| Local profile and absence of Lune backend | Project service architecture; owner confirms no hosted Lune browser services | Distinguish local profile from websites, extensions, backups and optional requests; no absolute “nothing leaves the device” promise. |
| Service gates and recipients | `components/helium_services/helium_services_helpers.{h,cc}` in prepared source | Helium default origin, independent GitHub update feeds, child service gates, instance overrides. No assumption that the service master controls crash reporting. |
| Setup consent and password managers | [Accepted Services feature](features/setup-services.md) and its bound regression evidence | One-time installation is future-build behavior. It neither enables future extension updates nor migrates vault contents. |
| Crash reports | `components/crash/core/app/crash_reporter_client.cc`, `chrome/browser/prefs/browser_prefs.cc`, `chrome/browser/crash_upload_list/helium_crash_reporting.cc`; core `crash-reporting-prefs.patch` and `crash-reporter-privacy-tweaks.patch` | Official-build endpoint is `https://crash.helium.computer/crash`; nonofficial builds have no default upload URL. Default mode is Ask; Automatic explicitly enables uploads. Local pending reports and possible memory contents are disclosed. A crash-server command-line override exists. Do not infer absence of crash reports from unbranded `GetCollectStatsConsent()`. |
| Crash privacy hardening | Core crash privacy patch | Startup disables uploads before starting the handler, removes arbitrary switch values and the GUID query parameter, and zeros the Crashpad client ID. These protections do not prove reports contain no sensitive data. |
| Browser updates | Current services helpers, `chrome/browser/mac/sparkle_glue.mm`, release delivery records | GitHub feed/download traffic; do not promise that Sparkle's full wire metadata has been captured in this audit. |
| Website | `website/public/index.html`, `main.js`, `styles.css`, `wrangler.jsonc`, `_headers` | Static hosting, no application storage bindings or API handler, locally served fonts/images, no source analytics/cookie/storage calls. Device architecture selection is local. Cloudflare account-level behavior remains unverified. |
| Live website | Read-only HTTPS retrieval of `https://lune.computer/` | HTML contained only the local `/main.js?v=64e02885f9a9` script; no analytics script observed in that response. This is not a Cloudflare account/log audit. |
| Support and retention | No verified operational inventory available in this task | Keep explicit draft notes for mailbox provider, access, attachments, retention and any crash/statistics access. Do not invent periods or blanket selling/sharing promises. |

## Provider sources

- [Helium privacy policy](https://helium.computer/privacy), revision July 16, 2026:
  describes its services and crash reporting but excludes derivatives. That
  leaves coverage of Lune-origin service requests unclear. The draft does not
  adopt its browser-wide assurances or retention periods. Clarification is
  required; no outreach has been sent or authorized here.
- [GitHub privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement):
  describes request/usage information and user-submitted content. Lune cannot
  set GitHub's independent retention or deletion practices.
- [Cloudflare privacy policy](https://www.cloudflare.com/privacypolicy/):
  distinguishes customer-property end users from Cloudflare's own website
  visitors and describes processing of traffic data. Review the actual Lune
  account configuration before claiming no analytics or logs at the host.

## Live analytics correction

A November 14 browser inspection of production loaded
`https://static.cloudflareinsights.com/beacon.min.js/vce701823e78c4301a35b7e07294d87301792088814092`
(HTTP 200) and sent a POST to `https://lune.computer/cdn-cgi/rum?` (HTTP 204).
The body included the page URL, a per-page-load ID, browser/OS version details,
JavaScript memory measurements and navigation/paint timings. No Cookie header
was present on that observed request; this does not establish a site-wide
no-cookies guarantee. The policy no longer makes that guarantee or claims no
analytics scripts.

This supersedes the earlier implication drawn from repository source and one
HTML response. Cloudflare can add the beacon at delivery, as documented in its
[RUM guide](https://developers.cloudflare.com/speed/observatory/rum-beacon/).
Its [edge analytics](https://developers.cloudflare.com/analytics/account-and-zone-analytics/zone-analytics/)
also measure requests independently of browser scripts. The page now discloses
traffic and performance analytics. Account access, configuration and retention
still require verification; no settings were changed. The local development
server does not inject this production analytics script.

## Personal-project legal research

An individual can be responsible for processing; a company is not a prerequisite.
GDPR Article 4(7) includes natural persons in its controller definition. Assess
actual purposes, means, and territorial scope for each activity instead of
equating browser authorship with control of every website request. The
[official GDPR text](https://eur-lex.europa.eu/eli/reg/2016/679) and its indexed
Article 4/Recital 18 excerpts support this distinction; direct full-text access
was challenged by EUR-Lex during this review.

The [ICO exemptions guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/exemptions/a-guide-to-the-data-protection-exemptions/)
limits the domestic exclusion to purely personal/household processing without
a professional or commercial connection. “Personal project” alone does not
establish an exemption. The [ICO transparency guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-be-informed/)
identifies purposes, bases, recipients, retention, transfers and rights among
the disclosures to evaluate where applicable. Its page is marked under review
following the UK Data (Use and Access) Act; do not treat it as a final
jurisdiction-specific determination for this project.

California's [CCPA guidance](https://oag.ca.gov/privacy/ccpa) describes business
and threshold criteria; [CalOPPA guidance](https://www.oag.ca.gov/privacy/facts/online-privacy/privacy-policy)
separately covers commercial websites and online services collecting relevant
information. Assess actual circumstances. The draft neither asserts blanket
applicability/exemption nor imports Helium's Wyoming governing-law clause.
Final legal applicability remains unresolved, rather than silently filled in
from a corporate template.

## Publication decision and remaining audit work

The owner accepted the reviewed policy and explicitly authorized publication on
November 14, 2026. Its metadata now records that effective date and published
status. The following questions remain audit follow-ups; publication does not
claim they have been independently resolved. The policy makes no provider
retention promise, corporate exemption claim, or legal-compliance certification.

- The owner confirms the mailbox is configured; establish private request handling
  and confirm monitoring, provider, access and retention.
- Inventory maintainer access, Cloudflare analytics/security/logging, support
  providers, retention/deletion and international processing. Fill any applicable
  legal bases and rights disclosures from that inventory.
- Verify telemetry, update metadata and crash behavior in the release the
  notice will cover, including pre-consent, disabled and enabled configurations.
  Do not transmit a real crash dump simply to test reporting.
- Clarify derivative-client coverage with Helium before making provider-policy
  assurances. The crash endpoint is part of this question too.
- Keep coverage aligned with current and future-release behavior. Review whether
  material changes require additional notice. The public footer carries the
  revision date and links to the versioned source and edit history.
- The setup link to `https://lune.computer/privacy` is selected for future builds.
  Frontend checks, compiled-bundle verification and strict patch replay pass.
  The owner waived paired architecture checks for this hosted-link/CSS change.
  The website footer link is included. Settings/About linking and inherited
  consent/terms wording remain follow-ups; issue #35 stays open.

## Paragraph relevance review

Reviewed each paragraph on November 14 at the owner's request. Keep text that
identifies the responsible person, scope, data, purposes, recipients, controls,
rights or policy changes. Move implementation/review instructions here. Do not
trade away necessary disclosures merely to reduce word count.

| Original paragraph or item | Decision and reason |
| --- | --- |
| Maintainer and scope | Keep: identifies who is responsible and what is covered. |
| Draft status | Subsequently removed from the visible page at the owner's request. Publication was subsequently authorized on November 14; published metadata removes noindex. |
| Browser profile | Keep local storage and absence of upload/sync. Change “stay” to “are stored” to avoid implying data can never leave through websites/extensions. Remove generic backup language and repeated deletion guidance. |
| No Lune backend / provider requests | Keep: distinguishes maintainer receipt from third-party processing and names common IP disclosure. |
| Browser updates | Keep recipient, request fields and independent control. Those explain a connection that can remain enabled when Helium is off. |
| Search | Keep: sending text before submission is material, as are the recipient and enablement condition. |
| Helium services | Keep operator, absence of an account requirement, and feature-specific requests, including local bang matching and optional filter refreshes. These explain identity requirements and data sent. |
| Proxy limits / custom providers | Keep: prevents the mistaken belief that installed-extension traffic or all filter requests stay behind Helium's proxy, and identifies the alternate recipient. |
| Password-manager setup exception | Keep only the separately authorized connection while services are off. Describe a one-time download, not a single HTTP request; metadata and package delivery can require several requests. |
| Helium policy relationship | State the scope directly: this policy covers Lune; Helium’s policy is informative about its services and does not govern Lune. Keep the derivative-coverage question in these internal notes rather than vague public-facing language. No provider-retention assurance is added. |
| Crash reporting | Keep default/automatic/disabled choices, independent control, recipient, local pending reports and sensitive-memory risk. Retain the macOS distinction to avoid implying this controls system diagnostics. |
| Cloudflare hosting | Keep recipient and request fields, with its policy link. |
| Website code | Replace the misleading absence-of-analytics claim after a live browser confirmed Cloudflare-injected analytics. Disclose page URLs, browser/OS details and performance measurements. Keep same-site fonts/artwork and local device detection. |
| Support messages | Keep what is received, why, and the public nature of GitHub issues. Remove advice about preparing attachments; that belongs in support guidance. |
| Contact / rights | Keep private contact, access/correction/deletion route, provider boundary and applicable rights. Remove repeated inability to retrieve local profiles. |
| Settings controls | Consolidate local deletion and connection controls here; retain the distinction between disabling and deleting previously sent data. |
| Changes | Subsequently removed as redundant with the footer revision/history links. Review any further material-change notification requirements as the project evolves. |
| Before-publication checklist | Move out of the policy; retained above with release, telemetry, crash, host, retention and legal questions unresolved. |

## Local build

The structural review groups the policy into five top-level topics: data on the
device, browser connections, website visits, information sent to the maintainer,
and choices/rights. Revision date and source/history links live in the footer;
the redundant policy-changes section was removed. Browser updates, search/suggestions, Helium
services and crash reports are subsections of browser connections. Crash
reporting retains its explicit independent-control disclosure. Information
received through correspondence is separate from the private request route,
which now follows Settings controls under choices and rights. The generated
contents list follows these top-level headings automatically. This changes
organization, not the disclosed data practices or unresolved publication gaps.

The build uses pinned `markdown-it` with raw HTML and automatic linkification
disabled. The page has no JavaScript, embeds or third-party fonts. It includes
section navigation, source/history links, revision metadata, selectable text,
light/dark colors and responsive/print styles. The Markdown download matches the
canonical file byte for byte. Generated files stay out of Git.

The deployment command refuses draft metadata, missing effective dates or
unresolved draft/placeholder markers. This prevents an accidental normal
deployment of the draft; it is not a substitute for publication review. The
existing main-push website workflow also watches `legal/privacy.md`. The owner
subsequently authorized commit, push and publication.

Local validation passes: five renderer/build tests, Wrangler deployment dry run,
served HTML/source byte parity, plain-text source response, homepage link, and
production-draft rejection that preserves the last successful local build.
Desktop 1440×1000 and mobile-emulated 390×844 checks cover light/dark rendering,
no horizontal overflow, section fragments and reachable footer. The privacy page
loads no scripts or cross-origin subresources. These are desktop browser
emulation checks, not physical iPhone acceptance. Evidence is retained in
`.work/privacy-draft/validation.json`. The local review server was used at `http://localhost:8787/privacy`. Publication
and final cleanup are recorded separately.
