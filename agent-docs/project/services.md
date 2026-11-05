# Self-hosted services and website

Status: proposed deployment. Domains, hosting, and credentials are not configured.
Source findings are recorded in [research](research.md).

## Start with Helium's own stack

Track `imputnet/helium-services` on its upstream-derived component branch. Use a
small Linux VM/container host with Docker Compose initially, because that matches
the existing implementation. Keep Lune environment templates and deployment
overlays under `deploy/` on `main`. Pin the services commit and deployed image
digests; do not automatically deploy an unreviewed moving branch.

| Component | Initial treatment |
| --- | --- |
| nginx, TLS, dictionary delivery | Deploy; configure hostname/certificates and Lune root redirect |
| Chrome Web Store extension proxy | Deploy; configure public base URL and unique HMAC secret |
| uBlock filter proxy | Deploy; preserve compatible filter/update paths |
| Bangs data | Serve from the stack; track refresh behavior and data sources |
| Sparkle feeds | Static output of the validated Lune release pipeline |
| Website download manifest | Generate from promoted Lune releases |
| Crash collection / minidumpster | Optional later; needs symbol storage and explicit product policy |
| Push service / minipush | Optional later; only if matching browser functionality is enabled |

The inspected Compose configuration includes nginx, extension-proxy replicas,
ubo proxy, and acme.sh. Bangs/dictionaries are served through nginx; other utilities
are not automatically started by the main Compose file. Do not assume running
`compose up` deploys every feature listed in the upstream README.

Helium supplies `sparkler` to generate macOS appcasts from GitHub releases and
`release-collector` to gather download metadata. Prefer the Xelium-style release
pipeline as Lune's sole feed writer initially. Running both it and a periodic
sparkler writer would create competing publication paths. Reuse these utilities
later only after adapting repository names, artifact naming, and promotion policy.

## Domain and client contract

Plan distinct roles under the owner-supplied domain:

- Website: product information, downloads, source, release status, privacy details.
- Services hostname: extension proxy, filters, dictionaries, bangs, connectivity.
- Updates hostname/path: static appcasts and release manifests.

Keep service paths compatible with the client: upstream currently exposes
`/ext/`, `/com`, `/ubo/`, `/dict`, `/bangs.json`, and `/connectivitycheck`.
The example environment configures `SERVICES_HOSTNAME`, `PROXY_BASE_URL`,
`UBO_PROXY_BASE_URL`, `HMAC_SECRET`, and certificate contact details.

Audit browser service preferences, extension/updater URLs, bundled uBlock settings,
onboarding links, and privacy/help links. Set Lune defaults in a small distribution
layer; do not rewrite all domains mechanically. Keep service consent controls
working and prevent an accidental fallback to Helium's production endpoints.
Validate the actual outbound requests of a packaged browser, not just config text.

## Deployment and validation

Use upstream setup/Compose as a starting point, not its entire production network.
Its Ansible/BGP setup is unnecessary for a first small deployment. The current
Compose defaults to IPv6 support; choose a suitable host or supply an explicit
network override. Arrange persistent certificate/secret storage and backups,
health checks, renewal checks, and a rollback to the prior image set.

Before switching browser defaults, verify TLS, certificate renewal, extension
installation and update, filter refresh, dictionary download, bangs lookup,
connectivity checks, and service failure behavior on both architectures. Avoid
general request logging that would undermine the privacy goals; document any
operational logs and their retention. Add rate limits without turning the extension
endpoint into an unrestricted open proxy.

Audit component licenses and preserve source/attribution when importing code.
The upstream services repository identifies its code as AGPL-3.0; browser-specific
code identifies GPL-3.0 with retained licenses for imported portions. Include
the actual source/build information with deployments and releases, and review
the relevant license texts before distribution. This bootstrap does not assign
a blanket license to mixed upstream code.

## Website

Keep a small Lune-owned static website on `main`; select a framework only when
there is a concrete need. Hosting should be independent of the browser build and
service runtime. Display both macOS downloads, minimum OS, current Chromium
version, release date, checksums, source links, and the relationship to upstreams.

Read download URLs and versions from the promoted release manifest. Detecting
architecture can improve the default choice, but always show both alternatives.
Use original Lune branding; Helium's UI library and website are optional references,
not dependencies required to self-host its services.
