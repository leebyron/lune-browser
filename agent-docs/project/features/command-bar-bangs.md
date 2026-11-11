# Command-T bang suggestions

Implementation candidate requested November 10, 2026. This feature is retained on the local platform branch `command-bar-bang-suggestions` at `53f3de78ae3ba29bcb73c5cfb30c1eb55f79a9ec`, based on the current development input `1cd15a9c968749af7911e609445823c3092512e6`. The development lock and published releases are unchanged; native owner acceptance is pending.

## Behavior

Every searchable installed `!` keyword participates in matching, including the consent-controlled Helium catalogue and user-defined bang engines. The existing `TemplateURLService` remains authoritative for active/searchable entries, keyword overrides, catalogue refresh and service consent. No additional catalogue fetcher or service is added.

Provider names and triggers match case-insensitive exact, prefix, word-boundary and substring input. Inputs of three to 64 characters also tolerate one insertion, deletion, substitution or adjacent transposition at the beginning of a name/trigger. Short triggers avoid fuzzy matches. Ordinary text does not receive a scope score: even exact bang matches rank below comparable tabs, history/bookmarks and engine website suggestions, with direct search/navigation retaining priority. A leading `!` promotes bang completions above ordinary results. Matching and personal ordering occur across the eligible catalogue before the nine-result cap. Aliases sharing a case-normalized provider name collapse to the first ranked completion, so each service occupies at most one row; the native viewport still shows five rows with scrolling.

Bare `!` shows familiar installed bangs as starting points, including Google, Wikipedia, YouTube and GitHub, then adapts to this profile's submitted Command-T bang searches. The catalogue has no global popularity counts; the initial order is a curated fallback. Local frequency and recent use adjust order within a relevance band. Personal use cannot make a partial match outrank an exact match or promote a plain-text bang above a comparably relevant website.

Rows display the same native provider pill as the applied input in the leading position, muted `Search <service name>` text immediately after it, and its actual `!trigger` aligned on the far right. Bang completion rows have no icon, favicon or reserved icon slot, and do not request favicon lookups. The shared native pill implementation supplies both input and result styling. Pointer or keyboard activation immediately applies the provider pill and keeps the palette open. A descriptive query such as `github` is replaced by the empty scoped input. Explicit bang input with terms, such as `!wik Cats and Dogs`, retains those terms after applying the chosen provider.

An applied bang shows only its provider pill and query input. No direct-search row, tabs, bookmarks, history or remote suggestions appear. Empty input has the placeholder `Search <service name>` after the pill; typing naturally hides it. Enter submits the scoped query directly to that service and records use. Empty or unavailable-engine submissions keep the palette open without navigating or falling back to another engine. Active bang scopes cancel previous suggestion work and request neither remote suggestions nor local history. Space after an exact recognized trigger, Escape and Backspace retain their existing scope behavior. Activation revalidates the provider in case a catalogue/engine update invalidated the visible row.

Every newly typed query starts with its highest ranked result selected. Only deliberate keyboard or pointer selection is preserved across asynchronous updates. Native row rebuilds ignore tracking-area entry under a stationary pointer, preventing a bang completion from taking selection from the plain search action above it.

Usage is stored in the local, unsynced profile dictionary `helium.command_bar.bang_usage`. Only submitted searches count; selecting a provider alone does not count. Incognito never writes usage. Records contain a saturated count and last-use time, with a maximum of 200 literal trigger keys and oldest-use eviction. This tracks Command-T use rather than inventing omnibox-wide or global statistics.

## Validation

The feature is a separate reusable platform quilt patch, `patches/helium/ui/command-bar-bang-suggestions.patch`, developed in the current prepared source tree, refreshed with quilt and unmerged through Helium tooling. The core gitlink is unchanged. A direct dependency on Helium service prefs is also declared for the existing preferences target, fixing its header dependency check while registering the new dictionary.

Evidence lives under `.work/bang-suggestions/`:

- `strict-replay-selection.json`: zero-fuzz replay reproduces all thirteen changed source files.
- `lint.log`: core/platform patch and translation-file checks pass.
- `gn-check.log`: Command-T and browser preference targets pass header dependency checks.
- `model-arm64.log` and `model-x86_64.log`: the production matching, ranking, activation branch, usage and result-selection functions pass focused tests with service/preference doubles. Cases cover ordinary website/tab priority, explicit bang priority, typo/case handling, retained query terms, stale entries, overrides, disabled entries, frequency/recency, Incognito writes, literal dotted keys, bounded history, one completion per service, highest-ranked default selection, deliberate selection across asynchronous updates, stationary-pointer hover and ranking across a 15,000-entry fixture before capping. Doubles do not establish production scan timing or service persistence.
- `repository-tests.log`: all 66 orchestrator tests pass.
- `native-checks.json` and `final-row.png`: the final shared native row renders the provider pill, placeholder-colored search text and actual trigger, with no icon. Earlier live native checks cover ordinary-text ranking, alias deduplication, immediate pointer/keyboard scope activation, retained pasted terms, Backspace and persisted personal ordering. The record identifies which checks preceded the final presentation and rowless-scope refinements.

The final arm64 and x86_64 builds pass (`build-arm64.log` and `build-x86_64.log`). Both isolated browser/WebUI smoke checks pass (`smoke-arm64.json` and `smoke-x86_64.json`), including local-page JavaScript, profile persistence after restart, packaged defaults and service disclosures. The x86_64 browser ran under Rosetta on the Apple silicon host; this is not native Intel hardware validation. The shared prepared tree also contains another task's non-overlapping `helium/ui/devtools-header-hover.patch`, recorded in `extra-local-input.json`. Local full builds and previews include that extra input; the bang commit and strict replay contain only this feature.

The isolated ad-hoc preview is `.work/bang-suggestions/Lune Bangs Selection Test.app`, with its own test bundle ID, disposable profile and loopback-only catalogue fixture. The earlier running previews are preserved. Native Intel hardware, macOS 13 and broad accessibility/IME acceptance require separate validation. No release or publication is implied by this candidate.
