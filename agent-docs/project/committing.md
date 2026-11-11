# Committing and completing validated changes

A change is complete when the validated solution is committed and adopted in its authorized destination, the specific issues it resolves are closed, and its temporary builds and artifacts are cleaned up. Apply this process to browser features, fixes, tooling, documentation and website changes. The owner's instruction to leave a preview open or retain a particular artifact takes precedence.

## Validate and commit

Confirm that the implementation solves the stated problem with checks appropriate to the change. Obtain native visual or interaction acceptance when the task requires it; an acceptance already given in the conversation remains valid. Record what was built, the exact source/input identities, completed checks and material limitations. Keep source inspection, automated tests, Rosetta execution and physical-device acceptance distinct.

Use focused, single-thesis commits and preserve upstream ancestry and authorship. Browser changes follow the prepared-source/quilt/export process in [architecture](architecture.md); distribution identity stays separate from reusable features. Update the development lock, patch provenance and current feature/status documentation when adopting a browser input. Follow [release commits](release-commits.md) for frozen release records and versions.

When committing and pushing are authorized, complete them without asking again. Publish exact core inputs before platform inputs, permanent component tags before the main lock, then the authorized main changes. Use explicit refspecs with `git -c push.followTags=false push`. Verify remote refs and required post-push checks. A validated development change does not itself authorize a release, deployment or schedule.

## Close the resolved issues

Read the specific GitHub issues associated with the change and compare their acceptance criteria with the validated behavior. Close every issue fully resolved by the adopted solution once its commits are available in the intended repository/branch. Use an appropriate closing reference in the merged commit/PR or explicitly close the issue, then verify its state. Record the issue and resolving commit in the feature or completion record.

Leave partially addressed or unrelated issues open and identify remaining work. Do not close issues merely because their titles sound related. If no specific issue is resolved, record that briefly; a new issue is unnecessary. Distinguish inclusion in future main builds from availability in an already published browser release. Preserve the existing requirement for human-written upstream Helium issue/PR descriptions.

## Quit temporary builds and remove their artifacts

After the solution is validated and accepted, quit temporary browser previews and native test/probe apps. Stop their disposable ChromeDriver sessions, loopback fixture servers, development servers and other task-owned background processes. Let an active required validation job finish before cleaning its inputs. Verify the processes exited before deleting their app bundles or profiles.

Inventory exact cleanup targets first. Delete the task's disposable preview app copies, temporary installers/packages, test profiles, generated replay/fixture trees and other temporary build artifacts once their useful results and source identities are recorded. The standing completion policy authorizes this routine cleanup; do not ask again for each known disposable artifact. Keep the installed daily-use app and personal profiles outside this cleanup.

Preserve the concise evidence needed to audit or reproduce the result: committed source and provenance, final check results, relevant screenshots or report hashes, and known limitations. Retain reusable prepared Chromium trees, compiler/download caches, current build outputs used for incremental work, release artifacts/evidence and inputs still required by another active task. Remove these only when the requested cleanup explicitly covers them and their dependencies have been checked. A directory's presence under `.work/`, a published HEAD or an old timestamp alone does not establish that it is disposable. Before removing a checkout, inspect tracked/ignored changes, stashes, local refs, running processes and dependencies for unpublished work. Use managed worktree cleanup for managed worktrees.

Update current docs that say a preview is open or point to a retained local artifact when it has been quit/deleted. Preserve dated reports as historical evidence and annotate later cleanup where necessary. Do not describe deleted local evidence as currently available.

## Verify completion

Verify the intended commits/input refs are published when requested, resolved issues are closed, temporary processes have exited and cleanup targets are absent. Run documentation link/consistency and whitespace checks for process edits; use the existing build/test evidence for unchanged browser code. Report the resulting commit or branch, relevant issue closures, check results and cleanup performed. Explicitly identify any remaining blocker or intentionally retained active artifact.
