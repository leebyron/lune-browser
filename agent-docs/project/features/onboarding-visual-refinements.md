# Accepted setup and website visual refinements

The owner accepted the final local previews on November 9, 2026 and authorized
single-thesis commits. No publication or deployment is included in these commits.

## Implementation

- Platform `605c296e` packages light/dark cyanotype JPEGs for setup, without runtime
  blending. Website `00f5c66` uses the identical assets. Root and content backgrounds
  match the sampled 64x64 image centers: #F1F6F2 in light and #012034 in dark.
- Website `9ea1c79` matches setup body text and primary/ghost buttons while retaining
  existing headings and native demo controls.
- Website `411e90b` uses the light/dark PNG exports from the Apple-compiled app icons,
  including the enlarged mark. PNG hashes match the native iconset exports.
- Platform `45518275` and generator `e13779d` fit the shared monochrome vector to its
  square canvas. All ten mapped consumers receive the same geometry. The mark is
  16 by 14.09px within a 16px slot; layout and semantic foreground colors are retained.

## Validation and limits

Final arm64 compilation passes. Website and packaged setup light/dark rendering,
asset hash parity, center-color matching, generator consistency and whitespace
checks pass. The website Dock still opens the interactive demo. Live arm64
inspection in Lune Icon Test confirms the larger default-browser footer mark.
The owner accepted the previews after these checks.

The earlier cyanotype candidate passed both architecture builds and the arm64
packaged onboarding flow. Intel packaged-flow startup failed twice before test
assertions with a missing DevToolsActivePort. The final near-white artwork and
monochrome sizing were rebuilt on arm64; no final Intel build/runtime pass is
claimed for those refinements. No development lock, release, or deployment changed.

Local detailed logs and preview screenshots remain under
`.work/onboarding/cyanotype/`, with the final build in
`.work/onboarding/build-Default.log`. Generated workspaces are not tracked.
