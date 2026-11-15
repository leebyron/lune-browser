# Terms page review

November 14, 2026. The owner requested a terms document after privacy publication, using the same generator. [legal/terms.md](../../legal/terms.md) was prepared as a local draft for `/terms`; it is now published effective November 15, 2026. The reviewed privacy introduction updates are published with it.

The draft follows the accepted privacy notice's terse personal-project voice. It names Lee Byron, preserves software-license rights, distinguishes third-party services, states availability/warranty limits and addresses liability with an express preservation of non-waivable rights. It links the privacy notice, public issue tracker and confirmed private privacy address. It creates no account, purchase, donation, arbitration, governing-law, indemnity or automatic future-consent regime.

## Source basis

- [Lune NOTICE](../../NOTICE) and [LICENSE](../../LICENSE): original work is GPL-3.0-or-later except where noted; imported work retains its licenses. The draft refers to those instruments rather than imposing additional software-use restrictions.
- [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html), especially sections 2, 7, 10, 15–17, and the [GNU licensing FAQ](https://www.gnu.org/licenses/gpl-faq.html): preserve license permissions and the existing warranty/liability allocation. The repository's full license was read; GNU search excerpts confirmed the official references, although direct page fetches timed out.
- [Helium terms](https://helium.computer/terms), revision July 8, 2026: useful organization and provider reference. Lune does not copy imput LLC's identity, tip rules or continued-use acceptance provision. Helium's terms remain linked as provider information, without asserting their applicability to every derivative-client request.
- [California Supreme Court opinion S282968](https://supreme.courts.ca.gov/sites/default/files/supremecourt/default/2026-08/S282968%20-%20R.pdf): official search evidence cautions against purporting to waive responsibility for willful injury under Civil Code 1668. The draft preserves non-excludable liability and applicable rights; no conclusion about enforceability, governing law or all applicable jurisdictions is claimed.

## Generator and checks

`website/scripts/legal.mjs` contains the shared renderer and page identities. `website/templates/legal.html` and `website/public/legal.css` provide the shared shell. Both documents use the same metadata, heading anchors, contents navigation, sticky logo, source/history links and revision footer. Raw HTML and unsafe link schemes remain disabled. Each source download exactly matches its canonical Markdown.

Seven renderer/build tests pass, covering both documents, unsafe content and metadata, unique heading anchors, publication guards, source parity and per-page URLs. A production build with draft terms fails before changing the successful local output. Desktop Light and mobile-emulated Dark checks confirm working section targets, the sticky desktop logo, hidden mobile contents and no horizontal overflow. These checks are not physical iPhone verification or legal approval.

The owner approved publication on November 15, 2026 after wording review. Adopt the setup and About legal-link patches with the internal terms-page link. Issue #35 remains open for the broader setup work. No new native browser build is needed to review the hosted page.

## Paragraph review — November 15, 2026

Reviewed every paragraph against relevance, brevity, browser focus and placement. The order is now operator/scope → software rights → outside services → warranties/liability → privacy/contact. Website coverage remains explicit but secondary. No additional obligations or service guarantees are introduced.

| Paragraph | Review and resulting change |
| --- | --- |
| Introduction | Identify the browser, individual maintainer and personal-project status first. Link the maintainer. Keep website scope in one short second sentence, with the requested hard break. |
| License provenance | Add linked Chromium and ungoogled-chromium alongside Helium. This explains the browser's composition and retained component licenses; it does not characterize those projects as service providers. Combine this with Lune's own GPL-3.0-or-later statement and preserve the “except where noted” qualifier. |
| License rights and references | Keep the practical rights to use, copy, modify and redistribute, and the protection against extra restrictions. Move the notice/bundled-license references here. Link `chrome://credits` directly, as subsequently requested by the owner. |
| Outside services | Tie the list to browser actions: visiting sites, installing extensions and using search or optional services. Combine separate-operator responsibility with the terms boundary. Avoid asserting a single set of provider terms governs everything. |
| Helium services | Keep Helium/imput links and the provider terms link because Helium has both upstream-code and service roles. Explicitly distinguish Helium's services from the Lune browser. No derivative-client contract assurance is added. |
| Warranty and availability | Lead with the browser and retain the existing license-consistent warranty qualification. One sentence addresses support, updates and availability; no separate uptime-oriented section is needed. |
| Liability and website coverage | Replace the website-centered paragraph with the browser's applicable license limitations, naming data loss and inability to use the browser. Link the project's notice, which directs readers to the applicable component licenses. Keep website coverage as a secondary sentence rather than omitting its scope or making it the main subject. |
| Mandatory rights | Retain immediately after the disclaimers: it prevents the text from claiming exclusions beyond what law permits. This is substantive, not boilerplate to cut. |
| Privacy | Keep a short policy link and the private privacy contact together. Do not duplicate the privacy policy's disclosures. |
| Other questions | End with the public project/terms contact route and a clear statement that issues are public. Separate this from privacy questions so readers do not inadvertently post them publicly. |

Additional primary-source checks: [Chromium project overview](https://www.chromium.org/chromium-projects/), [ungoogled-chromium license](https://github.com/ungoogled-software/ungoogled-chromium/blob/master/LICENSE), [Helium terms](https://helium.computer/terms), and Lune's bundled NOTICE/LICENSE. These support project identity, retained licensing and warranty/liability references; they do not establish enforceability of this draft in every jurisdiction.

The owner accepted four further editorial refinements: explicitly connect optional Lune features to Helium services; separate support/availability expectations from the warranty paragraph; label the NOTICE link “license notices” and describe its role accurately; and match the privacy page’s linked “lune.computer” followed by unlinked “website.” These edits retain the existing scope and draft status.

## Setup wording and app-link audit — November 15, 2026

The owner accepted the shorter browser-liability sentence and the setup footer “Read Lune’s privacy policy and terms of use.” Setup now points to `https://lune.computer/privacy` and `https://lune.computer/terms` in the shared prepared source, exported as `lune/onboarding-legal-notice.patch`. Svelte/TypeScript checks, production frontend bundling, patch lint and zero-fuzz exact-source replay pass. This patch is pending adoption/publication; no native build was run, consistent with the owner's link-only validation direction. Terms remain a hosted-page draft.

Source audit of the current Lune macOS configuration:

- **Setup:** the product-wide legal links are in `components/helium_onboarding/src/components/WelcomeFooter.svelte`; their copy is generated from `helium_onboarding_strings.grdp`. Both Lune destinations and the read-only wording are now implemented.
- **About Lune:** the app menu invokes `ShowAboutChrome`, which opens `chrome://help/`. The Settings About template includes privacy and terms controls, but both are gated behind Google Chrome branding (terms also allows Chrome for Testing branding). Lune's generated branding flag is false. The hidden privacy target is the inherited disabled Google policy domain; the hidden terms target is `chrome://terms/`. Neither currently exposes Lune's hosted notices. Recommend visible Lune policy/terms links here after `/terms` publication; this audit did not change About.
- **Internal terms page:** `chrome://terms/` is registered and loads `IDS_TERMS_HTML`; unbranded builds use `components/resources/terms/terms_chromium.html`. That resource is a “This Space Intentionally Blank” placeholder saying official builds show terms here; it is not a license notice. Consider replacing the placeholder with a link to Lune’s hosted terms.
- **Password-manager choices:** their privacy links point to Proton, Bitwarden, 1Password, KeePassXC, Dashlane and Apple. These are provider disclosures and remain unchanged.
- **Helium Services settings:** no separate privacy/terms link was found in `privacy_page/services_page.{ts,html}`. Its instance URL is a service endpoint, not a legal-document link.
- Other source matches belong to ChromeOS, branded Google features, or provider-specific disclosures; they are not evidence of another visible Lune macOS legal link. This is a source/configuration audit, not a complete runtime navigation crawl.

The shared Git repositories had stale alternates pointing at a removed preflight checkout. Their references were redirected to the already-present main repository object store only after verifying all existing refs and object connectivity. No Chromium source copy was created.

The separate website warranty/liability sentence was removed during owner review. This keeps the terms focused on the application and its existing software licenses. It removes an express website-specific disclaimer; it does not establish that the site processes no data or has no potential liability. The privacy notice continues to disclose Cloudflare hosting and analytics.


## About links — November 15, 2026

At the owner's request, pending platform patch `lune/about-legal-links.patch` adds visible Privacy policy and Terms of use links alongside the existing About Lune license information. Both use localized labels and open `https://lune.computer/privacy` and `https://lune.computer/terms` in a new tab. They are outside Chrome branding guards; the inherited Google-only controls remain unchanged.

Validation passes: unbranded macOS resource preprocessing retains both links; the labels parse and are registered unconditionally; the preprocessed TypeScript template compiles syntactically; strict zero-fuzz/zero-offset patch replay matches the edited source; merge/unmerge export and platform patch lint pass. No native browser build or runtime click verification was performed for this hosted-link change. Evidence: `.work/about-legal-links/validation.json`. These links are pending adoption and are not in the installed or published browser; publish `/terms` before shipping them.

The cleanup chat subsequently made the retained platform/core repositories self-contained and verified connectivity with no alternates. Its preservation report confirms the existing legal draft and tracked work survived unchanged. No additional source copy was created.


## Publication and browser adoption — November 15, 2026

The owner requested both publication and replacement of the internal terms placeholder. Website commit `7bb87498c981d2d6f21eaa2867e26916c6fabda6` passed the seven renderer tests, production build, deployment dry run, GitHub setup checks and Website deployment. Public HTTPS readback matches all 47 served files, including both pages and canonical Markdown. See [publication evidence](builds/2026-11-15-terms-publication.json).

The setup notice, About links and `chrome://terms` link are selected for future builds through signed input `inputs/browser-legal-links-1/macos`. Internal terms retains its lightweight bundled HTML and now links to the hosted terms; GRIT selects that resource for the unbranded macOS configuration. Strict replay and resource checks pass. See [browser-link evidence](builds/2026-11-15-browser-legal-links.json). No native build or browser release was performed under the owner's link-only validation scope; the installed application remains unchanged. Earlier pending/draft descriptions above record their original review stage.

Final [adoption checks](https://github.com/leebyron/lune-browser/actions/runs/43695635916) pass on attempt 2 after refreshing a clean CI-only checkout left on the previous input. The obsolete CI checkout and review servers on ports 8787/8788 are removed/stopped; use the public URLs now. Shared source, incremental outputs, caches and compact validation evidence remain.
