# Address-bar cursor follows editing focus

The owner accepted the Apple silicon preview on November 12, 2026: both cursor states now work. Signed input `inputs/address-field-cursor-3/macos` selects platform commit `21a79057a6fd6b60ba268fd0d719b510da94053e` for future main builds. Published releases retain their frozen inputs.

The idle address field shows the normal arrow. Focused address text shows the native I-beam; the surrounding glass and toolbar controls retain the arrow. Clicking the capsule, Cmd-L, selection, provider scope and app-switch focus behavior retain their existing ownership rules.

The reusable patch is `patches/helium/ui/address-field-focus-cursor.patch`. It changes one existing macOS implementation file and reuses `userEditing`; no build target, dependency, timer, monitor or additional runtime state is introduced. The field clears its previous cursor rectangles at editing transitions. The glass ancestor preserves the I-beam when AppKit forwards mouse movement and partitions its structural cursor rectangles into text and surrounding arrow regions. Begin/end editing invalidate the glass regions.

## Validation

Both final browser, ChromeDriver and installer builds pass, as do isolated browsing, profile persistence, packaged UI and settings checks. Intel execution uses Rosetta on Apple silicon. The plain review app's framework UUID matches the final arm64 output, and the owner confirmed focused I-beam and idle-arrow behavior.

`scripts/check-address-field-cursor.py SOURCE --arch ARCH` extracts the production field and glass methods and uses real AppKit field editors. Both architectures pass idle/focus/blur, structural regions, forwarded mouse movement, surrounding-control regions, repeated focus and resized-field checks. Independent negative controls reject the inherited glass arrow rectangles and inherited arrow-setting mouse handler. Existing paired focus-retention checks cover unchanged focus handlers. All 73 tooling tests, component patch/translation lint, signed input/lock checks and the Actions policy audit pass.

Two earlier previews passed field-only cursor checks but failed owner review. An owner-assisted native cursor trace established that `NSTextView` installed the I-beam, then its glass ancestor replaced it through forwarded `mouseMoved:` dispatch. The final regression fixture includes that ancestor. CUA synthetic input did not move the global pointer in this session; natural owner hover provides pointer acceptance.

The complete feature replays against the retained accepted-input preimage with zero fuzz, zero offsets and exact address-source parity. This is focused replay rather than a fresh full Chromium preparation. Review builds also contain the independently pending pinned-tab-groups topic; it does not change this address source and is excluded from the selected platform input. Physical Intel and macOS 13 remain unverified.

The [validation record](../builds/2026-11-12-address-field-cursor.json) retains exact inputs, build/check scope and acceptance. No specific GitHub issue was supplied. Temporary review apps, isolated profiles and diagnostic fixtures are removed after acceptance; reusable prepared sources, current outputs, quilt provenance and concise evidence are retained.
