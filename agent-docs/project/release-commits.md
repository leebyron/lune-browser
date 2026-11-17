# Release identity and commit boundaries

Use [release delivery](release-delivery.md#commands-and-gates) for commands and [release policy](releases.md) for gates.

## Identity and version rules

- Use `YY.MMDD.N` in the outer app bundle version fields and both Sparkle version fields. Record the full ISO date and `America/Los_Angeles` timezone. Start the numeric sequence at 1 each day. Chromium's engine and framework versions retain their own identity.
- Allocate serially against fetched main and retained release history. A committed allocation reserves the version even if the release fails. Retry unchanged inputs under the same version. Allocate a new version for changed inputs or replacement published bytes. Keep published source/input tags and bytes immutable. A corrective release must compare higher than any version clients could have installed.
- The two architectures share one allocation and signed `v<VERSION>` source tag. The enclosing Git commit supplies the full source SHA. Final signed artifact hashes identify delivered bytes.

## Two routine release commits

1. **Freeze inputs and notes.** Land any source, recipe or tooling changes with their documentation as ordinary implementation commits. After complete zero-fuzz preparation, stage `agent-docs/project/releases/<VERSION>.md` and run `scripts/release/reserve.py --version VERSION --prepared-report REPORT`. Stage the resulting `manifests/releases/<VERSION>.json` and commit both paths together. Previously committed notes also work. Build and package from the clean frozen commit. The record hashes the notes, policy and exact inputs, including the browser/patch locks, product config, download manifests, recipe and tools. It also binds the preparation report and log. Keep the record and referenced files fixed at the release tag.
2. **Promote stable delivery.** Once the gates pass, the publisher commits both feeds and their release, acceptance and freshness records together. It then marks the same public release latest. See [public readback and recovery](release-delivery.md#public-url-contract).

## Evidence after freezing

Retain detailed preparation, build, signing, test, upload and public-readback reports in the release evidence workspace. Keep exact source and output identities, hashes, execution modes, check results and material limits. The draft's compact validation and the promoted acceptance record provide the durable release results. Keep readback and cleanup results with the retained evidence and report them at completion. A separate delivery recap, status update or evidence commit is unnecessary for normal success.

A newly discovered defect, an enduring operational constraint or a requested audit record may warrant its own change. Bind supplemental checks to the exact tested artifacts and tool revision. Keep the frozen commit, signed tag and published assets immutable.
