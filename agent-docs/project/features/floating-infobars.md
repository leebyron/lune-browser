# Floating footer prompts

The owner accepted the footer prompt layout, stacking behavior, and light drop
shadows on November 9, 2026. This extends the Dock-message audit and removal from
the same conversation. The sidebar tint and default-width instructions were
explicitly withdrawn; this patch contains neither change.

## Behavior

- Page prompts float over the bottom of the content area without reducing the
  page viewport. The stack has 8 DIP left, right, and bottom insets.
- Split view uses the combined content area. The active page's prompts retain
  their existing tab ownership and return when that page is focused again.
- Multiple distinct prompts display together, with 8 DIP between rows. Floating
  containers opt out of the previous admission queue and surface already queued
  prompts. Other containers retain their existing priority admission policy.
  Existing delegate deduplication still suppresses identical messages.
- Corners follow the native window radius minus the 8 DIP inset, clamped during
  opening and closing animation. The shape is a rounded rectangle.
- On macOS the border uses AppKit's separator color at one physical pixel,
  matching the mounted sidebar/content divider. Other platforms retain the
  existing theme separator color and thickness.
- Each prompt has a low-opacity, elevation-4 shadow following the same corners.
  The shadow adds no layout or hit-test region.
- The close button has equal 8 DIP top, bottom, and trailing margins. Transparent
  gaps and rounded corners let page input pass through.

The implementation also stops the normal, app, and popup layouts from reserving
space for the former top bar or changing page-top corners when prompts appear.
Sharing controls and security warnings retain their actions and lifecycle.

## Inputs and scope

The signed platform commit is
`eaad00f9148bbe151ae9a85370041d738d6adc70`, based on the already-published
`inputs/downloads-1/macos` input (`e631e3559ca1aba129c0446c06460da4e0493bbb`).
Its only repository changes are `patches/helium/ui/floating-infobars.patch` and
one entry in `patches/series`. The input tag is
`inputs/floating-infobars-1/macos`; the development lock selects it for both
arm64 and x86_64. The previously committed Dock-prompt removal remains inherited.
Existing frozen release inputs, published binaries, and installed apps are unchanged.

## Validation and limits

- Developed in an isolated prepared Chromium 158 tree with quilt, refreshed,
  and unmerged into the macOS component.
- The patch reproduces the edited source with zero fuzz and zero offsets.
  An additional reconstruction starts from exact Chromium source commit
  `6449d9f9a6a906edff724b7b220199b3fde4615c` and replays all 41 relevant
  core/platform patches through the current published downloads input and this
  patch. This patch applies with zero fuzz and zero offsets.
- Fourteen of the fifteen reconstructed files exactly match the accepted preview
  source. The shared native-material implementation retains the downloads input's
  already-published ring-rendering revision rather than the earlier local preview
  revision. The separator helper is identical, and this exact composed translation
  unit compiles for arm64 and x86_64. The downloads revision is not introduced by
  this conversation's commit.
- Full browser and ChromeDriver builds pass for arm64 and x86_64. Native arm64
  checks verify single-page and combined split-view bounds, two distinct ordinary
  prompts, exact 8 DIP gaps and dismiss-button margins, individual dismissal and
  reflow, page interaction, and restoration after switching focused panes.
- The owner accepted the identified native preview. Physical Intel and older
  macOS visual acceptance were not performed for this change.
- Two regression cases cover draining an existing queue, admitting all priority
  classes, individual removal, and restoring admission limits. Their source
  compiles for both architectures; the unit-test executable was not run.
- The earlier broad smoke harness reached loopback navigation and profile
  write/read, but timed out during teardown. It is not recorded as a passing
  smoke run. No signing, notarization, installed-update acceptance, or binary
  release is claimed by this source integration.
- Inherited platform patch lint and inventory checks pass. The lock validator
  checks patch digests, series ordering, immutable tags, trees, core gitlink, and
  upstream ancestry before publication of the source input.
