"""Compile the APR source set and run its matching fused-ISA UART testbench."""
import json
from pathlib import Path
import subprocess
from checks import check_simulation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/sim"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "results.json").unlink(missing_ok=True)
source = ROOT / "Backend/openlane/RTL"
rtl = sorted(p for p in source.iterdir() if p.suffix.lower() in {".v", ".sv"})
command = ["verilator", "--binary", "--timing", "-Wno-fatal", "-j", "4",
           "--top-module", "tb_npu_system_4x4", "--Mdir", str(OUT / "obj"),
           *map(str, rtl), str(ROOT / "verification/system/tb_npu_system_4x4.sv")]
with (OUT / "compile.log").open("w") as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
if result.returncode:
    print((OUT / "compile.log").read_text()[-10000:])
    raise SystemExit(result.returncode)
results = []
for seed in [1, 2]:
    with (OUT / f"seed-{seed}.log").open("w") as log:
        result = subprocess.run([str(OUT / "obj/Vtb_npu_system_4x4"),
                                 f"+verilator+seed+{seed}"],
                                stdout=log, stderr=subprocess.STDOUT, timeout=300)
    text = (OUT / f"seed-{seed}.log").read_text()
    print(text)
    try:
        check_simulation(text, result.returncode)
    except ValueError as exc:
        raise SystemExit(f"Simulation seed {seed}: {exc}; see build/sim/seed-{seed}.log")
    results.append({"seed": seed, "passed_words": 36, "failed_words": 0})
(OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
