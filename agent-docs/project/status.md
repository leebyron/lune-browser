# Sources of project state

| Question | Source |
| --- | --- |
| What will a main build use? | [Browser lock](../../manifests/browser.lock.json) for exact component refs and engine. [Patch manifest](../../manifests/patches.json) for composition and provenance. |
| What is offered to installed browsers? | [Stable release metadata and paired appcasts](../../updates/stable/) on public main. Check the public feeds for delivery verification. |
| What is available for download? | [GitHub Releases](https://github.com/leebyron/lune-browser/releases). Resolve the actual published release when choosing an update-test or release-note baseline. |
| What source produced a specific release? | Its signed `v<VERSION>` tag and [frozen release record](../../manifests/releases/) at that tag. |
| What was accepted or tested? | Relevant [feature record](features/README.md), [build evidence](builds/) or artifact-bound release validation. Check scope and exact input identities. |
| What work remains? | [Open issues](https://github.com/leebyron/lune-browser/issues) and the [roadmap](roadmap.md). |
| Which workspace is active? | Inspect local Git state, running jobs and the [workspace coordination record](development.md#coordinate-shared-workspaces). |

Users on 26.1109.1 or 26.1109.2 need a manual install to move off the retired distribution feed. See [release delivery](release-delivery.md).

Keep this page as a lookup guide. Report task progress in the task, issue or CI run where it can be verified.
