# Setup safe areas and progress

Owner-requested setup navigation changes, adopted November 14, 2026 through `inputs/setup-safe-area-1/macos` at `71aa6b039d1c9a8d5085c0ae80085c3b20c43701`. This selects future main builds; published 26.1113.1 remains unchanged.

Floating browser alerts contribute their actual occupied bottom region to `env(safe-area-inset-bottom)` for documents using `viewport-fit=cover`. The value composes with existing physical/header insets, follows navigation and layout, and clears when the last alert disappears. Immediate removal now invalidates the container layout, including alerts whose animation is disabled. The read-only contents lookup avoids creating a WebContents during early window layout.

Setup opts into viewport coverage and positions its fixed controls above that inset. Progress includes Welcome and every reachable step; dots navigate in either direction without importing, accepting service consent or completing setup. Choices remain intact. Dots are 8px wide, separated by 12px, with 16px visible clearance above and below. Hover only changes dot color intensity. Tooltips appear immediately, with bold white text on a black pill in both color schemes, 5px from the dot. The footer has no entrance or safe-area-position animation.

The backdrop fade begins 12px above the actual button row and reaches the true viewport bottom, below the safe inset. Scroll clearance keeps the final content item fully above the fade; the old independent scroll mask is removed. Cyanotype artwork transitions from full opacity on Welcome to 50% on setup steps, independently of its introductory reveal. Reduced motion disables those animations.

## Validation and limits

Both architecture builds, packaged onboarding/navigation/style checks, small-window and dynamic viewport-fit checks, browsing, Settings and profile persistence pass. Intel executes under Rosetta. Native review confirms that closing the automation alert changes the inset from 52px to zero with no resize event or viewport-size change. The final search card sits about 12px above the fade at the bottom of the scroll area. All 17 focused preimages match the frozen preparation inventory; exported patches replay with zero fuzz and offsets and exact source parity. The later accepted base inputs were replayed before paired final builds.

The [completion record](../builds/2026-11-14-setup-safe-area-progress.json) records source identities, artifact guards and timings. Multiple simultaneous alerts, fullscreen and page zoom remain unverified; no fresh full Chromium preparation was performed. [Issue #35](https://github.com/leebyron/lune-browser/issues/35) remains open for the remaining defaults, service explanation, import and privacy work.

Temporary previews, test profiles and disposable replay snapshots are closed and removed. Shared prepared source, incremental outputs, compiler caches and concise reports/screenshots remain for continued setup work.
