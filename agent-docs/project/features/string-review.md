# String review and frame-thickness label

2026-11-06: owner requested confident wording restorations and a GitHub issue for
the remaining copy/localization work.

Restored `IDS_SETTINGS_ROUNDED_FRAME_THICKNESS` from “Frame thickness
(Experimental)” to “Frame thickness (applies after restart)”. The existing
restart button, preference, and behavior are unchanged. This is the only browser
copy changed in this increment. Kagi, feature descriptions, Helium credits, and
service disclosures remain as previously pinned.

The original 32 audit findings were 31 distinct IDs: 30 additions, one changed
Kagi description, and an intermediate frame-label version counted twice. The
Xelium integration explicitly accepted English fallbacks. Source-catalog coverage
is now advisory; patch lint and translation-file/placeholder validation remain
blocking. The audit keeps the last extracted addition for each resource/message
pair. This removes the known intermediate-wording false positive but does not
claim to model deleted messages or conditional resource variants. Full final-tree
catalog reconciliation is tracked in [issue #4](https://github.com/leebyron/lune-browser/issues/4),
alongside recommended copy decisions and translations for all 31 IDs (27 distinct
final English phrases). No translation has been fabricated or silently reused.

## Inputs and validation

- Platform: `5d9c3fc7e710515d3dcf184b9970f3693cb5ae4b`, retained by
  `inputs/frame-label-1/macos`, descended from `b3a4ba00`.
- Core remains `e2a09ea1efab4c9459be14513c446cab2723175e`.
- New reusable platform patch: `helium/ui/frame-thickness-label.patch`.
  Original Xelium patches and attribution are preserved; the restoration is a
  separate commit with its own pinned patch hash and selection provenance.
- Reconstructed the affected settings resource from the original Chromium
  snapshot and all 42 relevant locked patches. Replay uses the build pipeline's
  `--ignore-whitespace --fuzz=0` flags. An initial diagnostic without the pipeline's
  whitespace option rejected the existing service patch's EOF newline context;
  replay with the actual build flags passed without changing that patch.
- Developed the restoration in that prepared resource with quilt, refreshed,
  and unmerged into the platform component. Core Git status stays clean.
- Independent application of the new patch passes with zero fuzz. XML comparison
  confirms that message IDs and all other messages are unchanged.
- Patch lint, translation-file lint, lock/ancestry/tag/tree/gitlink validation,
  and all 44 orchestrator tests pass. The source audit reports the 31 remaining
  catalog gaps as advisory work linked to the issue.

Evidence is under ignored `.work/string-review/`: `strict-replay-matching-build.log`,
`replay.json`, `before.grdp`, quilt metadata, the isolated component, and the
independent `verify/` resource. No Chromium compilation, packaged runtime check,
signing, release, or deployment was performed for this text-only change. Existing
published builds and input tags remain unchanged.
