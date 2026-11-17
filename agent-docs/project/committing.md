# Completing a validated change

## Commit the change and its record together

- Validate at the scope of the change. Use [paired browser adoption checks](development.md) for browser inputs and focused tooling or link, consistency and whitespace checks for tooling or docs.
- Keep each commit focused on one change. Include its spec, relevant design decisions and pre-push validation in the implementation commit or the corresponding main input-adoption commit. Preserve separate upstreamable component commits and upstream authorship.
- Adopt browser inputs by updating `manifests/browser.lock.json` and `manifests/patches.json` together. Add to an existing feature record if the change establishes behavior or a constraint future agents need. Use the commit body or one concise linked report for checks, source and artifact identities, and material limits. Keep detailed logs, screenshots and timing data in the task evidence.
- Use separate documentation commits for a documentation change with its own purpose or an essential finding that only became available later. Use the [release commit boundaries](release-commits.md) for release work.

## Push and verify

1. Inspect `git log origin/main..HEAD` before pushing main. Publish only authorized commits. Publish exact core refs before platform refs, then permanent input tags before main. Use explicit refspecs with `git -c push.followTags=false push`.
2. Verify remote refs and required checks. Close and verify only the GitHub issues whose acceptance criteria are met by the pushed change. Link the resolving commit when closing an issue.
3. Report CI, issue closure and cleanup outcomes in the task or issue, pointing to the source commits and checks. Retain non-public evidence with the task if needed. Successful post-push checks, routine cleanup and issue closure require no follow-up commit or amendment. Fix failed checks that require a change in a focused commit.

## Quit temporary builds and remove their artifacts

Stop task-owned previews, drivers, fixtures and other temporary processes after required checks finish. Verify exit, inventory exact paths, then remove disposable copies, profiles, packaging intermediates and fixture trees after retaining evidence. A request to keep a preview or artifact takes precedence.

Preserve daily-use apps and profiles, reusable source/output caches, required release evidence and other tasks' inputs. Before removing a checkout, inspect ownership, running processes, tracked and ignored changes, stashes, local refs and dependencies including Git alternates. Use managed worktree cleanup for managed worktrees. Check current doc links if cleanup removes their target. Dated evidence can retain its historical paths.
