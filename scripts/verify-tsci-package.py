#!/usr/bin/env python3
"""Download a published release, verify its source manifest and rebuild cleanly."""
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

API = "https://registry-api.tscircuit.com/"
PACKAGE = "rushabhcodes/usb-c-e-paper-display"


def download(url):
    # Public endpoints: no credentials are sent to redirected object storage.
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Exact tsci version, for example 1.3.3")
    parser.add_argument("--directory", type=Path, help="Empty destination; defaults to a new cache directory")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    cache = Path.home() / ".cache"
    cache.mkdir(exist_ok=True)
    root = args.directory or Path(tempfile.mkdtemp(prefix="epaper-published-", dir=cache))
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise SystemExit("Use an empty directory for the clean rebuild")
    name = f"{PACKAGE}@{args.version}"
    url = API + "package_files/list?package_name_with_version=" + urllib.parse.quote(name, safe="")
    rows = json.loads(download(url))["package_files"]
    # Generated registry output is deliberately not downloaded. Native routing
    # must recreate dist from the published TSX and the pinned dependency patch.
    rows = [row for row in rows if not row["file_path"].startswith("dist/")]

    def fetch(row):
        relative = PurePosixPath(row["file_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid registry path: {relative}")
        target = root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(download(API + "package_files/download?package_file_id=" +
                                   urllib.parse.quote(row["package_file_id"], safe="")))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, rows))
    manifest = json.loads((root / "tsci-package-manifest.json").read_text())
    if manifest["format_version"] != 1 or manifest["package_json_hash_excludes"] != ["version"]:
        raise SystemExit("Unsupported package manifest")
    for name, expected in manifest["files"].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"Invalid manifest path: {name}")
        content = (root / name).read_bytes()
        if name == "package.json":
            package = json.loads(content)
            if package["version"] != args.version:
                raise SystemExit("Downloaded package version does not match requested release")
            package.pop("version")
            content = json.dumps(package, sort_keys=True, separators=(",", ":")).encode()
        if hashlib.sha256(content).hexdigest() != expected:
            raise SystemExit(f"Published source differs from manifest: {name}")
    helpers = manifest["helper_scripts"]
    if "scripts/refresh-supplier-stock.mjs" not in helpers:
        raise SystemExit("Stock refresh helper was omitted")
    if any((root / name).exists() for name in [".git", "node_modules", "dist"]):
        raise SystemExit("Clean checkout unexpectedly contains build state")
    print(f"Verified {len(manifest['files'])} source hashes and {len(helpers)} helpers in {root}", flush=True)
    logs = root / "verification-logs"
    logs.mkdir()
    commands = [
        ("install", ["bun", "install", "--frozen-lockfile"]),
        ("repackage", ["python", "scripts/publish-tsci.py", "--stage-only"]),
        ("stock", ["bun", "run", "refresh:stock"]),
        ("typecheck", ["bun", "run", "typecheck"]),
        ("native-tests", ["bun", "test", "tests"]),
        ("firmware-tests", ["python", "firmware/test.py"]),
        ("netlist", ["bun", "run", "check:netlist"]),
        ("schematic-placement", ["bun", "run", "check:schematic-placement"]),
        ("placement", ["bun", "run", "check:placement"]),
        ("build", ["bun", "run", "build", "--autorouter-debug", "--autorouter-debug-dir",
                   "dist/native-routing-final-release", "--autorouter-dump-srj", "all", "--autorouter-threads", "1"]),
        ("release-checks", ["python", "scripts/verify-release.py"]),
    ]
    for label, command in commands:
        print(f"Running {label}: {' '.join(command)}", flush=True)
        with (logs / f"{label}.log").open("w") as stream:
            subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, check=True)
        print(f"PASS {label}", flush=True)
    built = json.loads((root / "dist/index/circuit.json").read_text())
    fabrication = json.loads((root / "manufacturing/design.circuit.json").read_text())
    physical = lambda data: [e for e in data if e["type"].startswith(("pcb_", "cad_"))
                             and "error" not in e["type"] and "warning" not in e["type"]]
    if physical(built) != physical(fabrication):
        raise SystemExit("Rebuilt PCB/CAD differs from the fabrication release")
    report = {"result": "PASS", "package": PACKAGE, "version": args.version,
              "directory": str(root), "source_files_verified": len(manifest["files"]),
              "helper_scripts_verified": len(helpers), "downloaded_dist": False,
              "commands_passed": [label for label, _ in commands],
              "pcb_cad_matches_fabrication": True, "circuit_errors": 0, "circuit_warnings": 0}
    target = args.report or root / "verification-report.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
