# Tiny Transformer NPU — V0

An executable ASIC-flow learning baseline forked from
[Ammar-Wahidi/NPU](https://github.com/Ammar-Wahidi/NPU), pinned at
`f876e8e236aed42e3ca4627ca8e43f8d44f1a086`.

V0 uses the actual **4×4 INT8 physical RTL**, SKY130 and a pinned
LibreLane/OpenROAD/Yosys container. It fixes a CONV replay bug and models the
asynchronous UART input with a precise first-synchronizer timing exception.
DFT, ATPG and Transformer workloads are subsequent milestones.

**V0 executable checkpoint verified:** a clean checkout completed simulation
and the full physical flow. Setup/hold, routing, DRC and LVS pass; residual
capacitance, slew and fanout limits remain documented in the validation record.

```sh
make setup
make sim
make pnr
make artifacts
```

The default is a **1,750 × 1,750 µm standalone die**. It does not fit the
original OpenFrame slot. `make pnr-openframe` retains the original-size
experiment; that geometry has not passed this fork's V0 acceptance gate.

- [Setup, design choices and limitations](docs/V0.md)
- [Measured validation results and evidence](docs/VALIDATION.md)
- [工程判斷紀錄：control、clock domain、floorplan](docs/ENGINEERING_NOTES.md)
- [Local worktree, integration and cleanup](docs/WORKTREE.md)
- [Archived upstream README](docs/UPSTREAM_README.md)

The acceptance gate is a fresh checkout completing `make sim && make pnr`,
with newly generated GDS, three SPEF corners and post-route STA reports.
Archived upstream outputs are never substituted for generated results.
Successful flow execution is reported separately from residual electrical
violations and CDC/MTBF validation.

Apache-2.0; upstream attribution and [license](LICENSE) are retained.
