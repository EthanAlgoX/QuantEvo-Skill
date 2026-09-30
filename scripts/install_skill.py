#!/usr/bin/env python3
"""Install one self-contained canonical skill, preserving existing installs."""
import argparse
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path


def install(client, destination=None, upgrade=False):
    if destination is None:
        base = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))) if client == "codex" else Path.home()/".claude"
        destination = base/"skills"
    destination = Path(destination).expanduser().resolve()
    source = Path(__file__).resolve().parents[1]/"skills"/"quantevo"
    target = destination/"quantevo"
    if (target.exists() or target.is_symlink()) and not upgrade:
        raise FileExistsError(f"Existing skill preserved: {target}. Choose another --destination or move it before installing.")
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Install outside the canonical skill directory")
    if target.is_symlink():
        raise ValueError('Upgrade of a symlink is unsupported; preserve it and choose another destination')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".quantevo-install-", dir=destination) as staging:
        staged = Path(staging)/"quantevo"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        # Keep backups outside the skills root to avoid duplicate discovery.
        backup = None
        if upgrade and target.exists():
            if not target.is_dir() or not (target/'SKILL.md').is_file():
                raise ValueError('Existing target is not a skill directory')
            backup_root = destination.parent/'skill-backups'
            backup_root.mkdir(exist_ok=True)
            backup = backup_root/('quantevo-'+uuid.uuid4().hex[:12])
            target.rename(backup)
        elif target.exists() or target.is_symlink():
            raise FileExistsError(f"Existing skill preserved: {target}")
        try:
            staged.rename(target)
        except OSError:
            if backup:
                backup.rename(target)
            raise
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", choices=("codex", "claude"), required=True)
    parser.add_argument("--destination", type=Path, help="Custom skills parent directory")
    parser.add_argument('--upgrade', action='store_true', help='Replace an existing skill, preserving it outside the skills root')
    args = parser.parse_args()
    try:
        print(json.dumps({"installed": str(install(args.client, args.destination, args.upgrade))}))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
