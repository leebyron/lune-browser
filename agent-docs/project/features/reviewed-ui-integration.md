# Reviewed UI development integration

Historical November 8 baseline. The [November 9 onboarding integration](onboarding.md)
supersedes its input tip and removes the header launch-flag requirement.

On November 8, 2026, the owner requested that main include all recent work.
The development lock now selects platform commit
`01905fc411a170d7498ea04b3e315111bb806925`, retained by
`inputs/reviewed-ui-2026-11-08/macos`. The core remains
`3c3726b5935203480de96fdb08c9839a814fc2b9` and Chromium remains 158.0.8127.18.

## Included work

The platform is the existing reviewed stack, unchanged. It retains upstream
ancestry and every previous macOS input tag. No browser patches were rebased,
rewritten, dropped or fuzz-applied for this integration.

| Work | Platform tip | Evidence |
| --- | --- | --- |
| Sidebar, edge frame, footer and menu retention | `10fea4d3` | [Frame](edge-to-edge-frame.md), [footer](sidebar-footer.md), [menus](menu-reveal-retention.md) |
| Sidebar pin activation | `5e0957c5` | [Pin](sidebar-pin-activation.md) |
| Toolbar controls and navigation menus | `83fba93f` | [Toolbar](trailing-toolbar-controls.md) |
| Media Controls | `41312cdf` | [Media](media-toolbar-controls.md) |
| Native appearance, tint and shadows | `622ccfac` | [Appearance](chrome-appearance.md) |
| Header wheel forwarding | `d0c49b0a` | [Scrolling](header-scroll-through.md) |
| Shared native result selection | `f0e2df52` | [Suggestions](address-suggestion-selection.md) |
| Command-T and address-result layout | `7b9dda91` | [Menus](command-bar-corners.md) |
| Header modes, Settings, opposite-side panels and Customize inset | `01905fc4` | [Header](header-inset-prototype.md) |

Main incorporates the orchestration/evidence branches through Git merges,
preserving authorship. The two documentation conflicts were reconciled with
explicit owner approval: retain every feature section and prefer the newer
header-scroll publication/acceptance record. Latest website changes remain intact.
The selection manifest records all 39 additional patches beyond the previous
sidebar-pin input, ordered hashes, dependencies and original implementation commits.

## Validation and limits

The integration passes all 44 orchestration tests, lock/hash/tag/tree/gitlink and
upstream ancestry validation, core/platform patch lint, translation lint, and the
live Actions policy audit. A fresh recursive GitHub checkout of the published
input tag passes the locked core/platform checks. Existing reviewed source replay/build/runtime evidence
is linked above; this lock update does not claim a fresh Chromium build.
The final header stack has arm64 build/runtime evidence. Its final Intel build
and native Intel acceptance remain outstanding. Earlier stacks have Intel-under-
Rosetta validation as documented individually. Resize cursor work remains deferred.
The header inset retains its existing `--lune-obscured-header-prototype` gate;
this integration does not change the experiment's rollout or default behavior.

This is a development input integration, not a binary release or stable-feed
promotion. Earlier feature documents retain historical statements that a
candidate was not in the development lock; this record supersedes those statements.
Onboarding work in progress and unrelated uncommitted service/release-design
changes are excluded. No signing, release, deployment or scheduling is performed.
