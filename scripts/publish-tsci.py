#!/usr/bin/env python3
"""Stage the complete tracked project and publish it with the pinned tsci CLI.

Use --stage-only to inspect the package without publishing. A downloaded tsci
package can be republished using its manifest instead of a Git index.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "tsci-package-manifest.json"


def source_paths():
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT,
                            capture_output=True, text=True)
    if result.returncode == 0 and Path(result.stdout.strip()).resolve() == ROOT:
        paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        # tsci itself excludes dotfiles. Only indexed files are copied, so local
        # toolchains, credentials, caches and ignored downloads never enter staging.
        return sorted(p for p in paths if p and not any(x.startswith(".") for x in PurePosixPath(p).parts))
    manifest = json.loads((ROOT / MANIFEST).read_text())
    return sorted(manifest["files"])


def digest(path, content):
    if path == "package.json":
        package = json.loads(content)
        # tsci increments the staged release version; every other field is checked.
        package.pop("version", None)
        content = json.dumps(package, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(content).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-only", action="store_true")
    args = parser.parse_args()
    paths = source_paths()
    for name in paths:
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"Invalid package path: {name}")
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"Missing or symlinked package input: {name}")
    helpers = [name for name in paths if name.startswith(("scripts/", "firmware/", "enclosure/"))
               and Path(name).suffix in {".py", ".mjs", ".sh"}]
    if "scripts/publish-tsci.py" not in paths or "scripts/refresh-supplier-stock.mjs" not in paths:
        raise SystemExit("The publishing and stock helpers must be tracked before staging")

    fab = ROOT / "manufacturing"
    circuit_bytes = (fab / "design.circuit.json").read_bytes()
    circuit = json.loads(circuit_bytes)
    diagnostics = [e for e in circuit if "error" in e["type"] or "warning" in e["type"]]
    if diagnostics:
        raise SystemExit("Validate the fabrication circuit before publishing")
    provenance = json.loads((fab / "checks/routing-provenance.json").read_text())
    if provenance["circuit_sha256"] != hashlib.sha256(circuit_bytes).hexdigest():
        published = json.loads((ROOT / MANIFEST).read_text()) if (ROOT / MANIFEST).is_file() else {}
        canonical = json.dumps(circuit, separators=(",", ":")).encode()
        if (published.get("fabrication_circuit_original_sha256") != provenance["circuit_sha256"]
                or published.get("fabrication_circuit_canonical_sha256") != hashlib.sha256(canonical).hexdigest()):
            raise SystemExit("Fabrication circuit does not match its routing audit")
    for name, expected in provenance["source_files_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            # A registry download has a CLI-assigned version. Its manifest still
            # checks every other package field against the uploaded project.
            if name == "package.json" and (ROOT / MANIFEST).is_file():
                published = json.loads((ROOT / MANIFEST).read_text())
                if digest(name, (ROOT / name).read_bytes()) == published["files"][name]:
                    continue
            raise SystemExit(f"Design input changed since fabrication validation: {name}")
    if hashlib.sha256((ROOT / "tscircuit.config.ts").read_bytes()).hexdigest() != provenance["config_sha256"]:
        raise SystemExit("Runtime configuration changed since fabrication validation")

    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="tsci-package-", dir=output))
    hashes = {}
    for name in paths:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
        if name == "manufacturing/design.circuit.json":
            # The registry's per-file request limit rejects the formatted JSON.
            # Keep every record and value, changing only its whitespace.
            target.write_text(json.dumps(circuit, separators=(",", ":")))
            if json.loads(target.read_text()) != circuit:
                raise SystemExit("Fabrication JSON changed during minification")
        hashes[name] = digest(name, target.read_bytes())
    manifest = {"format_version": 1, "hash_algorithm": "sha256",
                "package_json_hash_excludes": ["version"],
                "files": hashes, "helper_scripts": helpers,
                "fabrication_circuit_original_sha256": provenance["circuit_sha256"],
                "fabrication_circuit_canonical_sha256": hashlib.sha256(
                    json.dumps(circuit, separators=(",", ":")).encode()).hexdigest()}
    (stage / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    dist = stage / "dist/index"
    dist.mkdir(parents=True)
    (dist / "circuit.json").write_text(json.dumps(circuit, separators=(",", ":")))
    shutil.copy2(fab / "pcb-top.svg", dist / "pcb.svg")
    shutil.copy2(fab / "schematic-1-usb-power.svg", dist / "schematic.svg")
    (output / "tsci-package-path.txt").write_text(str(stage) + "\n")
    print(f"Staged {len(paths)} source files and {len(helpers)} helper scripts at {stage}", flush=True)
    if not args.stage_only:
        subprocess.run(["bun", str(ROOT / "node_modules/.bin/tsci"), "push", "--compress", "--include-dist"],
                       cwd=stage, check=True)


if __name__ == "__main__":
    main()
