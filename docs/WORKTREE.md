# Branch and worktree workflow

`main` tracks the upstream baseline. `dev` is this fork's default branch and
integration line. Feature branches start from `origin/dev` and return through
PRs to `dev`. Do not merge this project's development work into `main`.

Updating `main` does not update `dev` or existing feature branches. Upstream
integration remains an explicit, tested operation; branch separation does not
eliminate merge conflicts.

## Start new work

From a checkout of this repository, choose a new task name and sibling path:

```sh
git fetch origin dev
git worktree add -b codex/task-name ../nanoNPU-task-name origin/dev
```

Replace `task-name` with the task's name. If either the branch or path exists,
append a timestamp suffix. Work inside the new worktree, commit and validate,
then publish:

```sh
git push -u origin HEAD
gh pr create --repo rightson/nanoNPU --base dev
```

Keep `dev` at reviewed checkpoints; use tags to identify validated milestones.
Until V0 PR #1 is merged, `dev` contains only the original upstream baseline.
Tasks that depend on the V0 implementation should start after that merge.

## Integrate upstream updates

In the primary checkout, with a clean working directory on `main`:

```sh
git fetch origin
git fetch upstream
git merge --ff-only origin/main
git merge --ff-only upstream/main
git push origin main
```

Stop if either fast-forward fails and inspect the divergence; do not reset or
force-push. From a feature worktree created from `origin/dev` as above, merge
`origin/main`, resolve conflicts, run the checks appropriate to the changes,
and open a PR to `dev`. RTL, constraints, or physical-flow changes may require
a fresh simulation and RTL-to-GDS validation.

## V0 integration

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
git -C tiny-transformer-npu diff --name-only origin/dev...codex/v0-reproduce-20260909b
```

V0 is published as [PR #1](https://github.com/rightson/nanoNPU/pull/1)
with `dev` as its base. The branch was created from the same commit as `dev`,
so this base change requires no rebase. When ready to merge the reviewed PR:

```sh
gh pr merge 1 --repo rightson/nanoNPU --merge
```

Build outputs and the PDK cache are ignored and are not included by merging.
Preserve wanted outputs before cleanup, stop active flows, and fetch the merged
`origin/dev` first. Run the following from the parent project directory. Nested
clean checkouts must be removed before their parent. These commands deliberately
refuse to discard remaining files; inspect and archive them if Git refuses.

```sh
v0_worktree="$PWD/tiny-transformer-npu-v0-20260909b"
git -C tiny-transformer-npu fetch origin dev
git -C tiny-transformer-npu worktree remove "$v0_worktree/build/clean-physical-checkout"
git -C tiny-transformer-npu worktree remove "$v0_worktree/build/clean-standalone-checkout"
git -C tiny-transformer-npu worktree remove "$v0_worktree/build/clean-uart-checkout"
git -C tiny-transformer-npu worktree remove "$v0_worktree"
git -C tiny-transformer-npu branch -d codex/v0-reproduce-20260909b
```

Validation results and their limits are in [VALIDATION.md](VALIDATION.md).

## Changed files

Relative to the pinned upstream commit:

```text
.dockerignore
.gitignore
AGENTS.md
Backend/openlane/RTL/CU.SV
Dockerfile.sim
Makefile
README.md
constraints/uart_async.sdc
docs/ENGINEERING_NOTES.md
docs/UPSTREAM_README.md
docs/V0.md
docs/VALIDATION.md
docs/WORKTREE.md
docs/evidence/fixed-simulation-seed-1.txt
docs/evidence/fixed-simulation-seed-2.txt
docs/evidence/simulation-results.json
docs/evidence/standalone-before-uart-exception/input-manifest.json
docs/evidence/standalone-before-uart-exception/metrics.json
docs/evidence/standalone-before-uart-exception/sta-summary.rpt
docs/evidence/synthesis-reproducibility.json
docs/evidence/uart-async-constraint-check.log
docs/evidence/upstream-simulation-seed-1.txt
docs/evidence/v0/artifacts.json
docs/evidence/v0/electrical-violations.rpt
docs/evidence/v0/flow-summary.txt
docs/evidence/v0/input-manifest.json
docs/evidence/v0/lvs.rpt
docs/evidence/v0/magic-drc.rpt
docs/evidence/v0/metrics.json
docs/evidence/v0/pnr-success.json
docs/evidence/v0/provenance.json
docs/evidence/v0/sta-summary.rpt
physical/librelane/standalone-overrides.json
physical/librelane/v0-overrides.json
scripts/checks.py
scripts/sim.py
scripts/test_artifacts.py
scripts/test_checks.py
scripts/v0.py
toolchain.lock.json
verification/system/tb_npu_system_4x4.sv
```

## Validation commands

The clean checkout completed `make check && make sim && make pnr` with exit 0.
The UART constraint probe also passed, and `scripts/v0.py artifacts` passed
again after copying the completed attempt into this worktree. See
[VALIDATION.md](VALIDATION.md) for counts, provenance and electrical residuals.
