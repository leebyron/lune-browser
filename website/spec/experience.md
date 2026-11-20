# Website experience

## Desktop and launch

The homepage introduces “A respectful browser for the Mac” through a macOS-style desktop and a continuous story inside an illustrated browser. Download and GitHub actions appear on the desktop and at the end of the story.

The desktop fills the viewport. Center the browser above the Dock, with a maximum logical height of 720px, width capped at 10/6 of its height, and 16px outer corners. At widths of 700px or less, scale the complete browser and its contents to 50%; keep the surrounding desktop actions at their own size.

Scrolling beyond 96px launches Lune. The normal Dock bounce lasts 660ms; reveal the window and running dot at 320ms. The chevron and Lune Dock button scroll to 180px, where reading begins and the intro has faded. Fast scrolling past that boundary finishes the reveal immediately. Returning to the top resets the launch.

Close and minimize return to the desktop. Closing the selected Lune tab returns immediately and keeps its row. Fullscreen uses the browser’s Fullscreen API and is disabled when unavailable. Finder and Trash are decorative Dock items.

## Story and copy

Open with the paired-circle Lune mark, then two separate paragraphs:

> I made Lune for myself
>
> I wanted a browser that stayed out of my way

The ten botanical points follow this order: Chromium, removed Google services, extension proxying, uBlock Origin, Mac details, Cmd-T, Helium’s !bangs, the disappearing toolbar, vertical tabs, and shared open source. Keep the exact homepage copy and destinations in [index.html](../public/index.html), rather than duplicating them here.

Use Rock Salt 400 at 16px/32px for the note and story, Syne 800 for the wordmarks, and Inter for interface text, buttons, and credits. Story links use the ink-colored sketched underline, with a 600ms wipe on hover or keyboard focus. Ordinary links retain regular underlines.

The opening mark starts at 70% of the content pane’s height and opens over 65% of a pane of scrolling. The note sits 128px below its center. The prelude is 1.28 panes tall, with 168px before the flower. Reveal the note when its first line’s resting center reaches 68% of the pane; stagger its second paragraph by 1200ms.

Reveal each point when its resting text center reaches 85% of the pane. Keep it visible past the top edge; hide it only when reversing below the lower threshold. Fade and lift by 6px over 600ms, with an 800ms feathered wipe; hide over 200ms. Scroll chooses visibility, while transitions finish when scrolling stops. Reversal cancels the note’s pending stagger.

A seeded flower, nine main leaves, connecting vine, shoots, tendrils, and roots form one continuous cyanotype illustration. Keep leaf attachments fixed through motion, resize, and mobile scaling. Use content-driven section heights, stable reading width during sidebar changes, and a restrained horizontal wave. Reuse the seeded shapes when remeasuring.

The flower opens to show 19 stamens. Seventeen pollen groups, two with independent companions, drift in slow figure eights and separate outward with scrolling. Pause idle motion offscreen. Cache root silhouettes between layout changes and reveal them with two shared radial masks. The darker soil continues through the coda.

End with the Lune mark, downloads and GitHub actions centered in the final pane. Keep 36px between the brand and actions, the upstream thanks between the actions and byline, and the author/Privacy/Terms byline at the bottom edge. Credit Helium and ungoogled-chromium with links.

## Browser illustration

Use edge-to-edge content with no inner gutter. Pinned and floating sidebars share a 216px width, 52px header, and matching control positions. Pinning changes content width immediately on desktop; the narrow layout transitions that boundary over 260ms. Keep the physical-pixel separator/rim independent of layout.

Tab rows are 30px tall with 8px corners, 2px gaps, and 9px side margins. New tab stays above the scrolling regular tabs; its icon uses 70% opacity and label 50%. Reveal separate close buttons on hover or keyboard focus. Closing another row removes it until reload; its close button never follows the row’s link.

The two pinned tiles link to Fastmail’s public homepage. Regular rows show Lune, lune-browser, Helium, ungoogled-chromium, and Lee Byron in that order. The selected Lune row has no navigation action. Other destinations open in separate tabs with `noopener noreferrer`. No external pages or private mail are embedded or fetched.

New tab opens the illustrated command menu when it is closed. Activating New tab while the menu is open dismisses it and opens Lune’s website in a separate tab. Escape and clicks elsewhere in the window dismiss the manual menu; scrolling clears the manual override and resumes the story state. The manual menu remains available with Reduced Motion.

The passive command demonstration opens empty when the Cmd-T sentence reaches 70% of the pane. The !bangs sentence triggers `!wiki` typing at the same threshold, followed by a Wikipedia pill and “Search Wikipedia” placeholder. Typing finishes at rest; faster scrolling can advance it. The pane stays 52px tall, at most 600px wide with 36px side margins and 18px corners. Show no autocomplete results. Dismiss at a separate later threshold before the cursor’s header hold; reversing restores the scoped state or resets to empty above the !bangs sentence. This demonstration accepts no input or focus and makes no search requests.

The simulated cursor pauses at the top edge during the toolbar sentence, then clicks the sidebar toggle during the vertical-tab sentence. Both sentences meet the same 58% reading height. Unpinning expands the page; retain the floating sidebar and toolbar until the cursor tip leaves its exterior retention area (128px horizontally, 64px vertically), then retract them together. Reverse scrolling reverses the demonstration. Position the cursor and click ring with measured numeric transforms on desktop and phones.

Real pointer proximity reveals the toolbar in the first 8px inside the window’s top edge or up to 16px above it, and the floating sidebar within 16px inside or outside its left edge. Retain the sidebar through 128px past its inner edge or outside the window; retain the toolbar through 64px below the glass controls and above the window. Exterior retention extends 128px horizontally and 64px vertically. Measure these distances in the illustration’s logical pixels, so its phone half scale applies equally inside and outside. Keyboard focus retains panels; Escape dismisses the relevant panel. The sidebar header can also reveal the toolbar. Window controls remain visible with either panel. Shield clicks through header gaps while allowing wheel input to scroll the story.

The address is read-only; navigation and Extensions glyphs are illustrative. uBlock Origin and 1Password link to their sites. CSS approximates native glass. OS menus, dragging/resizing, real command search, download progress, media sessions, and setup/update prompts are outside the illustration.

## Motion and accessibility

Native CSS scroll timelines and the JavaScript fallback must preserve the same story and reversal behavior. Remeasure after fonts load and viewport/content sizes change. Test cursor positioning across the 700px breakpoint, including Safari; CSS motion-path support alone does not establish correct SVG movement.

Reduced Motion shows settled text, the completed mark, open flower, and full roots. Disable launch bounce, zoom, leaf sway, idle pollen motion, sidebar translation, link wipes, and the simulated cursor/click. Hide the passive command demonstration while preserving manual New tab interaction.

Keep hidden window, panel, and offscreen story controls out of focus with `inert` and matching ARIA state. Keep headings, prose, and attribution selectable; interface surfaces are not selectable. Decorative artwork is hidden from accessibility APIs. Mobile shares the browser’s half scale without separate enlargement of prose or coda; the requested fixed viewport scale does not establish how every browser handles accessibility zoom.

## Downloads

Both download actions offer Apple silicon (`arm64`) and Intel (`x86_64`), labeled macOS 13+. Use permanent GitHub latest-asset URLs:

- [Lune-macos-arm64.dmg](https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-arm64.dmg)
- [Lune-macos-x86_64.dmg](https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-x86_64.dmg)

Only explicit macOS User-Agent Client Hints for `arm` or `x86` select a direct download. Missing, denied, or unknown architecture hints retain the chooser. Do not infer chip architecture from `MacIntel` or a legacy user-agent string.

Known Windows, iOS/iPadOS, Android, Linux, and ChromeOS devices get dimmed, disabled buttons without a dropdown chevron. Detect iPads presenting a Mac identity through multiple touch points. Unknown platforms retain the chooser. Position popovers within the viewport and dismiss them on scrolling or resize. Architecture detection runs locally.

## Claims and scope

Ground browser claims in the promoted release, not current upstream marketing or unreleased inputs. The Chromium line describes the project’s input policy; it is not evidence of continuous freshness. Website changes and deployments do not require Chromium version or freshness checks; browser releases follow the [release policy](../../agent-docs/project/releases.md).

Extension proxying concerns downloads and updates through optional Helium services, subject to consent. It does not proxy installed extensions’ own traffic. Blocking and removal of Google integrations do not guarantee anonymity, zero connections, or protection from every tracker. The [privacy policy](../../legal/privacy.md) is canonical for data handling; Helium’s policy does not govern Lune.

Do not add unsupported claims about fingerprinting prevention, DRM compatibility, performance, battery life, permanent support, or unreleased features. The [November 10 research](../../agent-docs/project/website-respect-story.md) retains the original evidence scope; it is not a current security audit.
