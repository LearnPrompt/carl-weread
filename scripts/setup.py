#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.config import ContextConfig, VALID_MODES, write_config


def default_config_path() -> Path:
    return Path.home() / ".config" / "carl-weread" / "config.toml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure carl-weread context mode.")
    parser.add_argument("--mode", required=True, choices=sorted(VALID_MODES), help="context mode")
    parser.add_argument("--path", type=Path, help="Obsidian vault or notes folder path for obsidian/folder mode")
    parser.add_argument("--output", type=Path, default=default_config_path(), help="config file path")
    args = parser.parse_args()

    try:
        write_config(ContextConfig(mode=args.mode, path=args.path), args.output)
    except ValueError as exc:
        print(f"配置失败：{exc}", file=sys.stderr)
        return 2

    print(f"已写入配置：{args.output.expanduser()}")
    print("提示：API Key 可通过 scripts/setup_api_key.py 写入私有 key 文件，不会写入配置文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
