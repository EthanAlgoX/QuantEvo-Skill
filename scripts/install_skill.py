#!/usr/bin/env python3
"""Install one self-contained canonical skill, preserving existing installs."""
import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path


def install(client, destination=None):
    if destination is None:
        base = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))) if client == "codex" else Path.home()/".claude"
        destination = base/"skills"
    destination = Path(destination).expanduser().resolve()
    source = Path(__file__).resolve().parents[1]/"skills"/"quantevo"
    target = destination/"quantevo"
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Existing skill preserved: {target}. Choose another --destination or move it before installing.")
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Install outside the canonical skill directory")
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".quantevo-install-", dir=destination) as staging:
        staged = Path(staging)/"quantevo"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        # Recheck before the rename; installer is intended for a single local writer.
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Existing skill preserved: {target}")
        staged.rename(target)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", choices=("codex", "claude"), required=True)
    parser.add_argument("--destination", type=Path, help="Custom skills parent directory")
    args = parser.parse_args()
    try:
        print(json.dumps({"installed": str(install(args.client, args.destination))}))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
