# Repository workflow

- `upstream` is `Ammar-Wahidi/NPU`; `origin` is `rightson/tiny-transformer-npu`.
- `main` is reserved for upstream synchronization. Do not merge project feature
  branches or `dev` into `main`.
- `dev` is the default branch and integration line for this fork. Target project
  pull requests at `dev` in this repository, not at the upstream repository.
- For every new feature/fix worktree, fetch `origin/dev`, then create an isolated
  branch and worktree explicitly from `origin/dev`. Do not use the currently
  checked-out branch or Git's implicit starting point. If the branch/path exists,
  append a timestamp suffix.
- Do not edit the primary checkout for complex work (multi-file changes,
  refactors, migrations, dependency/API/schema changes, risky experiments, or
  long-running tasks). Work only inside the task's isolated worktree. Skip this
  isolation rule only if the user explicitly says "no worktree".
- Existing feature worktrees remain on their own branches when `dev` advances.
  Do not rebase or force-push published history merely to change the PR base.
- Bring upstream changes into `dev` through an integration worktree created
  from `origin/dev`: merge the synchronized `origin/main`, resolve conflicts,
  run appropriate validation, and open a PR to `dev`.
- Keep generated GDS/SPEF, build outputs, and dependency caches out of Git.
  Preserve wanted artifacts before removing a worktree; do not force cleanup
  without explicit authorization to discard its remaining files.
- At completion, report the worktree path, branch, changed files, checks run,
  PR/merge command, and cleanup command. See `docs/WORKTREE.md` for examples.

The existing V0 branch was created from the same upstream commit as `dev`.
PR #1 targets `dev`; it does not need a history rewrite for this migration.
