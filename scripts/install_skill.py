#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

IGNORE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}
IGNORE_FILES = {".env"}


def default_target() -> Path:
    hermes_home = Path.home() / ".hermes"
    return hermes_home / "skills" / "carl-weread"


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts) or path.name in IGNORE_FILES or path.suffix == ".pyc"


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        if should_ignore(rel):
            continue
        dest = target / rel
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the full carl-weread repo as a Hermes skill directory.")
    parser.add_argument("--target", type=Path, default=default_target(), help="Target skill directory")
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1]
    target = args.target.expanduser()
    copy_tree(source, target)
    print(f"已安装完整 skill 目录：{target}")
    print("下一步：在目标 Hermes 环境运行 scripts/setup_api_key.py，然后运行 scripts/today_live.py。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
