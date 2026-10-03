# Validation record

V0 executable milestone status: **achieved**. Complete electrical signoff
remains incomplete because of the residual limits reported below.

Current clean-checkout run: `standalone-20260910-023402-179000`, source
commit `ea60b61`, command `make check && make sim && make pnr`, exit **0**.
It uses the standalone floorplan and precise UART asynchronous-input
exception. Verified final results:

| Check | Result |
| --- | --- |
| Runner checks | 8 passed |
| RTL simulation | 9 cases × 2 seeds, 72/72 word comparisons |
| Post-route STA | 9 corners; 0 setup and 0 hold violations |
| Worst setup / hold slack | +7.7160 ns / +0.0986 ns |
| Routing DRC / antenna / critical disconnected pins | 0 / 0 / 0 |
| Magic DRC | 0 errors |
| KLayout DRC | 0 errors |
| Netgen LVS | 0 errors; device, net and pin comparisons passed |
| Max capacitance / max slew / max fanout | 1 / 15 / 2 violations |

LibreLane's default corner policy makes the max-slew/max-cap checks non-fatal;
fanout violations are also reported in STA. This fork does not claim complete electrical signoff or
CDC/MTBF validation. The fresh [STA summary](evidence/v0/sta-summary.rpt)
and [input hashes](evidence/v0/input-manifest.json) are retained.
The [electrical report](evidence/v0/electrical-violations.rpt) identifies
`fanout8135`, a `buf_1` driven by `u_npu_sys.imem_wr_data[26]`, as the driver
associated with the capacitance and slew violations. Two additional nets
exceed the fanout limit. These are concrete follow-up closure items.

The accepted bundle contains a newly generated **150,927,428-byte GDS**,
three extracted SPEF files and the nine-corner STA summary. Artifact sizes
and SHA-256 hashes are in [artifacts.json](evidence/v0/artifacts.json), alongside
the [successful invocation receipt](evidence/v0/pnr-success.json),
[provenance record](evidence/v0/provenance.json) and [LVS report](evidence/v0/lvs.rpt).
The completed attempt was copied from the clean checkout to the implementation
worktree's `build/attempts/standalone-20260910-023402-179000`; artifact and input
hash verification passed again there. Only pinned dependency caches were
preseeded in the clean checkout. Later changes are documentation/evidence and testbench trailing-whitespace
normalization only; physical inputs and flow scripts are unchanged.
`make sim` was rerun after formatting and again passed 72/72 comparisons.

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
or signoff. Detailed routing reached zero routing DRC and zero antenna errors.
Magic DRC, KLayout DRC and Netgen LVS all passed with zero errors. Its nine-corner
post-route STA found no setup violations, but the input path from
`gpio_bot_in[0]` was reported with hold violations at the three slow PVT/extraction corners
(worst −0.273445 ns). There are also one max-cap and 15 max-slew violations
in the worst corner. These results do not satisfy the V0 acceptance gate.

The standalone configuration is now the default `make pnr`.
`STA_THREADS=2` limits concurrent STA memory use. The original geometry
remains available as `make pnr-openframe`.

## UART clock-domain correction

A clean checkout of `cb64487` passed eight checks and 72/72 simulation words.
Its physical run `standalone-20260910-015256-807000` tried a global 0.5 ns
hold-repair margin. This added over 5,000 buffers and was deliberately stopped
after structural inspection identified a constraint-modeling error. No output
from this experiment is accepted as a completed physical implementation.

The failed endpoint `_92312_/D` in the first standalone routed netlist belongs
to `u_npu_sys.u_uart_apb.u_bridge.u_uart_rx.rx_sync1`, the first register of
the existing two-register UART synchronizer. UART RX has no fixed clock phase.
`constraints/uart_async.sdc` therefore excepts only the external pin to that
first D pin, using a retained RTL net name to resolve the register. Both PNR
and signoff snapshots use this exception. Global hold-margin overrepair is
removed; the original clock, other I/O requirements and internal register
paths remain constrained.

An OpenROAD check against the original routed ODB and maximum-RC SPEF at
`ss_100C_1v60` reproduced the −0.273445 ns path before the exception, found
no timed path from the UART port to the first D pin afterward, and asserted
that the synchronizer's internal path remains timed. Its internal hold slack
was +2.194736 ns and setup slack +46.063087 ns in that check. See
[`evidence/uart-async-constraint-check.log`](evidence/uart-async-constraint-check.log).
This establishes the exception's scope, not metastability MTBF or complete CDC
signoff. The successful fresh flow recorded above validates the corrected
constraints through the full V0 execution chain.
