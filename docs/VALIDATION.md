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

The corrected RTL run `v0-20260910-000821-482000` uses a new input snapshot,
the same SKY130 PDK and original fixed die. Previous-run named ECO insertions
are removed by explicit flow overrides. OpenROAD terminated unexpectedly in
its nineteenth detailed-routing iteration after about 80 minutes in that step.
The last completed iteration had 781 violations. The log does not identify
the cause. This run failed and produced no accepted GDS/SPEF/STA bundle.

A clean detached checkout of `8c7c191` passed `make sim` (72/72), downloaded
and verified its own DEF input, and reached detailed routing in `make pnr`
(`v0-20260910-003243-665000`). This duplicate physical run was deliberately
stopped with exit 143 when the three concurrent experiments approached the
Docker VM memory limit. Its checkpoints are retained, but this is **not** a
successful clean-checkout `make sim && make pnr` acceptance run.

The separate `standalone-20260910-012100-744000` experiment enlarges the die
to 1,750 × 1,750 µm. Placement reports 22.218% utilization, compared with
76.223% for the original fixed die. Both configurations, and the clean
checkout, produce the same synthesis netlist SHA-256, 50,042 cells and
576,764.4128 µm² cell area. This confirms the floorplan comparison uses the
same synthesized logic; it does not establish final physical equivalence
or signoff. Detailed routing reached zero routing DRC. Its nine-corner
post-route STA found no setup violations, but the input path from
`gpio_bot_in[0]` has hold violations at the three slow PVT/extraction corners
(worst −0.273445 ns). There are also one max-cap and 15 max-slew violations
in the worst corner. These results do not satisfy the V0 acceptance gate.

The standalone configuration is now the default `make pnr`, with
post-global-route timing repair and 0.5 ns hold repair margin added. Original
SDC timing requirements remain unchanged. `STA_THREADS=2` limits concurrent
STA memory use. A new clean-checkout full run is required for this change.
The original geometry remains available as `make pnr-openframe`.
