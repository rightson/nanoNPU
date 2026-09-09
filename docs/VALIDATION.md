# Validation record

V0 milestone status: **not yet achieved**.

Environment: Apple Silicon macOS host, Docker 29.6.1 / Linux aarch64,
8 container CPUs, 12,528,664,576 bytes container memory.

Observed tool versions from the pinned physical container:

- LibreLane 3.0.5
- Verilator 5.044
- Yosys 0.62, commit `7326bb7d6641500ecb285c291a54a662cb1e76cf`
- OpenROAD `dcf36133a369abc8f3c5e5738cd4d82e4903c0e0`
- SKY130 open_pdks revision `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`

The physical container passed the tool version check. The first simulation
attempt parsed RTL but failed at C++ compilation because the upstream image
does not provide `make` on PATH. `Dockerfile.sim` adds explicit build tools.

## Simulation

- Original upstream physical RTL + original 4×4 testbench, seed 1:
  **28 passed, 8 failed**; simulator exit 0 correctly rejected by the runner.
- Adapted fused-ISA testbench alone: **28 passed, 8 failed**. Tracing exposed
  the second CONV execution overwriting the first result.
- One-shot CONV fix + fused-ISA testbench + control invariants:
  **seed 1: 36/36; seed 2: 36/36**. Golden arithmetic was not relaxed.
- Clean detached checkout of `07c85d5`: `make check && make sim` passed;
  each seed again passed 36/36 with no existing simulation build directory.
- `make check`: eight acceptance-check tests pass. They cover watchdog exits,
  incomplete runs, stale summaries, simulator crashes, missing extraction
  corners, modified input snapshots and LFS pointers masquerading as outputs.

Raw original and clean-checkout simulation transcripts are versioned in
[`evidence/`](evidence/).

## Physical implementation

The unmodified RTL run `v0-20260909-235800` passed synthesis, placement,
CTS and initial global routing, reaching post-global-route repair. It was
stopped because simulation had identified a functional bug; its physical
checkpoints do not validate the corrected RTL.

The corrected RTL is being rebuilt from a new input snapshot using the same
SKY130 PDK and fixed die. Previous-run named ECO insertions are removed by
explicit flow overrides. Final GDS/SPEF/STA and clean-checkout physical validation remain pending.
