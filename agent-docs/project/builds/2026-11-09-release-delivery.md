# Lune 26.1109.1 production acceptance in progress

This is acceptance evidence, not a publication announcement. The exact browser
source is `24f6531ae722dfa61e214e04a5efde83bf068f4f`; the production-only delivery
correction and newer acceptance tools are separate commits on
`production-release-policy`. Frozen browser inputs and the source kit remain
unchanged. The [evidence index](2026-11-09-release-delivery.json) binds results to
that source and the final Apple silicon DMG.

## Apple silicon

The official build passes compilation and the complete post-build source
inventory comparison. The final app and DMG pass Developer ID signatures,
Apple notarization, stapling and Gatekeeper. Sparkle verifies the signature of
the final immutable DMG bytes. Its signed outer version is 26.1109.1; Chromium
and the framework retain 158.0.8127.18. The app and framework Mach-O deployment
minimums are 13.0, matching the signed plist.

Runtime checks pass on native Apple silicon in isolated headless profiles:
UI/defaults/settings persistence, light/dark artwork, attribution, Helium bangs,
bundled uBlock filtering and list updates, and the complete packaged onboarding
flow. The actually installed Sparkle update passes visible About/version-page
identity, public HTTPS browsing to helium.computer and lune.computer, and profile
persistence across restart. Update acceptance uses loopback fixtures serving the
exact final signed DMG, not a public staging channel. Its positive test updates
published build 2 to 26.1109.1. Invalid-signature and unsupported-OS cases both
retain build 2, preserve the profile and pass relaunch/signature checks.

Normal headed checks also pass on the updater-installed Apple silicon app in a
separate disposable profile, launched without headless, debugging or feature
flags. Command-T opens public HTTPS sites and lune://version; Command-L selects
the URL. The version page and About display the signed release and engine
versions, and About retains Helium attribution. Entering and leaving fullscreen
keeps the native controls visible. Unpinning the sidebar and restoring its pinned
setting work. A synthetic bookmark survives a normal application-menu Quit and
relaunch with the same profile. The headed app uses the loopback fixture solely
for update checks; its embedded feed remains the production GitHub URL.

Saved native accessibility snapshots and screenshots are indexed below by hash.
These checks do not establish edge-pointer behavior, older-macOS compatibility
or native Intel acceptance. The Chrome Web Store opens, but extension installation
and update remain untested pending approval of its displayed terms; no extension
has been installed in this profile. The store's install button still says
"Add to Helium"; this inherited label is recorded, not treated as fixed.

The portable manual-update fixture passes a real loopback transfer of the final
Apple silicon DMG under macOS's Python 3.9.6, with all 167,305,692 bytes matching
the signed artifact's SHA-256. Its 16 release regression tests also pass,
including draft discovery and local update/wrong-architecture feed routing.
This establishes helper compatibility and byte delivery, not native Intel
browser acceptance; that check still requires the owner's hardware.

Two acceptance-test corrections were required; neither changes browser inputs:

- The accepted artwork uses wallpaper-light.jpg and wallpaper-dark.jpg. The old
  onboarding test still expected wallpaper.jpg. The corrected assertion follows
  the actual color scheme, and the complete flow now passes.
- The new runtime test navigated during uBlock startup. WebDriver's trace shows
  a reload aborting that navigation; bundled uBlock's unsuspendAllRequests has a
  matching tab-reload path. Waiting for its filter readiness resolves the test
  without disabling blocking or changing the app. Internal WebUI navigation uses
  ChromeDriver's canonical chrome:// URLs and verifies rendered version text.
  The earlier failed reports remain locally available; they are not acceptance.

## Remaining gates

Intel's frozen official build is still compiling. It requires matching signing,
packaging, smoke/onboarding, signed runtime and positive/negative installed-update
checks. Rosetta results cannot replace the owner's native Intel acceptance on
macOS 13.7.8 and the second Intel Mac (exact version pending).

Intel headed/native interaction, extension installation/update, wrong-architecture
offer rejection on native Intel, public HTTPS installed updates, fresh Chromium
comparison, public source/artifact verification, stable-feed readback, latest-link
readback and production website deployment remain to be completed. Historical
build-1/build-2 staging files are unchanged. No new release, feed, source package,
or website deployment has been published by this work yet.
