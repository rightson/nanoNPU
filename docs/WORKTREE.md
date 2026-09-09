# Local integration

Repository checkout:
`/Users/rightson/.codex/.chatgpt-projects/g-p-6a8a8951e6308191bf99e7b706a96146/tiny-transformer-npu`

Implementation worktree:
`/Users/rightson/.codex/.chatgpt-projects/g-p-6a8a8951e6308191bf99e7b706a96146/tiny-transformer-npu-v0-20260909b`

Branch: `codex/v0-reproduce-20260909b`.

Changes include the physical CU one-shot CONV fix, the adapted 4×4 system
testbench, pinned toolchain and simulation image, Make targets and Python
orchestration/acceptance checks, physical configuration overrides, and
validation documentation. The complete file list is available with:

```sh
git -C tiny-transformer-npu diff --name-only main...codex/v0-reproduce-20260909b
```

Run these commands from the parent project directory. Integration is local;
no remote repository or pull request has been created.

```sh
git -C tiny-transformer-npu merge --ff-only codex/v0-reproduce-20260909b
```

Build outputs and the PDK cache are ignored and are not included by merging.
Preserve any wanted outputs before cleanup, and stop active flows first.
The nested clean physical checkout must be removed before its parent:

```sh
v0_worktree="$PWD/tiny-transformer-npu-v0-20260909b"
git -C tiny-transformer-npu worktree remove --force "$v0_worktree/build/clean-physical-checkout"
git -C tiny-transformer-npu worktree remove --force "$v0_worktree/build/clean-standalone-checkout"
git -C tiny-transformer-npu worktree remove --force "$v0_worktree"
git -C tiny-transformer-npu branch -d codex/v0-reproduce-20260909b
```

Validation results and their limits are in [VALIDATION.md](VALIDATION.md).
