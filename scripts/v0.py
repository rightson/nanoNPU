"""V0 orchestration; upstream outputs under Final/ are never accepted as results."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "toolchain.lock.json").read_text())
BUILD = ROOT / "build"


def run(args, **kwargs):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, check=True, cwd=ROOT, **kwargs)


def container(args, image=None):
    return run(["docker", "run", "--rm", "--init", "--mount",
                f"type=bind,src={ROOT},dst=/work", "--workdir", "/work",
                "--entrypoint", "bash", image or LOCK["image"], "-c",
                # Preserve the image PATH; pass commands as argv without interpolation.
                'exec "$@"', "v0", *args])


def prepare(target=None, standalone=False):
    source = ROOT / "Backend/openlane"
    target = target or BUILD / "design"
    target.mkdir(parents=True, exist_ok=True)
    for name in ["RTL", "config.json", "pnr.sdc", "signoff.sdc"]:
        src, dst = source / name, target / name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    config = json.loads((target / "config.json").read_text())
    config.update(json.loads((ROOT / "physical/librelane/v0-overrides.json").read_text()))
    if standalone:
        config.update(json.loads((ROOT / "physical/librelane/standalone-overrides.json").read_text()))
    (target / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    if standalone:
        return target
    floorplan = BUILD / "inputs/project_macro.def"
    if not floorplan.exists():
        floorplan.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://media.githubusercontent.com/media/Ammar-Wahidi/NPU/"
               + LOCK["upstream_commit"]
               + "/Backend/openlane/fixed_dont_change/project_macro.def")
        tmp = floorplan.with_suffix(".download")
        with urllib.request.urlopen(url, timeout=120) as response, tmp.open("wb") as out:
            shutil.copyfileobj(response, out)
        tmp.replace(floorplan)
    data = floorplan.read_bytes()
    if len(data) != LOCK["def_size"] or hashlib.sha256(data).hexdigest() != LOCK["def_sha256"]:
        raise RuntimeError("DEF input checksum mismatch; remove build/inputs/project_macro.def and retry")
    (target / "fixed_dont_change").mkdir(exist_ok=True)
    shutil.copy2(floorplan, target / "fixed_dont_change/project_macro.def")
    return target


def artifacts():
    receipt = json.loads((BUILD / "pnr-success.json").read_text())
    folder = ROOT / receipt["run_dir"]
    snapshot = folder.parent.parent
    for name, expected in receipt["input_manifest"].items():
        actual = hashlib.sha256((snapshot / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Physical input changed after launch: {name}")
    found = {}
    for label, pattern in {"gds": "final/gds/*.gds", "spef": "final/spef/**/*.spef",
                           "sta": "*-openroad-stapostpnr*/summary.rpt"}.items():
        paths = sorted(p for p in folder.glob(pattern) if p.is_file() and p.stat().st_size)
        if not paths:
            raise RuntimeError(f"Missing fresh {label} artifacts in {folder}")
        if label == "spef" and len(paths) != 3:
            raise RuntimeError("Expected three extracted SPEF corners (min, nom, max)")
        for path in paths:
            with path.open("rb") as stream:
                if stream.read(100).startswith(b"version https://git-lfs.github.com/spec/v1"):
                    raise RuntimeError(f"LFS pointer is not a generated artifact: {path}")
        found[label] = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
                         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    (BUILD / "artifacts.json").write_text(json.dumps(found, indent=2) + "\n")
    print(json.dumps(found, indent=2))


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    if command == "doctor":
        run(["docker", "info", "--format", "{{.ServerVersion}} {{.Architecture}}"])
        container(["bash", "-c", "set -e; librelane --version; verilator --version; yosys -V; openroad -version"])
    elif command == "setup":
        run(["docker", "pull", LOCK["image"]])
        prepare()
    elif command == "sim":
        run(["docker", "build", "-f", "Dockerfile.sim", "-t", LOCK["sim_image"], "."])
        container(["python3", "scripts/sim.py"], image=LOCK["sim_image"])
    elif command in {"pnr", "pnr-standalone"}:
        (BUILD / "pnr-success.json").unlink(missing_ok=True)
        (BUILD / "artifacts.json").unlink(missing_ok=True)
        standalone = command == "pnr-standalone"
        tag = ("standalone-" if standalone else "v0-") + time.strftime("%Y%m%d-%H%M%S") + f"-{time.time_ns() % 1000000:06d}"
        target = prepare(BUILD / "attempts" / tag, standalone=standalone)
        manifest = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(target.rglob("*")) if p.is_file()}
        (target / "input-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        container(["python3", "-m", "librelane", "--pdk-root", "/work/.cache/pdk",
                   "--pdk", LOCK["pdk"], "--scl", LOCK["scl"],
                   "--jobs", "8", "--run-tag", tag, str((target / "config.json").relative_to(ROOT))])
        (BUILD / "pnr-success.json").write_text(json.dumps({
            "run_dir": str((target / "runs" / tag).relative_to(ROOT)),
            "input_manifest": manifest, "toolchain": LOCK}, indent=2) + "\n")
        artifacts()
    elif command == "artifacts":
        artifacts()
    else:
        raise RuntimeError(f"Unknown command {command}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        sys.exit(str(exc))
