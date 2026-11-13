# Leading emoji in sidebar group titles

The owner accepted this appearance on November 12, 2026 and requested adoption after specifying a 16 DIP font and single-emoji eligibility. Signed input `inputs/tab-group-emoji-1/macos` at `cdea745ea5600098e382a7a3c13dc5652b20fd39` selects the focused renderer for future main builds. Published browser releases retain their frozen inputs. No specific GitHub issue tracks this change.

A vertical group name beginning with an emoji and containing exactly one emoji overall renders that complete grapheme separately. Flags, skin-tone modifiers and joined sequences count as one emoji. Multiple emoji anywhere in the name, and names without a leading emoji, retain the ordinary full-label presentation. Explicit text presentation is honored; ordinary digits are not emoji.

The emoji uses a 16 DIP font and full opacity. Its painted glyph bounds, rather than font sidebearings, are centered at each display scale in the ordinary favicon location: a 16 DIP canvas at the row’s 9 DIP leading inset. The remaining title is whitespace-trimmed for display and starts at the ordinary tab title’s 32 DIP offset. Emoji-only names show only the icon. Header height, disclosure behavior, the full stored title, accessibility and renaming retain their existing paths.

The reusable patch is `helium/ui/tab-group-leading-emoji.patch`. It was developed with quilt, ported onto the current accepted platform base `99ca9faf1ae2e4b511cd952728adaa70c165faae`, and exported through platform merge/unmerge. Complete affected-file replay has zero fuzz, zero new-patch offsets and exact final parity. This input changes only the group header renderer; pending pinned-group hooks and caret diagnostics remain separate.

Both complete browser/driver/installer builds pass. Production Chromium ICU/Skia fixtures pass 21 Unicode cases and 10 raster checks per architecture, covering single versus multiple emoji, trimming, 1×/2× centering, clipping, full color and independence from section-text alpha. Browsing, UI, Settings and saved-profile relaunch checks pass. Intel execution uses Rosetta. Agent inspection of the final native Apple silicon preview confirms 16 DIP single-emoji styling and ordinary fallback for adjacent/separated emoji, including the owner’s two-flag title. Physical Intel and older macOS visual inspection are not claimed.

The [completion record](../builds/2026-11-12-tab-group-emoji.json) binds the source, both builds and validation. The temporary emoji preview, profiles and duplicated review artifacts are cleaned up. Shared pending-review source/quilt and the original pinned-group preview/profile are preserved; reusable build caches and current outputs remain.

```sh
python3 scripts/check-tab-group-emoji.py SOURCE --arch arm64 --report /tmp/group-emoji-arm64.json
python3 scripts/check-tab-group-emoji.py SOURCE --arch x86_64 --report /tmp/group-emoji-x86_64.json
```
