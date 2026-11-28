# Onboarding and native toolbar integration

The owner completed design feedback and authorized single-thesis commits and
publication to main on November 9, 2026. The platform stack follows the reviewed
`01905fc411a170d7498ea04b3e315111bb806925` input without rewriting its ancestry.
The development lock selects `d499c418e7d1e85c8447830401a4926d97882e2d` under `inputs/onboarding-2026-11-09-2/macos`.
No binary release or update-feed promotion is part of this integration.

## Implementation commits

The first commit removes the native toolbar prototype launch gate. Generic
browser behavior remains separate from Lune branding and distribution choices.

| Commit | Single thesis |
| --- | --- |
| `2eb08f11` | Enable native toolbar inset and cover modes without launch flags |
| `0713fe54` | Keep native sidebar spacing independent of toolbar visibility |
| `fb2282d8` | Describe sidebar pin actions in native tooltips |
| `33f5bf39` | Keep automatic browser updates independent of optional services |
| `b3421691` | Display and accept the Lune internal URL scheme |
| `08b72004` | Keep auxiliary panels opposite the tab sidebar |
| `57112ce6` | Define distinct native System and branded Lune theme palettes |
| `fa34d0de` | Expose System and Lune presets with native swatch colors |
| `df94e1cb` | Default new search choices to Startpage before Kagi and DuckDuckGo |
| `6f78e8d9` | Refresh Lune setup with local artwork and native appearance controls |
| `12fc4916` | Identify the setup tab with a welcome title and envelope symbol |
| `190cc762` | Match the setup root background to the painted page |
| `d499c418` | Match native tab symbols to the tab title foreground |

## Final behavior

- Setup offers On hover and Always. The native right-click menu also retains
  Always cover (experimental).
  The existing 52 pt inset, viewport-fit cover handling and safe-area values use
  saved preferences directly on macOS. No Lune launch flag is required.
- Toolbar visibility does not change native sidebar glass or its 4 px horizontal
  padding. The sidebar button describes its action: Pin sidebar or Unpin sidebar.
- Internal URLs display and accept `lune://`. The setup tab is Welcome to Lune,
  with native `envelope.open` artwork. Native tab symbols use the same resolved
  foreground as the tab title, including white System selection text; website
  favicons retain their original artwork.
- Setup uses bundled website wallpaper, Inter/Syne fonts and a transparent double
  lune mark. No background or font is fetched remotely. Light uses the website's
  #E7EDE3 base and a 10% screen-blended image; dark uses a darker tint. The document
  root, body and main share the sampled center color (#E7EDE4 / #0A2B44), including
  the reserved toolbar band. Font license files are included with the assets.
- Logo circles form over 1400 ms. The logo begins 50 px above screen center at
  120% size, then rises and shrinks over 3300 ms after a 200 ms delay. The wallpaper
  has a smaller 16 px drift, zooms from full cover to 105%, and fades over 1600 ms
  starting at 1300 ms. All content below the logo fades together over 1500 ms from
  2000 ms. Reduced motion shows the final state without these animations.
- Intro buttons use regular 16 px text. Policy text keeps the original tight 1.2
  line height. Automatic updates default on independently of optional services.
  Custom setup starts optional Helium services off; Use defaults enables them.
- Services retains Helium attribution and its own logo. Import uses the Lune app
  icon with a direct light top/dark bottom edge, an iconless Import action, and
  Next with an arrow for page navigation. The default-browser step is removed;
  the existing sidebar prompt supplies that action.
- Startpage is first and the missing-choice/default selection, then Kagi and
  DuckDuckGo. Saved choices are preserved.
- Customize Lune opens native Appearance and offers Appearance, Theme, Tab sidebar,
  and Show toolbar. Leaving closes the panel; Done has a checkmark and opens the
  new-tab page. Auxiliary panels stay opposite the tab sidebar, with no independent
  position control. System and Lune are first in both theme pickers, System first.
- System draws from AppKit semantic colors, including emphasized/unemphasized
  selection colors. Lune uses its brand palettes. Existing brand-colored profiles
  migrate without silently changing appearance; explicit later choices persist.

## Validation

Both final architecture builds and UI/internal-icon/settings smoke checks pass,
including the final native tab-symbol foreground fix. Packaged flows on both architectures confirm identical
root/body/main colors in Light, Dark and Auto, the Welcome to Lune title, all three
toolbar labels, search ordering, consent independence and completion behavior.
Settings checks pass on both architectures without the old launch flag, including
all modes, both sidebar sides, backend synchronization, the opposite-panel invariant
and restart persistence. The native arm64 preview also confirms the corrected
toolbar-band background. The rebuilt System preview confirms that the selected
Welcome to Lune envelope and title share the same white foreground.
The fixture commands are:

```sh
python3 scripts/check-onboarding-flow.py /path/to/output /path/to/fresh-evidence
python3 tests/toolbar-inset/check.py /path/to/output /path/to/fresh-evidence --toggle
python3 tests/toolbar-inset/check-settings.py /path/to/output /path/to/fresh-evidence
```

The toolbar fixtures live in the platform component; its renderer fixture needs
Pillow. Builds use the existing prepared Chromium 158 source. Strict zero-fuzz
replay reproduces all 61 changed files in the final commit order; this is not a
fresh full Chromium preparation. All thirteen implementation signatures verify.
Frontend checks report zero errors and warnings; platform patch lint passes.

Live arm64 inspection verifies the final welcome tab title/envelope symbol,
Pin/Unpin sidebar labels, experimental cover label, and unchanged sidebar glass
and row spacing when switching to Always. Earlier checks cover light/dark native
palettes, System-first swatches, opposite panels, Back/Done cleanup, search choice,
responsive animation timing and reduced motion.

Native Intel hardware, older macOS fallback, and inactive-window selection visual
acceptance remain unverified. Intel runtime checks use Rosetta. The inherited
renderer limitation remains: ordinary-page background images do not extend into
the reserved band, while solid root/body colors and opted-in cover images do.
No release signing, notarization, installed-update test or stable promotion is
claimed by this source publication.

A fresh recursive GitHub checkout of the published input tag matches the locked
platform/core commits and passes patch-series and translation validation. All 44
orchestration tests and lock/hash/tag/tree/gitlink/ancestry checks pass.

## Setup toolbar choices — November 11, 2026

The final setup page offers only **On hover** and **Always**, as requested by the
owner. A saved experimental cover preference displays as Always without changing
the saved setting on entry. Selecting either offered mode clears cover behavior;
the pinned preference follows the selected mode. The native right-click menu
retains **Always cover (experimental)**, and its implementation is unchanged.

Platform input `inputs/onboarding-toolbar-options-1/macos` selects commit
`bc6e31500baab1551d1ffcee4c3bbc44510b7f25` for future main builds. The focused quilt
patch changes only `components/helium_onboarding/src/pages/Finish.svelte`.
The existing packaged-flow check now expects and selects only the two setup
options. No specific open GitHub issue is resolved by this narrow request.

Validation: strict zero-fuzz, zero-offset replay matches the checked source;
platform patch lint passes; Svelte reports zero errors and warnings; TypeScript
and the production Vite bundle pass. A browser preview of the real setup
component confirms exactly two choices, saved cover displaying as Always without
mutating preferences, and both selections setting pinned/overlay preferences
correctly. This is frontend validation with the development browser bridge; no
full native rebuild or packaged-flow rerun is claimed for this change. Previously
published binaries retain their frozen inputs.

## Step header symbols — November 24, 2026

Search engine, Privacy, Services, Import, Password manager, and Customize Lune use the AppKit symbols `magnifyingglass`, `eye.slash`, `point.3.connected.trianglepath.dotted`, `square.and.arrow.down`, `lock.badge.checkmark`, and `paintbrush.pointed`. macOS source preparation generates monochrome masks from AppKit. Setup draws the masks in the heading color and keeps each decorative icon beside its heading when the text wraps. [Apple SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)

The light and dark Lune previews passed at 1100px and 360px respectively. Zero-fuzz source preparation reproduced all eight source files and six masks. The Vite bundle and GRIT manifest checks passed. The owner waived browser builds before source adoption. See the [validation record](../builds/2026-11-24-setup-header-icons.json).

## Guided browser import

**Start Import** discovers profiles after showing the macOS permission guidance in 13 px type. The shared Setup options grid shows one card per profile, in two columns on wide windows and one column on narrow windows. Browser artwork fills the icon slot. The card title shows the browser name with the profile in parentheses when that browser has multiple profiles. The subtitle lists the available data types. The primary **Import** button uses the `square.and.arrow.down` SF Symbol and replaces that icon with a spinner while transferring the profile. The Import label stays visible. A successful import disables the same button and changes its label to **Imported**, centered in the original button width. The footer shows secondary **Skip** until the first successful import, then primary **Next**. Both use the forward arrow. After a failed transfer, the card keeps its data summary and the Import button becomes available for retry. Screen readers announce the failure through the card’s live region.

The macOS recovery card spans the Setup grid with a 24 px gap above it. Its heading is inside the card and aligns with the numbered steps. On macOS 27 and later, the instructions link to Files & Folders, use the app icon beside **Lune.app**, and say to quit the other browser before importing. The right panel shows a scaled Settings illustration with a sidebar, toolbar and nested browser switches. The panel stacks below the steps at viewport widths of 820 px and below. Step 1 and the full desktop panel both open Files & Folders. The desktop uses a 15 px inset blur and the default pointer. The demonstration repeats while visible and clips its cursor at the desktop boundary. Reduced motion shows both switches on from the start. The scroll area accounts for the footer height.

After **Start Import**, Setup refreshes profiles on window focus and every five seconds while the import step is foregrounded. Scheduled scans keep the card actions visually steady. An import requested during a scan waits for the current list and resolves the selected stable profile ID against it. A failed scan invalidates the native indexes and a subsequent import retries discovery. The other import and navigation controls retain their appearance and guard activation while a transfer is running.

Arc profile discovery moves the profile named by Chromium’s `profile.last_used` to the first Arc card and filters out Arc’s reserved `__ARC_SYSTEM_PROFILE` directory or cached name. On macOS, the importer labels each profile with the Space titles assigned to it in Arc’s sidebar, in sidebar order. It checks the Arc device ID before assigning custom Spaces, hides profiles without a linked Space when the sidebar is readable, and uses the cached name when the linked Spaces are untitled. Arc’s native sidebar importer reads pinned links from one shared sidebar file and uses the first Favorites group it can resolve. History and extension candidates come from the selected Chromium profile directory. The Arc-specific follow-up is tracked in [issue #44](https://github.com/leebyron/lune-browser/issues/44).

On macOS, Arc’s saved Today tabs come from the unpinned containers of the selected profile’s Spaces. Pages in Split View come over as individual tabs. Each top-level pinned folder becomes a named, collapsed pinned group. Its descendants appear in sidebar order at one level. For profiles with several linked Spaces, each Space’s loose pins form their own group with the Space’s name. A single Space or an unnamed Space uses **Arc Pinned Tabs**. The bookmarks import keeps the original nested folders and pinned links.

Chrome and Brave profiles use Chromium’s read-only session-file reader to replay the latest saved unencrypted session and select the current page of each tab. On macOS, Firefox uses its saved session or recovery snapshots and reads the selected entry of each tab in its open, non-private windows. The profile summary ends in **Tabs** when the source contains at least one importable HTTP or HTTPS page. Setup waits for the profile transfer to succeed before creating any tabs or pinned groups. Tabs-only profiles can be imported directly. Setup opens regular tabs in the background in its current window. The source browser’s session files are read in place with no storage initialization. Session replay uses the saved window and tab IDs so background discovery leaves Lune’s Local State alone.

Setup skips Safari during browser discovery. The regular Settings importer can list Safari when its bookmarks file is readable.

Each Setup step has a same-document browser history entry identified by a URL fragment such as `#DataImport`. The final Customize Lune step uses `#Appearance`. The browser’s Back and Forward buttons restore the step and preserve completed imports in the current tab. On macOS the top 32 pt remains a native drag strip. Setup centers content in the full viewport and scrolls focused controls clear of the strip. The floating toolbar controls retain their own hit targets.

The welcome screen’s primary **Customize** button leads with `switch.2`. **Use defaults** leads with `checkmark.rectangle.stack`. Both footer lines use 13 px type with 20 px line height, and the credit ends with a period. In Password Manager, the forward action shows secondary **Skip** until a listed manager is installed, then primary **Next**.

See the [guided Setup import adoption record](../builds/2026-11-27-guided-setup-import-adoption.json) for paired native validation.
