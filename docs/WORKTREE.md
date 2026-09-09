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
git -C tiny-transformer-npu worktree remove --force "$v0_worktree/build/clean-uart-checkout"
git -C tiny-transformer-npu worktree remove --force "$v0_worktree"
git -C tiny-transformer-npu branch -d codex/v0-reproduce-20260909b
```

Validation results and their limits are in [VALIDATION.md](VALIDATION.md).

## Changed files

Relative to the pinned upstream commit:

```text
.dockerignore
.gitignore
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
