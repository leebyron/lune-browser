# Respect story: November 10 research

Historical source review from November 10, 2026, retained for its evidence and
limitations. It is not a current browser-security or performance audit. Current
copy, order, interaction requirements, and claim boundaries belong in the
[website specification](../../website/spec/experience.md). The original proposed
copy and ordering have been superseded.

## Evidence

| Point | Support and limit |
| --- | --- |
| Google service integrations removed; filtering starts without configuration | [ungoogled-chromium’s objectives and philosophy](https://github.com/ungoogled-software/ungoogled-chromium#motivation-and-philosophy), [Helium overview](https://github.com/imputnet/helium), and [Helium’s defaults](https://helium.computer/). The Lune input includes the ungoogled foundation and bundled uBlock; `ublock-install-as-component.patch` calls `AddUBlock()` during component loading. This does not promise anonymity or that every page element is blocked. |
| Third-party cookies blocked by default | The frozen Helium input `inputs/helium-2026-11-09/helium`, `patches/inox-patchset/modify-default-prefs.patch`, changes `kCookieControlsMode` from `kIncognitoOnly` to `kBlockThirdParty`. This limits one tracking mechanism; it does not prevent all tracking. |
| Optional services require consent | `ShouldAccessServices` checks both `kHeliumServicesEnabled` and `kHeliumServicesConsented`, with further per-service checks. See the pinned core input’s `patches/helium/core/services-schema-nag.patch`, `services-prefs.patch`, the prepared helper, and [Lune onboarding](features/onboarding.md). Lune’s own browser-update choice is separate; the website does not promise zero background connections. |
| Extensions can download and update through Helium’s proxy | [Helium’s extension explanation](https://helium.computer/), the pinned core service helpers and `patches/helium/core/ublock-helium-services.patch`; [Lune services](services.md) records the provider. This requires consent and enabling the service; it does not make arbitrary extension behavior private. |
| Command-T searches tabs, history and the web | The [26.1110.1 frozen release](../../manifests/releases/26.1110.1.json) identifies the reviewed core and platform inputs; [Command-T](features/command-bar.md), [corners](features/command-bar-corners.md), [chrome appearance](features/chrome-appearance.md) and the release evidence record the Mac work. The claim is Mac-specific controls, not a wholly native browser or universal website compatibility. |
| Tabs within reach, chrome steps aside | [Sidebar](features/sidebar-pin-activation.md), [edge frame](features/edge-to-edge-frame.md) and [toolbar modes](features/header-inset-prototype.md). |
| Setup may be customized or skipped | [Onboarding refinements](features/onboarding-visual-refinements.md) and [onboarding](features/onboarding.md) record the accepted Setup / Use defaults paths. |
| Open source and shared work | The public repository, full component input tags, frozen records and contribution boundaries in the [project definition](README.md). [Helium’s transparency statement](https://helium.computer/blog/transparency) explains the inherited ethic; it is not a Lune policy or guarantee. |

Upstream pages were read live on November 10 and checked against the pinned
Lune inputs, rather than assuming every current Helium website feature ships
in Lune. The [Helium privacy policy](https://helium.computer/privacy) explicitly
excludes derivatives, so its legal assurances are not attributed to Lune.

For current claim constraints, use [Claims and scope](../../website/spec/experience.md#claims-and-scope).
