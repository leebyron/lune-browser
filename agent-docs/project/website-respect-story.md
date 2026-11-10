# Respect story: evidence and editorial direction

November 10, 2026. This is website copy research, not a new browser-security or
performance audit. The owner supplied the positioning discussion that treats
respect as the browser’s relationship with its user: private, considered and
personal. The resulting story should show that relationship through observable
choices, without a manifesto or a feature checklist.

## Argument

After the setup-inspired logo reveal, the first sentence introduces Lune as a
private Mac browser with Chromium compatibility and room for the web. The
shorter sequence then establishes boundaries, consent, useful compatibility,
Mac craftsmanship, room for the page, agency during setup and inspectable shared
work. Each point is one complete sentence in the same visual style.

The distinguishing combination is Chromium compatibility, Helium’s privacy and
consent foundation, and Lune’s Mac-focused, page-first interaction work. These
inherited protections are credited; they are not presented as Lune inventions.

## Evidence

| Point | Support and limit |
| --- | --- |
| Google service integrations removed; filtering starts without configuration | [ungoogled-chromium’s objectives and philosophy](https://github.com/ungoogled-software/ungoogled-chromium#motivation-and-philosophy), [Helium overview](https://github.com/imputnet/helium), and [Helium’s defaults](https://helium.computer/). The Lune input includes the ungoogled foundation and bundled uBlock. This does not promise anonymity or that every page element is blocked. |
| Optional services require consent | `ShouldAccessServices` checks both `kHeliumServicesEnabled` and `kHeliumServicesConsented`, with further per-service checks. See the pinned core input’s `patches/helium/core/services-schema-nag.patch`, `services-prefs.patch`, the prepared helper, and [Lune onboarding](features/onboarding.md). Lune’s own browser-update choice is separate; the website does not promise zero background connections. |
| Extensions can download and update through Helium’s proxy | [Helium’s extension explanation](https://helium.computer/), the pinned core service helpers and `patches/helium/core/ublock-helium-services.patch`; [Lune services](services.md) records the provider. This requires consent and enabling the service; it does not make arbitrary extension behavior private. |
| Chromium compatibility with Mac controls and a keyboard command bar | The [frozen release](../../manifests/releases/26.1110.1.json) pins the same current core and platform inputs; [Command-T](features/command-bar.md), [corners](features/command-bar-corners.md), [chrome appearance](features/chrome-appearance.md) and the release evidence record the Mac work. The claim is Mac-specific controls, not a wholly native browser or universal website compatibility. |
| Tabs within reach, chrome steps aside | [Sidebar](features/sidebar-pin-activation.md), [edge frame](features/edge-to-edge-frame.md) and [toolbar modes](features/header-inset-prototype.md). The live website demonstrates this interaction. |
| Setup may be customized or skipped | [Onboarding refinements](features/onboarding-visual-refinements.md) and [onboarding](features/onboarding.md) record the accepted Setup / Use defaults paths. |
| Open source and shared work | The public repository, full component input tags, frozen records and contribution boundaries in the [project definition](README.md). [Helium’s transparency statement](https://helium.computer/blog/transparency) explains the inherited ethic; it is not a Lune policy or guarantee. |

Upstream pages were read live on November 10 and checked against the pinned
Lune inputs, rather than assuming every current Helium website feature ships
in Lune. The [Helium privacy policy](https://helium.computer/privacy) explicitly
excludes derivatives, so its legal assurances are not attributed to Lune.

## Deliberate omissions

Do not promise complete fingerprinting prevention, anonymity, zero network
traffic, universal streaming/DRM compatibility, measured performance or battery
advantages, permanent stewardship, or being always on the latest Chromium.
Do not turn optional research or open feature issues into shipped benefits.
Security maintenance remains important, but the website should not claim a
cadence stronger than the actual release process can demonstrate.
