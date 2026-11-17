# Working on Lune

Lune is a macOS Chromium distribution built from ungoogled-chromium, Helium and selected patches. Keep reusable browser features upstreamable and distribution identity separate.

## Read for the task

| Task | Guidance |
| --- | --- |
| Identify current inputs, published releases or open work | [Sources of project state](agent-docs/project/status.md) |
| Change component history or patch composition | [Architecture](agent-docs/project/architecture.md) |
| Develop or validate a browser feature | [Development loop](agent-docs/project/development.md), [relevant feature record](agent-docs/project/features/README.md) |
| Prepare sources, build or use the Mac runner | [Build runbook](agent-docs/project/building.md) |
| Freeze, sign, publish or verify a release | [Release delivery](agent-docs/project/release-delivery.md), [release policy](agent-docs/project/releases.md) |
| Commit, close issues and clean up | [Completion process](agent-docs/project/committing.md) |
| Change the website or service integration | [Website](agent-docs/project/website.md), [services](agent-docs/project/services.md) |

## Constraints

- Preserve upstream ancestry, licensing and attribution. Develop Chromium patches with quilt in prepared sources, then refresh and unmerge into the owning component. Stop on conflicts or failed validation. Keep the complete Helium/ungoogled series in its upstream order.
- Iterate with arm64 and focused native checks. Before main adopts a browser input, verify complete zero-fuzz preparation and source parity, then build and smoke-test arm64 and x86_64. The release gates are separate.
- Target the latest official macOS Chromium Stable independently of downstream cadence. Preserve the selected input commits and archive hashes. Use macOS 13 as the minimum for both architectures.
- Keep CI on the existing local Mac with owner/main/canonical-repository guards. Keep untrusted PR and fork code off the signing host and credentials in Keychain. Use the clean build environment.
- Publish an authorized release after one physical-device acceptance and all technical gates pass. Keep both architecture builds and automated checks, and label Rosetta execution accurately. Use the production stable feeds and immutable assets. Schedules, releases and deployments need task authorization.
- Include affected specifications and durable validation evidence in the implementation or input-adoption commit. Verify remote checks, close resolved issues and clean up after pushing without a routine follow-up commit. Preserve shared work and caches.
- Use descriptive branch names. Omit the `codex/` prefix unless tooling requires it. Check current upstream contribution rules and preserve Helium's requirement for human-written issue and PR descriptions.
